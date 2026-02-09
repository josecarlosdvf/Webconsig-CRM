"""Scope definitions and validation."""

# Domain scopes
CRM_READ = "crm:read"
CRM_WRITE = "crm:write"

SALES_READ = "sales:read"
SALES_WRITE = "sales:write"

FINANCE_READ = "finance:read"
FINANCE_WRITE = "finance:write"

BILLING_READ = "billing:read"
BILLING_WRITE = "billing:write"

INVENTORY_READ = "inventory:read"
INVENTORY_WRITE = "inventory:write"

AUTH_READ = "auth:read"
AUTH_WRITE = "auth:write"

HR_READ = "hr:read"
HR_WRITE = "hr:write"

# Shared scopes
AUDIT_READ = "audit:read"

IMPORT_READ = "import:read"
IMPORT_WRITE = "import:write"

EXTENSIONS_READ = "extensions:read"
EXTENSIONS_WRITE = "extensions:write"
EXTENSIONS_MANAGE = "extensions:manage"

# All valid scopes registry
VALID_SCOPES = {
    CRM_READ, CRM_WRITE,
    SALES_READ, SALES_WRITE,
    FINANCE_READ, FINANCE_WRITE,
    BILLING_READ, BILLING_WRITE,
    INVENTORY_READ, INVENTORY_WRITE,
    AUTH_READ, AUTH_WRITE,
    HR_READ, HR_WRITE,
    AUDIT_READ,
    IMPORT_READ, IMPORT_WRITE,
    EXTENSIONS_READ, EXTENSIONS_WRITE, EXTENSIONS_MANAGE,
}


def validate_scopes(scopes: list[str]) -> bool:
    """Validate if all scopes are valid."""
    return all(scope in VALID_SCOPES for scope in scopes)


def has_scope(user_scopes: list[str], required_scope: str) -> bool:
    """Check if user has a specific scope."""
    return required_scope in user_scopes


def has_any_scope(user_scopes: list[str], required_scopes: list[str]) -> bool:
    """Check if user has any of the required scopes."""
    return any(scope in user_scopes for scope in required_scopes)


def has_all_scopes(user_scopes: list[str], required_scopes: list[str]) -> bool:
    """Check if user has all required scopes."""
    return all(scope in user_scopes for scope in required_scopes)
