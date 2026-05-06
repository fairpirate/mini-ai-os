import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Terminal, Cpu, Zap, Search, Wrench, Brain } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useSocketStore } from '../../store/socketStore';

const MODE_CONFIG = {
  conversation: { label: 'CONVERSATION', icon: Brain, color: 'text-jarvis-highlight', bg: 'bg-jarvis-highlight/10 border-jarvis-highlight/30' },
  execution:    { label: 'EXECUTION',    icon: Zap,   color: 'text-jarvis-success',   bg: 'bg-jarvis-success/10 border-jarvis-success/30' },
  builder:      { label: 'BUILDER',      icon: Wrench, color: 'text-yellow-400',       bg: 'bg-yellow-400/10 border-yellow-400/30' },
  autonomous:   { label: 'AUTONOMOUS',   icon: Cpu,   color: 'text-purple-400',       bg: 'bg-purple-400/10 border-purple-400/30' },
  research:     { label: 'RESEARCH',     icon: Search, color: 'text-orange-400',       bg: 'bg-orange-400/10 border-orange-400/30' },
};

function detectMode(messages) {
  if (!messages.length) return null;
  const last = messages[messages.length - 1];
  if (!last?.text) return null;
  const t = last.text.toLowerCase();
  if (t.includes('research') || t.includes('search results')) return 'research';
  if (t.includes('executing') || t.includes('created file') || t.includes('completed')) return 'execution';
  if (t.includes('building') || t.includes('plugin') || t.includes('generating code')) return 'builder';
  if (t.includes('autonomous') || t.includes('workflow')) return 'autonomous';
  return 'conversation';
}

export const ChatPanel = ({ sendMessage }) => {
  const [input, setInput] = useState('');
  const { messages, currentAiStream, pendingApproval, setPendingApproval } = useSocketStore();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentAiStream]);

  const activeMode = detectMode(messages);
  const modeConf = activeMode ? MODE_CONFIG[activeMode] : null;
  const ModeIcon = modeConf?.icon || Terminal;

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    useSocketStore.getState().addMessage({ role: 'user', text: input });
    sendMessage('user_message', { text: input });
    setInput('');
  };

  return (
    <div className="glass-panel flex flex-col h-full overflow-hidden">
      <div className="p-4 border-b border-jarvis-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="text-jarvis-highlight w-5 h-5" />
          <div>
            <h2 className="neon-text font-semibold uppercase tracking-wider text-sm">MEGAN Neural Link</h2>
            <p className="text-gray-500 text-xs tracking-widest">Autonomous AI OS</p>
          </div>
        </div>
        {modeConf && (
          <AnimatePresence mode="wait">
            <motion.div
              key={activeMode}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className={`flex items-center gap-1 px-2 py-1 rounded border text-xs font-bold uppercase tracking-wider ${modeConf.bg} ${modeConf.color}`}
            >
              <ModeIcon className="w-3 h-3" />
              {modeConf.label}
            </motion.div>
          </AnimatePresence>
        )}
      </div>

      
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
        {messages.map((msg) => (
          <motion.div 
            key={msg.id}
            initial={{ opacity: 0, x: msg.role === 'user' ? 20 : -20 }}
            animate={{ opacity: 1, x: 0 }}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-[80%] rounded-lg p-3 text-sm ${
              msg.role === 'user' 
                ? 'bg-jarvis-highlight/20 border border-jarvis-highlight/30 text-white' 
                : msg.role === 'system'
                ? 'bg-jarvis-success/10 border border-jarvis-success/30 text-jarvis-success font-mono text-xs'
                : 'bg-white/5 border border-white/10 text-gray-200'
            }`}>
              <div className="markdown-content">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {typeof msg.text === 'string' ? msg.text : JSON.stringify(msg.text)}
                </ReactMarkdown>
              </div>
            </div>
          </motion.div>
        ))}
        
        {/* Streaming Placeholder */}
        {currentAiStream && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="max-w-[80%] rounded-lg p-3 text-sm bg-white/5 border border-jarvis-highlight/30 text-gray-200 shadow-[0_0_10px_rgba(0,200,255,0.2)]">
              <div className="markdown-content inline-block">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {currentAiStream || ""}
                </ReactMarkdown>
              </div>
              <span className="inline-block w-2 h-4 bg-jarvis-highlight ml-1 animate-pulse align-middle"></span>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Approval Overlay */}
      {pendingApproval && (
        <div className="p-4 bg-jarvis-alert/10 border-t border-jarvis-alert/50">
          <h3 className="text-jarvis-alert font-bold text-sm mb-2 uppercase tracking-wide">Security Override Required</h3>
          <p className="text-xs text-gray-300 mb-2">
            Tool: <span className="font-mono text-jarvis-highlight">{pendingApproval.tool}</span>
          </p>
          <div className="bg-black/50 p-2 rounded text-xs font-mono text-gray-400 mb-3 overflow-x-auto">
            {JSON.stringify(pendingApproval.params, null, 2)}
          </div>
          <div className="flex gap-2">
            <button 
              onClick={() => {
                sendMessage('tool_approval_response', { execution_id: pendingApproval.execution_id, approved: true });
                setPendingApproval(null);
              }}
              className="flex-1 bg-jarvis-success/20 hover:bg-jarvis-success/40 text-jarvis-success border border-jarvis-success/50 py-1 rounded text-xs font-bold transition-colors"
            >
              AUTHORIZE
            </button>
            <button 
              onClick={() => {
                sendMessage('tool_approval_response', { execution_id: pendingApproval.execution_id, approved: false });
                setPendingApproval(null);
              }}
              className="flex-1 bg-jarvis-alert/20 hover:bg-jarvis-alert/40 text-jarvis-alert border border-jarvis-alert/50 py-1 rounded text-xs font-bold transition-colors"
            >
              DENY
            </button>
          </div>
        </div>
      )}

      <form onSubmit={handleSend} className="p-3 border-t border-jarvis-border flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Input command..." 
          className="flex-1 bg-black/50 border border-jarvis-border rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-jarvis-highlight transition-colors"
        />
        <button type="submit" className="bg-jarvis-highlight/20 hover:bg-jarvis-highlight/40 text-jarvis-highlight p-2 rounded transition-colors border border-jarvis-highlight/30">
          <Send className="w-5 h-5" />
        </button>
      </form>
    </div>
  );
};
