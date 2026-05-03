import React from 'react';
import { motion } from 'framer-motion';
import { Activity, ShieldCheck, Zap } from 'lucide-react';
import { useSocketStore } from '../../store/socketStore';

const HealthRing = ({ value, color, label, icon: Icon }) => {
  const radius = 35;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  return (
    <div className="relative flex flex-col items-center group">
      <svg className="w-24 h-24 transform -rotate-90">
        {/* Background Track */}
        <circle
          cx="48"
          cy="48"
          r={radius}
          stroke="currentColor"
          strokeWidth="4"
          fill="transparent"
          className="text-white/5"
        />
        {/* Progress Ring */}
        <motion.circle
          cx="48"
          cy="48"
          r={radius}
          stroke="currentColor"
          strokeWidth="4"
          fill="transparent"
          strokeDasharray={circumference}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={color}
          style={{ strokeLinecap: 'round' }}
        />
      </svg>
      
      <div className="absolute inset-0 flex flex-col items-center justify-center pt-2">
        <Icon className={`w-4 h-4 mb-0.5 ${color} opacity-80 group-hover:opacity-100 transition-opacity`} />
        <span className="text-xs font-bold font-mono tracking-tighter">{Math.round(value)}%</span>
      </div>
      <span className="text-[10px] font-mono uppercase tracking-[0.2em] mt-1 text-gray-500">{label}</span>
      
      {/* Holographic Glow Effect */}
      <div className={`absolute inset-0 rounded-full blur-xl opacity-20 ${color.replace('text', 'bg')} pointer-events-none`}></div>
    </div>
  );
};

export const SystemHealth = () => {
  const { systemStats } = useSocketStore();
  const cpu = systemStats?.cpu?.percent || 0;
  const mem = systemStats?.memory?.percent || 0;
  
  // Calculate a generic "Health" score based on usage
  const health = Math.max(0, 100 - (cpu * 0.4 + mem * 0.6));

  return (
    <div className="glass-panel p-4 flex flex-col items-center justify-center gap-6 overflow-hidden relative">
      {/* Background Grid/Scanlines */}
      <div className="absolute inset-0 pointer-events-none opacity-5 overflow-hidden">
        <div className="absolute inset-0 bg-[linear-gradient(to_bottom,transparent_50%,#00c8ff_50%)] bg-[length:100%_4px] animate-scanline"></div>
      </div>

      <div className="flex items-center gap-6 z-10">
        <HealthRing value={cpu} color="text-jarvis-highlight" label="CPU" icon={Zap} />
        <HealthRing value={health} color="text-jarvis-success" label="Core" icon={ShieldCheck} />
        <HealthRing value={mem} color="text-purple-500" label="RAM" icon={Activity} />
      </div>
      
      <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden relative z-10">
        <motion.div 
          className="absolute inset-y-0 left-0 bg-jarvis-highlight"
          animate={{ width: `${health}%` }}
          transition={{ duration: 1 }}
        />
        <div className="absolute inset-0 bg-[linear-gradient(90deg,transparent,rgba(0,200,255,0.4),transparent)] animate-shimmer"></div>
      </div>
    </div>
  );
};
