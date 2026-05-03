import React from 'react';
import { motion } from 'framer-motion';

export const RadarBackground = () => {
  return (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none opacity-20 flex items-center justify-center">
      <div className="relative w-[150vw] h-[150vw] max-w-[2000px] max-h-[2000px] border border-jarvis-highlight/20 rounded-full flex items-center justify-center">
        <div className="absolute w-[75%] h-[75%] border border-jarvis-highlight/20 rounded-full" />
        <div className="absolute w-[50%] h-[50%] border border-jarvis-highlight/20 rounded-full" />
        <div className="absolute w-[25%] h-[25%] border border-jarvis-highlight/20 rounded-full" />
        
        {/* Crosshairs */}
        <div className="absolute w-full h-[1px] bg-jarvis-highlight/10" />
        <div className="absolute h-full w-[1px] bg-jarvis-highlight/10" />
        
        {/* Radar Sweeper */}
        <motion.div 
          className="absolute w-1/2 h-1/2 top-0 right-0 origin-bottom-left border-r border-jarvis-highlight/50 bg-gradient-to-br from-transparent to-jarvis-highlight/10"
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
        />
      </div>
    </div>
  );
};
