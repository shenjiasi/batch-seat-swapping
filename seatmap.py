import json

class Room(object):
    def __init__(self, room):
        assert(isinstance(room, str))
        room = room.lower()
        self.label = room
        sign = 1
        if room.startswith('lg'):
            sign = -1
            room = room[2:]
            assert(room.isnumeric())
        if not room.isnumeric():
            assert(room.endswith('a')) # XXX
            room = room[:-1] # XXX
        self.floor = sign * int(room[0])
        self.room = int(room[1:])
    def __str__(self):
        return 'f%dr%03d' % (self.floor, self.room)
    def __repr__(self):
        return self.__str__()
    def distance(self, other):
        assert(isinstance(other, Room))
        if self.floor == other.floor:
            return abs(self.room - other.room) # XXX
        else:
            return 1000 + abs(self.room - other.room) # XXX

class Seat(object):
    def __init__(self, label):
        self.label = label
        assert('-' in label)
        parts = label.split('-')
        assert(len(parts) == 2)
        self.room = Room(parts[0])
        self.desk = int(parts[1])
    def __str__(self):
        return '%sd%02d' % (self.room, self.desk)
    def __repr__(self):
        return self.__str__()
    def distance(self, other):
        assert(isinstance(other, Seat))
        return self.room.distance(other.room) * 100 + abs(self.desk - other.desk) # XXX

class Assignment(object):
    def __init__(self, seat, student):
        self.seat = seat
        self.student = student
    def __str__(self):
        return '%s: %s' % (self.seat, self.student)
    def __repr__(self):
        return self.__str__()
    def swap(self, other):
        assert(isinstance(other, Assignment))
        return Assignment(self.seat, other.student), Assignment(other.seat, self.student)
    def to_json(self):
        return '"%s":"%s"' % (self.seat.label, self.student)

class SeatMap(object):
    def __init__(self, assignments):
        self.assignments = sorted(assignments, key=(lambda a: str(a.seat)))
        self.rooms2d = self.to_table()
    def __str__(self):
        return str(self.rooms2d)
    def __repr__(self):
        return self.__str__()
    def __split_by_rooms(self):
        rooms = {}
        for a in self.assignments:
            r = str(a.seat.room)
            if r not in rooms:
                rooms[r] = []
            rooms[r].append(a)
        for r in rooms:
            rooms[r] = sorted(rooms[r], key=(lambda a: a.seat.desk))
        return rooms
    def __str_debug(self, rooms_split):
        s = '[\n'
        for r in rooms_split:
            al = rooms_split[r]
            s += '  [\n    ' + '\n    '.join(str(a) for a in al) + '\n  ]\n'
        s += ']\n'
        return s
    def to_table(self):
        rooms_split = self.__split_by_rooms()
        #print(self.__str_debug(rooms_split))
        rooms2d = {}
        for r in rooms_split:
            room_label = rooms_split[r][0].seat.room.label
            desks = {}
            for a in rooms_split[r]:
                assert(a.seat.room.label == room_label)
                assert(a.seat.desk not in desks)
                desks[a.seat.desk] = a.student
            rooms2d[room_label] = desks
        return rooms2d
    def to_json(self):
        return '{%s}' % ','.join([a.to_json() for a in self.assignments])
    def dump_json(self, filename):
        with open(filename, 'w') as f:
            f.write(self.to_json() + '\n')
    def to_csv(self, room_label):
        s = 'desk,student\n'
        desks = self.rooms2d[room_label]
        indices = sorted([d for d in desks])
        count = 0
        for d in range(indices[0], indices[-1]+1):
            s += str(d) + ','
            if d in desks:
                s += str(desks[d]) + '\n'
                count += 1
            else:
                s += 'N/A\n'
        assert(count == len(desks))
        return s
    def dump_csv(self, filename_prefix):
        for room_label in self.rooms2d:
            with open('%s-%s.csv' % (filename_prefix, room_label), 'w') as f:
                f.write(self.to_csv(room_label))
    def to_html(self):
        s = '<table><tr>\n'
        rooms = sorted([r for r in self.rooms2d])
        for room_label in rooms:
            s += '<th>%s</th>' % room_label
        s += '</tr>\n<tr style="vertical-align:top">\n'
        for room_label in rooms:
            s += '<td>%s</td>\n' % self.to_csv(room_label).replace('\n','<br>')
        s += '</tr></table>\n'
        return s
    def dump_html(self, filename):
        with open(filename, 'w') as f:
            f.write(self.to_html())


def load_seats(seats_filename):
    with open(seats_filename, 'r') as f:
        seats = json.load(f)
    free_seats = sorted(list(set(seats)))
    return [Seat(label) for label in free_seats]
