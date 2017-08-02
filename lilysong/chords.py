import re

pause_regex = (
    r'^r(?P<duration>([0-9]+\.*|\\longa|\\breve))?$'
)
chord_regex = (
    r'^(?P<root>[a-z]+)(?P<octave>\'*|,*)(?P<duration>([0-9]+\.*|\\longa|\\breve))?' +
    r'(:(?P<modifiers>[a-z0-9+-]+)(?P<added>(\.[0-9]+(\+|-)?)*))?' +
    r'(\^(?P<removed>(\.[0-9]+(\+|-)?)*))?'+
    r'(/(?P<inversion>[a-z]+))?(/\+(?P<bass>[a-z]+))?'+
    r'$'
)

steps2ly_std_list = [
    ({1:0, 3:0, 5:0}, ""),
    ({1:0, 3:-1, 5:0}, ":m"),
    ({1:0, 3:0, 5:0, 7:0}, ":7"),
    ({1:0, 3:-1, 5:0, 7:0}, ":m7"),
    ({1:0, 3:0, 5:0, 7:1}, ":maj7"),
    ({1:0, 3:-1, 5:0, 7:1}, ":m7+"),
    ({1:0, 2:0, 5:0}, ":sus2"),
    ({1:0, 4:0, 5:0}, ":sus4"),
    ({1:0, 3:0, 5:0, 6:0}, ":6"),
    ({1:0, 3:-1, 5:-1}, ":dim"),
    ({1:0, 3:0, 5:1}, ":aug")
]
steps2ly_std = { frozenset(k.items()): v for k, v in steps2ly_std_list }


class NoteNameDecoder:
    @staticmethod
    def nederlands(s):
        name_regex = r'^([a-g])(is|isis|es|eses|ih|eh|isih|eseh)?$'
        m = re.match(name_regex, s)
        if m is None:
            raise ValueError("{} is not a valid note name".format(repr(s)))
        return s

def verify_duration(s):
    if s in [r'\longa', r'\breve']:
        return s

    m = re.match('(1|2|4|8|16|32|64|128)(\.*)', s)
    if m is None:
        raise ValueError("{} is not a valid duration".format(repr(s)))

    return s

class Chord:
    def __init__(self, obj, note_name_decoder=NoteNameDecoder.nederlands, default_duration=None):
        self.root = None
        self.duration = None
        self.inversion = None
        self.bass = None

        if isinstance(obj, str):
            obj = obj.strip()
            m = re.match(pause_regex, obj)
            if m is not None:
                self.root = 'r'
                if m.group('duration') is not None:
                    self.duration = verify_duration(m.group('duration'))
                else:
                    self.duration = default_duration
                return
                
            m = re.match(chord_regex, obj)
            if m is None:
                raise ValueError("Invalid chord name!")
    
            self.root = note_name_decoder(m.group('root'))

            octabs = len(m.group('octave'))
            if octabs > 0:
                self.octave = octabs * (-1 if m.group('octave')[0] == ',' else 1)
            else:
                self.octave = 0

            if m.group('duration') is not None:
                self.duration = verify_duration(m.group('duration'))
            else:
                self.duration = default_duration

            # TODO: parse modifier, added and removed...
            # create list of pitches in the chord, like: [1, 3, 5] for major, [1, 3-, 5] for minor
            # parsing modifiers should be simple: [added] \ [removed]
            modstr = m.group('modifiers')
            if modstr is not None:
                mm = re.findall(r'(?:[a-z]+)|(?:[0-9]+(?:\+|-)?)', modstr)
            else:
                mm = []
            
            # sus <n> zapisz w osobnym słowniku
            # weź liczby, która zostały oraz (dim|m|aug) oraz (maj)?
            # i utwórz akord - pierwsza liczba - dodaje tercjowe, pozostałe liczby - dodane dźwięki
            # dodaj sus'y
            step = None
            rest = []
            sus_mode = False
            for e in mm:
                if sus_mode:
                    rest.append(e)
                    sus_mode = False
                else:
                    if e == 'sus':
                        sus_mode = True
                        rest.append(e)
                    elif step is None and e[0].isdigit():
                        step = e
                    else:
                        rest.append(e)


            if step == None:
                step = '5'

            step_sign = ''
            if not step[-1].isdigit():
                step_sign = step[-1]
                step = step[:-1]

            step = int(step)

            steps = {k: 0 for k in range(1, min(11, step), 2)}
            steps[step] = {'': 0, '-': -1, '+': 1}[step_sign]

            def add_step(s):
                sign = ''
                if not s[-1].isdigit():
                    sign = s[-1]
                    s = s[:-1]
                steps[int(s)] = {'': 0, '-': -1, '+': 1}[sign]

            # apply modifiers
            sus_mode = False
            for e in rest:
                if sus_mode:
                    del steps[3]
                    add_step(e)
                    sus_mode = False
                else:
                    if e == 'sus':
                        sus_mode = True
                    elif e == 'm':
                        if 3 in steps:
                            add_step('3-')
                    elif e == 'dim':
                        if 3 in steps:
                            add_step('3-')
                        if 5 in steps:
                            add_step('5-')
                        if 7 in steps:
                            add_step('7-')
                    elif e == 'aug':
                        if 5 in steps:
                            add_step('5+')
                    elif e == 'maj':
                        add_step("7+")
                    else:
                        raise ValueError("Unknown chord modifier {}".format(e))

            if m.group('added') is not None:
                added = re.findall('\.([0-9]+(?:\+|-)?)', m.group('added'))
            else:
                added =[]

            for e in added:
                add_step(e)

            if m.group('removed') is not None:
                removed = re.findall('\.([0-9]+(?:\+|-)?)', m.group('removed'))
            else:
                removed = []

            for e in removed:
                if not e[-1].isdigit():
                    del steps[int(e[:-1])]
                else:
                    del steps[int(e)]


            self.steps = steps

            if m.group('inversion') is not None:
                self.inversion = note_name_decoder(m.group('inversion'))

            if m.group('bass') is not None:
                self.bass = note_name_decoder(m.group('bass'))
        else:
            raise TypeError("obj has invalid type")

    def __repr__(self):
        chord_string = self.root

        if self.duration is not None:
            chord_string += self.duration
        
        # parse steps to modifier
        if frozenset(self.steps.items()) in steps2ly_std:
            chord_string += steps2ly_std[frozenset(self.steps.items())]
        else:
            chord_string += ":1"
            for k, v in self.steps.items():
                if k == 1:
                    continue
                else:
                    chord_string += '.' + str(k) + {0: '', 1: '+', -1: '-'}[v]

        if self.inversion is not None:
            chord_string += '/' + self.inversion

        if self.bass is not None:
            chord_string += '/+' + self.bass
        
        return 'lilysong.chords.Chord({})'.format(repr(chord_string))