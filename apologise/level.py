from math import pi, cos, sin
from random import random, randint

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
        # check for the trigger shapes
        for i, shape in enumerate(level.trigger_shapes):
            if shape in shapes:
                # can only have collided with the player
                level._triggers.append((level.triggers[i], shape))
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

class End:
    def __init__ (self, game, event_handler, text):
        self.game = game
        self.event_handler = event_handler
        self.text = text
        self.frame = conf.FRAME
        event_handler.add_key_handlers([
            (conf.KEYS_NEXT, lambda *args: self.game.quit_backend(), eh.MODE_ONDOWN)
        ])

    def update (self):
        pass

    def draw (self, screen):
        if self.dirty:
            screen.fill(conf.RANK_BG_COLOUR)
            # text
            size = conf.RANK_FONT_SIZE
            font = (conf.FONT, size, False)
            pad = conf.RANK_PADDING
            w, h = conf.RES
            args = [font, None, conf.RANK_FONT_COLOUR, None, w - 2 * pad, 1, False, conf.RANK_LINE_SPACING]
            spacing = conf.RANK_SPACING
            args[1] = self.text[0]
            sfc1, lines, br = self.game.img(args)
            args[1] = self.text[1]
            sfc2, lines, br = self.game.img(args)
            # blit
            dy = sfc1.get_height() + spacing
            y = (h - dy - sfc2.get_height()) / 2
            screen.blit(sfc1, ((w - sfc1.get_width()) / 2, y))
            screen.blit(sfc2, ((w - sfc2.get_width()) / 2, y + dy))
            self.dirty = False
            return True
        else:
            return False

