import React from 'react';
import { Clock, CheckCircle2, XCircle, Loader2, ChevronRight } from 'lucide-react';

function TaskHistory({ tasks }) {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="text-emerald-500" size={16} />;
      case 'failed': return <XCircle className="text-rose-500" size={16} />;
      case 'executing': return <Loader2 className="text-indigo-400 animate-spin" size={16} />;
      case 'approved': return <Clock className="text-amber-400" size={16} />;
      default: return <Clock className="text-slate-500" size={16} />;
    }
  };

  return (
    <div className="flex-1 flex flex-col premium-card bg-slate-900 border-slate-800 overflow-hidden min-h-0">
      <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
        <h2 className="font-semibold text-slate-200">Execution History</h2>
        <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-1 rounded">{tasks.length} Total</span>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {tasks.length === 0 ? (
           <div className="h-full flex items-center justify-center text-slate-600 text-xs italic">
              No history found
           </div>
        ) : (
          [...tasks].reverse().map((task, i) => (
            <div key={task.id} className="p-3 bg-slate-950/40 hover:bg-slate-800/40 border border-slate-800/50 rounded-xl transition-colors group cursor-pointer">
              <div className="flex items-center gap-3">
                <div className="shrink-0">{getStatusIcon(task.status)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-center mb-0.5">
                    <span className="text-xs font-bold text-slate-300 truncate">
                      Task {task.id.substring(0, 8)}
                    </span>
                    <span className="text-[9px] text-slate-500 font-mono">
                      {new Date(task.created_at * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit'})}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <p className="text-[10px] text-slate-500 truncate pr-2">
                      {task.plan.steps.length} steps • {task.plan.steps[0]?.action}...
                    </p>
                    <ChevronRight size={12} className="text-slate-700 group-hover:text-slate-400 transition-colors" />
                  </div>
                </div>
              </div>
              
              {task.status === 'completed' && task.results && task.results.length > 0 && (
                 <div className="mt-2 pt-2 border-t border-slate-800/50">
                    {task.results.map((res, j) => (
                       <div key={j} className="text-[9px] text-emerald-400/80 bg-emerald-500/5 px-2 py-1 rounded mt-1 truncate">
                          ✓ {res.output.substring(0, 50)}...
                       </div>
                    ))}
                 </div>
              )}
              {task.status === 'failed' && (
                  <div className="mt-2 pt-2 border-t border-slate-800/50">
                      <div className="text-[9px] text-rose-400/80 bg-rose-500/5 px-2 py-1 rounded mt-1">
                          ⚠ Execution failed at step {task.results.length}
                      </div>
                  </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default TaskHistory;
