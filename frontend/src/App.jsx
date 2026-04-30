import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Terminal, Database, Activity, Mic, MicOff, Send, CheckCircle, XCircle, Play, Layers } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatPanel from './components/ChatPanel';
import PlanApproval from './components/PlanApproval';
import TaskHistory from './components/TaskHistory';
import DataRegistry from './components/DataRegistry';
import SystemLogsView from './components/SystemLogsView';

const API_BASE = 'http://localhost:8000';

function App() {
  const [tasks, setTasks] = useState([]);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Mini AI OS Core initialized. How can I help you today?' }
  ]);
  const [activeTask, setActiveTask] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [inputText, setInputText] = useState("");
  const [activeView, setActiveView] = useState('dashboard');
  const [coreStatus, setCoreStatus] = useState({ backend: 'checking', ollama: 'checking' });

  useEffect(() => {
    fetchTasks();
    checkHealth();
    const interval = setInterval(() => {
      fetchTasks();
      checkHealth();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const res = await axios.get(`${API_BASE}/health`);
      setCoreStatus({ backend: 'online', ollama: res.data.ollama });
    } catch (err) {
      setCoreStatus({ backend: 'offline', ollama: 'offline' });
    }
  };

  const fetchTasks = async () => {
    try {
      const res = await axios.get(`${API_BASE}/tasks`);
      setTasks(res.data);
    } catch (err) {
      console.error("Failed to fetch tasks", err);
    }
  };

  const handleSend = async (text) => {
    const prompt = text || inputText;
    if (!prompt) return;

    setMessages([...messages, { role: 'user', content: prompt }]);
    setInputText("");

    try {
      const res = await axios.post(`${API_BASE}/plan`, { prompt });
      if (res.data.type === 'chat') {
        setMessages(prev => [...prev, { role: 'assistant', content: res.data.message }]);
        speak(res.data.message);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: "I've generated a plan for your request. Please review it in the tasks panel." }]);
        setActiveTask(res.data);
        speak("Plan generated. Awaiting approval.");
        fetchTasks();
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I encountered an error connecting to the core." }]);
    }
  };

  const speak = (text) => {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    synth.speak(utterance);
  };

  const toggleVoice = () => {
    if (isListening) {
      setIsListening(false);
    } else {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        alert("Speech recognition not supported in this browser.");
        return;
      }
      const recognition = new SpeechRecognition();
      recognition.onstart = () => setIsListening(true);
      recognition.onend = () => setIsListening(false);
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        handleSend(transcript);
      };
      recognition.start();
    }
  };

  return (
    <div className="flex h-screen bg-dark text-slate-100 overflow-hidden">
      {/* Sidebar Navigation */}
      <aside className="w-20 lg:w-64 border-r border-slate-800 flex flex-col items-center py-8 gap-8">
        <div className="flex items-center gap-3 px-4">
          <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <Layers className="text-white" size={24} />
          </div>
          <span className="hidden lg:block font-bold text-xl tracking-tight">AI Operating System</span>
        </div>
        
        <nav className="flex flex-col gap-4 w-full px-4 mt-8">
          {[
            { icon: <Activity />, label: 'Dashboard', id: 'dashboard' },
            { icon: <Database />, label: 'Data Registry', id: 'registry' },
            { icon: <Terminal />, label: 'System Logs', id: 'logs' }
          ].map((item) => (
            <button 
              key={item.id} 
              onClick={() => setActiveView(item.id)}
              className={`flex items-center gap-4 p-3 rounded-lg w-full transition-all duration-200 ${activeView === item.id ? 'bg-indigo-600/20 text-indigo-400 shadow-[inset_0_0_0_1px_rgba(79,70,229,0.3)]' : 'text-slate-400 hover:bg-slate-800'}`}
            >
              {item.icon}
              <span className="hidden lg:block font-medium">{item.label}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        <header className="h-16 border-b border-slate-800 flex items-center justify-between px-8 bg-slate-900/50 backdrop-blur-sm">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${coreStatus.backend === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></div>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">Core: {coreStatus.backend}</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${coreStatus.ollama === 'online' ? 'bg-emerald-500' : 'bg-amber-500'}`}></div>
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">AI: {coreStatus.ollama}</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
             <button onClick={toggleVoice} className={`p-2 rounded-full transition-all ${isListening ? 'bg-red-500/20 text-red-500 shadow-[0_0_15px_rgba(239,68,68,0.4)]' : 'bg-slate-800 text-slate-400 hover:text-white'}`}>
               {isListening ? <Mic size={20} /> : <MicOff size={20} />}
             </button>
          </div>
        </header>

        <div className="flex-1 flex gap-6 p-6 overflow-hidden">
          <AnimatePresence mode="wait">
            {activeView === 'dashboard' && (
              <motion.div 
                key="dashboard"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="flex-1 flex gap-6 overflow-hidden"
              >
                <div className="flex-1 flex flex-col gap-6 overflow-hidden">
                  <ChatPanel messages={messages} onSend={handleSend} inputText={inputText} setInputText={setInputText} isListening={isListening} />
                </div>
                <div className="w-96 flex flex-col gap-6 overflow-hidden">
                   <PlanApproval activeTask={activeTask} setActiveTask={setActiveTask} fetchTasks={fetchTasks} />
                   <TaskHistory tasks={tasks} />
                </div>
              </motion.div>
            )}

            {activeView === 'registry' && (
              <DataRegistry key="registry" />
            )}

            {activeView === 'logs' && (
              <SystemLogsView key="logs" tasks={tasks} />
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

export default App;
