#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import time
import collections

sys.path.append('submodules/subotto')

from listener import Statistics
from data import Session, Team, Player, Match, PlayerMatch, Event, StatsPlayerMatch, Base, AdvantagePhase

SLEEP_TIME = 0.5


class DisplayEvent:
    
    def __init__(self, t, static, animation=None):
        self.id = None
        self.time = t
        
        self.static = static
        self.animation = animation
        

class OverlayLogic:
    
    def __init__(self, stats):
        self.stats = stats
        
        # self.game_events = collections.deque()
        self.last_change_events = dict()    # last change of player done by each team, if it was not displayed yet
        
        self.display_events = collections.deque()
        
        self.start_id = 0 # id of the first display_event in the list (if it exists)
        self.end_id = 0 # id of the last display_event in the list + 1
        
        self.next_animation_time = time.time() # time when the animation space should be empty
    
    
    def receive_game_event(self, game_event):
        # Receive a new game event (only a few of them are kept for animation)
        if game_event.type == Event.EV_TYPE_CHANGE:
            # self.game_events.append(game_event)
            self.last_change_events[game_event.team_id] = game_event
    
    def ack_display_events_received(self, id):
        # The overlay filter tells us he received all events until that id
        # As a consequence, we distroy all these events (they are useless now)
        while len(self.display_events) > 0 and self.display_events[0].id <= id:
            self.pop_display_event()
    
    def get_display_events(self, id):
        # The overlay filter asks all the events with id starting from the given id.
        # Ideally exactly one display event should be returned each time, but more then one
        # can be returned in case there is a loss of syncronization.
        self.update()
        
        diff = id - self.start_id
        if diff < 0:
            # There are no events to return
            return []
        else:
            return list(self.display_events)[diff:]
    
    
    
    def push_display_event(self, event):
        event.id = self.end_id
        self.display_events.append(event)
        self.end_id += 1
        print 'New display event (time ', event.time, ')'
        print event.static
        print event.animation
    
    def pop_display_event(self):
        assert self.display_events[0].id == self.start_id
        self.display_events.popleft()
        self.start_id += 1
    
    
    def update(self):
        # Add a display_event using game_events
        t = time.time()
        
        static = None
        animation = None
        
        
        if self.stats.data['status'] == 'before':
            # Set static data
            static = {
                'type': 'countdown',
                'time_to_begin': self.stats.data['time_to_begin'],
            }
        
        elif self.stats.data['status'] == 'running' or self.stats.data['status'] == 'advantage':
            # Set static data
            static = {
                'type': 'running',
                'elapsed_time': self.stats.data['elapsed_time'],
                'teams': [
                    {
                        'name': team['name'],
                        'score': team['score'],
                    } for team in self.stats.data['teams'].itervalues()
                ],
            }
            
            # Set animation data
            if time.time() >= self.next_animation_time:
                for (team_id, change_event) in self.last_change_events.iteritems():
                    if change_event is not None:
                        animation = {
                            'type': 'change',
                            'duration': 5.0,
                            'team': change_event.team.name,
                            'players': self.stats.data['teams'][change_event.team_id]['players'],
                        }
                        
                        self.next_animation_time = time.time() + 6.0
                        self.last_change_events[team_id] = None
                        break
                        
                
                
        
        elif self.stats.data['status'] == 'ended':
            # Set static data
            static = {
                'type': 'ended',
                'teams': [
                    {
                        'name': team['name'],
                        'score': team['score'],
                    } for team in self.stats.data['teams']
                ],
            }
        
        else:
            raise Exception("Unknown match status")
        
        
        display_event = DisplayEvent(t, static, animation)
        self.push_display_event(display_event)



def listen_match(match_id, old_matches_id):

    session = Session()

    match = session.query(Match).filter(Match.id == match_id).one()
    old_matches = session.query(Match).filter(Match.id.in_(old_matches_id)).all()
    players = session.query(Player).all()
    old_player_matches = session.query(PlayerMatch).filter(PlayerMatch.match_id.in_(old_matches_id)).all()
    old_events = session.query(Event).filter(Event.match_id.in_(old_matches_id)).order_by(Event.timestamp).all()
    old_stats_player_matches = session.query(StatsPlayerMatch).filter(StatsPlayerMatch.match_id.in_(old_matches_id)).all()
    
    stats = Statistics(match, old_matches, players, old_player_matches, old_events, old_stats_player_matches)
    last_event_id = 0
    last_player_match_id = 0
    last_timestamp = None
    
    overlay_logic = OverlayLogic(stats)
    last_display_event_id = 0

    try:
        while True:
            session.rollback()
            for player_match in session.query(PlayerMatch).filter(PlayerMatch.match == match).filter(PlayerMatch.id > last_player_match_id).order_by(PlayerMatch.id):
                stats.new_player_match(player_match)
                last_player_match_id = player_match.id
            for event in session.query(Event).filter(Event.match == match).filter(Event.id > last_event_id).order_by(Event.id):
                if last_timestamp is not None and event.timestamp <= last_timestamp:
                    print >> sys.stderr, "> Timestamp monotonicity error at %s!\n" % (event.timestamp)
                    #sys.exit(1)
                stats.new_event(event)
                overlay_logic.receive_game_event(event)
                last_timestamp = event.timestamp
                last_event_id = event.id
            
            # Generate data
            stats.generate_current_data()
            data = stats.data
            
            # FIXME
            display_events = overlay_logic.get_display_events(last_display_event_id)
            for e in display_events:
                overlay_logic.ack_display_events_received(e.id)

            time.sleep(SLEEP_TIME)

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    match_id = int(sys.argv[1])
    old_matches_id = [1, 2, 3, 4]
    listen_match(match_id, old_matches_id)




