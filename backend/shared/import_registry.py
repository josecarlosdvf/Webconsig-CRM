"""Import schema registry setup."""

from domain.crm.schemas import ClientCreateRequest, LeadCreateRequest
from domain.sales.schemas import OpportunityCreateRequest
from domain.finance.schemas import (
    CompanyCreateRequest,
    AccountCreateRequest,
    PaymentCreateRequest,
    PayableCreateRequest,
    ReceivableCreateRequest,
)
from domain.billing.schemas import InvoiceCreateRequest
from domain.inventory.schemas import ItemCreateRequest
from domain.auth.schemas import UserCreateRequest, RoleCreateRequest
from domain.hr.schemas import (
    EmployeeCreateRequest,
    RecruitmentCreateRequest,
    CandidateCreateRequest,
    AbsenceCreateRequest,
    TimeEntryCreateRequest,
    LeaveRequestCreateRequest,
    DocumentCreateRequest,
    ContractCreateRequest,
    BenefitCreateRequest,
)

from shared.import_processor import register_import_schema


def setup_import_schemas():
    """Register all import schemas for validation."""
    
    # CRM
    register_import_schema("crm", "clients", ClientCreateRequest)
    register_import_schema("crm", "leads", LeadCreateRequest)
    
    # Sales
    register_import_schema("sales", "opportunities", OpportunityCreateRequest)
    
    # Finance
    register_import_schema("finance", "companies", CompanyCreateRequest)
    register_import_schema("finance", "accounts", AccountCreateRequest)
    register_import_schema("finance", "payments", PaymentCreateRequest)
    register_import_schema("finance", "payables", PayableCreateRequest)
    register_import_schema("finance", "receivables", ReceivableCreateRequest)
    
    # Billing
    register_import_schema("billing", "invoices", InvoiceCreateRequest)
    
    # Inventory
    register_import_schema("inventory", "items", ItemCreateRequest)
    
    # Auth
    register_import_schema("auth", "users", UserCreateRequest)
    register_import_schema("auth", "roles", RoleCreateRequest)
    
    # HR
    register_import_schema("hr", "employees", EmployeeCreateRequest)
    register_import_schema("hr", "recruitments", RecruitmentCreateRequest)
    register_import_schema("hr", "candidates", CandidateCreateRequest)
    register_import_schema("hr", "absences", AbsenceCreateRequest)
    register_import_schema("hr", "time_entries", TimeEntryCreateRequest)
    register_import_schema("hr", "leave_requests", LeaveRequestCreateRequest)
    register_import_schema("hr", "documents", DocumentCreateRequest)
    register_import_schema("hr", "contracts", ContractCreateRequest)
    register_import_schema("hr", "benefits", BenefitCreateRequest)
