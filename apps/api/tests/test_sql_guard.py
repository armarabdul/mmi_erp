import pytest
from app.security.sql_guard import SQLGuard

def test_sql_guard_rejects_drop():
    sql = "DROP TABLE sales;"
    is_valid, _, err = SQLGuard.validate_and_sanitize(sql)
    assert not is_valid
    assert "Forbidden" in err

def test_sql_guard_rejects_delete():
    sql = "DELETE FROM customers WHERE id = 1"
    is_valid, _, err = SQLGuard.validate_and_sanitize(sql)
    assert not is_valid
    assert "Forbidden" in err

def test_sql_guard_rejects_insert():
    sql = "INSERT INTO branches (name, city, region) VALUES ('Duqm', 'Duqm', 'Al Wusta')"
    is_valid, _, err = SQLGuard.validate_and_sanitize(sql)
    assert not is_valid
    assert "Forbidden" in err

def test_sql_guard_rejects_chained_statements():
    sql = "SELECT * FROM sales; DROP TABLE branches;"
    is_valid, _, err = SQLGuard.validate_and_sanitize(sql)
    assert not is_valid
    assert "Multiple SQL statements" in err

def test_sql_guard_rejects_unapproved_table():
    sql = "SELECT * FROM users"
    is_valid, _, err = SQLGuard.validate_and_sanitize(sql)
    assert not is_valid
    assert "not permitted" in err

def test_sql_guard_allows_valid_select():
    sql = "SELECT b.name, SUM(s.net_amount) as total_sales FROM sales s JOIN branches b ON s.branch_id = b.id GROUP BY b.name"
    is_valid, sanitized, err = SQLGuard.validate_and_sanitize(sql)
    assert is_valid
    assert err is None
    assert "LIMIT" in sanitized

def test_sql_guard_enforces_branch_filter():
    sql = "SELECT b.name, SUM(s.net_amount) as total_sales FROM sales s JOIN branches b ON s.branch_id = b.id GROUP BY b.name"
    is_valid, sanitized, err = SQLGuard.validate_and_sanitize(sql, branch_restriction_id=1)
    assert is_valid
    assert "branch_id = 1" in sanitized.lower()
