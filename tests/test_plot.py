import pytest
import time

from StringIO import StringIO
from mock import patch, Mock

from gramola.plot import Plot


DEFAULT_ROWS_FIXTURE = [
# values given to the Plot to get the graph below
[(10, 1), (20, 1), (30, 1), (40, 1), (50, 1),
 (60, 1), (70, 1), (80, 1), (90, 1), (100, 1)],
# grap expected
"""|         *
|        **
|       ***
|     *****
|    ******
|   *******
|  ********
| *********
+---+---+--
min=10, max=100, last=100
"""
]


FIVE_ROWS_FIXTURE = [
# values given to the Plot to get the graph below
[(10, 1), (20, 1), (30, 1), (40, 1), (50, 1),
 (60, 1), (70, 1), (80, 1), (90, 1), (100, 1)],
# grap expected
"""|        **
|      ****
|     *****
|   *******
| *********
+---+---+--
min=10, max=100, last=100
"""
]

MAXX_ROWS_FIXTURE = [
# values given to the Plot to get the graph below
[(10, 1), (50, 1), (10, 1), (10, 1)], 
# grap expected
"""|          
|          
|          
|          
|       *  
|       *  
|       *  
|       *  
+---+---+--
min=0, max=50, last=10
"""
]


@patch("gramola.plot.sys")
@patch.object(Plot, "width", return_value=10)
class TestPlotDrawing(object):
    def test_draw_default_rows(self, width_patched, sys_patched):
        sys_patched.stdout = StringIO()
        plot = Plot()
        plot.draw(DEFAULT_ROWS_FIXTURE[0])
        sys_patched.stdout.seek(0)
        output = sys_patched.stdout.read()
        assert output == DEFAULT_ROWS_FIXTURE[1]

    def test_draw_five_rows(self, width_patched, sys_patched):
        width_patched.return_value = 10
        sys_patched.stdout = StringIO()
        plot = Plot(rows=5)
        plot.draw(FIVE_ROWS_FIXTURE[0])
        sys_patched.stdout.seek(0)
        output = sys_patched.stdout.read()
        assert output == FIVE_ROWS_FIXTURE[1]

    def test_draw_maxx(self, width_patched, sys_patched):
        width_patched.return_value = 10
        sys_patched.stdout = StringIO()
        plot = Plot(max_x=100)
        plot.draw(MAXX_ROWS_FIXTURE[0])
        sys_patched.stdout.seek(0)
        output = sys_patched.stdout.read()
        assert sys_patched.stdout.read() == MAXX_ROWS_FIXTURE[1]
