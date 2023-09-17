import string
import random
import copy

import seatmap
import people

def the_seat_participates(a, students):
    if a.student is None:
        return True
    for s in students:
        if a.student.sid == s.sid:
            return True
    return False

def split_by_stu_participation(assignments, students):
    stay = []
    swap = []
    swap_not_none = 0
    for a in assignments:
        if the_seat_participates(a, students):
            swap.append(a)
            if a.student is not None:
                swap_not_none += 1
        else:
            stay.append(a)
    assert(len(stay) + len(swap) == len(assignments))
    print('Stay:', len(stay), stay)
    print('Swap:', len(swap), swap)
    assert(len(swap) > 1)
    assert(len(swap) >= len(students))
    assert(swap_not_none == len(students))
    return stay, swap


def shuffle_students(students, n_seats):
    if len(students) > n_seats:
        random.shuffle(students)
        return students[:n_seats]
    if len(students) < n_seats:
        students += [None for i in range((n_seats - len(students)))]
    random.shuffle(students)
    assert(len(students) == n_seats)
    return students

def construct_initial_seat_assignment(students, assigned_seats, dont_touch_seats, seats_filename):
    all_seats = seatmap.load_seats(seats_filename)

    # Sanity check
    print('All seats: ', len(all_seats), all_seats)
    print('Assigned seats: ', len(assigned_seats), assigned_seats)
    assert(len(assigned_seats) <= len(all_seats))
    assert(len(assigned_seats) + len(dont_touch_seats) <= len(all_seats))
    for s1 in assigned_seats + dont_touch_seats:
        found = False
        for s2 in all_seats:
            if s1 == s2.label:
                found = True
        assert(found)
    assert(len(assigned_seats) == len(students))

    assignments = []
    for s2 in all_seats:
        chosen_student = None
        for i1, s1 in enumerate(assigned_seats):
            if s1 == s2.label:
                chosen_student = students[i1]
        for s1 in dont_touch_seats:
            if s1 == s2.label:
                assert(chosen_student is None)
                chosen_student = people.NON_PARTICIPANT
        assignments.append(seatmap.Assignment(s2, chosen_student))

    # Sanity check
    n_stu = 0
    for a in assignments:
        if a.student is not None:
            n_stu += 1
    assert(n_stu == len(students) + len(dont_touch_seats)) # Participants + "someone else"

    return assignments



def extract_group(students, assignments):
    group = []
    for a in assignments:
        for s in students:
            if a.student == s:
                group.append(a)
                break
    assert(len(group) == len(students))
    return group

def distance_in_group(students, assignments):
    group = extract_group(students, assignments)
    #print(group)
    distances = []
    for i1 in range(len(group)):
        for i2 in range(i1+1, len(group)):
            d = group[i1].seat.distance(group[i2].seat)
            distances.append(d)
    if len(group) <= 1:
        assert(len(distances) == 0)
        return 0
    return sum(distances) / len(distances)

def calculate_cost(students, professors, assignments):
    split = people.split_by_profs(students, professors)
    #print(split)
    averages = []
    summary = []
    for p in split:
        #print(p, end=': ')
        d = distance_in_group(split[p], assignments)
        #print('%s: %.02f' % (p, d), end=', ')
        averages.append(d)
        summary.append(dict(prof=p, n_stus=len(split[p]), avg=d))
    #print(averages)
    result = sum(averages) / len(averages)
    #print(result)
    #print(summary)
    return result, summary

def swap_two_seats(assignments, i1, i2):
    assert(i1 != i2)
    a1 = assignments[i1]
    a2 = assignments[i2]
    b1, b2 = a1.swap(a2)
    replaced = copy.copy(assignments)
    replaced[i1] = b2
    replaced[i2] = b1
    return dict(a1=a1, a2=a2, replaced=replaced)

def improve_seats(students, professors, assignments):
    cost_original, _ = calculate_cost(students, professors, assignments)
    two = random.sample(range(len(assignments)), 2)
    assert(len(two) == 2)
    res = swap_two_seats(assignments, two[0], two[1])
    swapped = res['replaced']
    cost_swapped, _ = calculate_cost(students, professors, swapped)
    if cost_swapped < cost_original:
        return dict(a=swapped, two=(res['a1'], res['a2']), good=True,
                    cost_orig=cost_original, cost_now=cost_swapped)
    else:
        return dict(a=assignments, two=(res['a1'], res['a2']), good=False)

def improve_seats_multiple_times(students, professors, assignments, n_times):
    for i in range(n_times):
        res = improve_seats(students, professors, assignments)
        assignments = res['a']
        if res['good']:
            #print('Trial %d: Swap %s, Average distance %.02f -> %.02f'
            #      % (i, res['two'], res['cost_orig'], res['cost_now']))
            print('%.02f' % res['cost_now'], end=' ', flush=True)
    return assignments

def print_summaries(summary_init, summary_opt):
    by_prof_init = sorted(summary_init, key=(lambda s: s['prof']))
    by_prof_opt = sorted(summary_opt, key=(lambda s: s['prof']))
    assert(len(by_prof_init) == len(by_prof_opt))
    compare = []
    for si, so in zip(by_prof_init, by_prof_opt):
        assert(si['prof'] == so['prof'])
        assert(si['n_stus'] == so['n_stus'])
        compare.append(dict(prof=si['prof'], n_stus=si['n_stus'],
                            avg_init=si['avg'], avg_opt=so['avg']))
    by_n_stus = sorted(compare, key=(lambda c: c['n_stus']))
    for c in by_n_stus:
        print('% 15s with %2d students, mean distance % 12.02f -> % 12.02f' %(c['prof'], c['n_stus'], c['avg_init'], c['avg_opt']))


def assign_multiple_times(n_times):
    students, assigned_seats, dont_touch_seats, professors = people.load_inputs()
    initial = construct_initial_seat_assignment(students, assigned_seats, dont_touch_seats, 'input/seats.json')

    m = seatmap.SeatMap(initial)
    #print(m)
    m.dump_json('output/initial.json')
    m.dump_csv('output/initial')
    m.dump_html('output/initial.html')

    initial_stay, initial_swap = split_by_stu_participation(initial, students)
    optimized_swap = improve_seats_multiple_times(students, professors, initial_swap, n_times)
    optimized = initial_stay + optimized_swap

    m = seatmap.SeatMap(optimized)
    #print(m)
    m.dump_json('output/optimized.json')
    m.dump_csv('output/optimized')
    m.dump_html('output/optimized.html')
    m.dump_json_cleaned_sorted('output/swapped.json')

    res_init = calculate_cost(students, professors, initial)
    res_opt = calculate_cost(students, professors, optimized)
    print('\nAfter trying to swap %d times, average distance drops from %.02f to %.02f'
          % (n_times, res_init[0], res_opt[0]))
    print_summaries(res_init[1], res_opt[1])


assign_multiple_times(50000)
