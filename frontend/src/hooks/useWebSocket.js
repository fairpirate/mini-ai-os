import { useEffect, useRef, useCallback } from 'react';
import { useSocketStore } from '../store/socketStore';

export const useWebSocket = (url = 'ws://127.0.0.1:8000/ws/stream') => {
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);
  
  const { 
    setConnected, 
    setSystemStatus, 
    addMessage, 
    setAiThinking,
    appendAiStream,
    finalizeAiStream,
    setPendingApproval,
    addActiveTask,
    setSystemMetrics,
  } = useSocketStore();

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return;

    ws.current = new WebSocket(url);

    ws.current.onopen = () => {
      setConnected(true);
      setSystemStatus('Connected');
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
    };

    ws.current.onmessage = async (event) => {
      // Handle Binary Audio from TTS
      if (event.data instanceof Blob) {
        const arrayBuffer = await event.data.arrayBuffer();
        // Fire custom event to be picked up by useAudioPlayer
        const customEvent = new CustomEvent('tts_audio', { detail: arrayBuffer });
        window.dispatchEvent(customEvent);
        return;
      }

      try {
        const data = JSON.parse(event.data);
        handleEvent(data.event, data.payload);
      } catch (err) {
        console.error('Failed to parse WS message', err);
      }
    };

    ws.current.onclose = () => {
      setConnected(false);
      setSystemStatus('Connection Lost. Reconnecting...');
      // Auto reconnect
      reconnectTimeout.current = setTimeout(connect, 3000);
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket Error:', error);
      ws.current.close();
    };
  }, [url]);

  const handleEvent = (event, payload) => {
    switch (event) {
      case 'system_status':
        setSystemStatus(payload.message);
        addMessage({ role: 'system', text: payload.message });
        break;
      case 'ai_thinking':
        setAiThinking(payload.state);
        break;
      case 'ai_chunk':
        if (payload.done) {
          finalizeAiStream();
        } else {
          appendAiStream(payload.chunk);
        }
        break;
      case 'transcription':
        // Show voice transcript as a user message
        addMessage({ role: 'user', text: `🎤 ${payload.text}` });
        break;
      case 'task_update':
        addActiveTask(payload);
        break;
      case 'system_metrics':
        setSystemMetrics(payload);
        break;
      case 'system_error':
        addMessage({ role: 'system', text: `ERROR: ${payload.message}` });
        break;
      case 'tool_approval_required':
        setPendingApproval(payload);
        addMessage({ role: 'system', text: `Security Override Required: ${payload.tool}` });
        break;
      case 'tool_execution_started':
        addMessage({ role: 'system', text: `Executing Tool: ${payload.tool}...` });
        break;
      case 'tool_execution_completed':
        addMessage({ role: 'system', text: `Tool Output: ${payload.result}` });
        break;
      default:
        console.warn('Unknown event:', event, payload);
    }
  };

  useEffect(() => {
    connect();
    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
    };
  }, [connect]);

  const sendMessage = useCallback((eventOrData, payload) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      if (eventOrData instanceof Blob || eventOrData instanceof ArrayBuffer) {
        ws.current.send(eventOrData); // Send raw binary audio
      } else {
        ws.current.send(JSON.stringify({ event: eventOrData, payload }));
      }
    } else {
      console.warn('Cannot send message, WebSocket is not open.');
      addMessage({ role: 'system', text: 'ERROR: No connection to Neural Link.' });
    }
  }, []);

  return { sendMessage };
};
