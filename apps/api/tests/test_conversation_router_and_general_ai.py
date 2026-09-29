import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.conversation import ConversationMessage
from app.models.user_preference import UserPreference
from app.models.user import User

client = TestClient(app)

def get_token(email: str, password: str = "Demo@12345") -> str:
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]

# 1. "Hello" -> GENERAL_CONVERSATION
def test_case_1_hello_general_conversation():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "Hello", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["intent"] == "GENERAL_CONVERSATION"
    assert "Hello" in data["explanation"] or "help" in data["explanation"].lower()
    # Confirm NO database rows or SQL were generated
    assert data["table_data"] == []
    assert data["technical_details"]["validated_sql"] == ""
    assert data["technical_details"]["result_row_count"] == 0

# 2. "What can you do?" -> GENERAL_CONVERSATION
def test_case_2_capabilities_general_conversation():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "What can you do?", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["intent"] == "GENERAL_CONVERSATION"
    assert any(w in data["explanation"].lower() for w in ["assistant", "analytics", "erp", "sales", "help"])
    assert data["table_data"] == []
    assert data["technical_details"]["validated_sql"] == ""

# 3. "What is an invoice?" -> GENERAL_CONVERSATION
def test_case_3_concept_definition_general_conversation():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "What is an invoice?", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["intent"] == "GENERAL_CONVERSATION"
    assert "document" in data["explanation"].lower() or "invoice" in data["explanation"].lower() or "commercial" in data["explanation"].lower()
    assert data["table_data"] == []
    assert data["technical_details"]["validated_sql"] == ""

# 4. "Show sales this month" -> ERP_ANALYTICS
def test_case_4_show_sales_this_month_erp_analytics():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "Show sales this month", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["intent"] == "ERP_ANALYTICS"
    assert len(data["visualization"]["data"]) > 0
    assert "sales" in data["technical_details"]["validated_sql"].lower()

# 5. "Show sales by branch" -> ERP_ANALYTICS
def test_case_5_show_sales_by_branch_erp_analytics():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "Show sales by branch", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["intent"] == "ERP_ANALYTICS"
    assert data["visualization"]["chart_type"] == "bar"
    assert len(data["table_data"]) > 1

# 6. "Which branch performed better?" -> CONTEXTUAL/ERP_ANALYTICS
def test_case_6_which_branch_performed_better_contextual():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    conv_id = f"test-conv-{uuid.uuid4()}"

    # Step 1: Initial question
    res1 = client.post(
        "/api/v1/analytics/query",
        json={"question": "Show sales by branch this month", "language": "en", "conversation_id": conv_id},
        headers=headers,
    )
    assert res1.status_code == 200

    # Step 2: Contextual follow-up
    res2 = client.post(
        "/api/v1/analytics/query",
        json={"question": "Which branch performed better?", "language": "en", "conversation_id": conv_id},
        headers=headers,
    )
    assert res2.status_code == 200
    data = res2.json()
    assert data["success"] is True
    assert data["intent"] in ("CONTEXTUAL", "ERP_ANALYTICS")
    # Must identify the top performing branch (Muscat)
    assert len(data["visualization"]["data"]) >= 1
    assert data["visualization"]["data"][0]["branch"] == "Muscat"

# 7. "What about last month?" -> CONTEXTUAL/ERP_ANALYTICS
def test_case_7_what_about_last_month_contextual():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    conv_id = f"test-conv-{uuid.uuid4()}"

    # Turn 1: Sales by branch
    res1 = client.post(
        "/api/v1/analytics/query",
        json={"question": "Show sales by branch this month", "language": "en", "conversation_id": conv_id},
        headers=headers,
    )
    assert res1.status_code == 200

    # Turn 2: Follow-up for last month
    res2 = client.post(
        "/api/v1/analytics/query",
        json={"question": "What about last month?", "language": "en", "conversation_id": conv_id},
        headers=headers,
    )
    assert res2.status_code == 200
    data = res2.json()
    assert data["success"] is True
    assert data["intent"] in ("CONTEXTUAL", "ERP_ANALYTICS")
    assert "2026-08" in str(data["filters_applied"]) or "August" in data["visualization"]["title"]
    assert len(data["table_data"]) > 0

