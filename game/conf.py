from os import sep
from math import pi

import pygame as pg
import pymunk
from pymunk import Vec2d

# paths
DATA_DIR = ''
IMG_DIR = DATA_DIR + 'img' + sep
SOUND_DIR = DATA_DIR + 'sound' + sep
MUSIC_DIR = DATA_DIR + 'music' + sep
FONT_DIR = DATA_DIR + 'font' + sep

# display
WINDOW_ICON = None #IMG_DIR + 'icon.png'
WINDOW_TITLE = ''
MOUSE_VISIBLE = True
FLAGS = 0
FULLSCREEN = False
RESIZABLE = True
SIZE = (1000, 500)
RES_W = (1000, 500)
RES_F = pg.display.list_modes()[0]
MIN_RES_W = (320, 180)
ASPECT_RATIO = float(SIZE[0]) / SIZE[1]

# timing
FPS = 60
FRAME = 1. / FPS
STEP = .01

# input
KEYS_NEXT = (pg.K_RETURN, pg.K_SPACE, pg.K_KP_ENTER)
KEYS_BACK = (pg.K_ESCAPE, pg.K_BACKSPACE)
KEYS_MINIMISE = (pg.K_F10,)
KEYS_FULLSCREEN = (pg.K_F11, (pg.K_RETURN, pg.KMOD_ALT, True),
                   (pg.K_KP_ENTER, pg.KMOD_ALT, True))
KEYS_MOVE = ((pg.K_LEFT,), (pg.K_UP,), (pg.K_RIGHT,), (pg.K_DOWN,))
KEYS_JUMP = (pg.K_UP,)
KEYS_RESET = (pg.K_r,)

# audio
MUSIC_VOLUME = 50
SOUND_VOLUME = 50
EVENT_ENDMUSIC = pg.USEREVENT
SOUNDS = {'die': 8, 'step': 9, 'jump': 9, 'win': 6}
SOUND_VOLUMES = {'jump': 2, 'step': .5}
STEP_SND_DELAY = int(round(.2 * FPS))

# world
GRAVITY = Vec2d((0, 6000))
DAMPING = .00005
SHAPE_FRICT = .8
SHAPE_ELAST = 0
LINE_RADIUS = 2
SHAPE_GROUP = 1
GROUND_ANGLE_THRESHOLD = pi / 4
COLLISION_LAYER = 2 ** 0
DEATH_LAYER = 2 ** 1
DOOR_LAYER = 2 ** 2
TRIGGER_LAYER = 3 ** 2

# player
DEATH_RADIUS = 100
PLAYER_MASS = 50
PLAYER_ACCEL = 4000
PLAYER_PTS = [(-10, 15), (10, 15), (10, -15), (-10, -15)]
PLAYER_ELAST = 0
PLAYER_FRICT = .5
PLAYER_INITIAL_JUMP_FORCE = 20000
PLAYER_JUMP_FORCE = 5000
PLAYER_JUMP_TIME = 8

# thing
THING_MASS = 50
THING_PTS = [(-10, 15), (10, 15), (10, -15), (-10, -15)]
DEAD_THING_PTS = THING_PTS
DEAD_THING_POS_OFFSET = (0, 0)
THING_ELAST = .8
THING_FRICT = .5
THING_TURN_THRESHOLD_VEL = 10 ** -3
AI_DATA = {
    'walk': {'not_moving': False, 'accel': 1500},
    'run_away': {'not_moving': False, 'accel': 2500, 'turn_prox': 50, 'speedup_prox': 50, 'max_speedup': .5}
}
RUN_TIME = int(round(5 * FPS))

# levels
def dotdotdot (level):
    level.msgs[2] += '...................................'
    pts = ((531, 234), (850, 234), (850, 242), (531, 242))
    level.shapes.append(pts)
    p = pymunk.Poly(level.space.static_body, pts)
    p.friction = SHAPE_FRICT
    p.elast = SHAPE_ELAST
    p.group = SHAPE_GROUP
    p.layers = COLLISION_LAYER
    level.space.add_static(p)
    level.shapes_shapes.append(p)

