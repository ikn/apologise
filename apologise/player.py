from random import random

import pygame as pg
import pymunk as pm

import conf

ir = lambda x: int(round(x))

class Player:
    def __init__ (self, level, p):
        self.level = level
        self.mass = conf.PLAYER_MASS
        pts = conf.PLAYER_PTS
        self.body = b = pm.Body(self.mass, pm.inf)
        self.pos = b.position = tuple(p)
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

        # images
        f = self.level.game.img
        self.imgs = [f('player{0}.png'.format(i)) for i in xrange(conf.PLAYER_IMGS)]
        w, h = self.imgs[0].get_size()
        self.img_offset = (-w / 2., -h / 2.)
        self.death_img = self.level.game.img('death.png')
        w, h = self.death_img.get_size()
        self.death_img_offset = (-w / 2., -h / 2.)

        self.reset()

    def reset (self, p = None):
        if p is not None:
            self.body.position = p
        self.img = 0
        self.on = set()
        self._move = set()
        self.jumping = False
        self.dirn = 1
        self.step_snd = conf.STEP_SND_DELAY
        self.step_img = conf.STEP_IMG_DELAY
        self.dirty = True

    def on_shape (self):
        for s in self.on:
            if not hasattr(s, 'owner'):
                return True
                break
        return False

    def jump (self):
        if self.on:
            if self.on_shape():
                self.level.game.play_snd('jump')
                self.level.spawn_particles(self.pos + (0, 15), (self.level.shape_colour, conf.JUMP_PARTICLES))
            self.body.apply_impulse((0, -conf.PLAYER_INITIAL_JUMP_FORCE))
            self.jumping = conf.PLAYER_JUMP_TIME

    def move (self, d):
        self._move.add(d)

    def update (self):
        b = self.body
        self.pos = b.position
        # move
        f = 0
        move = self._move
        for d in move:
            if d in (0, 2):
                f += 1 if d > 1 else -1
        if f != 0:
            d = 1 if f > 0 else -1
            if d != self.dirn:
                self.dirn = d
                self.img = 0
                self.dirty = True
            self.step_img -= 1
            if self.step_img == 0:
                self.img += 1
                self.img %= conf.PLAYER_IMGS
                self.dirty = True
                self.step_img = conf.STEP_IMG_DELAY
            if self.on_shape():
                self.step_snd -= 1
                if self.step_snd == 0:
                    self.level.game.play_snd('step')
                    self.step_snd = conf.STEP_SND_DELAY
                # particles
                amount = conf.MOVE_PARTICLES * conf.PLAYER_ACCEL
                a = int(amount)
                amount = a + (random() <= amount - a)
                if amount > 0:
                    self.level.spawn_particles(self.pos + (0, 15), (self.level.shape_colour, amount))
        elif self.img != 0:
            self.img = 0
            self.dirty = True
        b.apply_impulse((f * conf.PLAYER_ACCEL, 0))
        # jump
        if 1 in move and self.jumping:
            b.apply_impulse((0, -conf.PLAYER_JUMP_FORCE))
            self.jumping -= 1
        elif self.jumping:
            self.jumping = False
        self._move = set()

    def draw (self, screen):
        p = self.body.position
        img = self.imgs[self.img]
        if self.dirn == -1:
            img = pg.transform.flip(img, True, False)
        for img, o in ((img, self.img_offset), (self.death_img, self.death_img_offset)):
            screen.blit(img, p + o)
        self.dirty = False