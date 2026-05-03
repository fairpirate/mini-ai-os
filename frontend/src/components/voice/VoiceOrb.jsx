import React from 'react';
import { motion } from 'framer-motion';

export const VoiceOrb = ({ isListening = false, isThinking = false, volume = 0 }) => {
  // Map volume (0-255) to scale factor (1-1.5)
  const micScale = isListening ? 1 + (volume / 255) * 0.5 : 1;
  const micOpacity = isListening ? 0.4 + (volume / 255) * 0.6 : 0.4;

  return (
    <div className="relative flex items-center justify-center w-32 h-32">
      {/* Outer Pulse */}
      <motion.div 
        className={`absolute inset-0 rounded-full blur-xl ${isThinking ? 'bg-jarvis-highlight/40' : isListening ? 'bg-jarvis-success/40' : 'bg-jarvis-highlight/10'}`}
        animate={
          isListening ? { scale: micScale, opacity: micOpacity } :
          isThinking ? { scale: [1, 1.2, 1], opacity: [0.4, 0.8, 0.4] } :
          { scale: [1, 1.05, 1], opacity: [0.1, 0.3, 0.1] }
        }
        transition={isListening ? { type: "tween", duration: 0.1 } : { repeat: Infinity, duration: isThinking ? 1 : 2 }}
      />
      
      {/* Core */}
      <motion.div 
        className={`relative z-10 w-16 h-16 rounded-full border border-white/30 flex items-center justify-center shadow-[0_0_20px_rgba(0,200,255,0.5)] ${isThinking ? 'bg-jarvis-highlight' : isListening ? 'bg-jarvis-success' : 'bg-transparent backdrop-blur-md'}`}
        animate={{
          scale: isThinking ? [1, 0.9, 1.1, 1] : 1
        }}
        transition={{ repeat: Infinity, duration: 1.5 }}
      >
        <div className="w-8 h-8 rounded-full bg-white opacity-80 blur-sm" />
      </motion.div>
    </div>
  );
};
