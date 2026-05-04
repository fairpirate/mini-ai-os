import React from 'react';
import { RadarBackground } from './components/shared/RadarBackground';
import { VoiceOrb } from './components/voice/VoiceOrb';
import { ChatPanel } from './components/chat/ChatPanel';
import { TaskQueuePanel } from './components/TaskQueuePanel';
import { SystemHealth } from './components/dashboard/SystemHealth';
import { AIAnalytics } from './components/dashboard/AIAnalytics';
import { NetworkMonitor } from './components/dashboard/NetworkMonitor';
import { MemoryGraph } from './components/dashboard/MemoryGraph';
import { PersonalitySelector } from './components/dashboard/PersonalitySelector';
import { LiveLogs } from './components/dashboard/LiveLogs';
import { useWebSocket } from './hooks/useWebSocket';
import { useSocketStore } from './store/socketStore';
import { useVoice } from './hooks/useVoice';
import { useAudioPlayer } from './hooks/useAudioPlayer';
import { useEffect } from 'react';
import { Mic, MicOff } from 'lucide-react';

function App() {
  const { sendMessage } = useWebSocket();
  const { isConnected, isAiThinking, systemStatus } = useSocketStore();
  
  const { isRecording, volume, startRecording, stopRecording } = useVoice(sendMessage, isAiThinking);
  const { enqueueAudio, stopAudio } = useAudioPlayer();

  useEffect(() => {
    const handleAudio = (e) => enqueueAudio(e.detail);
    window.addEventListener('tts_audio', handleAudio);
    return () => window.removeEventListener('tts_audio', handleAudio);
  }, []);

  const toggleMic = () => {
    if (isRecording) {
      stopRecording();
    } else {
      stopAudio(); // Stop AI speaking if we interrupt
      startRecording();
    }
  };

  return (
    <div className="min-h-screen w-full relative bg-jarvis-dark text-white overflow-hidden font-sans">
      <RadarBackground />
      
      {/* Main HUD Overlay */}
      <div className="relative z-10 w-full h-screen p-4 md:p-6 flex flex-col md:flex-row gap-6">
        
        {/* Left Column: Advanced Dashboard Modules */}
        <div className="w-full md:w-1/4 flex flex-col gap-4 h-full min-h-0">
          <SystemHealth />
          <div className="flex-1 overflow-y-auto space-y-4 scrollbar-hide pr-2">
            <NetworkMonitor />
            <AIAnalytics />
            <PersonalitySelector sendMessage={sendMessage} />
            <MemoryGraph />
            <TaskQueuePanel />
            <LiveLogs />
          </div>
        </div>
        
        {/* Center Column: Core AI Voice Orb */}
        <div className="w-full md:w-2/4 flex flex-col items-center justify-center pointer-events-none">
          <VoiceOrb isListening={isRecording} isThinking={isAiThinking} volume={volume} />
          
          <div className="mt-8 text-center pointer-events-auto">
            <h1 className="text-3xl font-light tracking-[0.2em] neon-text uppercase">Megan OS</h1>
            <p className="text-xs text-gray-400 tracking-widest mt-2 uppercase">Neural Engine V1.0</p>
            <p className={`text-xs mt-4 uppercase tracking-widest ${isConnected ? 'text-jarvis-success' : 'text-jarvis-alert'}`}>
              {systemStatus}
            </p>
            
            <button 
              onClick={toggleMic}
              className={`mt-6 p-4 rounded-full border transition-all ${
                isRecording 
                  ? 'bg-jarvis-alert/20 border-jarvis-alert text-jarvis-alert shadow-[0_0_15px_rgba(255,51,102,0.5)] animate-pulse' 
                  : 'bg-jarvis-panel border-jarvis-border text-jarvis-highlight hover:bg-jarvis-highlight/20 hover:shadow-[0_0_10px_rgba(0,200,255,0.3)]'
              }`}
            >
              {isRecording ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Right Column: Comms & Logs */}
        <div className="w-full md:w-1/4 h-full">
          <ChatPanel sendMessage={sendMessage} />
        </div>
        
      </div>
    </div>
  );
}

export default App;
