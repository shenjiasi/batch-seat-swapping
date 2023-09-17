import json
import math
import copy

class Student(object):
    def __init__(self, sid, prof):
        self.sid = sid
        self.prof = prof
    def __str__(self):
        if not self.participate():
            return 'Opt Out'
        return '%s@%s' % (self.sid, self.prof)
    def __repr__(self):
        return self.__str__()
    def participate(self):
        return self != NON_PARTICIPANT

NON_PARTICIPANT = Student('.', '.')


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


def check_no_duplicates(l):
    ok = True
    for x in l:
        found = 0
        for y in l:
            if x == y:
                found += 1
        assert(found >= 1)
        if found > 1:
            print('Warning: %s appears %d times' % (x, found))
            ok = False
    return ok

def load_students(stu_seat_filename, stu_fac_filename, sids_participate):
    with open(stu_seat_filename, 'r') as f:
        sids = json.load(f)
        #print(len(sids), sids)

    stus_with_seats = []
    assigned_seats = []
    dont_touch_seats = []
    for s in sids:
        sid = s.split(',')[0]
        seat = s.split(',')[1]
        if sid in sids_participate: # Filter by participants
            stus_with_seats.append(sid)
            assigned_seats.append(seat) # Seats of participants
        else:
            dont_touch_seats.append(seat) # Seats of non-participants

    #print(len(stus_with_seats), stus_with_seats)
    #print(len(assigned_seats), assigned_seats)
    assert(check_no_duplicates(stus_with_seats)) # No doubly-assigned students
    assert(check_no_duplicates(assigned_seats)) # No doubly-assigned seats
    assert(check_no_duplicates(dont_touch_seats)) # No doubly-assigned seats

    stus_with_seats = sorted(list(set(stus_with_seats)))
    assigned_seats = sorted(list(set(assigned_seats)))

    # Sanity checks
    for s1 in stus_with_seats:
        assert(s1 in sids_participate) # Filter by participants
    assert(len(stus_with_seats) <= len(sids_participate))
    assert(len(assigned_seats) <= len(sids_participate))
    assert(len(assigned_seats) + len(dont_touch_seats) == len(sids))

    with open(stu_fac_filename, 'r') as f:
        stu_fac = [s.split(',') for s in json.load(f)]
    all_facs = sorted(list(set([sf[1] for sf in stu_fac])))
    stu_fac_map = get_each_student_one_faculty(stu_fac)
    students = [Student(s, stu_fac_map[s]) for s in stus_with_seats]
    assert(len(students) == len(stus_with_seats))
    print(len(students), students)
    return students, assigned_seats, dont_touch_seats, all_facs

def load_sids_participate(filename):
    with open(filename, 'r') as f:
        sids = f.read().strip().split('\n')
    sids = sorted([s for s in sids if len(s) > 0])
    print('Participate:', len(sids), str(sids))
    assert(len(sids) > 1)
    return sids


def split_by_profs(students, professors):
    split = {}
    for p in professors:
        group = []
        for s in students:
            if s is not None and s.prof == p:
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


def load_inputs():
    sids_participate = load_sids_participate('input/participate.txt')
    students, assigned_seats, dont_touch_seats, professors = \
            load_students('input/students_seats.json', 'input/students_fac.json', sids_participate)
    students, professors = split_profs_into_subgroups(students, professors)
    return students, assigned_seats, dont_touch_seats, professors
