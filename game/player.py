import pygame as pg
import pymunk as pm

import conf

ir = lambda x: int(round(x))

class Player:
    def __init__ (self, level, p):
        self.level = level
        self.mass = conf.PLAYER_MASS
        pts = conf.PLAYER_PTS
        self.body = b = pm.Body(self.mass, pm.inf) #pm.moment_for_poly(self.mass, pts)
        b.position = tuple(p)
        s = self.shape = pm.Poly(b, pts)
        s.owner = self
        s.elasticity = conf.PLAYER_ELAST
        s.friction = conf.PLAYER_FRICT
        s.layers = conf.COLLISION_LAYER | conf.DOOR_LAYER | conf.TRIGGER_LAYER
        level.space.add(b, s)
        # sensor for death radius
        s = self.death_shape = pm.Circle(b, conf.DEATH_RADIUS)
        s.sensor = True
        s.layers = conf.DEATH_LAYER
        level.space.add(s)

        self._move = set()
        self.jumping = False
        self.on = set()
        self.dirty = True

    def jump (self):
        if self.on:
            self.body.apply_impulse((0, -conf.PLAYER_INITIAL_JUMP_FORCE))
            self.jumping = conf.PLAYER_JUMP_TIME

    def move (self, d):
        self._move.add(d)

    def update (self):
        b = self.body
        self.pos = b.position
        # move
        f = pm.Vec2d((0, 0))
        move = self._move
        for d in move:
            if d in (0, 2):
                f[d % 2] += 1 if d > 1 else -1
        b.apply_impulse(f * conf.PLAYER_ACCEL)
        # jump
        if 1 in move and self.jumping:
            b.apply_impulse((0, -conf.PLAYER_JUMP_FORCE))
            self.jumping -= 1
        elif self.jumping:
            self.jumping = False
        self._move = set()

    def draw (self, screen):
        pg.draw.polygon(screen, (0, 0, 0), self.shape.get_points())
        p = [ir(x) for x in self.body.position]
        pg.draw.circle(screen, (0, 0, 0), p, conf.DEATH_RADIUS, 1)
        self.dirty = False