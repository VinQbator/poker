# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from poker.constants import *


def test_first_values_are_represeantional():
    # other words: printed to the user
    assert str(PokerRoom.STARS) == 'PokerStars'
    assert str(PokerRoom.FTP) == 'Full Tilt Poker'
    assert str(PokerRoom.PKR) == 'PKR'

def test_values():
    assert PokerRoom.STARS.val == 'PokerStars'
    assert PokerRoom.FTP.val == 'Full Tilt Poker'
    assert PokerRoom.PKR.val == 'PKR'