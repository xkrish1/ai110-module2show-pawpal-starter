# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

My inital UML design has Owner, Pet, Planner, Daily Plan, and Task classes. The Planner has an Owner object variable that owns a Pet that has their own Tasks. The Daily Plan schedules the Tasks, which is produced by the Planner. This keeps each class focused on one responsibility and makes the scheduling strategy easy to swap or extend without touching the data model.

- What classes did you include, and what responsibilities did you assign to each?
Class	    Responsibility
Pet	        Store the animal's profile and own its list of care tasks
Task	    Represent one care activity and know whether it's due on a given day
Owner	    Store the owner's constraints (available time, preferences) and their pets
DailyPlan	Hold the scheduler's output — which tasks are scheduled, which are skipped and why
Planner	    Contain all scheduling logic — rank tasks, check time constraints, and produce a DailyPlan


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Missing relationship changes: 
- DailyPlan has no link back to Pet
  DailyPlan stores a flat list of Task objects but doesn't know which pet each task belongs to. With multiple pets this means display() can't group tasks by pet, and explain_choices() can't say "skipped Luna's walk because...". 
- skip_task swallows the reason
  The method accepts a reason string but DailyPlan has no field to store per-task skip reasons — only a single explanation: str. You'll lose the reason unless you store it somewhere structured.
- Planner only sees one Owner, not multiple pets directly
  generate_plan will need to iterate owner.pets → then each pet.tasks. That traversal is implicit and easy to forget. No bottleneck yet, but worth being intentional about.

Logic Bottlenecks:
- Task.is_due() has no anchor date
  frequency is a plain string ("daily", "weekly", "as-needed"). is_due(today) has no last_completed date to reason against — a weekly task can't know if it already ran this week without that info.
- rank_tasks tries to sort by three things at once
  Priority, urgency, and duration can conflict (a low-priority long task vs. a high-priority short task). Without a defined tiebreaker rule, the sort will be inconsistent.
- Owner.get_total_available_time() is redundant
  It just returns self.available_time_minutes, which is already a public attribute. The method adds no logic — Planner can read the attribute directly, or the method should do something more (e.g. subtract already-committed time).

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
