(Sciprt for the constraint, hk's part starts from constraint 3)

(I think we want to go through what we considered)



We have considered
- There are modules with single cohorts and double cohorts.
- There are blocked out timings.



In all of our variants, our primary decision variable is the time-indexed variable. 

We may have other decision variables, but they help to support the constraints or objective. (Do we have these?)



Constraint 1 ensures that each class must be assigned exactly once. For each job (which is the class session), it must be assigned to some time slot.



Constraint 2 ensures that at most one class can be conducted at a specific venue at any instant. Vij are constants of the current assignment of the venue to class.

For all venues, for all times, there should be one class going on. We consider the duration of each class.



Constraint 3 ensures that each instructor can teach at most one class. We have the set of jobs that can taught by instructor each instructor. For each instructor, for each job by the instructor, it should not clash.



(my part begins here)



Constraint 4 ensures that each sessions of each module follow precedence chains. We have set of classes belonging to the same module. For each module, for each precedence constraint, the class that happens after must start later than the class that happens earlier.



Constraint 5 ensures that ESD courses cannot schedule at venue and timing occupied by ESD courses. Pre-assigned classes refers to the non-ESD classes.



Constraint 6 ensures that scheduled classes must happen only during allowed timings. The day begins at 0830 and ends at 2000 for Monday, Tuesday and Thursday, and ends at 1300 on Monday and Friday. In addition, there is blocked out periods for HASS - between 1500 to 1800 for Monday, 0830-1000 for Tuesday, 1500-1800 on Thursday, 1130-1330 on Friday.



Constraint 7 ensures that there can only be one session from each cohort of each module in a day. For each module, for each cohort, the number of classes schedule for the day is at most one.



Constraint 8 ensures clashes between each module. For each module, for each cohort group, we consider the start time and end time.



There may be modules that have double cohort modules with single cohort modules (such as opti lecture then two tutorial sessions for each cohorts). Constraint ensure that each cohort in the double cohort module do not clash with the single cohort modules.



This concludes the 9 common constraints that we apply to all variants.



(How many constraints and how many variables currently?)