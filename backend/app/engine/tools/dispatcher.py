import uuid
import json
from typing import Dict, Any
from .registry import tool_registry
from .permissions import permission_manager
from ...ws.manager import manager
from ...core.logging import logger

class ActionDispatcher:
    """
    Orchestrates the execution of a tool request from the AI.
    Handles validation, permission checking, execution, and sending results.
    """
    async def dispatch(self, tool_name: str, params: Dict[str, Any], client_id: str) -> str:
        execution_id = str(uuid.uuid4())
        tool = tool_registry.get_tool(tool_name)
        
        if not tool:
            err_msg = f"Tool '{tool_name}' not found."
            logger.error(err_msg)
            return json.dumps({"status": "error", "message": err_msg})

        if not tool.validate_params(params):
            err_msg = f"Invalid parameters for '{tool_name}'."
            logger.error(err_msg)
            return json.dumps({"status": "error", "message": err_msg})

        # Check permissions (Will pause if HIGH risk)
        approved = await permission_manager.check_permission(tool, params, client_id, execution_id)
        
        if not approved:
            err_msg = f"Execution of '{tool_name}' was denied or timed out."
            logger.warning(err_msg)
            return json.dumps({"status": "error", "message": err_msg})

        # Execute
        try:
            logger.info(f"Executing '{tool_name}' with {params}")
            # Notify frontend that execution started
            await manager.send_personal_message({
                "event": "tool_execution_started",
                "payload": {"tool": tool_name, "execution_id": execution_id}
            }, client_id)

            result = await tool.execute(params)
            
            # Optionally log to DB here
            
            # Notify frontend of completion
            await manager.send_personal_message({
                "event": "tool_execution_completed",
                "payload": {"tool": tool_name, "execution_id": execution_id, "result": result}
            }, client_id)

            return json.dumps({"status": "success", "result": result})
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}", exc_info=True)
            return json.dumps({"status": "error", "message": str(e)})

dispatcher = ActionDispatcher()
