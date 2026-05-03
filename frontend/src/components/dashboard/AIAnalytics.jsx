import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, Zap, Gauge } from 'lucide-react';
import { useSocketStore } from '../../store/socketStore';

const MetricTile = ({ label, value, unit, icon: Icon, color }) => (
  <div className="flex-1 min-w-[100px] p-2 bg-white/5 border border-white/10 rounded-lg relative overflow-hidden group">
    <div className={`absolute top-0 right-0 p-1 opacity-20 group-hover:opacity-40 transition-opacity ${color}`}>
      <Icon className="w-6 h-6" />
    </div>
    <div className="relative z-10">
      <div className="text-[10px] uppercase tracking-widest text-gray-500 mb-1">{label}</div>
      <div className="flex items-baseline gap-1">
        <span className={`text-lg font-mono font-bold ${color}`}>{value}</span>
        <span className="text-[9px] text-gray-500 font-mono">{unit}</span>
      </div>
    </div>
    <div className={`absolute bottom-0 left-0 h-[2px] ${color.replace('text', 'bg')} transition-all duration-500`} style={{ width: '100%' }}></div>
  </div>
);

export const AIAnalytics = () => {
  const { aiMetrics } = useSocketStore();
  
  return (
    <div className="glass-panel p-4 flex flex-col gap-3">
      <div className="flex items-center gap-2 mb-1">
        <Cpu className="w-4 h-4 text-jarvis-highlight" />
        <h3 className="text-xs font-bold uppercase tracking-widest neon-text">Neural Performance</h3>
      </div>
      
      <div className="flex flex-wrap gap-2">
        <MetricTile 
          label="Latency" 
          value={aiMetrics.avg_latency.toFixed(2)} 
          unit="s" 
          icon={Zap} 
          color="text-jarvis-highlight" 
        />
        <MetricTile 
          label="Velocity" 
          value={aiMetrics.avg_tokens_per_sec.toFixed(1)} 
          unit="t/s" 
          icon={Gauge} 
          color="text-jarvis-success" 
        />
        <MetricTile 
          label="Total Synapse" 
          value={aiMetrics.total_calls} 
          unit="ops" 
          icon={Cpu} 
          color="text-purple-500" 
        />
      </div>

      <div className="mt-2 p-2 bg-black/40 rounded border border-white/5 text-[9px] font-mono text-gray-500 leading-tight">
        <div className="flex justify-between mb-1">
          <span>Engine Status</span>
          <span className="text-jarvis-success animate-pulse">OPTIMIZED</span>
        </div>
        <div className="flex justify-between">
          <span>Model Context</span>
          <span>4096 / 32768</span>
        </div>
      </div>
    </div>
  );
};
