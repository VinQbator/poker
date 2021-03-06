# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from ._common import PokerEnum


class PokerRoom(PokerEnum):
    STARS = 'PokerStars', 'STARS', 'PS'
    FTP = 'Full Tilt Poker', 'FTP', 'FULL TILT'
    PKR = 'PKR', 'PKR POKER'
    EIGHT = '888', '888poker'


class Currency(PokerEnum):
    USD = 'USD', '$'
    EUR = 'EUR', '€'
    GBP = 'GBP', '£'
    STARS_COIN = 'SC', 'StarsCoin'


class GameType(PokerEnum):
    TOUR = 'Tournament', 'TOUR'
    CASH = 'Cash game', 'CASH', 'RING'
    SNG = 'Sit & Go', 'SNG', 'SIT AND GO', 'Sit&go'


class Game(PokerEnum):
    HOLDEM = "Hold'em", 'HOLDEM', "HOLD'EM"
    OMAHA = 'Omaha', 'OMAHA'
    OHILO = 'Omaha Hi/Lo',
    RAZZ = 'Razz',
    STUD = 'Stud',
    OMAHA5 = '5 Card Omaha',
    BADUGI = 'Badugi',
    TD27LB = 'Triple Draw 2-7 Lowball'


class Limit(PokerEnum):
    NL = 'NL', 'No limit', 'No Limit', 'NO LIMIT'
    PL = 'PL', 'Pot limit', 'Pot Limit', 'POT LIMIT'
    FL = 'FL', 'Fixed limit', 'Limit', 'Fixed Limit', 'FIXED LIMIT', 'LIMIT'


class TourFormat(PokerEnum):
    ONEREB = '1R1A',
    REBUY = 'Rebuy', '+R'
    SECOND = '2x Chance',  # Second chance tournament, can rebuy twice
    ACTION = 'Action Hour',
    # '2nd Chance' is a regular tournament on sunday evening,
    # after Sunday million (name), NOT a tournament format


class TourSpeed(PokerEnum):
    SLOW = 'Slow',
    REGULAR = 'Regular',
    TURBO = 'Turbo',
    HYPER = 'Hyper-Turbo',
    DOUBLE = '2x-Turbo',


class MoneyType(PokerEnum):
    REAL = 'Real money', 'REAL MONEY'
    PLAY = 'Play money', 'PLAY MONEY'


class Action(PokerEnum):
    BET = 'bet', 'bets'
    RAISE = 'raise', 'raises',
    CHECK = 'check', 'checks'
    FOLD = 'fold', 'folded', 'folds'
    CALL = 'call', 'calls'
    RETURN = 'return', 'returned', 'uncalled'
    WIN = 'win', 'won', 'collected'
    SHOW = 'show',
    MUCK = "don't show", "didn't show", 'did not show', 'mucks'
    THINK = 'seconds left to act',


class Position(PokerEnum):
    __order__ = 'UTG UTG1 UTG2 UTG3 UTG4 HJ CO BTN SB BB'

    UTG = 'UTG', 'under the gun'
    UTG1 = 'UTG1', 'utg+1', 'utg + 1'
    UTG2 = 'UTG2', 'utg+2', 'utg + 2'
    UTG3 = 'UTG3', 'utg+3', 'utg + 3'
    UTG4 = 'UTG4', 'utg+4', 'utg + 4'
    HJ = 'HJ', 'hijack', 'utg+5', 'utg + 5'
    CO = 'CO', 'cutoff', 'cut off'
    BTN = 'BTN', 'bu', 'button'
    SB = 'SB', 'small blind'
    BB = 'BB', 'big blind'


class StreetName(PokerEnum):
    PREFLOP = 'PREFLOP'
    FLOP = 'FLOP'
    TURN = 'TURN'
    RIVER = 'RIVER'