# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

import re
from decimal import Decimal
import pytz
from zope.interface import implementer
from .. import handhistory as hh
from ..hand import Combo, Card
from ..constants import Limit, Game, GameType, MoneyType, Currency, Action


__all__ = ['PKRHandHistory']


@implementer(hh.IStreet)
class _Street(hh._BaseStreet):
    def _parse_cards(self, boardline):
        self.cards = (Card(boardline[6:9:2]), Card(boardline[11:14:2]), Card(boardline[16:19:2]))

    def _parse_actions(self, actionlines):
        actions = []
        for line in actionlines:
            if line.startswith('Pot sizes:'):
                self._parse_pot(line)
            elif 'did not respond in time' in line:
                continue
            elif ' ' in line:
                actions.append(hh._PlayerAction(*self._parse_player_action(line)))
            else:
                raise
        self.actions = tuple(actions) if actions else None

    def _parse_pot(self, line):
        amount_start_index = 12
        amount = line[amount_start_index:]
        self.pot = Decimal(amount)

    def _parse_player_action(self, line):
        space_index = line.find(' ')
        name = line[:space_index]
        end_action_index = line.find(' ', space_index + 1)
        # -1 means not found
        if end_action_index == -1:
            end_action_index = None  # until the end
        action = Action(line[space_index + 1:end_action_index])
        if end_action_index:
            amount_start_index = line.find('$') + 1
            amount = line[amount_start_index:]
            return name, action, Decimal(amount)
        else:
            return name, action, None


