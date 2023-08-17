import string
import math
import random
import copy
import json

import seatmap

class Student(object):
    def __init__(self, sid, prof):
        self.sid = sid
        self.prof = prof
    def __str__(self):
        return '%s@%s' % (self.sid, self.prof)
    def __repr__(self):
        return self.__str__()


def get_each_student_one_faculty(stu_fac):
    all_stus = sorted(list(set([sf[0] for sf in stu_fac])))
    for s in all_stus:
        fl = []
        for sf in stu_fac:
            if sf[0] == s:
                fl.append(sf[1])
        assert(len(fl) > 0)
        if len(fl) > 1:
            print('Warning: %s has multiple facs %s' % (s, fl))
            assert(len(set(fl)) == 1)
    stu_fac_map = {sf[0]: sf[1] for sf in stu_fac}
    return stu_fac_map

def load_students(students_filename, stu_fac_filename):
    with open(students_filename, 'r') as f:
        sids = json.load(f)
        #print(len(sids), sids)
    free_stus = sorted(list(set(sids)))

    with open(stu_fac_filename, 'r') as f:
        stu_fac = [s.split(',') for s in json.load(f)]
    all_facs = sorted(list(set([sf[1] for sf in stu_fac])))
    stu_fac_map = get_each_student_one_faculty(stu_fac)
    students = [Student(s, stu_fac_map[s]) for s in free_stus]
    assert(len(students) == len(free_stus))
    print(len(students), students)
    return students, all_facs


def load_profs_participate(filename):
    with open(filename, 'r') as f:
        profs = f.read().strip().split('\n')
    profs = sorted([p for p in profs if len(p) > 0])
    print('Participate:', len(profs), str(profs))
    return profs

def split_by_prof_participation(assignments, profs_participate):
    stay = []
    swap = []
    stus_participate = []
    for a in assignments:
        found = False
        for p in profs_participate:
            if a.student.prof.startswith(p + '-') and len(a.student.prof) == len(p) + 2:
                found = True
                #print(p, a.student.prof)
        if found:
            swap.append(a)
            stus_participate.append(a.student)
        else:
            stay.append(a)
    assert(len(stay) + len(swap) == len(assignments))
    print('Stay:', len(stay), stay)
    print('Swap:', len(swap), swap)
    return stay, swap, stus_participate


def shuffle_students(students, n_seats):
    if len(students) > n_seats:
        random.shuffle(students)
        return students[:n_seats]
    if len(students) < n_seats:
        students += [None * (n_seats - len(students))]
    random.shuffle(students)
    assert(len(students) == n_seats)
    return students

def assign_seats(students, seats_filename):
    seats = seatmap.load_seats(seats_filename)
    random.shuffle(seats)
    print(len(seats), seats)

    chosen_students = shuffle_students(students, len(seats))
    print(len(chosen_students), chosen_students)
    assert(len(chosen_students) == len(seats))

    assignments = []
    for (seat, chosen_student) in zip(seats, chosen_students):
        assignments.append(seatmap.Assignment(seat, chosen_student))
    return assignments, chosen_students



def split_by_profs(students, professors):
    split = {}
    for p in professors:
        group = []
        for s in students:
            if s.prof == p:
                group.append(s)
        split[p] = group
    return split

def split_subgroup_sizes(n, cap):
    assert(cap > 0)
    if n < cap:
        return [n]
    mod = n % cap
    div = math.floor(n / cap)

    # Split into subgroups of equal size
    if mod == 0:
        return div * [cap]

    # Spread "mod" number of trailing students into the "div" number of subgroups
    if mod <= div: # The number of subgroups is large enough
        temp = split_subgroup_sizes(n - mod, cap)
        for i in range(mod):
            temp[i] += 1
        assert(sum(temp) == n)
        return temp
    else: # There are not enough subgroups, so try a smaller subgroup size
        return split_subgroup_sizes(n, cap - 1)

