# -*- coding: utf-8 -*-
"""
:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
from gramola.datasources.graphite import GraphiteDataSource
from gramola.datasources.cloudwatch import CWDataSource

IMPLEMENTATIONS = [
    GraphiteDataSource,
    CWDataSource
]
