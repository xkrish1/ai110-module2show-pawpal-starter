from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Planner


TODAY = date(2026, 3, 25)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(name="Walk", duration=20, priority=3, frequency="daily"):
    return Task(name=name, category="walk", duration_minutes=duration,
                priority=priority, frequency=frequency)

def make_pet(name="Luna"):
    return Pet(name=name, species="dog", age=3)

def make_owner(minutes=60):
    owner = Owner(name="Alex", available_time_minutes=minutes)
    return owner


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

class TestTask:
    def test_mark_complete_sets_last_completed(self):
        task = make_task()
        task.mark_complete(TODAY)
        assert task.last_completed == TODAY

    def test_daily_task_is_always_due(self):
        task = make_task(frequency="daily")
        assert task.is_due(TODAY) is True

    def test_weekly_task_due_when_never_completed(self):
        task = make_task(frequency="weekly")  # last_completed is None
        assert task.is_due(TODAY) is True

    def test_weekly_task_due_after_7_days(self):
        task = make_task(frequency="weekly")
        task.last_completed = TODAY - timedelta(days=7)
        assert task.is_due(TODAY) is True

    def test_weekly_task_not_due_before_7_days(self):
        task = make_task(frequency="weekly")
        task.last_completed = TODAY - timedelta(days=3)
        assert task.is_due(TODAY) is False

    def test_as_needed_task_never_auto_due(self):
        task = make_task(frequency="as-needed")
        assert task.is_due(TODAY) is False

    def test_mark_complete_makes_weekly_not_due(self):
        task = make_task(frequency="weekly")
        task.mark_complete(TODAY)
        assert task.is_due(TODAY) is False  # completed today, not due again yet


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------

class TestPet:
    def test_add_task_increases_task_count(self):
        pet = make_pet()
        assert len(pet.tasks) == 0
        pet.add_task(make_task())
        assert len(pet.tasks) == 1

    def test_add_task_stamps_pet_name(self):
        pet = make_pet("Luna")
        task = make_task()
        pet.add_task(task)
        assert task.pet_name == "Luna"

    def test_get_tasks_by_priority_orders_highest_first(self):
        pet = make_pet()
        pet.add_task(make_task("Low", priority=1))
        pet.add_task(make_task("High", priority=5))
        pet.add_task(make_task("Mid", priority=3))
        result = pet.get_tasks_by_priority()
        assert [t.priority for t in result] == [5, 3, 1]

    def test_get_due_tasks_returns_only_due(self):
        pet = make_pet()
        daily = make_task("Daily", frequency="daily")
        weekly = make_task("Weekly", frequency="weekly")
        weekly.last_completed = TODAY - timedelta(days=2)  # not due yet
        pet.add_task(daily)
        pet.add_task(weekly)
        due = pet.get_due_tasks(TODAY)
        assert len(due) == 1
        assert due[0].name == "Daily"

    def test_get_due_tasks_empty_when_none_due(self):
        pet = make_pet()
        task = make_task(frequency="as-needed")
        pet.add_task(task)
        assert pet.get_due_tasks(TODAY) == []


# ---------------------------------------------------------------------------
# Owner tests
# ---------------------------------------------------------------------------

class TestOwner:
    def test_add_pet_increases_pet_count(self):
        owner = make_owner()
        assert len(owner.pets) == 0
        owner.add_pet(make_pet())
        assert len(owner.pets) == 1

    def test_add_multiple_pets(self):
        owner = make_owner()
        owner.add_pet(make_pet("Luna"))
        owner.add_pet(make_pet("Mochi"))
        assert len(owner.pets) == 2
        assert owner.pets[1].name == "Mochi"


# ---------------------------------------------------------------------------
# Planner tests
# ---------------------------------------------------------------------------

class TestPlanner:
    def _setup(self, owner_minutes=60):
        owner = make_owner(owner_minutes)
        pet = make_pet("Luna")
        owner.add_pet(pet)
        return owner, pet

    def test_generate_plan_schedules_due_tasks(self):
        owner, pet = self._setup(60)
        pet.add_task(make_task("Walk", duration=20, frequency="daily"))
        plan = Planner(owner).generate_plan(TODAY)
        assert len(plan.scheduled_tasks) == 1

    def test_generate_plan_skips_tasks_over_budget(self):
        owner, pet = self._setup(owner_minutes=10)
        pet.add_task(make_task("Walk", duration=20, frequency="daily"))
        plan = Planner(owner).generate_plan(TODAY)
        assert len(plan.scheduled_tasks) == 0
        assert len(plan.skipped_tasks) == 1

    def test_rank_tasks_orders_by_priority_then_duration(self):
        owner, pet = self._setup()
        planner = Planner(owner)
        tasks = [
            (pet, make_task("LowLong",  duration=30, priority=1)),
            (pet, make_task("HighShort", duration=5, priority=5)),
            (pet, make_task("HighLong", duration=20, priority=5)),
        ]
        ranked = planner.rank_tasks(tasks)
        names = [t.name for _, t in ranked]
        assert names == ["HighShort", "HighLong", "LowLong"]

    def test_fits_in_time_true_when_task_fits(self):
        planner = Planner(make_owner())
        assert planner.fits_in_time(make_task(duration=20), remaining_minutes=30) is True

    def test_fits_in_time_false_when_task_too_long(self):
        planner = Planner(make_owner())
        assert planner.fits_in_time(make_task(duration=30), remaining_minutes=20) is False

    def test_plan_collects_tasks_across_multiple_pets(self):
        owner = make_owner(60)
        luna = make_pet("Luna")
        mochi = make_pet("Mochi")
        luna.add_task(make_task("Luna Walk", duration=10, frequency="daily"))
        mochi.add_task(make_task("Mochi Feed", duration=5, frequency="daily"))
        owner.add_pet(luna)
        owner.add_pet(mochi)
        plan = Planner(owner).generate_plan(TODAY)
        assert len(plan.scheduled_tasks) == 2

    def test_total_time_matches_scheduled_tasks(self):
        owner, pet = self._setup(60)
        pet.add_task(make_task("Walk", duration=20, frequency="daily"))
        pet.add_task(make_task("Feed", duration=10, frequency="daily"))
        plan = Planner(owner).generate_plan(TODAY)
        assert plan.total_time_required() == 30
