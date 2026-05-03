import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ScrollText, Terminal } from 'lucide-react';
import { useSocketStore } from '../../store/socketStore';

export const LiveLogs = () => {
  const { messages } = useSocketStore();
  
  // Filter for system messages or use a dedicated logs buffer if we had one
  // For now, we'll show system messages as logs
  const sysLogs = messages.filter(m => m.role === 'system').slice(-10);

  return (
    <div className="glass-panel flex-1 flex flex-col min-h-[150px] overflow-hidden">
      <div className="p-3 border-b border-white/5 flex items-center justify-between bg-white/5">
        <div className="flex items-center gap-2">
          <Terminal className="w-3.5 h-3.5 text-jarvis-highlight" />
          <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] text-gray-400">System Kernel Logs</h3>
        </div>
        <div className="flex gap-1">
          <div className="w-1.5 h-1.5 rounded-full bg-jarvis-success animate-pulse"></div>
          <div className="w-1.5 h-1.5 rounded-full bg-gray-700"></div>
          <div className="w-1.5 h-1.5 rounded-full bg-gray-700"></div>
        </div>
      </div>
      
      <div className="flex-1 p-3 font-mono text-[9px] overflow-y-auto scrollbar-hide space-y-1.5">
        <AnimatePresence mode="popLayout">
          {sysLogs.length === 0 ? (
            <div className="text-gray-600 italic">Waiting for kernel events...</div>
          ) : (
            sysLogs.map((log, i) => (
              <motion.div
                key={log.id || i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex gap-2 text-jarvis-highlight/80 group"
              >
                <span className="text-gray-700 select-none">[{new Date(log.timestamp).toLocaleTimeString([], { hour12: false })}]</span>
                <span className="text-gray-500 select-none">SYS:</span>
                <span className="group-hover:text-white transition-colors">{log.text}</span>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
      
      <div className="p-1 px-3 bg-jarvis-highlight/5 border-t border-white/5 flex justify-between items-center">
        <span className="text-[8px] text-gray-600 font-mono tracking-tighter uppercase">Buffer: 1024KB</span>
        <span className="text-[8px] text-jarvis-highlight font-mono animate-flicker">LOGGING_ACTIVE</span>
      </div>
    </div>
  );
};