def split_profs_into_subgroups(students, professors):
    split = split_by_profs(students, professors)
    sub_professors = {}
    for p in split:
        n_students = len(split[p])
        sizes = split_subgroup_sizes(n_students, 7) # XXX
        #print(p, n_students, split[p])
        #print(sizes)
        #print('Split %s into %d subgroups: %s' % (p, len(sizes), str(sizes)))
        assert(sum(sizes) == n_students)
        subgroups = []
        last = 0
        for s in sizes:
            first = last
            last = first + s
            assert(last <= n_students)
            subgroups.append(split[p][first : last])
            #print(first, last, subgroups[-1])
        assert(last == n_students)
        for idx, g in enumerate(subgroups):
            sub_prof = '%s-%d' % (p, idx)
            sub_professors[sub_prof] = g

        # Sanity check
        p_students_after_subgroup = []
        for idx, g in enumerate(subgroups):
            p_students_after_subgroup += g
        assert(split[p] == p_students_after_subgroup)

    # Sanity check
    #print(sub_professors)
    #print(sub_professors.keys())
    all_students_after_split = []
    for sub_prof in sub_professors:
        print(sub_prof, sub_professors[sub_prof])
        all_students_after_split += sub_professors[sub_prof]
    assert(len(students) == len(all_students_after_split))
    assert(set(students) == set(all_students_after_split))

    sub_students, sub_professors = rename_student_profs_by_subgroups(students, sub_professors)
    return sub_students, sub_professors.keys()

def rename_student_profs_by_subgroups(students, sub_professors):
    #print(sub_professors)
    renamed_students = [copy.copy(stu) for stu in students]
    renamed_sub_professors = {}
    for p in sub_professors:
        subgroup = sub_professors[p]
        renamed = []
        for stu in subgroup:
            assert(isinstance(stu, Student))
            stu2 = copy.copy(stu)
            stu2.prof = p
            renamed.append(stu2)
            for i, s in enumerate(renamed_students):
                if s.sid == stu.sid:
                    renamed_students[i] = stu2
        renamed_sub_professors[p] = renamed

        # Sanity checks
        #print(subgroup, renamed)
        assert(len(subgroup) == len(renamed))
        for s, r in zip(subgroup, renamed):
            assert(s.sid == r.sid)
            assert(r.prof.startswith(s.prof + '-'))
            assert(len(r.prof) == len(s.prof) + 2)

    # Sanity checks
    assert(len(students) == len(renamed_students))
    for s1, s2 in zip(students, renamed_students):
        #print(s1, s2)
        assert(s1 != s2)
        assert(s1.sid == s2.sid)
        assert(s1.prof != s2.prof)
        assert(s2.prof.startswith(s1.prof + '-'))
        assert(len(s2.prof) == len(s1.prof) + 2)

    return renamed_students, renamed_sub_professors

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
    split = split_by_profs(students, professors)
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
    students, professors = load_students('input/students.json', 'input/students_fac.json')
    students, professors = split_profs_into_subgroups(students, professors)
    initial, chosen_students = assign_seats(students, 'input/seats.json')

    m = seatmap.SeatMap(initial)
    #print(m)
    m.dump_json('output/initial.json')
    m.dump_csv('output/initial')
    m.dump_html('output/initial.html')

    profs_participate = load_profs_participate('input/participate.txt')
    initial_stay, initial_swap, stus_participate = split_by_prof_participation(initial, profs_participate)
    optimized_swap = improve_seats_multiple_times(stus_participate, professors, initial_swap, n_times)
    optimized = initial_stay + optimized_swap

    m = seatmap.SeatMap(optimized)
    #print(m)
    m.dump_json('output/optimized.json')
    m.dump_csv('output/optimized')
    m.dump_html('output/optimized.html')

    res_init = calculate_cost(stus_participate, professors, initial)
    res_opt = calculate_cost(stus_participate, professors, optimized)
    print('\nAfter trying to swap %d times, average distance drops from %.02f to %.02f'
          % (n_times, res_init[0], res_opt[0]))
    print_summaries(res_init[1], res_opt[1])


assign_multiple_times(50000)