@implementer(hh.IHandHistory)
class PKRHandHistory(hh._SplittableHandHistoryMixin, hh._BaseHandHistory):
    """Parses PKR hand histories."""

    currency = Currency.USD
    tournament_ident = None
    tournament_name = None
    tournament_level = None

    _DATE_FORMAT = '%d %b %Y %H:%M:%S'
    _TZ = pytz.UTC
    _SPLIT_CARD_SPACE = slice(0, 3, 2)
    _STREET_SECTIONS = {'flop': 3, 'turn': 4, 'river': 5}
    _split_re = re.compile(r"Dealing Cards\n|Dealing |Moving |([^\n]*doesn't show|[^\n]*shows[^\n]*)\n|\n")#(r'Dealing Cards\n|Dealing |Taking |Moving |\n')#(r"Dealing |\nDealing Cards\n|Taking |Moving |\n")
    _blinds_re = re.compile(r"^Blinds are now \$([\d.]*) / \$([\d.]*)$")
    _hero_re = re.compile(r"^\[(. .)\]\[(. .)\] to (?P<hero_name>.*)$")
    _seat_re = re.compile(r"^Seat (\d\d?): (.*) - \$([\d.]*) ?(.*)$")
    _sizes_re = re.compile(r"^Pot sizes: \$([\d.]*)$")
    _card_re = re.compile(r"\[(. .)\]")
    _rake_re = re.compile(r"Taking Rake of \$([\d.]*) from pot \d$")
    _win_re = re.compile(r"^(.*) wins \$([\d.]*)")

    def parse_header(self):
        # sections[1] is after blinds, before preflop
        # section[2] is before flop
        # sections[-1] is before showdown
        self._split_raw()

        self.table_name = self._splitted[0][6:]          # cut off "Table "
        self.ident = self._splitted[1][15:]              # cut off "Starting Hand #"
        self._parse_date(self._splitted[2][20:])         # cut off "Start time of hand: "
        self.game = Game(self._splitted[4][11:])        # cut off "Game Type: "
        self.limit = Limit(self._splitted[5][12:])      # cut off "Limit Type: "
        self.game_type = GameType(self._splitted[6][12:])   # cut off "Table Type: "

        match = self._blinds_re.match(self._splitted[8])
        self.sb = Decimal(match.group(1))
        self.bb = Decimal(match.group(2))
        self.buyin = self.bb * 100

    def parse(self):
        """Parses the body of the hand history, but first parse header if not yet parsed."""
        if not self.header_parsed:
            self.parse_header()

        self._parse_players()
        self._parse_button()
        self._parse_hero()
        self._parse_preflop()
        self._parse_flop()
        self._parse_street('turn')
        self._parse_street('river')
        self._parse_showdown()
        self._parse_extra()

        self._del_split_vars()
        self.parsed = True

    def _parse_players(self):
        # In hh there is no indication of max_players,
        # so init for 10, as there are 10 player tables on PKR.
        players = self._init_seats(10)
        for line in self._splitted[10:]:
            match = self._seat_re.match(line)
            if not match:
                break
            seat_number = int(match.group(1))
            players[seat_number - 1] = hh._Player(
                name=match.group(2), stack=Decimal(match.group(3)), seat=seat_number, combo=None
            )
        self.max_players = seat_number
        self.players = players[:self.max_players]

    def _parse_button(self):
        button_row = self._splitted[self._sections[0] + 1]

        # cut last two because there can be 10 seats also
        # in case of one digit, the first char will be a space
        # but int() can convert it without hiccups :)
        button_seat = int(button_row[-2:])
        self.button = self.players[button_seat - 1]

    def _parse_hero(self):
        try:
            if len(self._sections) < 3:
                self.hero = None
                return
            dealt_row = self._splitted[self._sections[2] + 1]
            match = self._hero_re.match(dealt_row)
            if match is None:
                self.hero = None
                return
            first = match.group(1)[self._SPLIT_CARD_SPACE]
            second = match.group(2)[self._SPLIT_CARD_SPACE]
            hero, hero_index = self._get_hero_from_players(match.group('hero_name'))
            hero.combo = Combo(first + second)
            self.hero = self.players[hero_index] = hero
            if self.button.name == self.hero.name:
                self.button = self.hero
        except Exception as e:
            print('\nParsing hero failed:\nsections: %s\nsplitted: %s\nplayers: %s' % (self._sections, self._splitted, self.players))
            raise e

    def _parse_preflop(self):
        start_section = 2 if self.hero else 1
        start = self._sections[start_section] + 2
        #start = self._sections[2] + 2
        #print(start)
        if len(self._sections) < start_section + 2:
            stop = -1
        else:
            stop = self._sections[start_section + 1] - 1
        #stop = self._splitted.index('', start + 1) - 1
        self.preflop_actions = tuple(self._splitted[start:stop])

    def _parse_flop(self):
        section = self._STREET_SECTIONS['flop']
        if not self.hero: section -= 1
        if len(self._sections) > section + 2:
            start = self._sections[section]
            #start = self._sections[flop_section] + 1
            #stop = next(v for v in self._sections if v > start)
            from_start = self._splitted[start + 1:]
            stop = from_start.index(next((v for v in from_start if 'Pot sizes:' in v), None))
            actions = from_start[:stop+1]
            #stop = self._splitted.index('', start)
            #floplines = self._splitted[start:stop]
            print(actions)
            self.flop = _Street(actions)
        else:
            self.flop = None
            return
        # # try:
        # #     start = self._splitted.index(next((v for v in self._splitted if 'Flop' in v), None))
        # # except ValueError:
        # # flop_section = self._STREET_SECTIONS['flop']
        # # if not self.hero: flop_section -= 1
        # #start = self._sections[flop_section] + 1
        # #stop = next(v for v in self._sections if v > start)
        # from_start = self._splitted[start + 1:]
        # stop = from_start.index(next((v for v in from_start if 'Pot sizes:' in v), None))
        # actions = from_start[:stop]
        # #stop = self._splitted.index('', start)
        # #floplines = self._splitted[start:stop]
        # self.flop = _Street(actions)

    def _parse_street(self, street):
        section = self._STREET_SECTIONS[street]
        if not self.hero: section -= 1
        if len(self._sections) > section + 1:
            try:
                start = self._sections[section] + 1
                street_line = self._splitted[start]
                cards = list(map(lambda x: x[self._SPLIT_CARD_SPACE], self._card_re.findall(street_line)))
                setattr(self, street, Card(cards[0]))
                from_start = self._splitted[start + 1:]
                stop = from_start.index(next((v for v in from_start if 'Pot sizes:' in v), None))
                actions = from_start[:stop+1]
                setattr(self, "{}_actions".format(street), tuple(actions))
                sizes_line = self._splitted[start - 2]
                pot = Decimal(self._sizes_re.match(sizes_line).group(1))
                setattr(self, "{}_pot".format(street), pot)
            except Exception as e:
                print('Failed parsing %s:\npotline: %s\nactions: %s\nsplitted: %s' % (street, sizes_line, actions, self._splitted))
                raise e
        else:
            setattr(self, street, None)
            setattr(self, "{}_actions".format(street), None)
            setattr(self, "{}_pot".format(street), None)

    def _parse_showdown(self):
        start = self._sections[-1] - 1

        winners = []
        self.total_pot = 0
        if not self.flop is None:
            rake_line = self._splitted[start]
            print('Rake line: %s' % rake_line)
            match = self._rake_re.match(rake_line)
            self.rake = Decimal(match.group(1))
        else:
            self.rake = Decimal(0)
        self.total_pot += self.rake

        for line in self._splitted[start+1:]:
            #print(line)
            if 'shows' in line:
                #print('shows: %s' % line)
                self.show_down = True
            elif 'doesn\'t show' in line:
                #print('doesn\'t show: %s' % line)
                self.show_down = False
            elif 'wins' in line:
                try:
                    match = self._win_re.match(line)
                    winners.append(match.group(1))
                    self.total_pot += Decimal(match.group(2))
                except:
                    print('Failed parsing winner: %s' % line)

        self.winners = tuple(winners)


    def _parse_extra(self):
        self.extra = dict()
        self.extra['last_ident'] = self._splitted[3][11:]             # cut off "Last Hand #"
        self.extra['money_type'] = MoneyType(self._splitted[7][12:])  # cut off "Money Type: "
