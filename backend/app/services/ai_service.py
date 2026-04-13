from typing import List, Dict, Any
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings

class AIService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0
        )

    async def analyze_form_fields(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyzes raw form fields and returns their semantic intent.
        Input: [{'id': 'field1', 'label': 'Aadhaar Number', 'type': 'text'}, ...]
        Output: [{'field_id': 'field1', 'intent': 'aadhaar_number', 'confidence': 0.95}, ...]
        """
        prompt = ChatPromptTemplate.from_template("""
        You are an expert at understanding web forms. Analyze the following list of HTML fields and identify the semantic intent for each.
        Intents should be standardized (e.g., full_name, email, phone_number, aadhaar_number, pan_number, bank_account, ifsc_code, income, etc.).
        
        Fields: {fields}
        
        Return ONLY a JSON list of objects with "field_id", "intent", and "confidence".
        """)
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"fields": json.dumps(fields)})
        
        try:
            # Handle potential markdown formatting in response
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            return json.loads(content)
        except Exception as e:
            # Fallback or error logging
            return []

    async def map_profile_to_fields(self, analyzed_fields: List[Dict[str, Any]], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps user profile data to analyzed form fields.
        Input: analyzed_fields (from analyze_form_fields), profile_data (from DB)
        Output: {'field1': '1234-5678-9012', ...}
        """
        # This could be a pure logic mapping or another LLM call if the intent/profile keys don't match perfectly.
        # For Phase 1, we use direct intent-to-key mapping.
        fill_map = {}
        for field in analyzed_fields:
            intent = field.get("intent")
            field_id = field.get("field_id")
            if intent in profile_data:
                fill_map[field_id] = profile_data[intent]
        return fill_map

    async def parse_voice_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Parses a natural language transcript (Hindi/English) and extracts profile update fields.
        Input: "Mera name Rahul hai aur mera phone number 9876543210 hai"
        Output: {"full_name": "Rahul", "phone_number": "9876543210"}
        """
        prompt = ChatPromptTemplate.from_template("""
        You are a profile data extractor. Extract any user profile information from the following transcript.
        The transcript may be in Hindi, English, or Hinglish.
        Standardize the keys to: full_name, email, phone_number, address, aadhaar_number, pan_number, bank_account, ifsc_code, income.
        
        Transcript: {transcript}
        
        Return ONLY a JSON object with the extracted information. If a field is not present, do not include it.
        """)
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"transcript": transcript})
        
        try:
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            return json.loads(content)
        except Exception as e:
            return {}

ai_service = AIService()
