import re
from typing import Tuple, List, Set, Optional
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison
from sqlparse.tokens import DML, DDL, Keyword

FORBIDDEN_KEYWORDS: Set[str] = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", 
    "EXEC", "EXECUTE", "CREATE", "GRANT", "REVOKE", "MERGE",
    "REPLACE", "UPSERT", "ATTACH", "DETACH", "PRAGMA", "VACUUM",
    "INTO OUTFILE", "LOAD DATA", "SLEEP", "BENCHMARK", "PG_SLEEP",
    "SHUTDOWN", "CALL", "XP_CMDSHELL"
}

ALLOWED_TABLES: Set[str] = {
    "branches", "categories", "products", "customers", 
    "suppliers", "sales", "sale_items", "purchases", "inventory"
}

ALLOWED_COLUMNS: Set[str] = {
    # branches
    "id", "name", "city", "region",
    # categories
    "description",
    # products
    "category_id", "sku", "price", "cost", "active",
    # customers
    "email", "branch_id", "customer_type", "created_at",
    # suppliers
    "contact",
    # sales
    "invoice_number", "customer_id", "sale_date", "gross_amount", 
    "discount", "tax", "net_amount", "status",
    # sale_items
    "sale_id", "product_id", "quantity", "unit_price", "total_amount",
    # purchases
    "supplier_id", "purchase_date",
    # inventory
    "reorder_level", "updated_at",
    # aggregate expressions and aliases
    "total_sales", "sales", "revenue", "order_count", "units_sold", 
    "avg_order_value", "inventory_value", "purchase_value", "branch",
    "product", "category", "period", "count", "sum", "avg", "month_str"
}

MAX_ROW_LIMIT = 500

class SQLGuardError(Exception):
    pass

