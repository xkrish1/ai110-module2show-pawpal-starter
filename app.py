import streamlit as st
from datetime import date
from pawpal_system import Task, Pet, Owner, Planner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Bootstrap session state
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_time_minutes=60)
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

# ---------------------------------------------------------------------------
# Section 1: Owner setup
# ---------------------------------------------------------------------------

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    st.write(f"**Name:** {st.session_state.owner.name}")
with col2:
    st.write(f"**Time budget:** {st.session_state.owner.available_time_minutes} min")

# ---------------------------------------------------------------------------
# Section 2: Add a Pet
# ---------------------------------------------------------------------------

st.subheader("Pets")

with st.form("add_pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age", min_value=0, max_value=30, value=3)
    submitted_pet = st.form_submit_button("Add Pet")

if submitted_pet:
    new_pet = Pet(name=pet_name, species=species, age=age)
    st.session_state.owner.add_pet(new_pet)   # <-- Owner.add_pet() handles the data
    st.success(f"Added {pet_name} the {species}!")

# Show current pets
if st.session_state.owner.pets:
    for pet in st.session_state.owner.pets:
        st.write(f"- **{pet.name}** ({pet.species}, age {pet.age})"
                 + (f" — {', '.join(pet.health_conditions)}" if pet.health_conditions else ""))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Add a Task to a Pet
# ---------------------------------------------------------------------------

st.subheader("Tasks")

if not st.session_state.owner.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    with st.form("add_task_form"):
        pet_names = [p.name for p in st.session_state.owner.pets]
        col1, col2 = st.columns(2)
        with col1:
            selected_pet = st.selectbox("Assign to pet", pet_names)
            task_name = st.text_input("Task name", value="Morning walk")
            category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming", "enrichment"])
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
            priority = st.slider("Priority (1=low, 5=high)", min_value=1, max_value=5, value=3)
            frequency = st.selectbox("Frequency", ["daily", "weekly", "as-needed"])
        notes = st.text_input("Notes (optional)", value="")
        submitted_task = st.form_submit_button("Add Task")

    if submitted_task:
        pet = next(p for p in st.session_state.owner.pets if p.name == selected_pet)
        new_task = Task(
            name=task_name,
            category=category,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
            notes=notes,
        )
        pet.add_task(new_task)   # <-- Pet.add_task() handles the data
        st.success(f"Added '{task_name}' to {selected_pet}.")

    # Show all tasks sorted by scheduled time (Scheduler.sort_by_time)
    all_tasks = [t for p in st.session_state.owner.pets for t in p.tasks]
    if all_tasks:
        scheduler = st.session_state.scheduler
        sorted_tasks = scheduler.sort_by_time(all_tasks)
        st.write("**All tasks — sorted by scheduled time:**")
        st.table([
            {
                "Time": t.time,
                "Pet": t.pet_name,
                "Task": t.name,
                "Category": t.category,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Frequency": t.frequency,
            }
            for t in sorted_tasks
        ])

        # Conflict detection — flag exact-time collisions across all pets
        pairs = [(p, t) for p in st.session_state.owner.pets for t in p.tasks]
        conflicts = scheduler.detect_conflicts(pairs)
        if conflicts:
            st.write("**Scheduling conflicts detected:**")
            for warning in conflicts:
                st.warning(f"⚠️ {warning}")
        else:
            st.success("No scheduling conflicts detected.")

st.divider()

# ---------------------------------------------------------------------------
# Section 4: Generate Schedule
# ---------------------------------------------------------------------------

st.subheader("Generate Today's Schedule")

if st.button("Generate schedule"):
    if not st.session_state.owner.pets:
        st.warning("Add at least one pet and task first.")
    else:
        planner = Planner(owner=st.session_state.owner)
        plan = planner.generate_plan(today=date.today())   # <-- Planner.generate_plan()

        if not plan.scheduled_tasks:
            st.warning("No tasks could be scheduled. Check time budget or task frequencies.")
        else:
            st.success(f"Scheduled {len(plan.scheduled_tasks)} task(s).")
            for pet, task in plan.scheduled_tasks:
                st.write(f"- **[{task.priority}★] {task.name}** ({pet.name}) — {task.duration_minutes} min")

            st.write(f"**Total time:** {plan.total_time_required()} / "
                     f"{st.session_state.owner.available_time_minutes} min")

        if plan.skipped_tasks:
            st.warning("Skipped (not enough time):")
            for task, reason in plan.skipped_tasks:
                st.write(f"- {task.name}: {reason}")

        st.info(plan.explanation)

        # Show conflict warnings for the scheduled tasks
        scheduled_pairs = plan.scheduled_tasks  # list of (Pet, Task)
        conflicts = st.session_state.scheduler.detect_conflicts(scheduled_pairs)
        if conflicts:
            st.write("**Time conflicts in today's schedule:**")
            for warning in conflicts:
                st.warning(f"⚠️ {warning}")
