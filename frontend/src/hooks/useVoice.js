import { useState, useRef, useEffect } from 'react';

export const useVoice = (sendMessage) => {
  const [isRecording, setIsRecording] = useState(false);
  const [volume, setVolume] = useState(0);
  const mediaRecorder = useRef(null);
  const audioContext = useRef(null);
  const analyser = useRef(null);
  const streamRef = useRef(null);
  const animationRef = useRef(null);
  const recognitionRef = useRef(null);

  // Initialize Wake Word Listener
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = false;
      
      recognition.onresult = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript.toLowerCase();
        console.log("Heard background:", transcript);
        if (transcript.includes('hey jarvis') || transcript.includes('jarvis')) {
          console.log("Wake word detected!");
          if (!isRecording) startRecording();
        }
      };
      
      recognition.start();
      recognitionRef.current = recognition;
    }
    
    return () => {
      if (recognitionRef.current) recognitionRef.current.stop();
    };
  }, [isRecording]);

  const startRecording = async () => {
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
      
      const updateVolume = () => {
        analyser.current.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < bufferLength; i++) sum += dataArray[i];
        setVolume(sum / bufferLength);
        animationRef.current = requestAnimationFrame(updateVolume);
      };
      updateVolume();

      mediaRecorder.current = new MediaRecorder(stream);
      mediaRecorder.current.ondataavailable = (e) => {
        if (e.data.size > 0 && sendMessage) {
          sendMessage('audio_chunk', e.data);
        }
      };
      
      mediaRecorder.current.start(1000); // chunk every 1s
      setIsRecording(true);
    } catch (err) {
      console.error('Mic error:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      streamRef.current.getTracks().forEach(track => track.stop());
      cancelAnimationFrame(animationRef.current);
      setIsRecording(false);
      setVolume(0);
    }
  };

  return { isRecording, volume, startRecording, stopRecording };
};
