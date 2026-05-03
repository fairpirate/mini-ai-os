import { useState, useRef, useCallback } from 'react';

export const useAudioPlayer = () => {
  const audioContext = useRef(null);
  const isPlaying = useRef(false);
  const queue = useRef([]);

  const initAudio = () => {
    if (!audioContext.current) {
      audioContext.current = new (window.AudioContext || window.webkitAudioContext)();
    }
  };

  const playNext = async () => {
    if (queue.current.length === 0 || isPlaying.current || !audioContext.current) return;
    
    isPlaying.current = true;
    const arrayBuffer = queue.current.shift();
    
    try {
      const audioBuffer = await audioContext.current.decodeAudioData(arrayBuffer);
      const source = audioContext.current.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.current.destination);
      
      source.onended = () => {
        isPlaying.current = false;
        playNext();
      };
      
      source.start();
    } catch (e) {
      console.error('Audio decode error', e);
      isPlaying.current = false;
      playNext();
    }
  };

  const enqueueAudio = (arrayBuffer) => {
    initAudio();
    queue.current.push(arrayBuffer);
    if (!isPlaying.current) {
      playNext();
    }
  };

  const stopAudio = () => {
    queue.current = [];
    isPlaying.current = false;
    // In a full implementation, keep track of current source node to call source.stop()
  };

  return { enqueueAudio, stopAudio, initAudio };
};