# 8. Unauthorized ERP request remains blocked
def test_case_8_unauthorized_erp_request_blocked():
    # No Authorization header
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "Show sales by branch this month", "language": "en"},
    )
    assert res.status_code == 401

    # Invalid token
    res_bad = client.post(
        "/api/v1/analytics/query",
        json={"question": "Show sales by branch this month", "language": "en"},
        headers={"Authorization": "Bearer bad-token-12345"},
    )
    assert res_bad.status_code == 401

    # Malicious SQL injection via authenticated user is blocked by SQLGuard
    token = get_token("admin@mmi-demo.com")
    res_sqli = client.post(
        "/api/v1/analytics/query",
        json={"question": "DROP TABLE sales; SELECT * FROM products", "language": "en"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res_sqli.status_code == 200
    data_sqli = res_sqli.json()
    assert data_sqli["success"] is False
    assert "Security Guard Alert" in data_sqli["explanation"]

# 9. Branch user cannot access another branch
def test_case_9_branch_user_isolation_strictly_enforced():
    token = get_token("manager@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    conv_id = f"test-conv-{uuid.uuid4()}"

    # Muscat Branch Manager tries to ask for Salalah or All Branches
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "Show sales for Salalah branch this month", "language": "en", "conversation_id": conv_id},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    # SQLGuard forces user's assigned branch (Muscat, id=1)
    assert data["technical_details"]["branch_restricted"] is True
    assert "s.branch_id = 1" in data["technical_details"]["validated_sql"] or "b.id = 1" in data["technical_details"]["validated_sql"]
    for row in data["visualization"]["data"]:
        assert row.get("branch") == "Muscat"

    # Even with contextual follow-up, branch restriction remains enforced!
    res_followup = client.post(
        "/api/v1/analytics/query",
        json={"question": "Which branch performed better?", "language": "en", "conversation_id": conv_id},
        headers=headers,
    )
    assert res_followup.status_code == 200
    data_fu = res_followup.json()
    assert data_fu["technical_details"]["branch_restricted"] is True
    assert data_fu["visualization"]["data"][0]["branch"] == "Muscat"

# 10. General conversation cannot access the database
def test_case_10_general_conversation_zero_database_access():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "What is a purchase order?", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "GENERAL_CONVERSATION"
    assert data["technical_details"]["validated_sql"] == ""
    assert data["technical_details"]["result_row_count"] == 0
    assert data["table_columns"] == []
    assert data["table_data"] == []

# 11. Conversation history is persisted
def test_case_11_conversation_history_persistence():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    conv_id = f"test-conv-{uuid.uuid4()}"

    # Query 1: Greeting
    client.post(
        "/api/v1/analytics/query",
        json={"question": "Hello", "language": "en", "conversation_id": conv_id},
        headers=headers,
    )
    # Query 2: ERP query
    client.post(
        "/api/v1/analytics/query",
        json={"question": "Show sales this month", "language": "en", "conversation_id": conv_id},
        headers=headers,
    )

    # Check conversation history API
    hist_res = client.get(f"/api/v1/analytics/conversations/{conv_id}", headers=headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert hist_data["conversation_id"] == conv_id
    assert hist_data["total_messages"] == 2
    assert hist_data["messages"][0]["detected_intent"] == "GENERAL_CONVERSATION"
    assert hist_data["messages"][1]["detected_intent"] == "ERP_ANALYTICS"
    assert hist_data["messages"][1]["audit_reference"] is not None

# 12. User-specific preferences are applied only to response style, never permissions
def test_case_12_preferences_applied_to_style_never_permissions():
    token = get_token("manager@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Set user preferences to detailed
    pref_res = client.put(
        "/api/v1/analytics/preferences",
        json={
            "preferred_language": "en",
            "preferred_response_style": "detailed",
            "preferred_report_format": "table_and_chart",
            "terminology_preference": "formal",
        },
        headers=headers,
    )
    assert pref_res.status_code == 200
    assert pref_res.json()["preferred_response_style"] == "detailed"

    # Branch manager runs query - verify branch restriction CANNOT be bypassed by preferences
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "Show sales by branch this month", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    # Security permissions remain strict
    assert data["technical_details"]["branch_restricted"] is True
    assert len(data["visualization"]["data"]) == 1
    assert data["visualization"]["data"][0]["branch"] == "Muscat"

# 13. OpenAI failure produces a safe error without leaking internals
def test_case_13_openai_failure_produces_safe_error():
    from unittest.mock import patch
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Mock provider failure
    with patch("app.ai.openai_provider.OpenAIProvider.generate_text", side_effect=Exception("Internal connection refused to api.openai.com")):
        res = client.post(
            "/api/v1/analytics/query",
            json={"question": "Hello", "language": "en"},
            headers=headers,
        )
        assert res.status_code == 200
        data = res.json()
        # Verify no leaked credentials, passwords, or raw stack traces in explanation
        assert "password" not in data["explanation"].lower()
        assert "secret" not in data["explanation"].lower()
        assert "traceback" not in data["explanation"].lower()

# 14. Existing fast-path analytics still works
def test_case_14_existing_fast_path_remains_intact():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "Show me the top 10 products by sales", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["visualization"]["data"]) <= 10
    assert "CAST(SUM(si.total_amount) AS NUMERIC)" in data["technical_details"]["validated_sql"]

# 15. Existing Arabic/RTL functionality still works
def test_case_15_arabic_rtl_and_general_ai():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Arabic General AI
    res_ar_conv = client.post(
        "/api/v1/analytics/query",
        json={"question": "مرحبا", "language": "ar"},
        headers=headers,
    )
    assert res_ar_conv.status_code == 200
    data_ar_conv = res_ar_conv.json()
    assert data_ar_conv["intent"] == "GENERAL_CONVERSATION"
    assert "أهلاً" in data_ar_conv["explanation"] or "مرحبا" in data_ar_conv["explanation"] or "كيف" in data_ar_conv["explanation"]

    # Arabic ERP Concept
    res_ar_concept = client.post(
        "/api/v1/analytics/query",
        json={"question": "ما هو أمر الشراء؟", "language": "ar"},
        headers=headers,
    )
    assert res_ar_concept.status_code == 200
    data_ar_concept = res_ar_concept.json()
    assert data_ar_concept["intent"] == "GENERAL_CONVERSATION"
    assert "الشراء" in data_ar_concept["explanation"]

    # Arabic Fast-path analytics
    res_ar_analytics = client.post(
        "/api/v1/analytics/query",
        json={"question": "ما هي المبيعات حسب الفرع هذا الشهر؟", "language": "ar"},
        headers=headers,
    )
    assert res_ar_analytics.status_code == 200
    data_ar_analytics = res_ar_analytics.json()
    assert data_ar_analytics["intent"] == "ERP_ANALYTICS"
    assert data_ar_analytics["language"] == "ar"
    assert "المبيعات" in data_ar_analytics["visualization"]["title"]
    assert len(data_ar_analytics["visualization"]["data"]) > 0
