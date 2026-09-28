import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_token(email: str, password: str = "Demo@12345") -> str:
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]

def test_admin_sales_by_branch_scenario_1():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "Show me sales by branch this month", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["visualization"]["chart_type"] == "bar"
    assert len(data["visualization"]["data"]) > 1  # Admin sees multiple branches
    assert data["technical_details"]["branch_restricted"] is False

def test_arabic_query_scenario_2():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "ما هي المبيعات حسب الفرع هذا الشهر؟", "language": "ar"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["language"] == "ar"
    assert "المبيعات" in data["visualization"]["title"]
    assert len(data["visualization"]["data"]) > 0

def test_branch_manager_isolation_scenario_5():
    token = get_token("manager@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "Show me sales by branch this month", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["technical_details"]["branch_restricted"] is True
    # Manager must only see 1 branch (Muscat)
    assert len(data["visualization"]["data"]) == 1
    assert data["visualization"]["data"][0]["branch"] == "Muscat"

def test_top_products_scenario_3():
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

def test_unsafe_query_rejection_scenario_6():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "DROP TABLE sales; SELECT * FROM products", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert "Security Guard Alert" in data["explanation"]

def test_reports_preview_and_excel_export():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    # Preview
    prev_res = client.get("/api/v1/reports/sales-by-branch/preview", headers=headers)
    assert prev_res.status_code == 200
    assert len(prev_res.json()["data"]) > 0

    # Excel export
    exp_res = client.get("/api/v1/reports/sales-by-branch/export?format=xlsx", headers=headers)
    assert exp_res.status_code == 200
    assert len(exp_res.content) > 1000
    assert "spreadsheetml" in exp_res.headers["content-type"]

def test_dashboard_analytics_api():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/dashboard", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["kpis"]) == 6
    assert len(data["sales_trend"]) > 0
    assert len(data["sales_by_branch"]) > 0
    assert len(data["top_products"]) <= 10

def test_monthly_trend_scenario_4():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "Show me monthly sales for the last 12 months", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["visualization"]["chart_type"] == "line"
    assert len(data["visualization"]["data"]) > 0

def test_total_sales_value_this_month():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "What is the total sales value this month?", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["visualization"]["data"]) == 1
    assert "total_sales" in data["visualization"]["data"][0]

def test_highest_sales_branch():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post(
        "/api/v1/analytics/query",
        json={"question": "Which branch has the highest sales?", "language": "en"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert len(data["visualization"]["data"]) == 1
    assert data["visualization"]["data"][0]["branch"] == "Muscat"

def test_audit_logs_endpoint():
    token = get_token("admin@mmi-demo.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/audit?page=1&page_size=10", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_count"] > 0
    assert len(data["items"]) > 0

def test_root_health_liveness_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


