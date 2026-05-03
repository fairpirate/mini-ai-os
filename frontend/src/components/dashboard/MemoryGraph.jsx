import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Database, Zap } from 'lucide-react';
import { useSocketStore } from '../../store/socketStore';

export const MemoryGraph = () => {
  const { systemStats } = useSocketStore();
  const currentDocs = systemStats?.memory?.db_docs || 0;
  const [history, setHistory] = useState(new Array(20).fill(0));

  useEffect(() => {
    setHistory(prev => [...prev.slice(1), currentDocs]);
  }, [currentDocs]);

  // Generate SVG path for the history
  const max = Math.max(...history, 10);
  const width = 200;
  const height = 40;
  const points = history.map((val, i) => {
    const x = (i / (history.length - 1)) * width;
    const y = height - (val / max) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="glass-panel p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-jarvis-highlight" />
          <h3 className="text-xs font-bold uppercase tracking-widest neon-text">Neural Memory Depth</h3>
        </div>
        <div className="text-[10px] font-mono text-jarvis-highlight flex items-center gap-1">
          <div className="w-1.5 h-1.5 rounded-full bg-jarvis-highlight animate-pulse"></div>
          {currentDocs} NODES
        </div>
      </div>
      
      <div className="relative h-12 bg-black/40 rounded border border-white/5 overflow-hidden flex items-end">
        {/* Background Grid */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-[linear-gradient(90deg,transparent_19px,rgba(255,255,255,0.1)_20px)] bg-[length:20px_100%]"></div>
          <div className="absolute inset-0 bg-[linear-gradient(0deg,transparent_9px,rgba(255,255,255,0.1)_10px)] bg-[length:100%_10px]"></div>
        </div>
        
        {/* Sparkline */}
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-10 overflow-visible z-10">
          <motion.polyline
            fill="none"
            stroke="#00c8ff"
            strokeWidth="1.5"
            points={points}
            initial={false}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            style={{ filter: 'drop-shadow(0 0 4px rgba(0,200,255,0.5))' }}
          />
          {/* Area fill */}
          <motion.path
            d={`M0,${height} L${points} L${width},${height} Z`}
            fill="url(#memoryGradient)"
            className="opacity-20"
          />
          <defs>
            <linearGradient id="memoryGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#00c8ff" />
              <stop offset="100%" stopColor="transparent" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      
      <div className="flex justify-between items-center text-[8px] font-mono text-gray-600 uppercase tracking-tighter">
        <span>History: 40s</span>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-0.5"><Zap className="w-2 h-2" /> RECALL_READY</span>
          <span>CHROMA_V1.2</span>
        </div>
      </div>
    </div>
  );
};
