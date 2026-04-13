from typing import List, Dict, Any, Optional
import json
import re

class AIService:
    """
    AIService now provides a robust MANAUL (Rule-based) parsing engine.
    This ensures reliability without external API dependencies.
    """
    def __init__(self):
        # We keep the slots but don't require them for the manual engine
        self.llm = None 
        
    async def analyze_form_fields(self, fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        MANUAL VERSION: Analyzes raw form fields based on keywords in labels/names.
        """
        field_keywords = {
            "full_name": ["name", "firstname", "lastname", "naam", "user", "owner"],
            "email": ["email", "mail", "e-mail"],
            "phone_number": ["phone", "mobile", "contact", "tel", "number", "no"],
            "address": ["address", "addr", "location", "city", "state", "pincode", "zip", "pata"],
            "aadhaar_number": ["aadhaar", "adhar", "uidai", "uid"],
            "pan_number": ["pan", "tax", "permanent"],
            "bank_account": ["account", "acc", "bank_account"],
            "ifsc_code": ["ifsc", "branch", "bank_code"],
            "income": ["income", "salary", "earnings"]
        }

        analyzed = []
        for field in fields:
            # Check ID, Name, and Placeholder
            search_str = f"{field.get('id', '')} {field.get('name', '')} {field.get('placeholder', '')}".lower()
            
            detected_intent = "unknown"
            for intent, keywords in field_keywords.items():
                if any(kw in search_str for kw in keywords):
                    detected_intent = intent
                    break
            
            analyzed.append({
                "field_id": field.get("id") or field.get("name"),
                "intent": detected_intent,
                "confidence": 1.0 if detected_intent != "unknown" else 0.0
            })
        
        return analyzed

    async def map_profile_to_fields(self, analyzed_fields: List[Dict[str, Any]], profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps user profile data to analyzed form fields.
        """
        fill_map = {}
        for field in analyzed_fields:
            intent = field.get("intent")
            field_id = field.get("field_id")
            if intent in profile_data and profile_data[intent]:
                fill_map[field_id] = profile_data[intent]
        return fill_map

    async def parse_voice_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        MANUAL VERSION: Extracts data using regex patterns.
        Supports common Hindi/English patterns.
        """
        extracted = {}
        transcript_lower = transcript.lower()

        # 1. Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', transcript)
        if email_match:
            extracted["email"] = email_match.group(0)

        # 2. Phone (Indian 10-digit)
        phone_match = re.search(r'\b[6-9]\d{9}\b', transcript)
        if phone_match:
            extracted["phone_number"] = phone_match.group(0)

        # 3. Aadhaar (12 digits, optional spaces)
        aadhaar_match = re.search(r'\b\d{4}\s?\d{4}\s?\d{4}\b', transcript)
        if aadhaar_match:
            extracted["aadhaar_number"] = aadhaar_match.group(0).replace(" ", "")

        # 4. PAN Card
        pan_match = re.search(r'\b[a-z]{5}\d{4}[a-z]\b', transcript_lower)
        if pan_match:
            extracted["pan_number"] = pan_match.group(0).upper()

        # 5. Full Name (Pattern Match: "Mera naam [Name] hai" or "My name is [Name]")
        name_patterns = [
            r'(?:mera naam|my name is|name is|i am)[:\s]+([^,\.\n\sisaurhai]+)',
            r'naam[:\s]+([^,\.\n\sisaurhai]+)'
        ]
        for pattern in name_patterns:
            name_match = re.search(pattern, transcript_lower)
            if name_match:
                extracted["full_name"] = name_match.group(1).strip().title()
                break
        
        # 6. IFSC Code
        ifsc_match = re.search(r'\b[a-z]{4}0[a-z0-9]{6}\b', transcript_lower)
        if ifsc_match:
            extracted["ifsc_code"] = ifsc_match.group(0).upper()

        return extracted

ai_service = AIService()
