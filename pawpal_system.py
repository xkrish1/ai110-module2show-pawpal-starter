from dataclasses import dataclass, field
from datetime import date


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str
    category: str          # walk, feeding, meds, grooming, enrichment
    duration_minutes: int
    priority: int          # 1 (low) – 5 (high)
    frequency: str         # daily, weekly, as-needed
    notes: str = ""

    def is_due(self, today: date) -> bool:
        """Return True if this task should occur on the given date."""
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

    def get_total_available_time(self) -> int:
        """Return the owner's total available time in minutes today."""
        pass


class DailyPlan:
    def __init__(self, date: date):
        self.date = date
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []
        self.explanation: str = ""

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduled list."""
        pass

    def skip_task(self, task: Task, reason: str) -> None:
        """Add a task to the skipped list and record why."""
        pass

    def total_time_required(self) -> int:
        """Return the sum of durations for all scheduled tasks."""
        pass

    def display(self) -> str:
        """Return a formatted string summary of the plan for display."""
        pass


class Planner:
    def __init__(self, owner: Owner, strategy: str = "priority-first"):
        self.owner = owner
        self.strategy = strategy

    def generate_plan(self, today: date) -> DailyPlan:
        """Build and return a DailyPlan for the given date."""
        pass

    def rank_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority, urgency, and duration."""
        pass

    def fits_in_time(self, task: Task, remaining_minutes: int) -> bool:
        """Return True if the task fits within the remaining time budget."""
        pass

    def explain_choices(self, plan: DailyPlan) -> str:
        """Generate a natural-language explanation of why tasks were chosen or skipped."""
        pass
