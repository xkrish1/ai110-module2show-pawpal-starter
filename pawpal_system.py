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
    pet_name: str = ""
    last_completed: date | None = None

    def is_due(self, today: date) -> bool:
        """Return True if this task should occur today (daily=always, weekly=every 7 days, as-needed=never)."""
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

    def to_dict(self) -> dict:
        """Return a dictionary representation of this task."""
        return {
            "name": self.name,
            "category": self.category,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
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
