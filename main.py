from datetime import date
from pawpal_system import Task, Pet, Owner, Planner, Scheduler


# ---------------------------------------------------------------------------
# Set up Owner
# ---------------------------------------------------------------------------

owner = Owner(
    name="Alex",
    available_time_minutes=60,
    preferences={"prefer_morning": True}
)

# ---------------------------------------------------------------------------
# Set up Pets
# ---------------------------------------------------------------------------

luna = Pet(name="Luna", species="dog", age=3)
mochi = Pet(name="Mochi", species="cat", age=5, health_conditions=["hyperthyroidism"])

# ---------------------------------------------------------------------------
# Add Tasks to Luna (dog)
# ---------------------------------------------------------------------------

luna.add_task(Task(
    name="Morning Walk",
    category="walk",
    duration_minutes=20,
    priority=5,
    frequency="daily",
    time="08:00",
))

luna.add_task(Task(
    name="Breakfast",
    category="feeding",
    duration_minutes=5,
    priority=5,
    frequency="daily",
    time="07:30",
))

luna.add_task(Task(
    name="Brush coat",
    category="grooming",
    duration_minutes=15,
    priority=2,
    frequency="weekly",
))

# ---------------------------------------------------------------------------
# Add Tasks to Mochi (cat)
# ---------------------------------------------------------------------------

mochi.add_task(Task(
    name="Breakfast",
    category="feeding",
    duration_minutes=5,
    priority=5,
    frequency="daily",
    time="08:00",
))

mochi.add_task(Task(
    name="Thyroid medication",
    category="meds",
    duration_minutes=5,
    priority=5,
    frequency="daily",
    notes="Hide pill in treat",
    time="09:00",
))

mochi.add_task(Task(
    name="Puzzle feeder enrichment",
    category="enrichment",
    duration_minutes=10,
    priority=3,
    frequency="daily",
    time="07:30",
))

# ---------------------------------------------------------------------------
# Register pets with owner
# ---------------------------------------------------------------------------

owner.add_pet(luna)
owner.add_pet(mochi)

# ---------------------------------------------------------------------------
# Generate and print today's plan
# ---------------------------------------------------------------------------

planner = Planner(owner=owner, strategy="priority-first")
plan = planner.generate_plan(today=date.today())

print(plan.display())

# ---------------------------------------------------------------------------
# Demonstrate Scheduler: sorting, filtering, recurrence, conflicts
# ---------------------------------------------------------------------------
scheduler = Scheduler()

# Show all tasks across pets, unsorted
all_tasks = [t for p in owner.pets for t in p.tasks]
print('\nAll tasks (unsorted by time):')
for t in all_tasks:
    print(f" - {t.pet_name}: {t.name} at {t.time}")

print('\nTasks sorted by time:')
for t in scheduler.sort_by_time(all_tasks):
    print(f" - {t.pet_name}: {t.name} at {t.time}")

print('\nFilter tasks for Mochi (not completed):')
for t in scheduler.filter_tasks(all_tasks, pet_name='Mochi', completed=False):
    print(f" - {t.pet_name}: {t.name} at {t.time}")

# Create a recurrence example: mark Mochi's breakfast complete and auto-create next
mochi_breakfast = next(t for t in mochi.tasks if t.name == 'Breakfast')
new_task = scheduler.mark_task_complete(mochi, mochi_breakfast, today=date.today())
if new_task:
    print(f"\nMarked complete and created recurrence for next due date: {new_task.due_date} ({new_task.name})")

# Conflict detection example (exact time matches)
pairs = [(p, t) for p in owner.pets for t in p.tasks]
conflicts = scheduler.detect_conflicts(pairs)
if conflicts:
    print('\nConflicts detected:')
    for w in conflicts:
        print(' -', w)
else:
    print('\nNo conflicts detected')
