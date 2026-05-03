import React from 'react';
import { motion } from 'framer-motion';
import { User, Shield, Terminal, Heart, Zap } from 'lucide-react';
import { useSocketStore } from '../../store/socketStore';

const personalities = [
  { id: 'jarvis', name: 'JARVIS', icon: Zap, color: 'text-jarvis-highlight' },
  { id: 'stark', name: 'STARK', icon: Heart, color: 'text-jarvis-alert' },
  { id: 'tactical', name: 'TACTICAL', icon: Shield, color: 'text-jarvis-success' },
  { id: 'developer', name: 'DEV', icon: Terminal, color: 'text-purple-500' },
  { id: 'friendly', name: 'FRIENDLY', icon: User, color: 'text-yellow-400' },
];

export const PersonalitySelector = ({ sendMessage }) => {
  return (
    <div className="glass-panel p-4 flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <User className="w-4 h-4 text-jarvis-highlight" />
        <h3 className="text-xs font-bold uppercase tracking-widest neon-text">Personality Matrix</h3>
      </div>
      
      <div className="grid grid-cols-5 gap-2">
        {personalities.map((p) => (
          <button
            key={p.id}
            onClick={() => sendMessage('change_personality', { profile_id: p.id })}
            className="flex flex-col items-center gap-1.5 group"
          >
            <div className={`p-2 rounded-lg bg-white/5 border border-white/10 group-hover:border-jarvis-highlight/50 group-hover:bg-jarvis-highlight/10 transition-all duration-300`}>
              <p.icon className={`w-4 h-4 ${p.color}`} />
            </div>
            <span className="text-[8px] font-bold font-mono tracking-tighter uppercase text-gray-500 group-hover:text-white transition-colors">{p.name}</span>
          </button>
        ))}
      </div>
      
      {/* Emotional Bias Slider (Simulated) */}
      <div className="mt-2 pt-3 border-t border-white/5">
        <div className="flex justify-between items-center mb-2">
          <span className="text-[9px] font-mono text-gray-500 uppercase tracking-widest">Emotional Bias</span>
          <span className="text-[9px] font-mono text-jarvis-highlight">NEUTRAL</span>
        </div>
        <div className="h-1 bg-white/5 rounded-full relative overflow-hidden group cursor-pointer" 
             onClick={(e) => {
               const rect = e.currentTarget.getBoundingClientRect();
               const x = e.clientX - rect.left;
               const bias = (x / rect.width) * 2 - 1; // -1 to 1
               sendMessage('update_emotion', { bias });
             }}>
          <motion.div 
            className="absolute inset-y-0 left-1/2 w-0.5 bg-jarvis-highlight shadow-[0_0_8px_#00c8ff]"
            initial={{ left: '50%' }}
          />
          <div className="absolute inset-0 bg-gradient-to-r from-jarvis-alert/20 via-transparent to-jarvis-success/20"></div>
        </div>
      </div>
    </div>
  );
};
