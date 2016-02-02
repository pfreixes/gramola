# -*- coding: utf-8 -*-
"""
Implements the ploting module to render the graphic over the console using a graphic
like the following one:

+                *                   *
+                **                  **
+           *    ***                 **
+          ***   ****                ***
+ *       ****   *****          **   ****
+ **    ******   *******       ****  *****
+***   ********************   *****  ******
+*******************************************
+-------------------------------------------
min=1, max=34, last=2

The plot is rendred using 10 rows, it means that all datapoints that have to be displayed
will be scaled until they fit between the range [0, 10]. By default the Plot uses the
max value picked up from the list of datapoints and finds out wich is the fewer number
that divides it getting at max the value 10, for example:

    datapoints = 10, 22, 35, 66, 14, 8
    max = 66
    Fewer division that gets less than 10,  66 / 7 = 9.4

    datapoints displayed = 2, 4, 6, 10, 3, 2

The user can also set a maxium value that will be used to get the divission value, for
example if the user is tracking the CPU usage the maxium value that it will get is 100. Using
this 100 the division number turns out 10, so the above datapoints will get the following
values:

    datapoints displayed = 1, 3, 4, 7, 2, 1

:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import os
import sys

from itertools import dropwhile

DEFAULT_ROWS = 10


class Plot(object):

    def __init__(self, max_x=None, rows=DEFAULT_ROWS):
        self.rows = rows
        self.max_x = max_x
        self.__drawn = False

    def width(self):
        width, _ = getTerminalSize()
        return width

    def draw(self, datapoints):
        """ Render using the the datapoints given as a parameters, Gramola
        subministres a list of tuples (value,ts).
        """
        if len(datapoints) > self.width():
            raise Exception("Given to many datapoints {}, doesnt fit into screen of {}".format(len(datapoints), self.width()))

        if self.__drawn:
            # remove the two lines used to render the plot by the
            # the previous call to refresh the plot using the
            # same console space
            for i in range(0, self.rows+1):
                sys.stdout.write("\033[K")   # remove line
                sys.stdout.write("\033[1A")  # up the cursor

        # FIXME: nowadays Gramola supports only integer values
        values = [int(value) for value, ts in datapoints or [0]]

        # find the right division value
        max_x = self.max_x or max(values)
        divide_by = next(dropwhile(lambda i: max_x / i > self.rows, range(1, max_x)))

        for row in range(self.rows, 0, -1):
            for v in values:
                if v / divide_by >= row:
                    sys.stdout.write("*")
                else:
                    sys.stdout.write(" ")
            sys.stdout.write("\n")
        sys.stdout.write("-"*self.width() + "\n")
        sys.stdout.write("min={}, max={}, last={}".format(min(values), max(values), values[-1]))
        sys.stdout.flush()
        self.__drawn = True


# Code get from the console module
def getTerminalSize():
    env = os.environ
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct, os
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (env.get('LINES', 25), env.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])
