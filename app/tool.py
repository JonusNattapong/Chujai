import json
import time
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Result from a tool execution."""
    output: str = ""
    data: Dict[str, Any] = Field(default_factory=dict)


class PlanningTool(BaseModel):
    """Tool for managing plans."""
    
    plans: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the planning tool with the given arguments.
        
        Commands:
        - create: Create a new plan
        - update: Update an existing plan
        - get: Get an existing plan
        - mark_step: Mark a step as completed, in_progress, or blocked
        - add_notes: Add notes to a step
        """
        command = kwargs.get("command", "")
        plan_id = kwargs.get("plan_id", f"plan_{int(time.time())}")
        
        if command == "create":
            return await self._create_plan(plan_id, **kwargs)
        elif command == "update":
            return await self._update_plan(plan_id, **kwargs)
        elif command == "get":
            return await self._get_plan(plan_id)
        elif command == "mark_step":
            return await self._mark_step(plan_id, **kwargs)
        elif command == "add_notes":
            return await self._add_notes(plan_id, **kwargs)
        else:
            return ToolResult(output=f"Unknown command: {command}")
    
    async def _create_plan(self, plan_id: str, **kwargs) -> ToolResult:
        """Create a new plan."""
        title = kwargs.get("title", "New Plan")
        steps = kwargs.get("steps", [])
        
        # Create the plan
        self.plans[plan_id] = {
            "title": title,
            "steps": steps,
            "step_statuses": ["not_started"] * len(steps),
            "step_notes": [""] * len(steps),
            "created_at": time.time()
        }
        
        return ToolResult(
            output=f"Created plan: {title} with {len(steps)} steps.",
            data=self.plans[plan_id]
        )
    
    async def _update_plan(self, plan_id: str, **kwargs) -> ToolResult:
        """Update an existing plan."""
        if plan_id not in self.plans:
            return ToolResult(output=f"Plan {plan_id} not found.")
        
        # Get the plan
        plan = self.plans[plan_id]
        
        # Update title if provided
        if "title" in kwargs:
            plan["title"] = kwargs["title"]
        
        # Replace steps if provided
        if "steps" in kwargs:
            old_len = len(plan["steps"])
            new_len = len(kwargs["steps"])
            plan["steps"] = kwargs["steps"]
            
            # Adjust statuses and notes
            if new_len > old_len:
                plan["step_statuses"].extend(["not_started"] * (new_len - old_len))
                plan["step_notes"].extend([""] * (new_len - old_len))
            elif new_len < old_len:
                plan["step_statuses"] = plan["step_statuses"][:new_len]
                plan["step_notes"] = plan["step_notes"][:new_len]
        
        # Add steps if provided
        if "add_steps" in kwargs:
            plan["steps"].extend(kwargs["add_steps"])
            plan["step_statuses"].extend(["not_started"] * len(kwargs["add_steps"]))
            plan["step_notes"].extend([""] * len(kwargs["add_steps"]))
        
        # Remove steps if indices provided
        if "remove_indices" in kwargs:
            indices = sorted(kwargs["remove_indices"], reverse=True)
            for i in indices:
                if 0 <= i < len(plan["steps"]):
                    del plan["steps"][i]
                    if i < len(plan["step_statuses"]):
                        del plan["step_statuses"][i]
                    if i < len(plan["step_notes"]):
                        del plan["step_notes"][i]
        
        return ToolResult(
            output=f"Updated plan: {plan['title']} with {len(plan['steps'])} steps.",
            data=plan
        )
    
    async def _get_plan(self, plan_id: str) -> ToolResult:
        """Get an existing plan."""
        if plan_id not in self.plans:
            return ToolResult(output=f"Plan {plan_id} not found.")
        
        plan = self.plans[plan_id]
        
        # Create a formatted representation of the plan
        title = plan["title"]
        steps = plan["steps"]
        step_statuses = plan["step_statuses"]
        step_notes = plan["step_notes"]
        
        # Count steps by status
        status_counts = {
            "completed": 0,
            "in_progress": 0,
            "blocked": 0,
            "not_started": 0,
        }
        
        for status in step_statuses:
            if status in status_counts:
                status_counts[status] += 1
        
        completed = status_counts["completed"]
        total = len(steps)
        progress = (completed / total) * 100 if total > 0 else 0
        
        plan_text = f"Plan: {title} (ID: {plan_id})\n"
        plan_text += "=" * len(plan_text) + "\n\n"
        
        plan_text += f"Progress: {completed}/{total} steps completed ({progress:.1f}%)\n"
        plan_text += f"Status: {status_counts['completed']} completed, {status_counts['in_progress']} in progress, "
        plan_text += f"{status_counts['blocked']} blocked, {status_counts['not_started']} not started\n\n"
        plan_text += "Steps:\n"
        
        for i, (step, status, notes) in enumerate(zip(steps, step_statuses, step_notes)):
            if status == "completed":
                status_mark = "[✓]"
            elif status == "in_progress":
                status_mark = "[→]"
            elif status == "blocked":
                status_mark = "[!]"
            else:  # not_started
                status_mark = "[ ]"
                
            plan_text += f"{i}. {status_mark} {step}\n"
            if notes:
                plan_text += f"   Notes: {notes}\n"
        
        return ToolResult(output=plan_text, data=plan)
    
    async def _mark_step(self, plan_id: str, **kwargs) -> ToolResult:
        """Mark a step as completed, in_progress, or blocked."""
        if plan_id not in self.plans:
            return ToolResult(output=f"Plan {plan_id} not found.")
        
        step_index = kwargs.get("step_index")
        step_status = kwargs.get("step_status", "completed")
        
        if step_index is None:
            return ToolResult(output="Step index not provided.")
        
        plan = self.plans[plan_id]
        steps = plan["steps"]
        
        if step_index < 0 or step_index >= len(steps):
            return ToolResult(output=f"Step index {step_index} out of range.")
        
        # Ensure step_statuses list is long enough
        while len(plan["step_statuses"]) <= step_index:
            plan["step_statuses"].append("not_started")
        
        # Update the status
        plan["step_statuses"][step_index] = step_status
        
        return ToolResult(
            output=f"Marked step {step_index} as {step_status}.",
            data=plan
        )
    
    async def _add_notes(self, plan_id: str, **kwargs) -> ToolResult:
        """Add notes to a step."""
        if plan_id not in self.plans:
            return ToolResult(output=f"Plan {plan_id} not found.")
        
        step_index = kwargs.get("step_index")
        notes = kwargs.get("notes", "")
        
        if step_index is None:
            return ToolResult(output="Step index not provided.")
        
        plan = self.plans[plan_id]
        steps = plan["steps"]
        
        if step_index < 0 or step_index >= len(steps):
            return ToolResult(output=f"Step index {step_index} out of range.")
        
        # Ensure step_notes list is long enough
        while len(plan["step_notes"]) <= step_index:
            plan["step_notes"].append("")
        
        # Update the notes
        plan["step_notes"][step_index] = notes
        
        return ToolResult(
            output=f"Added notes to step {step_index}.",
            data=plan
        )
    
    def to_param(self) -> Dict:
        """Convert the tool to a parameter format for LLMs."""
        return {
            "type": "function",
            "function": {
                "name": "planning",
                "description": "Create and manage plans with steps",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "enum": ["create", "update", "get", "mark_step", "add_notes"],
                            "description": "The command to execute"
                        },
                        "plan_id": {
                            "type": "string",
                            "description": "The ID of the plan to operate on"
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the plan (for create/update)"
                        },
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "The steps of the plan (for create/update)"
                        },
                        "add_steps": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Steps to add to the plan (for update)"
                        },
                        "remove_indices": {
                            "type": "array",
                            "items": {
                                "type": "integer"
                            },
                            "description": "Indices of steps to remove (for update)"
                        },
                        "step_index": {
                            "type": "integer",
                            "description": "The index of the step to operate on (for mark_step/add_notes)"
                        },
                        "step_status": {
                            "type": "string",
                            "enum": ["not_started", "in_progress", "completed", "blocked"],
                            "description": "The status to set for the step (for mark_step)"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes to add to the step (for add_notes)"
                        }
                    },
                    "required": ["command"]
                }
            }
        }
