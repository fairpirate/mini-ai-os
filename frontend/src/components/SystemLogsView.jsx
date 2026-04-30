import React from 'react';
import { Terminal, CheckCircle2, XCircle, Clock, Search, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';

const SystemLogsView = ({ tasks }) => {
  const sortedTasks = [...tasks].sort((a, b) => b.created_at - a.created_at);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="text-emerald-400" size={18} />;
      case 'failed': return <XCircle className="text-red-400" size={18} />;
      case 'executing': return <Terminal className="text-indigo-400 animate-pulse" size={18} />;
      case 'approved': return <Clock className="text-blue-400" size={18} />;
      default: return <AlertTriangle className="text-amber-400" size={18} />;
    }
  };

  const getLogEntryColor = (status) => {
    switch (status) {
      case 'completed': return 'border-l-emerald-500';
      case 'failed': return 'border-l-red-500';
      case 'executing': return 'border-l-indigo-500';
      default: return 'border-l-slate-700';
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex-1 flex flex-col gap-6"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Terminal className="text-indigo-400" size={28} />
          <h2 className="text-2xl font-bold">System Logs</h2>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
          <input 
            type="text" 
            placeholder="Search logs..." 
            className="bg-slate-800 border-none rounded-lg pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none w-64"
          />
        </div>
      </div>

      <div className="bg-slate-950 rounded-2xl border border-slate-800 flex-1 overflow-hidden flex flex-col">
        <div className="p-4 bg-slate-900/50 border-b border-slate-800 flex items-center justify-between">
          <div className="flex gap-4 text-sm font-medium">
             <button className="text-indigo-400 border-b-2 border-indigo-400 pb-1">All Tasks</button>
             <button className="text-slate-500 hover:text-slate-300 transition-colors">Success</button>
             <button className="text-slate-500 hover:text-slate-300 transition-colors">Errors</button>
          </div>
          <span className="text-xs text-slate-500 font-mono">Showing {tasks.length} entries</span>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-sm">
          {sortedTasks.length === 0 ? (
            <div className="flex items-center justify-center h-full text-slate-600 italic">
              No system activity detected...
            </div>
          ) : (
            sortedTasks.map((task, i) => (
              <div 
                key={task.id} 
                className={`p-4 bg-slate-900/80 border border-slate-800 border-l-4 ${getLogEntryColor(task.status)} rounded-lg hover:bg-slate-900 transition-colors`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(task.status)}
                    <span className="text-slate-300 font-bold uppercase text-xs">TASK_{task.id.slice(0, 8)}</span>
                    <span className="text-slate-600">|</span>
                    <span className="text-slate-400">{task.status}</span>
                  </div>
                  <span className="text-slate-600 text-xs">{new Date(task.created_at * 1000).toISOString()}</span>
                </div>
                
                <div className="text-slate-300 mb-3">
                   {task.plan.steps.map(s => s.description).join(", ")}
                </div>

                {task.results && task.results.length > 0 && (
                  <div className="mt-2 space-y-2">
                    {task.results.map((res, idx) => (
                      <div key={idx} className="bg-black/40 p-2 rounded border border-slate-800 leading-relaxed overflow-x-auto">
                        <span className="text-emerald-500">[{res.action}]</span> <span className="text-slate-400">{res.output}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default SystemLogsView;
