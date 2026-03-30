from dataclasses import dataclass, field
from datetime import date, timedelta
from copy import deepcopy


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
    time: str = "00:00"       # scheduled time as HH:MM
    due_date: date | None = None
    notes: str = ""
    pet_name: str = ""
    last_completed: date | None = None

    def is_due(self, today: date) -> bool:
        """Return True if this task should occur today (daily=always, weekly=every 7 days, as-needed=never)."""
        # If a specific due_date is set, honor it first
        if self.due_date is not None:
            return self.due_date <= today
        if self.frequency == "daily":
            return True
        if self.frequency == "weekly":
            if self.last_completed is None:
                return True
            return (today - self.last_completed).days >= 7
        return False  # as-needed

    def mark_complete(self, today: date) -> None:
        """Mark this task as completed on the given date."""
        self.last_completed = today
        # Clear any explicit due date once completed
        if self.due_date is not None and self.due_date <= today:
            self.due_date = None

    def to_dict(self) -> dict:
        """Return a dictionary representation of this task."""
        return {
            "name": self.name,
            "category": self.category,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "time": self.time,
            "due_date": str(self.due_date) if self.due_date else None,
            "notes": self.notes,
            "pet_name": self.pet_name,
            "last_completed": str(self.last_completed) if self.last_completed else None,
        }


@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_conditions: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet and stamp it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks_by_priority(self) -> list[Task]:
        """Return tasks sorted by priority descending (5 = highest)."""
        return sorted(self.tasks, key=lambda t: t.priority, reverse=True)

    def get_due_tasks(self, today: date) -> list[Task]:
        """Return all tasks that are due on the given date."""
        return [t for t in self.tasks if t.is_due(today)]


# ---------------------------------------------------------------------------
# Regular classes
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, available_time_minutes: int, preferences: dict = None):
        """Create an owner with a daily time budget and optional scheduling preferences."""
        self.name = name
        self.available_time_minutes = available_time_minutes
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list."""
        self.pets.append(pet)


class DailyPlan:
    def __init__(self, today: date):
        """Create an empty plan for the given date."""
        self.date = today
        self.scheduled_tasks: list[tuple[Pet, Task]] = []
        self.skipped_tasks: list[tuple[Task, str]] = []
        self.explanation: str = ""

    def add_task(self, pet: Pet, task: Task) -> None:
        """Add a (pet, task) pair to the scheduled list."""
        self.scheduled_tasks.append((pet, task))

    def skip_task(self, task: Task, reason: str) -> None:
        """Record a task as skipped with the reason why."""
        self.skipped_tasks.append((task, reason))

    def total_time_required(self) -> int:
        """Return the total duration of all scheduled tasks in minutes."""
        return sum(task.duration_minutes for _, task in self.scheduled_tasks)

    def display(self) -> str:
        """Return a formatted plan string grouped by pet."""
        lines = [f"Daily Plan for {self.date}\n{'=' * 30}"]

        # Group scheduled tasks by pet name
        by_pet: dict[str, list[Task]] = {}
        for pet, task in self.scheduled_tasks:
            by_pet.setdefault(pet.name, []).append(task)

        for pet_name, tasks in by_pet.items():
            lines.append(f"\n{pet_name}:")
            for task in tasks:
                lines.append(f"  [{task.priority}★] {task.name} ({task.duration_minutes} min)")

        lines.append(f"\nTotal time: {self.total_time_required()} min")

        if self.skipped_tasks:
            lines.append("\nSkipped:")
            for task, reason in self.skipped_tasks:
                lines.append(f"  - {task.name}: {reason}")

        if self.explanation:
            lines.append(f"\nNotes: {self.explanation}")

        return "\n".join(lines)


class Planner:
    def __init__(self, owner: Owner, strategy: str = "priority-first"):
        """Create a planner for the given owner using the specified scheduling strategy."""
        self.owner = owner
        self.strategy = strategy

    def generate_plan(self, today: date) -> DailyPlan:
        """Collect due tasks across all pets, rank them, and schedule until the time budget is full."""
        plan = DailyPlan(today)
        remaining = self.owner.available_time_minutes

        # Collect all due (pet, task) pairs across every pet
        all_due = [
            (pet, task)
            for pet in self.owner.pets
            for task in pet.get_due_tasks(today)
        ]

        for pet, task in self.rank_tasks(all_due):
            if self.fits_in_time(task, remaining):
                plan.add_task(pet, task)
                remaining -= task.duration_minutes
            else:
                plan.skip_task(task, f"not enough time remaining ({remaining} min left, needs {task.duration_minutes} min)")

        plan.explanation = self.explain_choices(plan)
        return plan

    def rank_tasks(self, tasks: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Sort tasks by priority descending, then duration ascending so more tasks fit in the budget."""
        return sorted(tasks, key=lambda pt: (-pt[1].priority, pt[1].duration_minutes))

    def fits_in_time(self, task: Task, remaining_minutes: int) -> bool:
        """Return True if the task fits within the remaining time budget."""
        return task.duration_minutes <= remaining_minutes

    def explain_choices(self, plan: DailyPlan) -> str:
        """Generate a natural-language summary of scheduling decisions."""
        n_scheduled = len(plan.scheduled_tasks)
        n_skipped = len(plan.skipped_tasks)
        total = plan.total_time_required()
        budget = self.owner.available_time_minutes

        parts = [
            f"Scheduled {n_scheduled} task(s) using {total} of {budget} available minutes."
        ]
        if n_skipped:
            skipped_names = ", ".join(t.name for t, _ in plan.skipped_tasks)
            parts.append(f"Skipped {n_skipped} task(s) due to time constraints: {skipped_names}.")

        return " ".join(parts)


