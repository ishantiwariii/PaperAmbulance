from typing import Annotated, Any, Dict, List, TypedDict, Union
from langgraph.graph import StateGraph, END
from app.services.ai_service import ai_service
from app.db import models
from sqlalchemy.orm import Session

class FormAgentState(TypedDict):
    """
    Maintains the state of the form filling process.
    """
    user_id: str
    raw_fields: List[Dict[str, Any]]
    profile_data: Dict[str, Any]
    analysis: List[Dict[str, Any]]
    fill_map: Dict[str, Any]
    missing_fields: List[str]
    status: str # 'analyzing', 'matching', 'awaiting_data', 'ready'
    message: str

class FormAgent:
    def __init__(self):
        self.workflow = StateGraph(FormAgentState)
        self._build_graph()

    def _build_graph(self):
        # 1. Add Nodes
        self.workflow.add_node("analyze", self.analyze_node)
        self.workflow.add_node("match_data", self.match_data_node)
        
        # 2. Define Flow
        self.workflow.set_entry_point("analyze")
        self.workflow.add_edge("analyze", "match_data")
        self.workflow.add_edge("match_data", END)
        
        # Compile
        self.app = self.workflow.compile()

    async def analyze_node(self, state: FormAgentState):
        """Node to understand the fields on the page."""
        analysis = await ai_service.analyze_form_fields(state["raw_fields"])
        return {
            "analysis": analysis,
            "status": "matching",
            "message": "Form fields analyzed successfully."
        }

    async def match_data_node(self, state: FormAgentState):
        """Node to map analyzed fields to user profile data."""
        profile = state["profile_data"]
        analysis = state["analysis"]
        
        fill_map = await ai_service.map_profile_to_fields(analysis, profile)
        
        # Identify missing data that the user *should* have provided
        # based on what the form needs
        all_required_intents = [item["intent"] for item in analysis if item["intent"] != "unknown"]
        missing = [intent for intent in all_required_intents if intent not in profile or not profile[intent]]
        
        status = "ready" if not missing else "awaiting_data"
        msg = "Ready to fill!" if status == "ready" else f"Missing info: {', '.join(missing)}"
        
        return {
            "fill_map": fill_map,
            "missing_fields": missing,
            "status": status,
            "message": msg
        }

    async def run(self, raw_fields: List[Dict[str, Any]], profile_data: Dict[str, Any], user_id: str):
        """Entry point to execute the agent."""
        initial_state = {
            "user_id": user_id,
            "raw_fields": raw_fields,
            "profile_data": profile_data,
            "analysis": [],
            "fill_map": {},
            "missing_fields": [],
            "status": "starting",
            "message": "Agent initialized."
        }
        return await self.app.ainvoke(initial_state)

form_agent = FormAgent()
