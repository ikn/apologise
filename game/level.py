from math import pi

import pygame as pg
import pymunk as pm
from ext import evthandler as eh

import conf
from player import Player
from thing import Thing, DeadThing

ir = lambda x: int(round(x))

def col_cb (space, arbiter, level, is_sep):
    shapes = arbiter.shapes
    p = level.player
    if not is_sep:
        # check for the death shape
        d_s = p.death_shape
        i = None
        for j, s in enumerate(shapes):
            if s is d_s:
                i = j
                break
        if i is not None:
            level.kill_thing(shapes[not i])
            return False
        # check for the door shapes
        if level.exit_shape in shapes:
            # can only have collided with the player
            level.won = True
            return False
    # tell player and things if they're on the ground
    for i in (0, 1):
        s = shapes[i]
        other = shapes[not i]
        if s is not None and hasattr(s, 'owner'):
            # check the collision is in the right direction
            cs = arbiter.contacts
            do = False
            for c in cs:
                angle = ((1 if i else -1) * c.normal).get_angle()
                target = -pi / 2
                if abs(target - angle) <= conf.GROUND_ANGLE_THRESHOLD:
                    do = True
            if do:
                current = s.owner.on
                if is_sep:
                    try:
                        current.remove(other)
                    except KeyError:
                        pass
                else:
                    current.add(other)
    return True

