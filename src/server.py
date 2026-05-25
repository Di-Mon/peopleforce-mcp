import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.streamable_http import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse

from auth import BearerAuthMiddleware
from peopleforce import PeopleForceClient

load_dotenv()


@asynccontextmanager
async def lifespan(app: Any) -> AsyncIterator[dict[str, Any]]:
    api_key = os.environ["PEOPLEFORCE_API_KEY"]
    client = PeopleForceClient(api_key)
    try:
        yield {"pf": client}
    finally:
        await client.close()


mcp = FastMCP(
    "peopleforce",
    lifespan=lifespan,
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


def _pf() -> PeopleForceClient:
    return mcp.get_context().request_context.lifespan_context["pf"]


# ==============================================================================
# Employees
# ==============================================================================


@mcp.tool()
async def list_employees(
    status: str | None = None,
    department: str | None = None,
    location: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> dict[str, Any]:
    """
    Return a paginated list of employees.

    Args:
        status:     Filter by employment status, e.g. "active", "terminated".
        department: Filter by department name or ID.
        location:   Filter by office location name or ID.
        page:       Page number (1-based).
        per_page:   Results per page (default 50).
    """
    return await _pf().list_employees(status, department, location, page, per_page)


@mcp.tool()
async def get_employee(employee_id: str) -> dict[str, Any]:
    """
    Fetch the full profile of a single employee by their PeopleForce ID.

    Args:
        employee_id: Numeric or string employee ID.
    """
    return await _pf().get_employee(employee_id)


@mcp.tool()
async def get_employee_by_email(email: str) -> dict[str, Any]:
    """
    Look up an employee by their work email address.

    Args:
        email: Work email, e.g. "jane.doe@company.com".
    """
    return await _pf().get_employee_by_email(email)


@mcp.tool()
async def list_terminated_employees(page: int = 1, per_page: int = 50) -> dict[str, Any]:
    """
    Return a paginated list of terminated (former) employees.

    Args:
        page:     Page number.
        per_page: Results per page.
    """
    return await _pf().list_terminated_employees(page, per_page)


@mcp.tool()
async def list_employee_birthdays(month: int | None = None) -> Any:
    """
    Return employees with upcoming or current-month birthdays.

    Args:
        month: Optional month number (1–12) to filter by. Defaults to current month.
    """
    return await _pf().list_employee_birthdays(month)


@mcp.tool()
async def list_employee_anniversaries(month: int | None = None) -> Any:
    """
    Return employees with work anniversaries.

    Args:
        month: Optional month number (1–12) to filter by.
    """
    return await _pf().list_employee_anniversaries(month)


@mcp.tool()
async def list_employee_fields() -> Any:
    """
    Return all custom and standard employee profile field definitions.
    Useful for understanding what data is stored on employee profiles.
    """
    return await _pf().list_employee_fields()


@mcp.tool()
async def get_employee_table(employee_id: str) -> Any:
    """
    Return custom table data attached to an employee's profile.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_table(employee_id)


@mcp.tool()
async def get_employee_certifications(employee_id: str) -> Any:
    """
    Return certifications and licences on file for an employee.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_certifications(employee_id)


@mcp.tool()
async def get_employee_documents(employee_id: str) -> Any:
    """
    Return the list of documents attached to an employee's profile.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_documents(employee_id)


@mcp.tool()
async def get_employee_document(employee_id: str, document_id: str) -> Any:
    """
    Fetch a single document from an employee's profile.

    Args:
        employee_id:  Employee ID.
        document_id:  Document ID.
    """
    return await _pf().get_employee_document(employee_id, document_id)


@mcp.tool()
async def get_employee_field_histories(employee_id: str, field: str | None = None) -> Any:
    """
    Return the change history of employee profile fields.

    Args:
        employee_id: Employee ID.
        field:       Optional field name to filter history to a single field.
    """
    return await _pf().get_employee_field_histories(employee_id, field)


@mcp.tool()
async def get_employee_assets(employee_id: str) -> Any:
    """
    Return assets (equipment, hardware, etc.) assigned to an employee.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_assets(employee_id)


@mcp.tool()
async def get_employee_dependents(employee_id: str) -> Any:
    """
    Return dependents registered on an employee's profile.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_dependents(employee_id)


@mcp.tool()
async def get_employee_educations(employee_id: str) -> Any:
    """
    Return education history for an employee.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_educations(employee_id)


@mcp.tool()
async def get_employee_emergency_contacts(employee_id: str) -> Any:
    """
    Return emergency contacts for an employee.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_emergency_contacts(employee_id)


@mcp.tool()
async def get_employee_leave_types(employee_id: str) -> Any:
    """
    Return leave types available to a specific employee.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_leave_types(employee_id)


@mcp.tool()
async def get_employee_employment_statuses(employee_id: str) -> Any:
    """
    Return the employment status history for an employee (e.g. full-time → part-time).

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_employment_statuses(employee_id)


@mcp.tool()
async def get_employee_holidays(employee_id: str) -> Any:
    """
    Return public holidays applicable to an employee based on their holiday policy.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_holidays(employee_id)


@mcp.tool()
async def get_employee_leave_balances(employee_id: str) -> Any:
    """
    Return current leave balances (days remaining per leave type) for an employee.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_leave_balances(employee_id)


@mcp.tool()
async def get_employee_notes(employee_id: str) -> Any:
    """
    Return internal HR notes attached to an employee's profile.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_notes(employee_id)


@mcp.tool()
async def get_employee_positions(employee_id: str) -> Any:
    """
    Return the position history for an employee (title, department, manager over time).

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_positions(employee_id)


@mcp.tool()
async def get_employee_salaries(employee_id: str) -> Any:
    """
    Return the salary history for an employee.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_salaries(employee_id)


@mcp.tool()
async def get_employee_tasks(employee_id: str) -> Any:
    """
    Return tasks assigned to an employee.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_tasks(employee_id)


@mcp.tool()
async def get_employee_additional_compensations(employee_id: str) -> Any:
    """
    Return additional compensation entries (bonuses, allowances) for an employee.

    Args:
        employee_id: Employee ID.
    """
    return await _pf().get_employee_additional_compensations(employee_id)


@mcp.tool()
async def list_employee_skills() -> Any:
    """Return all skills defined across employees."""
    return await _pf().list_employee_skills()


@mcp.tool()
async def list_employee_tables() -> Any:
    """Return all custom table definitions available on employee profiles."""
    return await _pf().list_employee_tables()


@mcp.tool()
async def list_employee_table_columns() -> Any:
    """Return column definitions for employee custom tables."""
    return await _pf().list_employee_table_columns()


@mcp.tool()
async def list_employee_table_column_options() -> Any:
    """Return dropdown/select options for employee custom table columns."""
    return await _pf().list_employee_table_column_options()


# ==============================================================================
# Organisation
# ==============================================================================


@mcp.tool()
async def list_departments() -> dict[str, Any]:
    """Return all departments. Includes id, name, parent_id, and manager_id."""
    return await _pf().list_departments()


@mcp.tool()
async def list_divisions(page: int = 1, per_page: int = 50) -> Any:
    """
    Return all divisions.

    Args:
        page:     Page number.
        per_page: Results per page.
    """
    return await _pf().list_divisions(page, per_page)


@mcp.tool()
async def list_positions(page: int = 1, per_page: int = 50) -> Any:
    """
    Return all positions (job titles/roles) defined in the organisation.

    Args:
        page:     Page number.
        per_page: Results per page.
    """
    return await _pf().list_positions(page, per_page)


@mcp.tool()
async def list_job_groups(page: int = 1, per_page: int = 50) -> Any:
    """
    Return all job groups (career bands or families).

    Args:
        page:     Page number.
        per_page: Results per page.
    """
    return await _pf().list_job_groups(page, per_page)


@mcp.tool()
async def get_job_group(job_group_id: str) -> Any:
    """
    Fetch a single job group by ID.

    Args:
        job_group_id: Job group ID.
    """
    return await _pf().get_job_group(job_group_id)


@mcp.tool()
async def list_job_levels() -> Any:
    """Return all job levels (seniority levels) defined in the organisation."""
    return await _pf().list_job_levels()


@mcp.tool()
async def list_job_profiles(page: int = 1, per_page: int = 50) -> Any:
    """
    Return all job profiles (role templates with competencies and requirements).

    Args:
        page:     Page number.
        per_page: Results per page.
    """
    return await _pf().list_job_profiles(page, per_page)


@mcp.tool()
async def get_job_profile(job_profile_id: str) -> Any:
    """
    Fetch a single job profile by ID.

    Args:
        job_profile_id: Job profile ID.
    """
    return await _pf().get_job_profile(job_profile_id)


@mcp.tool()
async def list_competencies() -> Any:
    """Return all competencies defined in the organisation."""
    return await _pf().list_competencies()


@mcp.tool()
async def list_locations() -> Any:
    """Return all office/work locations."""
    return await _pf().list_locations()


@mcp.tool()
async def list_employment_types() -> Any:
    """Return all employment types (e.g. full-time, part-time, contractor)."""
    return await _pf().list_employment_types()


@mcp.tool()
async def list_external_users(page: int = 1, per_page: int = 50) -> Any:
    """
    Return external/non-employee users with system access.

    Args:
        page:     Page number.
        per_page: Results per page.
    """
    return await _pf().list_external_users(page, per_page)


@mcp.tool()
async def list_planned_positions(page: int = 1, per_page: int = 50) -> Any:
    """
    Return headcount planning positions (open or planned roles not yet filled).

    Args:
        page:     Page number.
        per_page: Results per page.
    """
    return await _pf().list_planned_positions(page, per_page)


# ==============================================================================
# Leave / Time-off
# ==============================================================================


@mcp.tool()
async def list_leave_requests(
    employee_id: str | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> dict[str, Any]:
    """
    Return time-off / leave requests.

    Args:
        employee_id: Filter to a specific employee.
        status:      Filter by status: "pending", "approved", "rejected".
        start_date:  ISO date YYYY-MM-DD — requests starting on or after this date.
        end_date:    ISO date YYYY-MM-DD — requests ending on or before this date.
        page:        Page number.
        per_page:    Results per page.
    """
    return await _pf().list_leave_requests(employee_id, status, start_date, end_date, page, per_page)


@mcp.tool()
async def get_leave_request(leave_request_id: str) -> Any:
    """
    Fetch a single leave request by ID.

    Args:
        leave_request_id: Leave request ID.
    """
    return await _pf().get_leave_request(leave_request_id)


@mcp.tool()
async def list_pending_leave_requests(page: int = 1, per_page: int = 50) -> Any:
    """
    Return all leave requests currently awaiting approval.

    Args:
        page:     Page number.
        per_page: Results per page.
    """
    return await _pf().list_pending_leave_requests(page, per_page)


@mcp.tool()
async def list_leave_types() -> Any:
    """Return all leave types defined (e.g. Annual Leave, Sick Leave, Parental Leave)."""
    return await _pf().list_leave_types()


@mcp.tool()
async def list_leave_policies() -> Any:
    """Return all leave policies, including accrual rules and entitlement amounts."""
    return await _pf().list_leave_policies()


# ==============================================================================
# Recruitment
# ==============================================================================


@mcp.tool()
async def list_recruitments(
    status: str | None = None,
    department: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> dict[str, Any]:
    """
    Return open vacancies and recruitment pipeline entries.

    Args:
        status:     Vacancy status, e.g. "open", "closed", "draft".
        department: Filter by department name or ID.
        page:       Page number.
        per_page:   Results per page.
    """
    return await _pf().list_recruitments(status, department, page, per_page)


@mcp.tool()
async def list_vacancy_fields() -> Any:
    """Return custom field definitions available on vacancy records."""
    return await _pf().list_vacancy_fields()


@mcp.tool()
async def get_recruitment_vacancy(vacancy_id: str | None = None) -> Any:
    """
    Fetch a recruitment vacancy record.

    Args:
        vacancy_id: Vacancy ID.
    """
    return await _pf().get_recruitment_vacancy(vacancy_id)


@mcp.tool()
async def get_vacancy_pipeline_stats(vacancy_id: str) -> Any:
    """
    Return candidate pipeline stage counts for a vacancy (e.g. Applied: 12, Interview: 4).

    Args:
        vacancy_id: Vacancy ID.
    """
    return await _pf().get_vacancy_pipeline_stats(vacancy_id)


@mcp.tool()
async def get_vacancy_application(vacancy_id: str, application_id: str) -> Any:
    """
    Fetch a single candidate application for a vacancy.

    Args:
        vacancy_id:     Vacancy ID.
        application_id: Application ID.
    """
    return await _pf().get_vacancy_application(vacancy_id, application_id)


@mcp.tool()
async def list_recruitment_pipelines() -> Any:
    """Return all recruitment pipeline stage definitions."""
    return await _pf().list_recruitment_pipelines()


@mcp.tool()
async def list_candidates(
    vacancy_id: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> Any:
    """
    Return candidates in the recruitment pipeline.

    Args:
        vacancy_id: Filter to candidates for a specific vacancy.
        status:     Filter by candidate status.
        page:       Page number.
        per_page:   Results per page.
    """
    return await _pf().list_candidates(vacancy_id, status, page, per_page)


@mcp.tool()
async def get_candidate(candidate_id: str) -> Any:
    """
    Fetch a single candidate's full record.

    Args:
        candidate_id: Candidate ID.
    """
    return await _pf().get_candidate(candidate_id)


@mcp.tool()
async def get_candidate_notes(candidate_id: str) -> Any:
    """
    Return recruiter/interviewer notes on a candidate.

    Args:
        candidate_id: Candidate ID.
    """
    return await _pf().get_candidate_notes(candidate_id)


@mcp.tool()
async def get_candidate_educations(candidate_id: str) -> Any:
    """
    Return education history from a candidate's profile.

    Args:
        candidate_id: Candidate ID.
    """
    return await _pf().get_candidate_educations(candidate_id)


@mcp.tool()
async def get_candidate_experiences(candidate_id: str) -> Any:
    """
    Return work experience history from a candidate's profile.

    Args:
        candidate_id: Candidate ID.
    """
    return await _pf().get_candidate_experiences(candidate_id)


@mcp.tool()
async def list_candidate_movements(page: int = 1, per_page: int = 50) -> Any:
    """
    Return candidate stage movement events (pipeline transitions).

    Args:
        page:     Page number.
        per_page: Results per page.
    """
    return await _pf().list_candidate_movements(page, per_page)


@mcp.tool()
async def list_candidate_fields() -> Any:
    """Return custom field definitions available on candidate records."""
    return await _pf().list_candidate_fields()


@mcp.tool()
async def list_recruitment_sources() -> Any:
    """Return all recruitment sources (e.g. LinkedIn, Referral, Job Board)."""
    return await _pf().list_recruitment_sources()


@mcp.tool()
async def list_career_vacancies(page: int = 1, per_page: int = 50) -> Any:
    """
    Return publicly listed vacancies from the careers portal (public-facing job board).

    Args:
        page:     Page number.
        per_page: Results per page.
    """
    return await _pf().list_career_vacancies(page, per_page)


@mcp.tool()
async def get_career_vacancy(vacancy_id: str) -> Any:
    """
    Fetch a single public-facing vacancy from the careers portal.

    Args:
        vacancy_id: Vacancy ID.
    """
    return await _pf().get_career_vacancy(vacancy_id)


@mcp.tool()
async def list_career_employment_types() -> Any:
    """Return employment types used in the public careers portal."""
    return await _pf().list_career_employment_types()


@mcp.tool()
async def list_career_locations() -> Any:
    """Return locations used in the public careers portal."""
    return await _pf().list_career_locations()


# ==============================================================================
# Time Tracking
# ==============================================================================


@mcp.tool()
async def list_timesheets(
    employee_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> Any:
    """
    Return timesheet summaries.

    Args:
        employee_id: Filter to a specific employee.
        start_date:  ISO date YYYY-MM-DD.
        end_date:    ISO date YYYY-MM-DD.
        page:        Page number.
        per_page:    Results per page.
    """
    return await _pf().list_timesheets(employee_id, start_date, end_date, page, per_page)


@mcp.tool()
async def list_timesheet_entries(
    employee_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> Any:
    """
    Return individual timesheet entries (clock-in/out or logged hours).

    Args:
        employee_id: Filter to a specific employee.
        start_date:  ISO date YYYY-MM-DD.
        end_date:    ISO date YYYY-MM-DD.
        page:        Page number.
        per_page:    Results per page.
    """
    return await _pf().list_timesheet_entries(employee_id, start_date, end_date, page, per_page)


@mcp.tool()
async def list_time_projects() -> Any:
    """Return all time-tracking projects employees can log hours against."""
    return await _pf().list_time_projects()


@mcp.tool()
async def list_overtime_requests(
    employee_id: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> Any:
    """
    Return overtime requests.

    Args:
        employee_id: Filter to a specific employee.
        status:      Filter by status: "pending", "approved", "rejected".
        page:        Page number.
        per_page:    Results per page.
    """
    return await _pf().list_overtime_requests(employee_id, status, page, per_page)


@mcp.tool()
async def get_overtime_request(overtime_request_id: str) -> Any:
    """
    Fetch a single overtime request by ID.

    Args:
        overtime_request_id: Overtime request ID.
    """
    return await _pf().get_overtime_request(overtime_request_id)


# ==============================================================================
# Assets
# ==============================================================================


@mcp.tool()
async def list_assets(page: int = 1, per_page: int = 50) -> Any:
    """
    Return all company assets (hardware, equipment, etc.).

    Args:
        page:     Page number.
        per_page: Results per page.
    """
    return await _pf().list_assets(page, per_page)


@mcp.tool()
async def get_asset(asset_id: str) -> Any:
    """
    Fetch a single asset record by ID.

    Args:
        asset_id: Asset ID.
    """
    return await _pf().get_asset(asset_id)


@mcp.tool()
async def list_asset_categories() -> Any:
    """Return all asset categories (e.g. Laptop, Phone, Access Card)."""
    return await _pf().list_asset_categories()


# ==============================================================================
# Misc
# ==============================================================================


@mcp.tool()
async def list_audits(page: int = 1, per_page: int = 50) -> Any:
    """
    Return the audit log of actions performed in PeopleForce.

    Args:
        page:     Page number.
        per_page: Results per page.
    """
    return await _pf().list_audits(page, per_page)


@mcp.tool()
async def list_calendars() -> Any:
    """Return all calendars configured in PeopleForce (team, company, holiday calendars)."""
    return await _pf().list_calendars()


@mcp.tool()
async def list_tasks(
    employee_id: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> Any:
    """
    Return tasks created in PeopleForce (onboarding tasks, reminders, etc.).

    Args:
        employee_id: Filter to tasks assigned to a specific employee.
        status:      Filter by status, e.g. "open", "completed".
        page:        Page number.
        per_page:    Results per page.
    """
    return await _pf().list_tasks(employee_id, status, page, per_page)


@mcp.tool()
async def list_teams() -> Any:
    """Return all teams defined in PeopleForce."""
    return await _pf().list_teams()


@mcp.tool()
async def list_holidays(year: int | None = None) -> Any:
    """
    Return public holidays.

    Args:
        year: Filter to a specific year (e.g. 2025). Defaults to current year.
    """
    return await _pf().list_holidays(year)


@mcp.tool()
async def list_holiday_policies() -> Any:
    """Return all holiday policies (which public holidays apply to which employees)."""
    return await _pf().list_holiday_policies()


@mcp.tool()
async def list_knowledge_articles(
    category_id: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> Any:
    """
    Return articles from the PeopleForce knowledge base.

    Args:
        category_id: Filter to a specific category.
        page:        Page number.
        per_page:    Results per page.
    """
    return await _pf().list_knowledge_articles(category_id, page, per_page)


@mcp.tool()
async def get_knowledge_article(article_id: str) -> Any:
    """
    Fetch a single knowledge base article by ID.

    Args:
        article_id: Article ID.
    """
    return await _pf().get_knowledge_article(article_id)


@mcp.tool()
async def list_knowledge_categories() -> Any:
    """Return all knowledge base categories."""
    return await _pf().list_knowledge_categories()


@mcp.tool()
async def list_skills() -> Any:
    """Return all skill definitions in the skills catalogue."""
    return await _pf().list_skills()


@mcp.tool()
async def list_pay_schedules() -> Any:
    """Return all pay schedules (payroll frequency and dates)."""
    return await _pf().list_pay_schedules()


@mcp.tool()
async def list_objectives(
    employee_id: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> Any:
    """
    Return OKR / performance objectives.

    Args:
        employee_id: Filter to a specific employee.
        page:        Page number.
        per_page:    Results per page.
    """
    return await _pf().list_objectives(employee_id, page, per_page)


@mcp.tool()
async def list_kpis(
    employee_id: str | None = None,
    page: int = 1,
    per_page: int = 50,
) -> Any:
    """
    Return KPIs (key performance indicators).

    Args:
        employee_id: Filter to a specific employee.
        page:        Page number.
        per_page:    Results per page.
    """
    return await _pf().list_kpis(employee_id, page, per_page)


@mcp.tool()
async def list_working_patterns() -> Any:
    """Return all working pattern templates (e.g. Mon–Fri 9–5, shift patterns)."""
    return await _pf().list_working_patterns()


@mcp.tool()
async def list_compensation_types() -> Any:
    """Return all compensation type definitions (e.g. base salary, bonus, commission)."""
    return await _pf().list_compensation_types()


@mcp.tool()
async def list_termination_reasons() -> Any:
    """Return all termination reason options used when offboarding employees."""
    return await _pf().list_termination_reasons()


@mcp.tool()
async def list_termination_types() -> Any:
    """Return all termination type options (e.g. voluntary, involuntary, retirement)."""
    return await _pf().list_termination_types()


@mcp.tool()
async def list_probation_policies() -> Any:
    """Return all probation period policies."""
    return await _pf().list_probation_policies()


@mcp.tool()
async def list_document_folders() -> Any:
    """Return all document folder definitions in PeopleForce."""
    return await _pf().list_document_folders()


@mcp.tool()
async def get_document_folder(folder_id: str) -> Any:
    """
    Fetch a single document folder by ID.

    Args:
        folder_id: Document folder ID.
    """
    return await _pf().get_document_folder(folder_id)


# ==============================================================================
# ASGI app assembly
# ==============================================================================
# Stack: _OAuthMiddleware → BearerAuthMiddleware → _HealthMiddleware → mcp_asgi
# _OAuthMiddleware intercepts POST /oauth/token before auth is checked.
# _HealthMiddleware short-circuits /health before MCP routing.


class _HealthMiddleware:
    _BODY = b'{"status":"ok"}'
    _HEADERS = [
        (b"content-type", b"application/json"),
        (b"content-length", str(len(_BODY)).encode()),
    ]

    def __init__(self, asgi_app: Any) -> None:
        self._app = asgi_app

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope.get("type") == "http" and scope.get("path") == "/health":
            await send({"type": "http.response.start", "status": 200, "headers": self._HEADERS})
            await send({"type": "http.response.body", "body": self._BODY})
            return
        await self._app(scope, receive, send)


class _OAuthMiddleware:
    _DISCOVERY_PATHS = {
        "/.well-known/oauth-authorization-server",
        "/.well-known/oauth-protected-resource",
        "/.well-known/oauth-protected-resource/mcp",
    }

    def __init__(self, asgi_app: Any) -> None:
        self._app = asgi_app

    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        if scope.get("type") == "http":
            path = scope.get("path", "")
            method = scope.get("method", "")

            if path in self._DISCOVERY_PATHS and method == "GET":
                from oauth import handle_authorization_server_metadata, handle_protected_resource_metadata
                if "authorization-server" in path:
                    await handle_authorization_server_metadata(scope, send)
                else:
                    await handle_protected_resource_metadata(scope, send)
                return

            if path == "/authorize" and method == "GET":
                from oauth import handle_authorize_request
                await handle_authorize_request(scope, send)
                return

            if path == "/token" and method == "POST":
                body = b""
                while True:
                    msg = await receive()
                    body += msg.get("body", b"")
                    if not msg.get("more_body", False):
                        break
                from oauth import handle_token_request
                await handle_token_request(body, send)
                return

        await self._app(scope, receive, send)


_mcp_asgi = mcp.streamable_http_app()
app = _OAuthMiddleware(BearerAuthMiddleware(_HealthMiddleware(_mcp_asgi)))