class SQLGuard:
    @classmethod
    def validate_and_sanitize(
        cls, 
        sql_query: str, 
        branch_restriction_id: Optional[int] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Validates SQL against strict read-only rules, AST verification,
        and injects mandatory branch restriction for RBAC if specified.
        Returns: (is_valid, sanitized_sql, error_message)
        """
        if not sql_query or not sql_query.strip():
            return False, "", "Empty SQL query provided"

        # 1. Clean query
        cleaned = sql_query.strip().rstrip(";")
        
        # 2. Check for multiple statements (prevent query chaining SQL injection)
        parsed_statements = sqlparse.split(cleaned)
        if len(parsed_statements) > 1:
            return False, "", "Forbidden: Multiple SQL statements detected"

        # 3. Check forbidden words with word boundaries
        upper_sql = cleaned.upper()
        for forbidden in FORBIDDEN_KEYWORDS:
            pattern = rf"\b{re.escape(forbidden)}\b"
            if re.search(pattern, upper_sql):
                return False, "", f"Forbidden SQL operation detected: '{forbidden}'. Only SELECT queries are permitted."

        # 4. Must start with SELECT or WITH (for CTEs)
        parsed = sqlparse.parse(cleaned)[0]
        first_token = None
        for token in parsed.tokens:
            if not token.is_whitespace and not token.ttype in (sqlparse.tokens.Comment, sqlparse.tokens.Comment.Multiline):
                first_token = token
                break

        if not first_token or first_token.value.upper() not in ("SELECT", "WITH"):
            return False, "", "Forbidden query: Must begin with SELECT or WITH statement"

        # 5. Extract tables and check against whitelist
        tables_found = cls._extract_tables(parsed)
        for tbl in tables_found:
            tbl_clean = tbl.lower().replace('"', '').replace('`', '').replace("'", "")
            # Skip aliases or CTE names
            if "." in tbl_clean:
                tbl_clean = tbl_clean.split(".")[-1]
            if tbl_clean not in ALLOWED_TABLES and tbl_clean != "":
                return False, "", f"Security Guard: Access to table '{tbl_clean}' is not permitted"

        # 6. Branch Security Injection (Section 23 - Server-side Authorization)
        # If user is restricted to a branch (e.g. Branch Manager), enforce branch filter
        if branch_restriction_id is not None:
            cleaned = cls._enforce_branch_filter(cleaned, branch_restriction_id)

        # 7. Enforce LIMIT row boundary to prevent memory exhaustion / DoS
        if "LIMIT" not in upper_sql:
            cleaned = f"{cleaned} LIMIT {MAX_ROW_LIMIT}"
        else:
            # Check limit value
            limit_match = re.search(r"LIMIT\s+(\d+)", upper_sql)
            if limit_match:
                limit_val = int(limit_match.group(1))
                if limit_val > MAX_ROW_LIMIT:
                    cleaned = re.sub(r"LIMIT\s+\d+", f"LIMIT {MAX_ROW_LIMIT}", cleaned, flags=re.IGNORECASE)

        return True, cleaned, None

    @classmethod
    def _extract_tables(cls, parsed: sqlparse.sql.Statement) -> Set[str]:
        tables = set()
        from_seen = False
        join_seen = False

        for token in parsed.tokens:
            if token.is_whitespace:
                continue
            if token.value.upper() in ("FROM", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN"):
                from_seen = True
                join_seen = True
                continue
            if from_seen or join_seen:
                if isinstance(token, IdentifierList):
                    for identifier in token.get_identifiers():
                        tables.add(identifier.get_real_name() or identifier.get_name() or str(identifier))
                elif isinstance(token, Identifier):
                    tables.add(token.get_real_name() or token.get_name() or str(token))
                elif token.ttype is sqlparse.tokens.Keyword and token.value.upper() not in ("ON", "AS", "WHERE", "GROUP", "ORDER"):
                    tables.add(token.value)
                from_seen = False
                join_seen = False
            if isinstance(token, Where):
                pass
        return tables

    @classmethod
    def _enforce_branch_filter(cls, sql: str, branch_id: int) -> str:
        """
        Guarantees that a Branch Manager cannot see data from other branches,
        regardless of what was requested in the natural language prompt.
        """
        # Detect if sales or purchases or customers or inventory is joined
        upper = sql.upper()
        filter_clause = ""
        
        if re.search(r"\bsales\s+as\s+s\b|\bsales\s+s\b", sql, re.IGNORECASE):
            filter_clause = f"s.branch_id = {branch_id}"
        elif re.search(r"\bpurchases\s+as\s+p\b|\bpurchases\s+p\b", sql, re.IGNORECASE):
            filter_clause = f"p.branch_id = {branch_id}"
        elif re.search(r"\binventory\s+as\s+i\b|\binventory\s+i\b", sql, re.IGNORECASE):
            filter_clause = f"i.branch_id = {branch_id}"
        elif re.search(r"\bbranches\s+as\s+b\b|\bbranches\s+b\b", sql, re.IGNORECASE):
            filter_clause = f"b.id = {branch_id}"
        elif "sales" in sql.lower():
            filter_clause = f"sales.branch_id = {branch_id}"
        elif "purchases" in sql.lower():
            filter_clause = f"purchases.branch_id = {branch_id}"
        elif "inventory" in sql.lower():
            filter_clause = f"inventory.branch_id = {branch_id}"
        elif "branches" in sql.lower():
            filter_clause = f"branches.id = {branch_id}"
        else:
            filter_clause = f"branch_id = {branch_id}"

        # Inject into WHERE clause or append WHERE
        if "WHERE" in upper:
            # Replace first WHERE with WHERE <filter_clause> AND
            idx = upper.find("WHERE")
            return sql[:idx + 5] + f" {filter_clause} AND " + sql[idx + 5:]
        else:
            # Check for GROUP BY, ORDER BY, LIMIT
            for keyword in ["GROUP BY", "ORDER BY", "LIMIT"]:
                if keyword in upper:
                    idx = upper.find(keyword)
                    return sql[:idx] + f" WHERE {filter_clause} " + sql[idx:]
            return f"{sql} WHERE {filter_clause}"
