import { useState, useRef, useEffect, useCallback } from 'react';

export const useVoice = (sendMessage, isThinking = false) => {
  const [isRecording, setIsRecording] = useState(false);
  const [volume, setVolume] = useState(0);
  const mediaRecorder = useRef(null);
  const audioContext = useRef(null);
  const analyser = useRef(null);
  const streamRef = useRef(null);
  const animationRef = useRef(null);
  const recognitionRef = useRef(null);
  const silenceStart = useRef(null);
  const SILENCE_THRESHOLD = 15; // Adjusted based on testing
  const SILENCE_DURATION = 1500; // 1.5 seconds of silence to stop

  const stopRecording = useCallback(() => {
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop();
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      setIsRecording(false);
      setVolume(0);
      silenceStart.current = null;
      console.log("Recording stopped.");
    }
  }, []);

  const startRecording = useCallback(async () => {
    if (isRecording || isThinking) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      audioContext.current = new (window.AudioContext || window.webkitAudioContext)();
      analyser.current = audioContext.current.createAnalyser();
      const source = audioContext.current.createMediaStreamSource(stream);
      source.connect(analyser.current);
      analyser.current.fftSize = 256;
      
      const bufferLength = analyser.current.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      const checkSilence = () => {
        analyser.current.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < bufferLength; i++) sum += dataArray[i];
        const currentVolume = sum / bufferLength;
        setVolume(currentVolume);

        // Silence detection logic
        if (currentVolume < SILENCE_THRESHOLD) {
          if (!silenceStart.current) silenceStart.current = Date.now();
          else if (Date.now() - silenceStart.current > SILENCE_DURATION) {
            console.log("Silence detected, stopping...");
            stopRecording();
            return;
          }
        } else {
          silenceStart.current = null;
        }

        animationRef.current = requestAnimationFrame(checkSilence);
      };
      
      checkSilence();

      mediaRecorder.current = new MediaRecorder(stream);
      const chunks = [];
      
      mediaRecorder.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      mediaRecorder.current.onstop = () => {
        if (chunks.length > 0 && sendMessage) {
          const blob = new Blob(chunks, { type: 'audio/webm;codecs=opus' });
          console.log("Sending audio blob of size:", blob.size);
          sendMessage(blob); // Send raw binary blob
        }
      };
      
      mediaRecorder.current.start(); 
      setIsRecording(true);
      console.log("Recording started...");
    } catch (err) {
      console.error('Mic error:', err);
    }
  }, [isRecording, isThinking, sendMessage, stopRecording]);

  // Wake Word Listener
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition && !isRecording && !isThinking) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = false;
      
      recognition.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
        console.log("Heard background:", transcript);
        if (transcript.includes('hey megan') || transcript.includes('megan')) {
          console.log("Wake word detected!");
          startRecording();
        }
      };
      
      recognition.onerror = (e) => {
        console.warn("Speech recognition error:", e.error);
        if (e.error === 'not-allowed') recognition.stop();
      };

      try {
        recognition.start();
        recognitionRef.current = recognition;
      } catch (e) {
        console.warn("Recognition already started or failed:", e);
      }
    }
    
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
    };
  }, [isRecording, isThinking, startRecording]);

  return { isRecording, volume, startRecording, stopRecording };
};
