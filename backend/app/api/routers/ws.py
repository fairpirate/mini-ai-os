from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError
import asyncio
import json
import uuid

from ...ws.manager import manager
from ...core.logging import logger
from ...engine.ollama import ai_service
from ...engine.queue import task_manager
from ...engine.tools.permissions import permission_manager
from ...engine.tools.dispatcher import dispatcher
from ...engine.memory import memory_manager
from ...engine.agents.runner import run_agentic_workflow
from ...core.metrics import metrics_service
from ...engine.personality import personality_manager

router = APIRouter()

class WSEvent(BaseModel):
    event: str
    payload: dict

async def run_ai_pipeline(prompt: str, session_history: list, client_id: str, websocket: WebSocket):
    """Shared AI processing pipeline for both text and voice inputs."""
    await manager.send_personal_message({"event": "ai_thinking", "payload": {"state": True}}, client_id)
    # Broadcast to plugins
    from ...engine.plugins.manager import plugin_manager
    asyncio.create_task(plugin_manager.broadcast_event("user_message", {"text": prompt, "client_id": client_id}))
    
    try:
        # 1. Recall Memories
        recalled_memories = memory_manager.recall_memories(prompt)
        augmented_prompt = prompt
        if recalled_memories:
            memory_context = "\n".join([f"- {mem}" for mem in recalled_memories])
            augmented_prompt = f"System Note: Relevant past memories:\n{memory_context}\n\nUser: {prompt}"
            logger.info(f"Injected {len(recalled_memories)} memories into prompt.")

        # 2. Heuristic: Should we use the Multi-Agent Workflow?
        # If the prompt implies a complex task (e.g., "research", "build", "plan"), use agents.
        complex_keywords = ["research", "build", "plan", "analyze", "create a project", "workflow"]
        is_complex = any(word in prompt.lower() for word in complex_keywords)

        if is_complex:
            logger.info(f"Routing '{prompt}' to multi-agent workflow.")
            full_response = ""
            async for update in run_agentic_workflow(prompt, session_history):
                if update.get("done"):
                    break
                
                agent_name = update.get("agent", "unknown")
                text = update.get("text", "")
                formatted_chunk = f"**[{agent_name.capitalize()}]**: {text}\n\n"
                full_response += formatted_chunk
                
                await manager.send_personal_message({
                    "event": "ai_chunk", 
                    "payload": {"chunk": formatted_chunk, "done": False}
                }, client_id)
            
            await manager.send_personal_message({"event": "ai_chunk", "payload": {"chunk": "", "done": True}}, client_id)
            
            session_history.append({"role": "user", "content": prompt})
            session_history.append({"role": "assistant", "content": full_response})
            
            # Save to memory
            memory_blob = f"Goal: {prompt}\nExecution Summary: {full_response}"
            asyncio.create_task(asyncio.to_thread(memory_manager.save_memory, memory_blob))
            return

        # 3. Standard stream response for simple queries
        response_text = ""
        async for chunk in ai_service.stream_response(augmented_prompt, history=session_history, mode="jarvis"):
            response_text += chunk
            await manager.send_personal_message({"event": "ai_chunk", "payload": {"chunk": chunk, "done": False}}, client_id)
        await manager.send_personal_message({"event": "ai_chunk", "payload": {"chunk": "", "done": True}}, client_id)

        session_history.append({"role": "user", "content": prompt})
        session_history.append({"role": "assistant", "content": response_text})

        # 4. Check if the AI generated a tool call
        is_tool_call = False
        try:
            parsed = json.loads(response_text.strip())
            if isinstance(parsed, dict) and parsed.get("type") == "tool_call":
                is_tool_call = True
                tool_name = parsed.get("tool")
                params = parsed.get("params", {})
                asyncio.create_task(dispatcher.dispatch(tool_name, params, client_id))
        except json.JSONDecodeError:
            pass

        # 5. TTS for non-tool-call responses
        if not is_tool_call:
            from ...engine.audio.tts import tts_engine
            async for audio_chunk in tts_engine.synthesize_stream(response_text):
                if audio_chunk:
                    await websocket.send_bytes(audio_chunk)

            # Save interaction to long-term memory
            memory_blob = f"User: {prompt}\nJarvis: {response_text}"
            asyncio.create_task(asyncio.to_thread(memory_manager.save_memory, memory_blob))

    except Exception as e:
        logger.error(f"AI pipeline failed for {client_id}: {e}")
    finally:
        await manager.send_personal_message({"event": "ai_thinking", "payload": {"state": False}}, client_id)

