import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, Loader2, Clock, ChevronDown, ChevronUp, ListTodo } from 'lucide-react';
import { useSocketStore } from '../store/socketStore';
import { useState } from 'react';

const STATUS_CONFIG = {
  completed: { icon: CheckCircle, color: 'text-jarvis-success', bg: 'bg-jarvis-success/10 border-jarvis-success/30', label: 'DONE' },
  executing: { icon: Loader2,     color: 'text-jarvis-highlight', bg: 'bg-jarvis-highlight/10 border-jarvis-highlight/30', label: 'RUNNING', spin: true },
  failed:    { icon: XCircle,     color: 'text-jarvis-alert',   bg: 'bg-jarvis-alert/10 border-jarvis-alert/30',   label: 'FAILED' },
  pending:   { icon: Clock,       color: 'text-gray-400',        bg: 'bg-white/5 border-white/10',                  label: 'QUEUED' },
};

const StepBadge = ({ step }) => {
  const cfg = STATUS_CONFIG[step.status] || STATUS_CONFIG.pending;
  const Icon = cfg.icon;
  return (
    <div className={`flex items-center gap-1.5 text-xs font-mono px-2 py-0.5 rounded border ${cfg.bg}`}>
      <Icon className={`w-3 h-3 ${cfg.color} ${cfg.spin ? 'animate-spin' : ''}`} />
      <span className={cfg.color}>Step {step.id}</span>
      {step.attempts > 1 && (
        <span className="text-jarvis-alert/70">×{step.attempts}</span>
      )}
    </div>
  );
};

const TaskCard = ({ task }) => {
  const [expanded, setExpanded] = useState(false);
  const cfg = STATUS_CONFIG[task.status] || STATUS_CONFIG.pending;
  const Icon = cfg.icon;
  const steps = task.plan?.steps || [];

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={`rounded-lg border text-xs font-mono overflow-hidden ${cfg.bg}`}
    >
      {/* Header */}
      <button
        className="w-full flex items-center gap-2 p-2 text-left"
        onClick={() => setExpanded(e => !e)}
      >
        <Icon className={`w-3.5 h-3.5 flex-shrink-0 ${cfg.color} ${cfg.spin ? 'animate-spin' : ''}`} />
        <span className={`flex-1 truncate ${cfg.color}`}>{task.id}</span>
        <span className={`uppercase tracking-widest text-[9px] font-bold ${cfg.color}`}>{cfg.label}</span>
        {steps.length > 0 && (
          expanded
            ? <ChevronUp className="w-3 h-3 text-gray-500" />
            : <ChevronDown className="w-3 h-3 text-gray-500" />
        )}
      </button>

      {/* Steps */}
      <AnimatePresence>
        {expanded && steps.length > 0 && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-white/5 px-2 pb-2 pt-1 flex flex-wrap gap-1"
          >
            {steps.map(step => <StepBadge key={step.id} step={step} />)}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export const TaskQueuePanel = () => {
  const { activeTasks } = useSocketStore();

  return (
    <div className="glass-panel flex flex-col flex-1 min-h-0 overflow-hidden">
      <div className="p-4 border-b border-jarvis-border flex items-center gap-2">
        <ListTodo className="text-jarvis-highlight w-5 h-5" />
        <h2 className="neon-text font-semibold uppercase tracking-wider text-sm">Task Queue</h2>
        {activeTasks.length > 0 && (
          <span className="ml-auto text-[10px] font-mono bg-jarvis-highlight/20 text-jarvis-highlight border border-jarvis-highlight/30 px-1.5 py-0.5 rounded">
            {activeTasks.length}
          </span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2 scrollbar-hide">
        <AnimatePresence mode="popLayout">
          {activeTasks.length === 0 ? (
            <motion.p
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-xs text-gray-500 font-mono text-center mt-4"
            >
              No active tasks.
            </motion.p>
          ) : (
            activeTasks.map(task => <TaskCard key={task.id} task={task} />)
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
