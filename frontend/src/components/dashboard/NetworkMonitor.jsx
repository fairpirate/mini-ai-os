import React from 'react';
import { motion } from 'framer-motion';
import { Globe, ArrowUp, ArrowDown } from 'lucide-react';
import { useSocketStore } from '../../store/socketStore';

const NetworkBar = ({ value, label, icon: Icon, color }) => {
  // Max scale 5MB/s for visualization
  const percent = Math.min(100, (value / 5120) * 100);

  return (
    <div className="flex-1">
      <div className="flex justify-between items-center mb-1">
        <div className="flex items-center gap-1.5">
          <Icon className={`w-3 h-3 ${color}`} />
          <span className="text-[10px] text-gray-500 uppercase tracking-wider">{label}</span>
        </div>
        <span className={`text-xs font-mono font-bold ${color}`}>{value.toFixed(1)} <span className="text-[9px] opacity-50">KB/s</span></span>
      </div>
      <div className="h-1 bg-white/5 rounded-full overflow-hidden relative">
        <motion.div 
          className={`absolute inset-y-0 left-0 ${color.replace('text', 'bg')}`}
          animate={{ width: `${percent}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
    </div>
  );
};

export const NetworkMonitor = () => {
  const { systemStats } = useSocketStore();
  const net = systemStats?.network || { sent_kbps: 0, recv_kbps: 0 };

  return (
    <div className="glass-panel p-4 flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <Globe className="w-4 h-4 text-jarvis-highlight" />
        <h3 className="text-xs font-bold uppercase tracking-widest neon-text">Link Telemetry</h3>
      </div>
      
      <div className="flex flex-col gap-4">
        <NetworkBar 
          label="Uplink" 
          value={net.sent_kbps} 
          icon={ArrowUp} 
          color="text-jarvis-highlight" 
        />
        <NetworkBar 
          label="Downlink" 
          value={net.recv_kbps} 
          icon={ArrowDown} 
          color="text-jarvis-success" 
        />
      </div>

      <div className="grid grid-cols-2 gap-2 pt-2 border-t border-white/5">
        <div className="text-[9px] font-mono">
          <div className="text-gray-600 mb-0.5">LATENCY</div>
          <div className="text-jarvis-highlight">12ms</div>
        </div>
        <div className="text-[9px] font-mono">
          <div className="text-gray-600 mb-0.5">PACKET LOSS</div>
          <div className="text-jarvis-highlight">0.00%</div>
        </div>
      </div>
    </div>
  );
};
