import json
import math
import copy

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
    free_stus = sorted(list(set([s.split(',')[0] for s in sids])))
    #print(len(free_stus), free_stus)

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
    assert(len(profs) > 1)
    return profs


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
    students, professors = load_students('input/students_seats.json', 'input/students_fac.json')
    students, professors = split_profs_into_subgroups(students, professors)
    profs_participate = load_profs_participate('input/participate.txt')
    return students, professors, profs_participate
