from unittest import TestCase
from lilysong.chords import Chord


class TestChords(TestCase):
    def check_steps(self, s, steps):
        c = Chord(s)
        self.assertDictEqual(c.steps, steps)

    def test_chords_parsing_steps(self):
        self.check_steps("c", {1:0, 3:0, 5:0})
        self.check_steps("c:m", {1:0, 3:-1, 5:0})
        self.check_steps("c:7", {1:0, 3:0, 5:0, 7:0})
        self.check_steps("c:m7", {1:0, 3:-1, 5:0, 7:0})
        self.check_steps("c:m7+", {1:0, 3:-1, 5:0, 7:1})
        self.check_steps("c:maj7", {1:0, 3:0, 5:0, 7:1})

        self.check_steps("c:sus2", {1:0, 2:0, 5:0})
        self.check_steps("c:sus4", {1:0, 4:0, 5:0})

        self.check_steps("c:6", {1:0, 3:0, 5:0, 6:0})
        self.check_steps("c:m6", {1:0, 3:-1, 5:0, 6:0})
        self.check_steps("c:6^.5", {1:0, 3:0, 6:0})

        self.check_steps("c:aug", {1:0, 3:0, 5:1})
        self.check_steps("c:dim", {1:0, 3:-1, 5:-1})

        self.check_steps("c:dim7", {1:0, 3:-1, 5:-1, 7:-1})
        self.check_steps("c:aug7", {1:0, 3:0, 5:1, 7:0})
        self.check_steps("c:m7.5-", {1:0, 3:-1, 5:-1, 7:0})

        self.check_steps("c:9", {1:0, 3:0, 5:0, 7:0, 9:0})
        self.check_steps("c:maj9", {1:0, 3:0, 5:0, 7:1, 9:0})
        self.check_steps("c:m9", {1:0, 3:-1, 5:0, 7:0, 9:0})

        self.check_steps("c:11", {1:0, 3:0, 5:0, 7:0, 9:0, 11:0})
        self.check_steps("c:maj11", {1:0, 3:0, 5:0, 7:1, 9:0, 11:0})
        self.check_steps("c:m11", {1:0, 3:-1, 5:0, 7:0, 9:0, 11:0})

        self.check_steps("c:13", {1:0, 3:0, 5:0, 7:0, 9:0, 13:0})
        self.check_steps("c:13.11", {1:0, 3:0, 5:0, 7:0, 9:0, 11:0, 13:0})
        self.check_steps("c:maj13.11", {1:0, 3:0, 5:0, 7:1, 9:0, 11:0, 13:0})
        self.check_steps("c:m13.11", {1:0, 3:-1, 5:0, 7:0, 9:0, 11:0, 13:0})

        self.check_steps("c:1.5", {1:0, 5:0})
        self.check_steps("c:1.5.8", {1:0, 5:0, 8:0})
        