from typing import Any

import httpx

BASE_URL = "https://app.peopleforce.io/api/public/v3"
CAREERS_BASE = "https://app.peopleforce.io/api/careers/v1"


class PeopleForceClient:
    """Thin async wrapper around the PeopleForce REST API."""

    def __init__(self, api_key: str) -> None:
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            headers={"X-Api-Key": api_key, "Accept": "application/json"},
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        filtered = {k: v for k, v in (params or {}).items() if v is not None}
        try:
            response = await self._client.get(path, params=filtered)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500]
            raise RuntimeError(
                f"PeopleForce API error {exc.response.status_code}: {body}"
            ) from exc
        except httpx.RequestError as exc:
            raise RuntimeError(f"PeopleForce API request failed: {exc}") from exc
        return response.json()

    # ------------------------------------------------------------------
    # Employees
    # ------------------------------------------------------------------

    async def list_employees(
        self,
        status: str | None = None,
        department: str | None = None,
        location: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> dict[str, Any]:
        return await self._get("/employees", {"status": status, "department": department,
                                              "location": location, "page": page, "per_page": per_page})

    async def get_employee(self, employee_id: str) -> dict[str, Any]:
        return await self._get(f"/employees/{employee_id}")

    async def get_employee_by_email(self, email: str) -> dict[str, Any]:
        result = await self._get("/employees", {"email": email, "per_page": 1})
        employees = result.get("data", result) if isinstance(result, dict) else result
        if not employees:
            raise RuntimeError(f"No employee found with email: {email}")
        return employees[0]

    async def list_terminated_employees(self, page: int = 1, per_page: int = 50) -> dict[str, Any]:
        return await self._get("/employees/terminated", {"page": page, "per_page": per_page})

    async def list_employee_birthdays(self, month: int | None = None) -> Any:
        return await self._get("/employees/birthdays", {"month": month})

    async def list_employee_anniversaries(self, month: int | None = None) -> Any:
        return await self._get("/employees/anniversaries", {"month": month})

    async def list_employee_fields(self) -> Any:
        return await self._get("/employee_fields")

    async def get_employee_table(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/table")

    async def get_employee_certifications(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/certifications")

    async def get_employee_documents(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/documents")

    async def get_employee_document(self, employee_id: str, document_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/documents/{document_id}")

    async def get_employee_field_histories(self, employee_id: str, field: str | None = None) -> Any:
        return await self._get(f"/employees/{employee_id}/field-histories", {"field": field})

    async def get_employee_assets(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/assets")

    async def get_employee_dependents(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/dependents")

    async def get_employee_educations(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/educations")

    async def get_employee_emergency_contacts(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/emergency_contacts")

    async def get_employee_leave_types(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/employee_leave_types")

    async def get_employee_employment_statuses(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/employment_statuses")

    async def get_employee_holidays(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/holidays")

    async def get_employee_leave_balances(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/leave_balances")

    async def get_employee_notes(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/notes")

    async def get_employee_positions(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/positions")

    async def get_employee_salaries(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/salaries")

    async def get_employee_tasks(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/tasks")

    async def get_employee_additional_compensations(self, employee_id: str) -> Any:
        return await self._get(f"/employees/{employee_id}/additional_compensations")

    async def list_employee_skills(self) -> Any:
        return await self._get("/employees/skills")

    async def list_employee_tables(self) -> Any:
        return await self._get("/employee-tables")

    async def list_employee_table_columns(self) -> Any:
        return await self._get("/employee-table-columns")

    async def list_employee_table_column_options(self) -> Any:
        return await self._get("/employee-table-column-options")

    # ------------------------------------------------------------------
    # Organisation
    # ------------------------------------------------------------------

    async def list_departments(self) -> dict[str, Any]:
        return await self._get("/departments")

    async def list_divisions(self, page: int = 1, per_page: int = 50) -> Any:
        return await self._get("/divisions", {"page": page, "per_page": per_page})

    async def list_positions(self, page: int = 1, per_page: int = 50) -> Any:
        return await self._get("/positions", {"page": page, "per_page": per_page})

    async def list_job_groups(self, page: int = 1, per_page: int = 50) -> Any:
        return await self._get("/job_groups", {"page": page, "per_page": per_page})

    async def get_job_group(self, job_group_id: str) -> Any:
        return await self._get(f"/job_groups/{job_group_id}")

    async def list_job_levels(self) -> Any:
        return await self._get("/job_levels")

    async def list_job_profiles(self, page: int = 1, per_page: int = 50) -> Any:
        return await self._get("/job_profiles", {"page": page, "per_page": per_page})

    async def get_job_profile(self, job_profile_id: str) -> Any:
        return await self._get(f"/job_profiles/{job_profile_id}")

    async def list_competencies(self) -> Any:
        return await self._get("/competencies")

    async def list_locations(self) -> Any:
        return await self._get("/locations")

    async def list_employment_types(self) -> Any:
        return await self._get("/employment_types")

    async def list_external_users(self, page: int = 1, per_page: int = 50) -> Any:
        return await self._get("/external_users", {"page": page, "per_page": per_page})

    async def list_planned_positions(self, page: int = 1, per_page: int = 50) -> Any:
        return await self._get("/planning/positions", {"page": page, "per_page": per_page})

    # ------------------------------------------------------------------
    # Leave / Time-off
    # ------------------------------------------------------------------

    async def list_leave_requests(
        self,
        employee_id: str | None = None,
        status: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> dict[str, Any]:
        return await self._get("/leave_requests", {"employee_id": employee_id, "status": status,
                                                   "start_date": start_date, "end_date": end_date,
                                                   "page": page, "per_page": per_page})

    async def get_leave_request(self, leave_request_id: str) -> Any:
        return await self._get(f"/leave_requests/{leave_request_id}")

    async def list_pending_leave_requests(self, page: int = 1, per_page: int = 50) -> Any:
        return await self._get("/pending-leave_requests", {"page": page, "per_page": per_page})

    async def list_leave_types(self) -> Any:
        return await self._get("/leave_types")

    async def list_leave_policies(self) -> Any:
        return await self._get("/leave_policies")

    # ------------------------------------------------------------------
    # Recruitment
    # ------------------------------------------------------------------

    async def list_recruitments(
        self,
        status: str | None = None,
        department: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> dict[str, Any]:
        return await self._get("/vacancies", {"status": status, "department": department,
                                              "page": page, "per_page": per_page})

    async def list_vacancy_fields(self) -> Any:
        return await self._get("/vacancy-fields")

    async def get_recruitment_vacancy(self, vacancy_id: str | None = None) -> Any:
        return await self._get("/recruitment/vacancy", {"id": vacancy_id})

    async def get_vacancy_pipeline_stats(self, vacancy_id: str) -> Any:
        return await self._get(f"/recruitment/vacancies/{vacancy_id}/pipeline-stats")

    async def get_vacancy_application(self, vacancy_id: str, application_id: str) -> Any:
        return await self._get(f"/recruitment/vacancies/{vacancy_id}/applications/{application_id}")

    async def list_recruitment_pipelines(self) -> Any:
        return await self._get("/recruitment/pipelines")

    async def list_candidates(
        self,
        vacancy_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> Any:
        return await self._get("/recruitment/candidates", {"vacancy_id": vacancy_id,
                                                           "status": status, "page": page,
                                                           "per_page": per_page})

    async def get_candidate(self, candidate_id: str) -> Any:
        return await self._get(f"/recruitment/candidates/{candidate_id}")

    async def get_candidate_notes(self, candidate_id: str) -> Any:
        return await self._get(f"/recruitment/candidates/{candidate_id}/notes")

    async def get_candidate_educations(self, candidate_id: str) -> Any:
        return await self._get(f"/recruitment/candidates/{candidate_id}/educations")

    async def get_candidate_experiences(self, candidate_id: str) -> Any:
        return await self._get(f"/recruitment/candidates/{candidate_id}/experiences")

    async def list_candidate_movements(self, page: int = 1, per_page: int = 50) -> Any:
        return await self._get("/recruitment/candidate-movements", {"page": page, "per_page": per_page})

    async def list_candidate_fields(self) -> Any:
        return await self._get("/recruitment/candidate-fields")

    async def list_recruitment_sources(self) -> Any:
        return await self._get("/sources")

    async def list_career_vacancies(self, page: int = 1, per_page: int = 50) -> Any:
        return await self._get(f"{CAREERS_BASE}/vacancies", {"page": page, "per_page": per_page})

    async def get_career_vacancy(self, vacancy_id: str) -> Any:
        return await self._get(f"{CAREERS_BASE}/vacancies/{vacancy_id}")

    async def list_career_employment_types(self) -> Any:
        return await self._get(f"{CAREERS_BASE}/employment-types")

    async def list_career_locations(self) -> Any:
        return await self._get(f"{CAREERS_BASE}/locations")

    # ------------------------------------------------------------------
    # Time Tracking
    # ------------------------------------------------------------------

    async def list_timesheets(
        self,
        employee_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> Any:
        return await self._get("/time/timesheets", {"employee_id": employee_id,
                                                    "start_date": start_date, "end_date": end_date,
                                                    "page": page, "per_page": per_page})

    async def list_timesheet_entries(
        self,
        employee_id: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> Any:
        return await self._get("/time/timesheet_entries", {"employee_id": employee_id,
                                                           "start_date": start_date, "end_date": end_date,
                                                           "page": page, "per_page": per_page})

    async def list_time_projects(self) -> Any:
        return await self._get("/time/projects")

    async def list_overtime_requests(
        self,
        employee_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> Any:
        return await self._get("/time/overtime_requests", {"employee_id": employee_id,
                                                           "status": status, "page": page,
                                                           "per_page": per_page})

    async def get_overtime_request(self, overtime_request_id: str) -> Any:
        return await self._get(f"/time/overtime_requests/{overtime_request_id}")

    # ------------------------------------------------------------------
    # Assets
    # ------------------------------------------------------------------

    async def list_assets(self, page: int = 1, per_page: int = 50) -> Any:
        return await self._get("/assets", {"page": page, "per_page": per_page})

    async def get_asset(self, asset_id: str) -> Any:
        return await self._get(f"/assets/{asset_id}")

    async def list_asset_categories(self) -> Any:
        return await self._get("/asset_categories")

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------

    async def list_audits(self, page: int = 1, per_page: int = 50) -> Any:
        return await self._get("/audits", {"page": page, "per_page": per_page})

    async def list_calendars(self) -> Any:
        return await self._get("/calendars")

    async def list_tasks(
        self,
        employee_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> Any:
        return await self._get("/tasks", {"employee_id": employee_id, "status": status,
                                          "page": page, "per_page": per_page})

    async def list_teams(self) -> Any:
        return await self._get("/teams")

    async def list_holidays(self, year: int | None = None) -> Any:
        return await self._get("/holidays", {"year": year})

    async def list_holiday_policies(self) -> Any:
        return await self._get("/holiday_policies")

    async def list_knowledge_articles(self, category_id: str | None = None, page: int = 1, per_page: int = 50) -> Any:
        return await self._get("/knowledge_base/articles", {"category_id": category_id,
                                                            "page": page, "per_page": per_page})

    async def get_knowledge_article(self, article_id: str) -> Any:
        return await self._get(f"/knowledge_base/articles/{article_id}")

    async def list_knowledge_categories(self) -> Any:
        return await self._get("/knowledge_base/categories")

    async def list_skills(self) -> Any:
        return await self._get("/skills")

    async def list_pay_schedules(self) -> Any:
        return await self._get("/pay_schedules")

    async def list_objectives(self, employee_id: str | None = None, page: int = 1, per_page: int = 50) -> Any:
        return await self._get("/objectives", {"employee_id": employee_id, "page": page, "per_page": per_page})

    async def list_kpis(self, employee_id: str | None = None, page: int = 1, per_page: int = 50) -> Any:
        return await self._get("/key_performance_indicators", {"employee_id": employee_id,
                                                               "page": page, "per_page": per_page})

    async def list_working_patterns(self) -> Any:
        return await self._get("/working_patterns")

    async def list_compensation_types(self) -> Any:
        return await self._get("/compensation_types")

    async def list_termination_reasons(self) -> Any:
        return await self._get("/termination_reasons")

    async def list_termination_types(self) -> Any:
        return await self._get("/termination_types")

    async def list_probation_policies(self) -> Any:
        return await self._get("/probation_policies")

    async def list_document_folders(self) -> Any:
        return await self._get("/document_folders")

    async def get_document_folder(self, folder_id: str) -> Any:
        return await self._get(f"/document_folders/{folder_id}")
