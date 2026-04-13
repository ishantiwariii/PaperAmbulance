import asyncio
import os
import sys
from typing import List, Dict, Any

# Ensure we can import from the app directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set dummy env if not present for local testing without .env loading
# But we have a .env, so we can use python-dotenv
from dotenv import load_dotenv
load_dotenv()

from app.services.agent_service import form_agent

async def run_simulation():
    # Set console encoding for Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("--- Starting PaperAmbulance AI Agent Simulation ---")
    
    # 1. Mock Raw Form Fields (What the Chrome Extension would detect)
    mock_raw_fields = [
        {"id": "input_1", "label": "Full Name", "type": "text"},
        {"id": "dob_field", "label": "Date of Birth", "type": "date"},
        {"id": "f_name", "label": "पिता का नाम (Father's Name)", "type": "text"},
        {"id": "pan_val", "label": "Permanent Account Number", "type": "text"},
        {"id": "aadhaar_id", "label": "Aadhaar Card Number", "type": "number"},
        {"id": "annual_inc", "label": "Annual Family Income", "type": "text"},
        {"id": "submit_btn", "label": "Submit Application", "type": "submit"}
    ]
    
    # 2. Mock User Profile Data (What is stored in NeonDB)
    mock_profile_data = {
        "full_name": "Rajesh Kumar",
        "date_of_birth": "1990-05-15",
        "father_name": "Ramesh Kumar",
        "pan_number": "ABCDE1234F",
        "aadhaar_number": "1234-5678-9012",
        # Note: missing income on purpose to test "missing_fields"
    }
    
    user_id = "user_test_123"
    
    print("\n[Input] Fields detected on page:")
    for f in mock_raw_fields:
        print(f"  - {f['label']} (ID: {f['id']})")
        
    print(f"\n[Input] User Profile keys: {list(mock_profile_data.keys())}")
    
    # 3. Running the Agent
    print("\n--- Running FormAgent (Gemini 2.5 Flash) ---")
    try:
        result = await form_agent.run(
            raw_fields=mock_raw_fields,
            profile_data=mock_profile_data,
            user_id=user_id
        )
        
        # 4. Results
        print("\n--- Simulation Results ---")
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        
        print("\nFill Map (Generated auto-fill values):")
        fill_map = result.get("fill_map", {})
        if not fill_map:
            print("  (Empty - No mappings found)")
        for field_id, value in fill_map.items():
            print(f"  {field_id} -> {value}")
            
        print("\nMissing Data identified:")
        missing = result.get("missing_fields", [])
        if not missing:
            print("  (None - All required data present)")
        else:
            for m in missing:
                print(f"  - {m}")
                
        print("\nAI Analysis Summary:")
        for item in result.get("analysis", []):
            print(f"  Field: {item.get('field_id')} -> Intent: {item.get('intent')} (Conf: {item.get('confidence')})")

    except Exception as e:
        print(f"\n❌ Error during simulation: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_simulation())