async def metrics_broadcaster():
    """Background task to broadcast system metrics to all clients."""
    while True:
        try:
            stats = metrics_service.get_system_stats()
            ai_stats = metrics_service.get_ai_stats()
            await manager.broadcast({
                "event": "system_metrics",
                "payload": {
                    "system": stats,
                    "ai": ai_stats,
                    "timestamp": time.time()
                }
            })
        except Exception as e:
            logger.error(f"Metrics broadcaster error: {e}")
        await asyncio.sleep(2) # Update every 2 seconds

# Start broadcaster when the module is loaded (FastAPI will handle the loop)
asyncio.create_task(metrics_broadcaster())

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for HUD, Chat, and Voice streams.
    Handles real-time AI processing, tool events, and metrics.
    """
    client_id = str(uuid.uuid4())
    await manager.connect(websocket, client_id)
    
    # Send initial connection success event
    await manager.send_personal_message({
        "event": "system_status",
        "payload": {"status": "connected", "message": "JARVIS Neural Link Established"}
    }, client_id)

    # Temporary memory for this session
    session_history = []

    try:
        while True:
            message = await websocket.receive()
            
            # Handle Text Events
            if "text" in message:
                try:
                    data = json.loads(message["text"])
                    ws_event = WSEvent(**data)
                    
                    if ws_event.event == "user_message":
                        prompt = ws_event.payload.get("text", "")
                        if not prompt: continue
                        await run_ai_pipeline(prompt, session_history, client_id, websocket)

                    elif ws_event.event == "change_personality":
                        profile_id = ws_event.payload.get("profile_id")
                        if personality_manager.switch_profile(profile_id):
                            new_profile = personality_manager.get_active_profile()
                            await manager.send_personal_message({
                                "event": "system_status",
                                "payload": {"status": "personality_changed", "message": f"Personality synchronized to {new_profile.name}"}
                            }, client_id)
                        else:
                            await manager.send_personal_message({
                                "event": "system_status",
                                "payload": {"status": "error", "message": "Failed to sync personality profile."}
                            }, client_id)

                    elif ws_event.event == "update_emotion":
                        bias = ws_event.payload.get("bias", 0.0)
                        personality_manager.update_emotional_bias(bias)
                        logger.info(f"Emotional bias updated: {bias}")

                    elif ws_event.event == "voice_state":
                        pass
                        
                    elif ws_event.event == "tool_approval_response":
                        execution_id = ws_event.payload.get("execution_id")
                        approved = ws_event.payload.get("approved", False)
                        permission_manager.resolve_approval(execution_id, approved)
                        
                    elif ws_event.event == "tool_execution_request":
                        tool_name = ws_event.payload.get("tool")
                        params = ws_event.payload.get("params", {})
                        # Dispatch tool asynchronously without blocking WS router
                        asyncio.create_task(dispatcher.dispatch(tool_name, params, client_id))
                        
                except (json.JSONDecodeError, ValidationError) as e:
                    logger.error(f"Invalid WS data from {client_id}: {e}")
            
            # Handle Binary Audio Stream (from frontend mic)
            elif "bytes" in message:
                audio_data = message["bytes"]
                from ...engine.audio.stt import stt_engine
                transcript = await stt_engine.transcribe(audio_data)
                
                if transcript:
                    logger.info(f"Heard: {transcript}")
                    # Send transcript to frontend so user sees it
                    await manager.send_personal_message({
                        "event": "transcription",
                        "payload": {"text": transcript}
                    }, client_id)
                    # Directly invoke the AI pipeline with the transcript
                    await run_ai_pipeline(transcript, session_history, client_id, websocket)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)
