import psutil
import time
import asyncio
from typing import Dict, Any
from .logging import logger
from ..engine.memory import memory_manager

class MetricsService:
    """
    Collects system and AI performance metrics for the JARVIS HUD.
    """
    def __init__(self):
        self.start_time = time.time()
        self._last_network_bytes = psutil.net_io_counters()
        self._last_network_time = time.time()
        
        # AI Specific Metrics (populated by OllamaService)
        self.ai_latency_history = []
        self.tokens_per_sec_history = []
        self.total_generations = 0

    def get_system_stats(self) -> Dict[str, Any]:
        """Returns current CPU, RAM, and Network stats."""
        try:
            # CPU and RAM
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            
            # Network Speed Calculation
            current_net = psutil.net_io_counters()
            current_time = time.time()
            dt = current_time - self._last_network_time
            
            bytes_sent = (current_net.bytes_sent - self._last_network_bytes.bytes_sent) / dt
            bytes_recv = (current_net.bytes_recv - self._last_network_bytes.bytes_recv) / dt
            
            self._last_network_bytes = current_net
            self._last_network_time = current_time
            
            # Memory DB Stats
            mem_db_stats = memory_manager.get_stats()
            
            return {
                "cpu": {
                    "percent": cpu_percent,
                    "cores": psutil.cpu_count()
                },
                "memory": {
                    "percent": memory.percent,
                    "used": memory.used,
                    "total": memory.total,
                    "db_docs": mem_db_stats.get("long_term", 0) + mem_db_stats.get("project", 0)
                },
                "network": {
                    "sent_kbps": bytes_sent / 1024,
                    "recv_kbps": bytes_recv / 1024
                },
                "uptime": time.time() - self.start_time
            }
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return {}

    def record_ai_performance(self, latency: float, tokens: int):
        """Records performance of a single LLM generation."""
        self.total_generations += 1
        tps = tokens / latency if latency > 0 else 0
        
        self.ai_latency_history.append(latency)
        self.tokens_per_sec_history.append(tps)
        
        # Keep last 100
        if len(self.ai_latency_history) > 100:
            self.ai_latency_history.pop(0)
            self.tokens_per_sec_history.pop(0)

    def get_ai_stats(self) -> Dict[str, Any]:
        """Returns aggregated AI performance stats."""
        avg_latency = sum(self.ai_latency_history) / len(self.ai_latency_history) if self.ai_latency_history else 0
        avg_tps = sum(self.tokens_per_sec_history) / len(self.tokens_per_sec_history) if self.tokens_per_sec_history else 0
        
        return {
            "avg_latency": avg_latency,
            "avg_tokens_per_sec": avg_tps,
            "total_calls": self.total_generations
        }

# Singleton instance
metrics_service = MetricsService()
