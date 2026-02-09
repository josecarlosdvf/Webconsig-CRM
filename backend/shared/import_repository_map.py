"""Repository mapping for import execution."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from domain.crm import repository as crm_repo
from domain.sales import repository as sales_repo
from domain.finance import repository as finance_repo
from domain.billing import repository as billing_repo
from domain.inventory import repository as inventory_repo
from domain.auth import repository as auth_repo
from domain.hr import repository as hr_repo


class RepositoryAdapter:
    """
    Adapter interface for import processor.
    
    Wraps domain repositories to provide a consistent interface
    for the import processor.
    """
    
    def __init__(self, repository, create_method_name: str = "create"):
        self.repository = repository
        self.create_method_name = create_method_name
    
    async def create(self, session: AsyncSession, tenant_id: UUID, data: dict[str, Any]):
        """
        Create a record using the domain repository.
        
        Args:
            session: Database session
            tenant_id: Tenant ID
            data: Validated data dict (from Pydantic schema)
        """
        # Get the create method from repository
        create_method = getattr(self.repository, self.create_method_name)
        
        # Different repositories have different signatures
        # Most follow: create_X(session, entity_instance)
        # We need to instantiate the model first
        
        # This is a simplified approach - in production, we'd need:
        # 1. Model class mapping per entity
        # 2. Proper instance creation with tenant_id
        # 3. Handle relationships and nested data
        
        # For now, return the method for the caller to handle
        return create_method


# Repository mapping: domain.entity -> (repository, create_method_name)
REPOSITORY_MAP = {
    # CRM
    "crm.clients": (crm_repo, "create_client"),
    "crm.leads": (crm_repo, "create_lead"),
    
    # Sales
    "sales.opportunities": (sales_repo, "create_opportunity"),
    
    # Finance
    "finance.companies": (finance_repo, "create_company"),
    "finance.accounts": (finance_repo, "create_account"),
    "finance.payments": (finance_repo, "create_payment"),
    "finance.payables": (finance_repo, "create_payable"),
    "finance.receivables": (finance_repo, "create_receivable"),
    
    # Billing
    "billing.invoices": (billing_repo, "create_invoice"),
    
    # Inventory
    "inventory.items": (inventory_repo, "create_item"),
    
    # Auth
    "auth.users": (auth_repo, "create_user"),
    "auth.roles": (auth_repo, "create_role"),
    
    # HR
    "hr.employees": (hr_repo, "create_employee"),
    "hr.recruitments": (hr_repo, "create_recruitment"),
    "hr.candidates": (hr_repo, "create_candidate"),
    "hr.absences": (hr_repo, "create_absence"),
    "hr.time_entries": (hr_repo, "create_time_entry"),
    "hr.leave_requests": (hr_repo, "create_leave_request"),
    "hr.documents": (hr_repo, "create_document"),
    "hr.contracts": (hr_repo, "create_contract"),
    "hr.benefits": (hr_repo, "create_benefit"),
}


def get_repository_adapter(domain: str, entity: str) -> RepositoryAdapter | None:
    """
    Get repository adapter for a domain.entity.
    
    Args:
        domain: Domain name (e.g., "crm")
        entity: Entity name (e.g., "clients")
        
    Returns:
        RepositoryAdapter instance or None if not found
    """
    key = f"{domain}.{entity}"
    mapping = REPOSITORY_MAP.get(key)
    
    if not mapping:
        return None
    
    repository, method_name = mapping
    return RepositoryAdapter(repository, method_name)