class Level:
    def __init__ (self, game, event_handler, ID = 0):
        self.game = game
        self.event_handler = event_handler
        self.frame = conf.FRAME
        event_handler.add_key_handlers(
            [(conf.KEYS_MOVE[i], [(self.move, (i,))], eh.MODE_HELD) for i in xrange(3)] + [
            (conf.KEYS_JUMP, self.jump, eh.MODE_ONDOWN),
            (conf.KEYS_RESET, lambda *args: self.init(), eh.MODE_ONDOWN),
            (conf.KEYS_NEXT, self.skip_msg, eh.MODE_ONDOWN),
            (conf.KEYS_BACK, self.toggle_paused, eh.MODE_ONDOWN)
        ])
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
        self.total_kills = 0
        self.paused = False
        self.init()

    def init (self):
        # don't allow reset when paused or already won
        if self.paused or self.transition:
            return
        data = conf.LEVEL_DATA[self.ID]
        self.run_timer = 0
        self.kills = 0
        self.won = False
        self.particles = []
        # background
        self.bg = self.game.img('bg{0}.png'.format(self.ID))
        # player
        s = self.space
        if not hasattr(self, 'player'):
            self.player = Player(self, data['start'])
        # doors
        try:
            s.remove_static(self.exit_shape)
        except AttributeError:
            pass
        else:
            self.player.reset(data['start'])
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
            pass
        self.shapes = [((0, 0), (1000, 0)), ((1000, 0), (1000, 540)), ((0, 500), (1000, 500)), ((0, 0), (0, 500))]
        self.shapes += data['shapes']
        self.shapes_shapes = ss = []
        rm = []
        for pts in self.shapes:
            if pts[1] is False:
                rm.append(pts)
                pts = pts[0]
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
        for pts in rm:
            self.shapes.remove(pts)
        self.shape_colour = data['shape_colour']
        # messages
        msgs = data['msg']
        if msgs[0] is None:
            self.msgs = []
            self.msg = None
        else:
            self.msgs = list(msgs[:-1])
            self.msg = 0
        self.end_msg = msgs[-1]
        self.msg_colour = data['msg_colour']
        self.msg_arrow = self.game.img('arrow{0}.png'.format(data['msg_arrow']))
        # music
        try:
            music = data['music']
        except KeyError:
            self.game.music = []
            self.game.play_music()
        else:
            try:
                if music != self.music:
                    raise AttributeError()
            except AttributeError:
                self.music = music
                self.game.find_music(str(music))
                self.game.play_music()
        # triggers
        try:
            s.remove_static(*self.trigger_shapes)
        except AttributeError:
            pass
        trigger_data = data.get('triggers', [])
        self.triggers = ts = []
        self.trigger_shapes = tss = []
        for pts, cb in trigger_data:
            ts.append(cb)
            shape = pm.Poly(s.static_body, pts)
            shape.group = conf.SHAPE_GROUP
            shape.layers = conf.TRIGGER_LAYER
            shape.sensor = True
            s.add_static(shape)
            tss.append(shape)
        self._triggers = []

    def next_level (self):
        self.game.files = {}
        self.game.imgs = {}
        self.total_kills += self.kills
        self.ID += 1
        if self.ID < len(conf.LEVEL_DATA):
            self.init()
        elif self.ID == len(conf.LEVEL_DATA):
            self.end()

    def toggle_paused (self, *args):
        if self.paused:
            self.paused = False
            pg.mixer.music.set_volume(conf.MUSIC_VOLUME * .01)
            pg.mouse.set_visible(False)
        else:
            self.paused = True
            pg.mixer.music.set_volume(conf.PAUSED_MUSIC_VOLUME * .01)
            pg.mouse.set_visible(True)
            self.dirty = True

    def move (self, k, t, m, d):
        if not self.paused and not self.won and (self.msg is None or self.msg >= len(self.msgs) - 1):
            try:
                self.player.move(d)
            except AttributeError:
                # no player yet
                pass

    def jump (self, *args):
        if not self.paused and not self.won and (self.msg is None or self.msg >= len(self.msgs) - 1):
            try:
                self.player.jump()
            except AttributeError:
                # no player yet
                pass

    def kill_thing (self, s):
        self.game.play_snd('die')
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

    def spawn_particles (self, pos, *colours):
        # colours is a list of (colour, amount) tuples
        pos = list(pos)
        ptcls = []
        max_speed = conf.PARTICLE_SPEED
        life = conf.PARTICLE_LIFE
        max_size = conf.PARTICLE_SIZE
        for c, amount in colours:
            while amount > 0:
                size = randint(1, max_size)
                amount -= size
                angle = random() * 2 * pi
                speed = random() * max_speed
                v = [speed * cos(angle), speed * sin(angle)]
                t = randint(0, life)
                ptcls.append((c, pm.Vec2d(pos), pm.Vec2d(v), t, size))
        self.particles.append(ptcls)

    def skip_msg (self, *args):
        if self.msg is not None:
            if self.won and not self.transition:
                self.start_transition()
            elif self.msg < len(self.msgs) + 1:
                self.msg += 1

    def quit (self):
        self.game.quit_backend()

    def end (self):
        # display rank
        if self.total_kills <= conf.MIN_KILLS:
            rank = conf.GOOD_RANK
        elif self.total_kills < conf.MAX_KILLS:
            rank = conf.DEFAULT_RANK
        else:
            rank = conf.BAD_RANK
        self.game.start_backend(End, rank)
        self.total_kills = 0
        self.ID = 0
        self.init()

    def update (self):
        if self.paused:
            return
        # blocking messages/finished
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
        # triggers
        for cb, shape in self._triggers:
            cb(self)
            self.space.remove_static(shape)
            self.triggers.remove(cb)
            self.trigger_shapes.remove(shape)
        self._triggers = []
        # physics/entities
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
        # particles
        i = 0
        ptcls = self.particles
        while i < len(ptcls):
            if ptcls[i]:
                new = []
                for c, p, v, t, size in ptcls[i]:
                    p += v
                    t -= 1
                    if t > 0:
                        new.append((c, p, v, t, size))
                ptcls[i] = new
                i += 1
            else:
                ptcls.pop(i)

    def draw (self, screen):
        if self.paused and not self.dirty:
            return False
        if self.transition and self.transition != conf.TRANSITION_TIME - 1:
            screen.blit(self.transition_sfc, (0, 0))
            return True
        # background
        screen.blit(self.bg, (0, 0))
        # messages
        if self.msg is not None:
            if self.msg is True:
                texts = self.msgs + [self.end_msg]
                arrow = not self.transition
            else:
                texts = self.msgs[:self.msg + 1]
                arrow = self.msg < len(self.msgs) - 1
            size = conf.MSG_SIZE
            font = (conf.FONT, size, False)
            pad = conf.MSG_PADDING
            w, h = conf.RES
            line_spacing = conf.MSG_LINE_SPACING
            args = [font, None, self.msg_colour, None, w - 2 * pad, 0, False, line_spacing]
            y = pad
            spacing = conf.MSG_SPACING
            for text in texts:
                args[1] = text
                sfc, lines, br = self.game.img(args)
                screen.blit(sfc, (pad, y))
                dy = lines * size + (lines - 1) * line_spacing + spacing
                y += dy
            # arrow
            if arrow:
                o = (size - self.msg_arrow.get_height()) / 2
                screen.blit(self.msg_arrow, (br[0] + pad + conf.ARROW_PADDING, br[1] + y - dy + o))
        # entities
        for t in self.things:
            t.draw(screen)
        self.player.draw(screen)
        # particles
        for ptcls in self.particles:
            for c, p, v, t, size in ptcls:
                screen.fill(c, (ir(p[0]), ir(p[1]), size, size))
        # pause screen
        if self.paused:
            sfc = pg.Surface(conf.RES).convert_alpha()
            if self.ID < 3:
                c = (210, 210, 170)
                d = 220
            elif self.ID < 5:
                c = (160, 160, 110)
                d = 120
            else:
                c = (180, 180, 165)
                d = 200
            sfc.fill((0, 0, 0, d))
            screen.blit(sfc, (0, 0))
            # text
            if self.ID != 0:
                text = ('PAUSED', 'move: arrow keys, WASD\nreset: R')
                size = conf.RANK_FONT_SIZE
                font = (conf.FONT, size, False)
                pad = conf.RANK_PADDING
                w, h = conf.RES
                args = [font, None, c, None, w - 2 * pad, 1, False, conf.RANK_LINE_SPACING]
                spacing = conf.RANK_SPACING
                args[1] = text[0]
                sfc1, lines, br = self.game.img(args)
                args[1] = text[1]
                sfc2, lines, br = self.game.img(args)
                # blit
                dy = sfc1.get_height() + spacing
                y = (h - dy - sfc2.get_height()) / 2
                screen.blit(sfc1, ((w - sfc1.get_width()) / 2, y))
                screen.blit(sfc2, ((w - sfc2.get_width()) / 2, y + dy))
        if self.dirty:
            self.dirty = False
        return True
