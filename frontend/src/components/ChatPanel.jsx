import React, { useRef, useEffect } from 'react';
import { Send, User, Bot } from 'lucide-react';
import { motion } from 'framer-motion';

function ChatPanel({ messages, onSend, inputText, setInputText, isListening }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSend();
  };

  return (
    <div className="flex-1 flex flex-col premium-card bg-slate-900 border-slate-800 h-full relative overflow-hidden">
      <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/80 backdrop-blur-md sticky top-0 z-10">
        <h2 className="font-semibold text-slate-200">Neural Interface</h2>
        <div className="flex gap-2">
            <span className="text-xs bg-indigo-500/10 text-indigo-400 px-2 py-1 rounded">Gemma 3.1</span>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.map((msg, i) => (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            key={i} 
            className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-indigo-600' : 'bg-slate-700 text-indigo-400'}`}>
              {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
            </div>
            <div className={`max-w-[80%] p-4 rounded-2xl ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-slate-800 text-slate-200 rounded-tl-none border border-slate-700'}`}>
              <p className="text-sm leading-relaxed">{msg.content}</p>
            </div>
          </motion.div>
        ))}
        {isListening && (
           <div className="flex gap-4">
              <div className="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center">
                 <Bot size={18} className="text-indigo-400" />
              </div>
              <div className="bg-slate-800 p-4 rounded-2xl rounded-tl-none border border-slate-700">
                 <div className="flex gap-1">
                    {[1, 2, 3].map(i => (
                       <motion.div 
                          key={i}
                          animate={{ height: [4, 12, 4] }}
                          transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                          className="w-1 bg-indigo-500" 
                       />
                    ))}
                 </div>
              </div>
           </div>
        )}
      </div>

      <div className="p-4 bg-slate-900 border-t border-slate-800">
        <form onSubmit={handleSubmit} className="relative">
          <input 
            type="text" 
            placeholder="Type your command..." 
            className="w-full bg-slate-950 border border-slate-800 rounded-xl py-4 pl-4 pr-16 focus:outline-none focus:ring-2 focus:ring-indigo-600 transition-all text-slate-200"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
          />
          <button type="submit" className="absolute right-2 top-2 p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 transition-colors">
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatPanel;
