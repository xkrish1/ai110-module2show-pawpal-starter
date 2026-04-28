# PawPal+ — Final UML Class Diagram

```mermaid
classDiagram
    class Task {
        +str name
        +str category
        +int duration_minutes
        +int priority
        +str frequency
        +str time
        +date due_date
        +str notes
        +str pet_name
        +date last_completed
        +is_due(today: date) bool
        +mark_complete(today: date) None
        +to_dict() dict
    }

    class Pet {
        +str name
        +str species
        +int age
        +list health_conditions
        +list tasks
        +add_task(task: Task) None
        +get_tasks_by_priority() list
        +get_due_tasks(today: date) list
    }

    class Owner {
        +str name
        +int available_time_minutes
        +dict preferences
        +list pets
        +add_pet(pet: Pet) None
    }

    class DailyPlan {
        +date date
        +list scheduled_tasks
        +list skipped_tasks
        +str explanation
        +add_task(pet: Pet, task: Task) None
        +skip_task(task: Task, reason: str) None
        +total_time_required() int
        +display() str
    }

    class Planner {
        +Owner owner
        +str strategy
        +generate_plan(today: date) DailyPlan
        +rank_tasks(tasks: list) list
        +fits_in_time(task: Task, remaining: int) bool
        +explain_choices(plan: DailyPlan) str
    }

    class Scheduler {
        +sort_by_time(tasks: list) list
        +filter_tasks(tasks, pet_name, completed, today) list
        +mark_task_complete(pet, task, today) Task
        +detect_conflicts(tasks: list) list
    }

    Owner "1" --> "*" Pet : owns
    Pet "1" --> "*" Task : has
    Planner --> Owner : uses
    Planner ..> DailyPlan : produces
    DailyPlan --> Pet : references
    DailyPlan --> Task : schedules
    Scheduler --> Pet : queries
    Scheduler --> Task : manages
```
