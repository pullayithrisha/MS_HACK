import os
import requests
import logging
import datetime
from typing import List, Dict
from pydantic import BaseModel

class MemoryResponse(BaseModel):
    response: str
    recalled_context: List[str]
    source: str  # "HINDSIGHT" or "MOCK"

class MemoryAgent:
    def __init__(self):
        self.api_key = os.getenv("HINDSIGHT_API_KEY")
        self.base_url = os.getenv("HINDSIGHT_URL", "https://api.hindsight.vectorize.io")
        self.mock_memory = []
        
        # Determine if we can use real Hindsight
        if self.api_key and self.api_key.lower() != "mock":
            self.use_mock = False
            logging.info("Initialized with REAL Hindsight API")
        else:
            self.use_mock = True
            logging.info("Initialized with MOCK Hindsight Memory")

    def _hindsight_store(self, session_id: str, text: str):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"items": [{"content": text}]}
        res = requests.post(f"{self.base_url}/v1/default/banks/{session_id}/memories", json=payload, headers=headers, timeout=30)
        res.raise_for_status()

    def _hindsight_recall(self, session_id: str, query: str) -> List[str]:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"query": query}
        res = requests.post(f"{self.base_url}/v1/default/banks/{session_id}/memories/recall", json=payload, headers=headers, timeout=30)
        if res.status_code == 404:
            return []
        res.raise_for_status()
        data = res.json()
        return [item.get("content", item.get("text", str(item))) for item in data.get("results", [])]

    def store_memory(self, session_id: str, content: str):
        # We parse global preferences (like "I prefer") to store them in a global session
        sentences = [s.strip() for s in content.split(".") if s.strip()]
        for sentence in sentences:
            # Store preferences globally, everything else in the specific deal session
            target_session = "user_global" if "i prefer" in sentence.lower() else session_id
            
            if self.use_mock:
                self.mock_memory.append({
                    "session_id": target_session,
                    "content": sentence,
                    "timestamp": datetime.datetime.now().isoformat()
                })
            else:
                try:
                    self._hindsight_store(target_session, sentence)
                except Exception as e:
                    logging.error(f"Hindsight API Store Error: {e}. Falling back to mock memory.")
                    self.use_mock = True
                    self.mock_memory.append({
                        "session_id": target_session,
                        "content": sentence,
                        "timestamp": datetime.datetime.now().isoformat()
                    })

    def recall_memory(self, session_id: str, query: str) -> List[str]:
        recalled = []
        if self.use_mock:
            for mem in self.mock_memory:
                if mem["session_id"] in [session_id, "user_global"]:
                    recalled.append(mem["content"])
        else:
            try:
                recalled.extend(self._hindsight_recall(session_id, query))
                recalled.extend(self._hindsight_recall("user_global", query))
            except Exception as e:
                logging.error(f"Hindsight API Recall Error: {e}. Falling back to mock memory.")
                self.use_mock = True
                for mem in self.mock_memory:
                    if mem["session_id"] in [session_id, "user_global"]:
                        recalled.append(mem["content"])
        return recalled

    def generate_response(self, session_id: str, user_input: str) -> MemoryResponse:
        recalled = self.recall_memory(session_id, user_input)
        
        # Simulate LLM Logic for consistent demo behavior
        lower_input = user_input.lower()
        response_text = ""
        
        is_stark = "stark industries" in lower_input or "stark" in session_id.lower()
        is_wayne = "wayne enterprises" in lower_input or "wayne" in session_id.lower()
        
        has_aws = any("aws" in r.lower() for r in recalled)
        has_implementation = any("implementation" in r.lower() for r in recalled)
        has_short = any("short email" in r.lower() for r in recalled)
        
        if is_stark:
            if has_implementation and has_aws:
                if has_short:
                    response_text = "Hi Tony, following up on our call. Our AWS integration deploys in under 24 hours, directly addressing your implementation timeline concerns. Let's sync with procurement. -Alex"
                else:
                    response_text = "Subject: TechFlow + Stark Industries Follow-up\n\nHi Tony,\n\nFollowing up on our call. I know implementation time and AWS integration are top priorities for you. Our platform deploys on AWS in under 24 hours, meaning you won't have the long setup delays you mentioned.\n\nLet's schedule a brief sync with your procurement team.\n\nBest,\nAlex"
            else:
                response_text = "Subject: TechFlow Follow-up\n\nHi Tony,\n\nIt was great speaking today. I've attached our general brochure. Let me know if you want to move forward.\n\nBest,\nAlex"
                
        elif is_wayne:
            if has_short:
                response_text = "Hi Bruce, our enterprise security is SOC2 compliant and ready for your review. Let's sync with procurement next week. -Alex"
            else:
                response_text = "Subject: Wayne Enterprises Follow-up\n\nHi Bruce, we have robust security features. I've attached the full security documentation for your review. Let me know if you have questions.\n\nBest,\nAlex"
        else:
            response_text = "I've drafted a generic follow-up. Please provide more specifics or let me know the client name."

        # Store input for next time
        if "draft" not in lower_input: # don't store the prompt/command itself
            self.store_memory(session_id, user_input)
            
        source = "MOCK" if self.use_mock else "HINDSIGHT"
        
        return MemoryResponse(
            response=response_text,
            recalled_context=recalled,
            source=source
        )