class Level:
    def __init__ (self, game, event_handler, ID = 0):
        self.game = game
        self.event_handler = event_handler
        self.frame = conf.FRAME
        event_handler.add_key_handlers(
            [(conf.KEYS_MOVE[i], [(self.move, (i,))], eh.MODE_HELD) for i in xrange(4)] + [
            (conf.KEYS_JUMP, self.jump, eh.MODE_ONDOWN),
            (conf.KEYS_RESET, lambda *args: self.init(True), eh.MODE_ONDOWN),
            (conf.KEYS_NEXT, self.skip_msg, eh.MODE_ONDOWN)
        ])
        self.kills = 0
        self.transition = False
        # space
        self.space = s = pm.Space()
        begin_col_cb = lambda *args: col_cb(*args, is_sep = False)
        sep_col_cb = lambda *args: col_cb(*args, is_sep = True)
        s.add_collision_handler(0, 0, begin_col_cb, None, None, sep_col_cb, self)
        s.gravity = conf.GRAVITY
        s.damping = conf.DAMPING
        s.collision_bias = 0
        self.ID = ID
        self.init()

        self.pts = []
        def f (e, level):
            level.pts.append(e.pos)
            print level.pts
        event_handler.add_event_handlers({pg.MOUSEBUTTONDOWN: [(f, (self,))]})

    def init (self, reset_player = False):
        data = conf.LEVEL_DATA[self.ID]
        self.run_timer = 0
        self.won = False
        self.first = True
        s = self.space
        # messages
        try:
            s.remove_static(*self.msg_shapes)
        except AttributeError:
            pass
        msgs = data['msg']
        if msgs[0] is None:
            self.msgs = ()
            self.msg = None
        else:
            self.msgs = msgs[:-1]
            self.msg = 0
        self.end_msg = msgs[-1]
        # player
        if not hasattr(self, 'player'):
            self.player = Player(self, data['start'])
        # doors
        try:
            s.remove_static(self.exit_shape)
        except AttributeError:
            pass
        else:
            if reset_player:
                self.player.body.position = data['start']
            else:
                # move player to and through entrance
                a, b = self.exit
                offset = self.player.body.position - b
                a, b = data['entrance']
                if a[0] == b[0]:
                    offset[0] *= -1
                else:
                    offset[1] *= -1
                self.player.body.position = offset + b
        self.entrance = data['entrance']
        a, b = self.exit = data['exit']
        self.exit_shape = l = pm.Segment(s.static_body, a, b, conf.LINE_RADIUS)
        l.group = conf.SHAPE_GROUP
        l.layers = conf.DOOR_LAYER
        l.sensor = True
        s.add_static(l)
        # things
        try:
            for t in self.things:
                t.die()
        except AttributeError:
            pass
        self.things = []
        ts = self.things
        for p, d, ai in data['things']:
            t = Thing(self, p, d, ai)
            t.dead = False
            ts.append(t)
        # static shapes
        try:
            for shape in self.shapes_shapes:
                s.remove_static(shape)
        except AttributeError:
            self.shapes = [((0, 0), (1000, 0)), ((1000, 0), (1000, 540)), ((0, 500), (1000, 500)), ((0, 0), (0, 500))]
        self.shapes += data['shapes']
        self.shapes_shapes = ss = []
        for pts in self.shapes:
            if len(pts) == 2:
                p = pm.Segment(s.static_body, pts[0], pts[1], conf.LINE_RADIUS)
            else:
                p = pm.Poly(s.static_body, pts)
            p.friction = conf.SHAPE_FRICT
            p.elast = conf.SHAPE_ELAST
            p.group = conf.SHAPE_GROUP
            p.layers = conf.COLLISION_LAYER
            s.add_static(p)
            ss.append(p)

    def next_level (self):
        self.ID += 1
        if self.ID < len(conf.LEVEL_DATA):
            self.init()
        elif self.ID == len(conf.LEVEL_DATA):
            self.end()

    def move (self, k, t, m, d):
        try:
            self.player.move(d)
        except AttributeError:
            # no player yet
            pass

    def jump (self, k, t, m):
        try:
            self.player.jump()
        except AttributeError:
            # no player yet
            pass

    def kill_thing (self, s):
        self.kills += 1
        for t in self.things:
            if s is t.shape:
                t.dead = True
            elif isinstance(t, Thing):
                t.set_ai('run_away')
                self.run_timer = conf.RUN_TIME

    def start_transition (self):
        self.transition = conf.TRANSITION_TIME
        self.transition_sfc = pg.Surface(conf.RES).convert_alpha()
        self.transition_sfc.fill(conf.TRANSITION_COLOUR)

    def skip_msg (self, *args):
        if self.msg is not None:
            if self.won and not self.transition:
                self.start_transition()
            elif self.msg < len(self.msgs) + 1:
                self.msg += 1

    def quit (self):
        self.game.quit_backend()

    def end (self):
        self.quit()

    def update (self):
        if self.won:
            if self.transition:
                self.transition -= 1
                if self.transition == 0:
                    self.next_level()
                    del self.transition_sfc
            elif self.end_msg is None:
                self.start_transition()
            elif self.msg is not True:
                self.msg = True
            return
        elif self.msg is not None and self.msg < len(self.msgs) - 1:
            return
        if self.first:
            self.msg_shapes = []
            for sfc, pos in self.get_msg_data():
                r = sfc.get_bounding_rect().move(pos)
                pts = (r.topleft, r.topright, r.bottomright, r.bottomleft)
                shape = pm.Poly(self.space.static_body, pts)
                self.space.add_static(shape)
                self.msg_shapes.append(shape)
            self.first = False
        self.space.step(conf.STEP)
        self.player.update()
        rm = []
        ts = self.things
        stop = False
        if self.run_timer:
            self.run_timer -= 1
            if self.run_timer == 0:
                stop = True
        for t in ts:
            if t.dead:
                rm.append(t)
            else:
                if stop and isinstance(t, Thing):
                    t.set_ai()
                t.update()
        for t in rm:
            t.die()
            ts.remove(t)
            dt = DeadThing(self, t.body.position + conf.DEAD_THING_POS_OFFSET)
            dt.dead = False
            ts.append(dt)

    def get_msg_data (self):
        if self.msg is None:
            return []
        if self.msg is True:
            texts = self.msgs + (self.end_msg,)
        else:
            texts = self.msgs[:self.msg + 1]
        size = conf.MSG_SIZE
        font = (conf.FONT, size, False)
        pad = conf.MSG_PADDING
        w, h = conf.RES
        line_spacing = conf.MSG_LINE_SPACING
        args = [font, None, conf.MSG_COLOUR, None, w - 2 * pad, 0, False, line_spacing]
        y = pad
        spacing = conf.MSG_SPACING
        data = []
        for text in texts:
            args[1] = text
            sfc, lines = self.game.img(args)
            data.append((sfc, (pad, y)))
            y += lines * size + (lines - 1) * line_spacing + spacing
        return data

    def draw (self, screen):
        if self.transition:
            screen.blit(self.transition_sfc, (0, 0))
            return True
        # background
        screen.fill((255, 255, 255))
        # shapes
        for pts in self.shapes:
            if len(pts) == 2:
                pg.draw.line(screen, (0, 0, 0), pts[0], pts[1], conf.LINE_RADIUS * 4)
            else:
                pg.draw.polygon(screen, (0, 0, 0), pts)
        # doors
        for c, (a, b) in (((0, 0, 255), self.entrance), ((255, 0, 0), self.exit)):
            pg.draw.line(screen, c, a, b, conf.LINE_RADIUS * 4)
        # messages
        data = self.get_msg_data()
        for sfc, pos in data:
            screen.blit(sfc, pos)
        # entities
        self.player.draw(screen)
        for t in self.things:
            t.draw(screen)
        return True