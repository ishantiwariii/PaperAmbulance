import pytest
from app.services.agent_service import form_agent

@pytest.mark.asyncio
async def test_form_agent_analysis():
    """
    Verifies that the agent can correctly identify intents from HTML labels.
    """
    mock_raw_fields = [
        {"id": "field_1", "label": "Full Name", "type": "text"},
        {"id": "field_2", "label": "Aadhaar Card", "type": "text"}
    ]
    
    mock_profile_data = {
        "full_name": "Test User",
        "aadhaar_number": "0000-0000-0000"
    }
    
    result = await form_agent.run(
        raw_fields=mock_raw_fields,
        profile_data=mock_profile_data,
        user_id="test_user"
    )
    
    # Assertions
    assert result["status"] == "ready"
    assert "full_name" in [a["intent"] for a in result["analysis"]]
    assert result["fill_map"]["field_1"] == "Test User"
    assert result["fill_map"]["field_2"] == "0000-0000-0000"

@pytest.mark.asyncio
async def test_form_agent_missing_data():
    """
    Verifies that the agent correctly identifies missing fields.
    """
    mock_raw_fields = [
        {"id": "field_income", "label": "Monthly Income", "type": "text"}
    ]
    
    mock_profile_data = {
        "full_name": "Test User"
        # income is missing
    }
    
    result = await form_agent.run(
        raw_fields=mock_raw_fields,
        profile_data=mock_profile_data,
        user_id="test_user"
    )
    
    assert result["status"] == "awaiting_data"
    assert "income" in result["missing_fields"]
    assert "income" in result["message"].lower()