LEVEL_DATA = [
    {
        'start': (50, 485),
        'entrance': ((0, 0), (0, 500)),
        'exit': ((1000, 0), (1000, 500)),
        'things': [((300, 485), 1, 'walk'), ((350, 485), -1, 'walk'),
                   ((400, 485), -1, 'walk'), ((430, 485), -1, 'walk'),
                   ((600, 485), -1, 'walk'), ((750, 485), 1, 'walk')],
        'shapes': [],
        'msg': (None, "It's been like this all my life.")
    }, {
        'start': (100, 485),
        'entrance': ((0, 0), (0, 500)),
        'exit': ((1000, 0), (1000, 500)),
        'things': [((370, 485), -1, 'walk'), ((700, 485), 1, 'walk')],
        'shapes': [
            ((150, 500), (250, 470), (240, 500)),
            ((240, 500), (260, 440), (370, 500)),
            ((480, 450), (530, 440), (550, 500), (470, 500)),
            ((850, 440), (1000, 415), (1000, 450), (970, 500), (860, 500)),
        ],
        'msg': ("Creation itself makes a mockery of my loneliness by placing these other beings in my path.",
                "As if this entire universe is some kind of game, a little puzzle for nothing more than enjoyment.")
    }, {
        'start': (25, 395),
        'entrance': ((0, 0), (0, 500)),
        'exit': ((1000, 450), (1000, 500)),
        'things': [((400, 485), -1, 'walk'), ((450, 485), 1, 'walk'), ((480, 485), -1, 'walk'), ((720, 380), -1, 'walk')],
        'shapes': [
            ((0, 415), (40, 411), (42, 425), (0, 460)),
            ((100, 500), (130, 460), (280, 430), (340, 500)),
            ((600, 400), (700, 420), (700, 500), (680, 500)),
            ((700, 420), (770, 390), (710, 500), (700, 500)),
            ((710, 500), (740, 435), (800, 450), (850, 500)),
            ((810, 410), (820, 350), (1000, 310), (1000, 450), (850, 440)),
            ((955, 320), (1000, 100), (1000, 310))
        ],
        'msg': ("I can't even get close enough to anyone to apologise.",
                "It ends today.")
    }, {
        'start': (50, 165),
        'entrance': ((0, 120), (0, 170)),
        'exit': ((1000, 400), (1000, 500)),
        'things': [((230, 145), 1, 'walk'), ((30, 370), -1, 'walk')],
        'shapes': [
            ((0, 170), (100, 190), (110, 220), (50, 270), (0, 270)),
            ((0, 400), (90, 385), (150, 385), (185, 395), (130, 440), (0, 470)),
            ((135, 385), (130, 290), (150, 385)),
            ((200, 160), (330, 155), (320, 190), (215, 205)),
            ((236, 202), (250, 390), (250, 200)),
            ((300, 220), (310, 210), (390, 205), (410, 220), (310, 230)),
            ((370, 170), (500, 155), (800, 170), (810, 180), (805, 210), (375, 185)),
            ((855, 290), (880, 185), (870, 295)),
            ((660, 270), (1000, 295), (1000, 385), (690, 310)),
            ((550, 330), (635, 305), (730, 335), (665, 365), (590, 360)),
            ((345, 340), (370, 305), (400, 290), (630, 275), (635, 295), (500, 330)),
            ((205, 500), (215, 485), (255, 480), (250, 500)),
            ((340, 500), (325, 410), (380, 415), (375, 500)),
            ((315, 500), (335, 460), (340, 500)),
        ],
        'msg': ("I've managed to come by some information about a temple of sorts.", None)
    }, {
        'start': (100, 485),
        'entrance': ((0, 400), (0, 500)),
        'exit': ((620, 500), (1000, 500)),
        'things': [],
        'shapes': [
            ((350, 470), (380, 470), (380, 500), (350, 500)),
            ((380, 445), (410, 445), (410, 500), (380, 500)),
            ((410, 420), (440, 420), (440, 500), (410, 500)),
            ((440, 395), (470, 395), (470, 500), (440, 500)),
            ((470, 370), (500, 370), (500, 500), (470, 500)),
            ((500, 345), (530, 345), (530, 500), (500, 500)),
            ((530, 320), (560, 320), (560, 500), (530, 500)),
            ((560, 295), (590, 295), (590, 500), (560, 500)),
            ((560, 295), (590, 295), (590, 500), (560, 500)),
            ((590, 270), (620, 270), (620, 500), (590, 500)),
            ((504, 234), (531, 234), (531, 242), (504, 242)),
            ((850, 240), (1000, 240), (1000, 265), (850, 265))
        ],
        'msg': ("This place is supposed to hold the secret to ridding the world of all evil - or something.",
                "I suppose that means me.",
                "I guess I've still got a choice...", None),
        'triggers': [
            (((504, 200), (531, 200), (504, 234), (504, 234)), dotdotdot),
            (((950, 0), (1000, 0), (1000, 240), (950, 240)), lambda level: setattr(level, 'won', True))
        ]
    }
]

# graphics
FONT = 'Chunk.otf'
MSG_SIZE = 35
MSG_COLOUR = (0, 0, 0)
MSG_PADDING = 20
MSG_LINE_SPACING = 10
MSG_SPACING = 40
TRANSITION_TIME = int(round(1.5 * FPS))
TRANSITION_COLOUR = (0, 0, 0, 10)