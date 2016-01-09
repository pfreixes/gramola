# -*- coding: utf-8 -*-
"""
:moduleauthor: Pau Freixes, pfreixes@gmail.com
"""
import logging

_logger = logging.getLogger('gramola')
warning = _logger.warn
info = _logger.info
debug = _logger.debug
error = _logger.error

def setup(verbose=False, quite=False):
    if quite:
        _logger.addHandler(logging.NullHandler())
    else:
        _logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        logging.basicConfig(format='%(message)s')
