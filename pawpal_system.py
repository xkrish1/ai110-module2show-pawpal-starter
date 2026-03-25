from dataclasses import dataclass, field
from datetime import date


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str
    category: str              # walk, feeding, meds, grooming, enrichment
    duration_minutes: int
    priority: int              # 1 (low) – 5 (high)
    frequency: str             # daily, weekly, as-needed
    notes: str = ""
    pet_name: str = ""         # which pet this task belongs to
    last_completed: date | None = None  # needed for is_due() logic on weekly/as-needed tasks

    def is_due(self, today: date) -> bool:
        """Return True if this task should occur on the given date.

        Rules:
        - daily: always due
        - weekly: due if last_completed is None or >= 7 days ago
        - as-needed: never auto-scheduled; must be added manually
        """
        pass

    def to_dict(self) -> dict:
        """Return a dictionary representation of this task."""
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_conditions: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        pass

    def get_tasks_by_priority(self) -> list[Task]:
        """Return this pet's tasks sorted by priority (highest first)."""
        pass

    def get_due_tasks(self, today: date) -> list[Task]:
        """Return tasks that are due on the given date."""
        pass


# ---------------------------------------------------------------------------
# Regular classes
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, available_time_minutes: int, preferences: dict = None):
        self.name = name
        self.available_time_minutes = available_time_minutes
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list."""
        pass


class DailyPlan:
    def __init__(self, today: date):
        self.date = today
        self.scheduled_tasks: list[tuple[Pet, Task]] = []   # (pet, task) pairs so display can group by pet
        self.skipped_tasks: list[tuple[Task, str]] = []     # (task, reason) pairs so reasons are preserved
        self.explanation: str = ""

    def add_task(self, _pet: Pet, _task: Task) -> None:
        """Add a (pet, task) pair to the scheduled list."""
        pass

    def skip_task(self, task: Task, reason: str) -> None:
        """Add a (task, reason) pair to the skipped list."""
        pass

    def total_time_required(self) -> int:
        """Return the sum of durations for all scheduled tasks."""
        pass

    def display(self) -> str:
        """Return a formatted string summary of the plan, grouped by pet."""
        pass


class Planner:
    def __init__(self, owner: Owner, strategy: str = "priority-first"):
        self.owner = owner
        self.strategy = strategy

    def generate_plan(self, today: date) -> DailyPlan:
        """Build and return a DailyPlan by iterating owner.pets → pet.tasks."""
        pass

    def rank_tasks(self, tasks: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Sort (pet, task) pairs by: priority descending, then duration ascending.

        Tiebreaker rule: when two tasks share the same priority, prefer the
        shorter one so more tasks fit within the time budget.
        """
        pass

    def fits_in_time(self, task: Task, remaining_minutes: int) -> bool:
        """Return True if the task fits within the remaining time budget."""
        pass

    def explain_choices(self, plan: DailyPlan) -> str:
        """Generate a natural-language explanation of why tasks were chosen or skipped."""
        pass
