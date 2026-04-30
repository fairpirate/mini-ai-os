import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { File, HardDrive, RefreshCw, Clock, Database } from 'lucide-react';
import { motion } from 'framer-motion';

const API_BASE = 'http://localhost:8000';

const DataRegistry = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/files`);
      setFiles(res.data);
    } catch (err) {
      console.error("Failed to fetch files", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const formatSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex-1 flex flex-col gap-6"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Database className="text-indigo-400" size={28} />
          <h2 className="text-2xl font-bold">Data Registry</h2>
        </div>
        <button 
          onClick={fetchFiles}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors disabled:opacity-50"
        >
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
          <div className="flex items-center gap-3 mb-2">
            <HardDrive size={20} className="text-emerald-400" />
            <span className="text-sm font-medium text-slate-400 uppercase tracking-wider">Storage Usage</span>
          </div>
          <div className="text-2xl font-bold">{files.length} Files</div>
          <div className="text-sm text-slate-500">Virtual Sandbox Environment</div>
        </div>
      </div>

      <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-800/30">
          <div className="grid grid-cols-4 text-sm font-semibold text-slate-400 uppercase tracking-wider">
            <div className="col-span-2">File Name</div>
            <div>Size</div>
            <div>Modified</div>
          </div>
        </div>
        <div className="divide-y divide-slate-800 max-h-[600px] overflow-y-auto">
          {files.length === 0 ? (
            <div className="p-12 text-center text-slate-500 italic">
              No files found in the registry. Try creating some via the dashboard.
            </div>
          ) : (
            files.map((file, i) => (
              <motion.div 
                key={file.name}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                className="px-6 py-4 grid grid-cols-4 items-center hover:bg-slate-800/50 transition-colors"
              >
                <div className="col-span-2 flex items-center gap-3">
                  <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400">
                    <File size={20} />
                  </div>
                  <span className="font-medium text-slate-200">{file.name}</span>
                </div>
                <div className="text-slate-400 text-sm font-mono">{formatSize(file.size)}</div>
                <div className="text-slate-400 text-sm flex items-center gap-2">
                  <Clock size={14} />
                  {formatDate(file.modified_at)}
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default DataRegistry;
