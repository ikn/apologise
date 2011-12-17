import pygame as pg
import pymunk as pm

import conf

class Thing:
    def __init__ (self, level, p, d, ai):
        self.level = level
        self.mass = conf.THING_MASS
        pts = conf.THING_PTS
        self.body = b = pm.Body(self.mass, pm.inf) #pm.moment_for_poly(self.mass, pts))
        b.position = tuple(p)
        s = self.shape = pm.Poly(b, pts)
        s.owner = self
        s.elasticity = conf.THING_ELAST
        s.friction = conf.THING_FRICT
        s.layers = conf.COLLISION_LAYER | conf.DEATH_LAYER
        level.space.add(b, s)

        self.dirn = d
        self.jumping = False
        self.on = set()
        self.first = True
        self.default_ai = ai
        self.set_ai()
        self.dirty = True

    def set_ai (self, s = None):
        if s is None:
            s = self.default_ai
        self.ai = s
        self.ai_data = dict(conf.AI_DATA[s])

    def move (self, d):
        if self.ai in ('walk', 'run_away'):
            data = self.ai_data
            accel = data['accel']
            if self.ai == 'run_away':
                # go faster when near player
                speed_prox = data['speedup_prox']
                r = conf.DEATH_RADIUS
                dist = data.get('prox', r + speed_prox)
                if dist < r + speed_prox:
                    accel /= max((dist - r) / speed_prox, data['max_speedup'])
            f = [0, 0]
            f[d % 2] += (1 if d > 1 else -1) * accel
            self.body.apply_impulse(f)

    def die (self):
        self.level.space.remove(self.body, self.shape)

    def jump (self):
        if self.on:
            self.level.game.play_snd('jump')
            self.body.apply_impulse((0, -conf.PLAYER_INITIAL_JUMP_FORCE))
            self.jumping = conf.PLAYER_JUMP_TIME
            return True
        else:
            return False

    def update (self):
        # AI
        ai = self.ai
        data = self.ai_data
        if ai in ('walk', 'run_away'):
            turned = False
            # turn on hitting something
            v = self.body.velocity
            if self.jumping:
                self.body.apply_impulse((0, -conf.PLAYER_JUMP_FORCE))
                self.jumping -= 1
                if self.jumping == 0:
                    data['not_moving'] = True
            elif v[0] * self.dirn < 0 or abs(v[0]) <= conf.THING_TURN_THRESHOLD_VEL:
                if data['not_moving']:
                    data['not_moving'] = False
                    self.dirn *= -1
                    turned = True
                else:
                    if not self.first:
                        if not self.jump():
                            self.dirn *= -1
                            turned = True
        if ai == 'run_away' and not turned:
            # run from player
            p_p = self.level.player.pos
            p = self.body.position
            d = p_p.get_distance(p)
            data['prox'] = d
            r = conf.DEATH_RADIUS
            if d < r + data['turn_prox']:
                data['not_moving'] = False
                self.dirn = 1 if p_p[0] < p[0] else -1
        # move
        self.move(self.dirn + 1)
        if self.first:
            self.first = False

    def draw (self, screen):
        pg.draw.polygon(screen, (0, 0, 0), self.shape.get_points())
        self.dirty = False

class DeadThing:
    def __init__ (self, level, p):
        self.level = level
        self.body = b = pm.Body(conf.THING_MASS, pm.inf) #pm.moment_for_poly(self.mass, pts))
        b.position = tuple(p)
        pts = conf.DEAD_THING_PTS
        s = self.shape = pm.Poly(b, pts)
        s.owner = self
        s.elasticity = conf.THING_ELAST
        s.friction = conf.THING_FRICT
        s.layers = conf.COLLISION_LAYER
        level.space.add(b, s)

        self.moving = True
        self.on = set()
        self.dirty = True

    def die (self):
        if self.moving:
            self.level.space.remove(self.body, self.shape)
        else:
            self.level.space.remove_static(self.shape)

    def update (self):
        if self.moving and self.on:
            self.die()
            self.moving = False
            p = self.body.position
            self.body = b = pm.Body(None, None)
            b.position = p
            pts = conf.DEAD_THING_PTS
            s = self.shape = pm.Poly(b, pts)
            s.owner = self
            s.elasticity = conf.THING_ELAST
            s.friction = conf.THING_FRICT
            s.layers = conf.COLLISION_LAYER
            self.level.space.add_static(s)

    def draw (self, screen):
        pg.draw.polygon(screen, (0, 0, 0), self.shape.get_points())
        self.dirty = False