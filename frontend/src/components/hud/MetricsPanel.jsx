import React from 'react';
import { motion } from 'framer-motion';
import { Cpu, HardDrive, Wifi, WifiOff } from 'lucide-react';

export const MetricsPanel = ({ isConnected }) => {
  return (
    <div className="glass-panel p-4 flex flex-col gap-4">
      <h2 className="neon-text font-semibold uppercase tracking-wider text-sm flex items-center gap-2">
        <Cpu className="w-4 h-4" /> System Telemetry
      </h2>
      
      <div className="space-y-4">
        {/* CPU Metric */}
        <div>
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>Neural Core</span>
            <span className="text-jarvis-highlight">{isConnected ? 'Active' : 'Offline'}</span>
          </div>
          <div className="h-1.5 w-full bg-black/50 rounded overflow-hidden">
            <motion.div 
              className={`h-full ${isConnected ? 'bg-jarvis-highlight' : 'bg-gray-600'}`}
              initial={{ width: 0 }}
              animate={{ width: isConnected ? '42%' : '0%' }}
              transition={{ duration: 1 }}
            />
          </div>
        </div>
        
        {/* Network Status */}
        <div className="flex items-center gap-3 pt-2 border-t border-jarvis-border">
          {isConnected ? (
            <>
              <Wifi className="w-4 h-4 text-jarvis-success" />
              <span className="text-xs text-jarvis-success tracking-widest uppercase">Uplink Active</span>
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4 text-jarvis-alert" />
              <span className="text-xs text-jarvis-alert tracking-widest uppercase">Uplink Disconnected</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
