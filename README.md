# Batch Seat Swapping

The batch seat swapping algorithm applies to students who have been assigned a
seat in the CSE RPg Labs and whose primary supervisors participate in the
scheme.  The algorithm searches for improved seat arrangements among
participating students so that those who share the same primary supervisor
move closer.

## Step-by-Step Instructions

### Step 1: Prepare Input Files

Input files should be placed under the `input/` directory using the following
file names:

* **File `input/students_seats.json`:** List of student-seat pairs assigned by the
  initial RPG Lab seat application process.
* **File `input/seats.json`:** List of all RPG Lab seats that are available to CSE.
  These seats contain both occupied ones (i.e., those that have been assigned
  in `input/students_seats.json`) and empty seats (i.e., those that have not been
  assigned to any student).
* **File `input/students_fac.json`:** List of student-faculty pairs. For students
  that are co-supervised by multiple faculty members, their corresponding faculty
  members in this file are their primary supervisors.
* **File `input/participate.txt`:** List of faculty members who voluntarily
  sign up to batch-swap the seats for all of their own students.

We have included a set of sample input files for illustration and testing
purposes.  Please replace them with authentic data.

### Step 2: Run the Batch-Swapping Script

```
python3 assign.py
```

### Step 3: Export the Output Files

The most important output file is this one:

* **File `output/swapped.json`**: List of updated student-seat pairs after
  batch swapping.

Please load this file into CSSystem. 

Please disregard other files under the `output/` directory, as they are
generated for debugging and illustration purposes only:

* File `output/optimized.html`: Visual representation of updated seat-student
  pairs.
* File `output/optimized.json`: List of updated seat-student pairs.
* File `output/initial.html`: Visual representation of initial seat-student
  pairs.
* File `output/initial.json`: List of initial seat-student pairs.


## Additional Information

Please note that while the scheme aims to reduce the average within-group
distance for all participating students, there are no guarantees for individual
success, fairness, or precise seat proximity calculations. In particular, the
current limitations are as follows:

  1. There are no guarantees on individual success rates; some students may not
     experience improved seat proximity to their group-mates.
  2. While participating, some students may be initially assigned a desirable
     seat (e.g., next to a window) but later be swapped to a less desirable
     seat (e.g., next to a hallway). The newly assigned seats may be in
     different rooms than those initially assigned. If a student participates,
     they must move to the newly assigned seat.
  3. Seat proximity is currently calculated by subtracting room and seat
     numbers, which is less accurate than measuring physical distance. Due to
     limited manpower for this exercise, we are unable to provide precise
     calculations this year but hope to improve this aspect in the future.

Current algorithm: Random hill climbing.
