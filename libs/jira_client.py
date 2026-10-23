"""Local-only mock ticket adapter used by the tutorial extension.

Despite the filename, this module intentionally has no Jira Cloud client, credentials,
HTTP imports, or network behavior.  Every record is in memory and marked simulation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol


SIMULATION_MARKER = "[SIMULATION/MOCK]"
FakeCreateMode = Literal["none", "create_error", "ambiguous_timeout"]


class FakeTicketCreateError(RuntimeError):
    """Raised when the deliberately injected local create failure is selected."""


class AmbiguousFakeCreateTimeout(TimeoutError):
    """A local test seam: record was created but acknowledgement was lost."""


@dataclass(frozen=True)
class FakeTicketRequest:
    """Required payload for the local fake adapter; it never leaves this process."""

    correlation_id: str
    incident_id: str
    service: str
    summary: str
    impact: str
    evidence: str
    incident_category: str
    priority: Literal["P1", "P2", "P3"]
    runbook_id: str
    planned_steps: tuple[str, ...]
    project_key: str = "SIM"
    issue_type: str = "Incident"
    assignee_fixture: str | None = None
    simulation_marker: str = SIMULATION_MARKER


@dataclass(frozen=True)
class FakeComment:
    body: str
    simulation_marker: str = SIMULATION_MARKER


@dataclass
class FakeTicket:
    key: str
    url: str
    request: FakeTicketRequest
    comments: list[FakeComment] = field(default_factory=list)
    local_lifecycle: str = "SIMULATED_CREATED_LOCAL_ONLY"
    simulation_marker: str = SIMULATION_MARKER


class TicketAdapter(Protocol):
    """Narrow adapter boundary. A future live adapter is deliberately out of scope."""

    def create_ticket(self, request: FakeTicketRequest) -> FakeTicket: ...

    def find_by_correlation(self, correlation_id: str) -> FakeTicket | None: ...

    def add_progress_comment(self, key: str, body: str) -> FakeComment: ...

    def set_local_lifecycle(self, key: str, lifecycle: str) -> FakeTicket: ...


class FakeJiraAdapter:
    """Deterministic in-memory mock adapter. It cannot contact Jira or any network."""

    def __init__(
        self,
        *,
        project_key: str = "SIM",
        issue_type: str = "Incident",
        assignee_fixture: str | None = "mock-engineer-fixture",
        create_mode: FakeCreateMode = "none",
    ) -> None:
        self.project_key = project_key
        self.issue_type = issue_type
        self.assignee_fixture = assignee_fixture
        self.create_mode = create_mode
        self._tickets: list[FakeTicket] = []
        self._timeout_raised = False

    @property
    def tickets(self) -> tuple[FakeTicket, ...]:
        return tuple(self._tickets)

    def create_ticket(self, request: FakeTicketRequest) -> FakeTicket:
        if self.create_mode == "create_error":
            raise FakeTicketCreateError("Injected local fake-ticket create failure")
        existing = self.find_by_correlation(request.correlation_id)
        if existing is not None:
            return existing
        key = f"{self.project_key}-{len(self._tickets) + 1}"
        normalized = FakeTicketRequest(
            **{
                **request.__dict__,
                "project_key": self.project_key,
                "issue_type": self.issue_type,
                "assignee_fixture": self.assignee_fixture,
            }
        )
        ticket = FakeTicket(
            key=key,
            url=f"https://jira.example.invalid/browse/{key}",
            request=normalized,
        )
        self._tickets.append(ticket)
        if self.create_mode == "ambiguous_timeout" and not self._timeout_raised:
            self._timeout_raised = True
            raise AmbiguousFakeCreateTimeout(
                "Injected local ambiguous create timeout; reconcile by correlation"
            )
        return ticket

    def find_by_correlation(self, correlation_id: str) -> FakeTicket | None:
        return next(
            (ticket for ticket in self._tickets if ticket.request.correlation_id == correlation_id),
            None,
        )

    def _ticket(self, key: str) -> FakeTicket:
        for ticket in self._tickets:
            if ticket.key == key:
                return ticket
        raise KeyError(f"No local mock ticket {key}")

    def add_progress_comment(self, key: str, body: str) -> FakeComment:
        ticket = self._ticket(key)
        comment = FakeComment(body=f"{SIMULATION_MARKER} {body}")
        ticket.comments.append(comment)
        return comment

    def set_local_lifecycle(self, key: str, lifecycle: str) -> FakeTicket:
        if not lifecycle.startswith("SIMULATED_"):
            raise ValueError("Mock lifecycle states must be explicitly simulated")
        ticket = self._ticket(key)
        ticket.local_lifecycle = lifecycle
        return ticket
