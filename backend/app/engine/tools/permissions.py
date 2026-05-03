from .base import AsyncTool, RiskLevel
from ...ws.manager import manager
import asyncio
from ...core.logging import logger

class PermissionManager:
    """
    Handles sandboxing and approval flows for tool execution.
    """
    def __init__(self):
        # Maps an execution ID to its asyncio.Event for pausing/resuming execution
        self.pending_approvals = {}

    async def check_permission(self, tool: AsyncTool, params: dict, client_id: str, execution_id: str) -> bool:
        """
        Determines if a tool requires user approval. 
        If HIGH risk, pauses execution and asks the frontend.
        """
        if tool.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
            # Automatically approved
            return True

        if tool.risk_level == RiskLevel.HIGH:
            logger.info(f"High risk tool {tool.name} requested. Requesting approval for execution {execution_id}.")
            
            # Send approval request to frontend
            await manager.send_personal_message({
                "event": "tool_approval_required",
                "payload": {
                    "execution_id": execution_id,
                    "tool": tool.name,
                    "params": params,
                    "description": tool.description
                }
            }, client_id)

            # Create an event to wait for the frontend's response
            approval_event = asyncio.Event()
            self.pending_approvals[execution_id] = {"event": approval_event, "approved": False}

            # Wait for user response (timeout after 60 seconds)
            try:
                await asyncio.wait_for(approval_event.wait(), timeout=60.0)
            except asyncio.TimeoutError:
                logger.warning(f"Execution {execution_id} timed out waiting for approval.")
                del self.pending_approvals[execution_id]
                return False

            # Retrieve result and cleanup
            approved = self.pending_approvals[execution_id]["approved"]
            del self.pending_approvals[execution_id]
            return approved

    def resolve_approval(self, execution_id: str, approved: bool):
        """Called by the WebSocket router when the user responds."""
        if execution_id in self.pending_approvals:
            self.pending_approvals[execution_id]["approved"] = approved
            self.pending_approvals[execution_id]["event"].set()

permission_manager = PermissionManager()
