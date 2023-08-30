# Batch Seat Swapping

Swap student seat assignments in batch so that students who share the same
primary supervisor move closer.

## Inputs

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
  participate in batch-swapping the seats for all of their own students.

## Algorithm

Random hill-climbing.

## Outputs

* File `output/optimized.{json,html}`: List of seat-student pairs after the
  batch swapping.
