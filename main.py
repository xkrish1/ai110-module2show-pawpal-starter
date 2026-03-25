from datetime import date
from pawpal_system import Task, Pet, Owner, Planner


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
))

luna.add_task(Task(
    name="Breakfast",
    category="feeding",
    duration_minutes=5,
    priority=5,
    frequency="daily",
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
))

mochi.add_task(Task(
    name="Thyroid medication",
    category="meds",
    duration_minutes=5,
    priority=5,
    frequency="daily",
    notes="Hide pill in treat",
))

mochi.add_task(Task(
    name="Puzzle feeder enrichment",
    category="enrichment",
    duration_minutes=10,
    priority=3,
    frequency="daily",
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
