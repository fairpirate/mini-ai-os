import React, { useState } from 'react';
import axios from 'axios';
import { CheckCircle, XCircle, AlertTriangle, Play, ChevronRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000';

function PlanApproval({ activeTask, setActiveTask, fetchTasks }) {
  const [loading, setLoading] = useState(false);

  if (!activeTask) {
    return (
      <div className="premium-card bg-slate-900 border-dashed border-slate-800 flex flex-col items-center justify-center py-12 text-center">
        <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mb-4 text-slate-500">
           <Play size={24} />
        </div>
        <h3 className="text-slate-400 font-medium">No plans pending approval</h3>
        <p className="text-xs text-slate-600 mt-1">Ask the AI to perform an action to generate a plan</p>
      </div>
    );
  }

  const handleApprove = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/approve/${activeTask.id}`);
      setActiveTask(null);
      fetchTasks();
    } catch (err) {
      alert("Failed to approve task");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk) => {
    switch(risk) {
      case 'low': return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20';
      case 'medium': return 'text-amber-400 bg-amber-400/10 border-amber-400/20';
      case 'high': return 'text-rose-400 bg-rose-400/10 border-rose-400/20';
      default: return 'text-slate-400 bg-slate-400/10 border-slate-400/20';
    }
  };

  return (
    <div className="premium-card bg-slate-900 border-indigo-500/20 flex flex-col gap-4 overflow-hidden relative">
      <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500"></div>
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-bold text-slate-200">Execution Plan</h3>
          <p className="text-xs text-slate-500 mt-0.5">ID: {activeTask.id.substring(0, 8)}...</p>
        </div>
        <div className="flex gap-2">
           <button onClick={() => setActiveTask(null)} className="p-2 hover:bg-slate-800 rounded-lg text-slate-500"><XCircle size={18}/></button>
        </div>
      </div>

      <div className="space-y-3 mt-2 max-h-64 overflow-y-auto pr-1">
        {activeTask.plan.steps.map((step, i) => (
          <div key={i} className="bg-slate-950/50 border border-slate-800/50 p-3 rounded-lg flex gap-3">
             <div className="flex flex-col items-center gap-1">
                <span className="w-6 h-6 rounded-full bg-indigo-600/20 text-indigo-400 flex items-center justify-center text-[10px] font-bold">{step.id}</span>
                {i < activeTask.plan.steps.length - 1 && <div className="w-0.5 h-full bg-slate-800 my-1"></div>}
             </div>
             <div className="flex-1 min-w-0">
                <div className="flex justify-between items-center mb-1">
                   <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">{step.action}</h4>
                   <span className={`text-[9px] px-2 py-0.5 rounded border ${getRiskColor(step.risk)}`}>
                      {step.risk} risk
                   </span>
                </div>
                <p className="text-xs text-slate-400 leading-normal">{step.description}</p>
             </div>
          </div>
        ))}
      </div>

      <div className="flex gap-3 mt-2">
        <button 
          onClick={handleApprove}
          disabled={loading}
          className="flex-1 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white py-3 rounded-xl font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20"
        >
          {loading ? "Initializing..." : <><CheckCircle size={18} /> Approve & Execute</>}
        </button>
      </div>
    </div>
  );
}

export default PlanApproval;
