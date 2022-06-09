
# [acosta:08/163@13:52] Created.

"""
Simple progressbar and "spinner" classes that can be used for console
applications to show progress. For usage examples see 'test_it()' below.
"""


import math, sys


# classes ================================================================{{{1

# Spinner ----------------------------------------------------------------{{{2
class Spinner:
    """Method 'write' will print out a "spinning" marker."""
    spinner = ('|', '/', '-', '\\')
    def __init__(self):
        self.idx = 0

    def __str__(self):
        self.idx = (self.idx + 1) % 4
        return self.spinner[self.idx]

    def write(self, s=sys.stdout):
        s.write('\b\b%s ' % (str(self)))
        s.flush()


# ProgressBar ------------------------------------------------------------{{{2
class ProgressBar:
    """print out a progress bar with percentage completed."""
    pbar = ('[', '=', '>', ' ', ']')
    def __init__(self, max, width=50):
        """'max' is the max number to be expected. 'width' is the width (in
        number of screen characters)."""
        self.quota = 0.0
        self.max = float(max)
        self.maxl = len(str(max))
        self.completed = 0
        self.uncompleted = width
        self.value = 0
        self.width = width

    def __call__(self, value):
        """Increase counter to 'value'."""
        self.value = value
        self.quota = value/self.max
        self.completed = int(math.ceil(self.quota * self.width))
        self.uncompleted = self.width - self.completed
        return self

    def __str__(self):
        """The progress bar as a string."""
        return ''.join(
            (
                ' 0 ',
                self.bar(),
                ' %3d%%' % self.percent(),
                ' (%0*d/%d)' % (self.maxl, self.value, self.max),
            ))

    def bar(self):
        """Just the bar, but no values and no percentage."""
        def _bar(x):
            if x > 1:
                return (x - 1) * self.pbar[1] + self.pbar[2]
            if x == 1:
                return self.pbar[2]
            return ''

        return ''.join(
            (
                self.pbar[0],
                _bar(self.completed),
                self.uncompleted * self.pbar[3],
                self.pbar[4],
            ))

    def percent(self):
        return int(self.quota * 100.0)

    def write(self, s=sys.stdout):
        """Print out progress bar to stream."""
        s.write("\r%s   " % str(self))
        s.flush()

    def final(self, s=sys.stdout):
        """Print out final progress bar to stream."""
        self(self.max)
        self.write(s)
        s.write('\n')
        s.flush()


# functions =============================================================={{{1

# test_it ----------------------------------------------------------------{{{2
def test_it():
    """Test method."""
    import time
    s = Spinner()
    max = 10000
    p = ProgressBar(max, 50)
    x = 1
    p(x).write()
    while x < max:
        if x % 100 == 0:
            s.write()
            time.sleep(0.1)
        if x % 1000 == 0:
            p(x).write()
        x += 1
    p(x).write()
    sys.stdout.write('\n')


# __main__ ==============================================================={{{1
if __name__ == '__main__':
    test_it()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
