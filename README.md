# Batch Seat Swapping

Swap student seat assignments in batch so that students from the same group move closer.

## Inputs

* File `input/students.json`: List of students who (1) have been assigned fixed
  seats in the RPG hubs and (2) consent to participate in batch swapping.
* File `input/seats.json`: List of seats that are available for swapping. These
  seats may be the seats that have been assigned initially to the students in
  `input/students.json`.
* File `input/students_facs.json`: List of student-faculty pairs.
* File `input/participate.txt`: List of faculty members who voluntarily
  participate in batch-swapping the seats for their students.

## Algorithm

Random hill-climbing

## Outputs

* File `output/optimized.{json,html}`: List of seat-student pairs after the
  batch swapping.
