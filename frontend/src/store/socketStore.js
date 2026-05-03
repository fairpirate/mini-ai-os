import { create } from 'zustand';

export const useSocketStore = create((set) => ({
  isConnected: false,
  isAiThinking: false,
  isListening: false,
  systemStatus: 'Disconnected',
  messages: [
    { id: 'sys-1', role: 'system', text: 'Initializing Neural Link...', timestamp: Date.now() }
  ],
  currentAiStream: '',
  pendingApproval: null,
  activeTasks: [], // Live task objects from the executor
  systemStats: { cpu: { percent: 0 }, memory: { percent: 0 }, network: { sent_kbps: 0, recv_kbps: 0 } },
  aiMetrics: { avg_latency: 0, avg_tokens_per_sec: 0, total_calls: 0 },
  logs: [],
  
  setConnected: (status) => set({ isConnected: status }),
  setAiThinking: (status) => set({ isAiThinking: status }),
  setListening: (status) => set({ isListening: status }),
  setSystemStatus: (message) => set({ systemStatus: message }),
  setPendingApproval: (approval) => set({ pendingApproval: approval }),
  
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, { ...message, id: message.id || Date.now(), timestamp: Date.now() }] 
  })),
  
  appendAiStream: (chunk) => set((state) => ({
    currentAiStream: state.currentAiStream + chunk
  })),
  
  finalizeAiStream: () => set((state) => {
    if (!state.currentAiStream) return state;
    return {
      messages: [...state.messages, { id: Date.now(), role: 'ai', text: state.currentAiStream, timestamp: Date.now() }],
      currentAiStream: ''
    };
  }),

  // Task Queue actions
  setActiveTasks: (tasks) => set({ activeTasks: tasks }),
  updateTask: (taskId, update) => set((state) => ({
    activeTasks: state.activeTasks.map(t => t.id === taskId ? { ...t, ...update } : t)
  })),
  addActiveTask: (task) => set((state) => ({
    // Replace if already exists, otherwise prepend
    activeTasks: state.activeTasks.some(t => t.id === task.id)
      ? state.activeTasks.map(t => t.id === task.id ? { ...t, ...task } : t)
      : [task, ...state.activeTasks].slice(0, 20) // Keep max 20
  })),

  setSystemMetrics: (metrics) => set({ 
    systemStats: metrics.system, 
    aiMetrics: metrics.ai 
  }),

  addLog: (log) => set((state) => ({
    logs: [log, ...state.logs].slice(0, 50) // Keep last 50 logs
  })),
}));