class Scheduler:
    """Lightweight scheduler utilities: sorting by time, filtering, recurring task handling, and conflict detection.

    This class operates on Pet and Task objects already present in memory and returns helpful lists/warnings
    but does not modify the Planner logic directly.
    """

    @staticmethod
    def _time_to_minutes(t: str) -> int:
        """Convert an HH:MM string to minutes since midnight. Invalid formats return 0."""
        try:
            parts = t.split(":")
            return int(parts[0]) * 60 + int(parts[1])
        except Exception:
            return 0

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by their `time` attribute (HH:MM)."""
        return sorted(tasks, key=lambda t: self._time_to_minutes(t.time))

    def filter_tasks(self, tasks: list[Task], pet_name: str | None = None,
                     completed: bool | None = None, today: date | None = None) -> list[Task]:
        """Filter tasks by `pet_name` and/or completion status for `today`.

        - If `completed` is True, return tasks with last_completed == today.
        - If `completed` is False, return tasks whose last_completed is not today.
        - If `today` is not provided but `completed` is requested, assume today's date.
        """
        result = tasks
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        if completed is not None:
            if today is None:
                today = date.today()
            if completed:
                result = [t for t in result if t.last_completed == today]
            else:
                result = [t for t in result if t.last_completed != today]
        return result

    def mark_task_complete(self, pet: Pet, task: Task, today: date) -> Task | None:
        """Mark `task` complete for `pet` and, if recurring, create the next occurrence.

        Returns the newly created Task for the next occurrence, or None if not recurring.
        """
        task.mark_complete(today)

        if task.frequency not in ("daily", "weekly"):
            return None

        # Create a new task instance for the next occurrence and set its due_date
        days = 1 if task.frequency == "daily" else 7
        next_due = today + timedelta(days=days)

        new_task = deepcopy(task)
        new_task.last_completed = None
        new_task.due_date = next_due
        new_task.pet_name = pet.name

        # Append to pet tasks so it appears in future planning
        pet.tasks.append(new_task)
        return new_task

    def detect_conflicts(self, tasks: list[tuple[Pet, Task]]) -> list[str]:
        """Return a list of warning strings for tasks that share the same `time`.

        This is a lightweight check: only exact time matches are treated as conflicts.
        """
        by_time: dict[str, list[tuple[Pet, Task]]] = {}
        for pet, task in tasks:
            key = task.time or "00:00"
            by_time.setdefault(key, []).append((pet, task))

        warnings: list[str] = []
        for tstr, items in by_time.items():
            if len(items) > 1:
                parts = [f"{pet.name}:{task.name}" for pet, task in items]
                warnings.append(f"Conflict at {tstr} -> " + ", ".join(parts))
        return warnings
