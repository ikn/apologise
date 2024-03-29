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
WINDOW_ICON = IMG_DIR + 'icon.png'
WINDOW_TITLE = 'Can\'t Even Apologise'
MOUSE_VISIBLE = False
FLAGS = 0
FULLSCREEN = False
RESIZABLE = False
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
# support WASD on QWERTY, QWERTZ, AZERTY, Dvorak
KEYS_MOVE = (
    (pg.K_LEFT, pg.K_a, pg.K_q),
    (pg.K_UP, pg.K_w, pg.K_z, pg.K_COMMA),
    (pg.K_RIGHT, pg.K_d, pg.K_e, pg.K_s)
)
KEYS_JUMP = KEYS_MOVE[1]
KEYS_RESET = (pg.K_r,)

# audio
MUSIC_VOLUME = 70
PAUSED_MUSIC_VOLUME = 20
SOUND_VOLUME = 50
EVENT_ENDMUSIC = pg.USEREVENT
SOUNDS = {'die': 1, 'step': 13}
SOUND_VOLUMES = {'step': .5, 'jump': 4}
STEP_SND_DELAY = int(round(.2 * FPS))

# world
GRAVITY = Vec2d((0, 6000))
DAMPING = .00005
SHAPE_FRICT = .8
SHAPE_ELAST = 0
LINE_RADIUS = 2
SHAPE_GROUP = 1
GROUND_ANGLE_THRESHOLD = pi / 6
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
DEAD_THING_PTS = [(-10, 13.5), (10, 13.5), (10, -13.5), (-10, -13.5)]
DEAD_THING_POS_OFFSET = (0, 0)
THING_ELAST = 0
THING_FRICT = .5
THING_TURN_THRESHOLD_VEL = 10 ** -3
AI_DATA = {
    'walk': {'not_moving': False, 'accel': 1500, 'img_delay': int(round(.2 * FPS))},
    'run_away': {'not_moving': False, 'accel': 2500, 'turn_prox': 50, 'speedup_prox': 50, 'max_speedup': .5, 'img_delay': int(round(.1 * FPS))}
}
RUN_TIME = int(round(5 * FPS))

# levels
def dotdotdot (level):
    level.msgs[2] += '...................................'
    pts = ((531, 234), (850, 234), (850, 242), (531, 242))
    p = pymunk.Poly(level.space.static_body, pts)
    p.friction = SHAPE_FRICT
    p.elast = SHAPE_ELAST
    p.group = SHAPE_GROUP
    p.layers = COLLISION_LAYER
    level.space.add_static(p)
    level.shapes_shapes.append(p)

LEVEL_DATA = [
    {
        'start': (70, 485),
        'entrance': ((0, 0), (0, 500)),
        'exit': ((1000, 0), (1000, 500)),
        'things': [((300, 485), 1, 'walk'), ((350, 485), -1, 'walk'),
                   ((400, 485), -1, 'walk'), ((430, 485), -1, 'walk'),
                   ((600, 485), -1, 'walk'), ((750, 485), 1, 'walk')],
        'shapes': [],
        'shape_colour': (20, 15, 0),
        'msg': (None, "It's been like this all my life."),
        'msg_colour': (30, 20, 0),
        'msg_arrow': 0,
        'music': 0
    }, {
        'start': (50, 485),
        'entrance': ((0, 0), (0, 500)),
        'exit': ((1000, 0), (1000, 500)),
        'things': [((370, 485), -1, 'walk'), ((700, 485), 1, 'walk')],
        'shapes': [
            ((150, 500), (250, 470), (240, 500)),
            ((240, 500), (260, 440), (310, 500)),
            ((480, 450), (530, 440), (550, 500), (470, 500)),
            ((850, 440), (1000, 415), (1000, 450), (866, 465)),
            ((915, 500), (925, 455), (985, 450), (950, 500))
        ],
        'shape_colour': (20, 15, 0),
        'msg': ("Creation itself makes a mockery of my loneliness by placing these other beings in my path.",
                "As if this entire universe is some kind of game, a little puzzle for nothing more than enjoyment."),
        'msg_colour': (30, 20, 0),
        'msg_arrow': 0,
        'music': 0
    }, {
        'start': (25, 395),
        'entrance': ((0, 0), (0, 500)),
        'exit': ((1000, 450), (1000, 500)),
        'things': [((15, 270), 1, 'walk'), ((400, 485), -1, 'walk'),
                   ((450, 485), 1, 'walk'), ((480, 485), -1, 'walk'),
                   ((720, 380), -1, 'walk')],
        'shapes': [
            ((0, 300), (48, 291), (31, 286), (0, 284)),
            ((48, 291), (42, 230), (31, 286)),
            ((0, 415), (40, 411), (42, 425), (0, 460)),
            ((100, 500), (130, 460), (280, 430), (340, 500)),
            ((590, 451), (580, 415), (603, 453)),
            ((595, 460), (595, 443), (620, 435), (625, 451)),
            ((728, 447), (725, 430), (758, 446)),
            ((751, 443), (763, 410), (760, 443)),
            ((590, 450), (760, 443), (731, 560), (637, 560)),
            ((740, 500), (751, 450), (820, 472), (850, 500)),
            ((810, 410), (820, 350), (1000, 310), (1000, 450), (870, 460)),
            ((955, 320), (1000, 100), (1000, 310))
        ],
        'shape_colour': (20, 15, 0),
        'msg': ("I can't even get close enough to anyone to apologise.",
                "It ends today."),
        'msg_colour': (30, 20, 0),
        'msg_arrow': 0,
        'music': 0
    }, {
        'start': (50, 165),
        'entrance': ((0, 120), (0, 170)),
        'exit': ((1000, 400), (1000, 500)),
        'things': [((230, 145), 1, 'walk'), ((30, 370), -1, 'walk'), ((765, 485), 1, 'walk')],
        'shapes': [
            ((0, 170), (100, 190), (110, 220), (50, 270), (0, 270)),
            ((0, 400), (90, 385), (150, 385), (185, 395), (130, 440), (0, 450)),
            ((135, 385), (130, 290), (150, 385)),
            ((200, 160), (330, 155), (320, 190), (215, 205)),
            ((236, 202), (250, 390), (250, 200)),
            ((300, 220), (310, 210), (390, 205), (410, 220), (310, 230)),
            ((370, 170), (500, 155), (800, 170), (810, 180), (805, 210), (375, 185)),
            ((855, 290), (880, 185), (870, 295)),
            ((660, 270), (1000, 295), (1000, 355), (690, 310)),
            ((950, 210), (955, 0), (1000, 0), (1000, 285)),
            ((550, 330), (635, 305), (730, 335), (665, 355), (590, 360)),
            ((345, 340), (370, 305), (400, 290), (630, 275), (635, 295), (500, 330)),
            ((205, 500), (215, 485), (255, 480), (250, 500)),
            ((420, 500), (405, 415), (460, 410), (455, 500)),
            ((395, 500), (415, 460), (420, 500)),
            ((539, 402), (551, 388), (699, 402), (705, 419), (600, 430)),
            ((653, 400), (706, 386), (698, 406)),
            ((730, 387), (744, 370), (803, 370), (843, 389)),
            ((725, 456), (730, 500), (716, 500)),
            ((798, 500), (801, 454), (807, 500))
        ],
        'shape_colour': (5, 2, 0),
        'msg': ("I've managed to come by some information about a temple of sorts.", None),
        'msg_colour': (150, 100, 0),
        'msg_arrow': 1,
        'music': 1
    }, {
        'start': (50, 235),
        'entrance': ((0, 150), (0, 250)),
        'exit': ((1000, 60), (1000, 260)),
        'things': [((180, 235), 1, 'walk'), ((390, 265), 1, 'walk'), ((740, 161), -1, 'walk')],
        'shapes': [
            ((0, 250), (190, 250), (295, 280), (300, 500), (0, 500)),
            ((85, 250), (95, 230), (120, 230), (135, 250)),
            ((175, 205), (180, 190), (570, 185), (567, 195), (275, 215)),
            ((280, 500), (285, 305), (630, 305), (670, 500)),
            ((630, 340), (670, 338), (680, 485)),
            ((650, 386), (715, 376), (720, 500), (662, 500)),
            ((715, 418), (770, 413), (780, 500), (705, 500)),
            ((773, 455), (820, 450), (832, 500), (766, 500)),
            ((675, 300), (750, 300), (800, 340)),
            ((825, 483), (936, 494), (940, 500), (825, 500)),
            ((958, 340), (1000, 335), (1000, 396)),
            ((800, 340), (960, 320), (1000, 335), (858, 363)),
            ((960, 320), (950, 260), (1000, 260), (1000, 335)),
            ((930, 500), (935, 430), (1000, 420), (1000, 500)),
            ((691, 174), (771, 178), (737, 196), (707, 191)),
            ((689, 174), (699, 120), (696, 178)),
            ((758, 180), (753, 122), (765, 181))
        ],
        'shape_colour': (5, 2, 0),
        'msg': (None, None),
        'msg_colour': (150, 100, 0),
        'msg_arrow': 1,
        'music': 1
    }, {
        'start': (50, 485),
        'entrance': ((0, 300), (0, 500)),
        'exit': ((620, 500), (1000, 500)),
        'things': [((605, 255), -1, 'walk')],
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
            (((504, 234), (531, 234), (531, 242), (504, 242)), False),
            ((850, 240), (1000, 240), (1000, 265), (850, 265))
        ],
        'shape_colour': (10, 10, 10),
        'msg': ("This place is supposed to hold the secret to ridding the world of all evil - or something.",
                "I suppose that means me.",
                "I guess I've still got a choice...", None),
        'msg_colour': (10, 10, 10),
        'msg_arrow': 2,
        'triggers': [
            (((504, 200), (531, 200), (504, 234), (504, 234)), dotdotdot),
            (((990, 0), (1000, 0), (1000, 240), (990, 240)), lambda level: setattr(level, 'won', True))
        ]
    }
]

# end
MIN_KILLS = 17
MAX_KILLS = 20
BAD_RANK = ('EVIL', 'You went out of your way to kill.  Way to go.')
DEFAULT_RANK = ('SYMPATHETIC', 'You didn\'t kill everyone.  I guess that\'s good?')
GOOD_RANK = ('HEROIC', 'You went out of your way to avoid kills.  Heroic indeed!')

# graphics
FONT = 'Chunk.otf'
MSG_SIZE = 35
MSG_PADDING = 20
MSG_LINE_SPACING = 10
MSG_SPACING = 40
ARROW_PADDING = 15
TRANSITION_TIME = int(round(1.5 * FPS))
TRANSITION_COLOUR = (0, 0, 0, 10)
PLAYER_IMGS = 6
THING_IMGS = PLAYER_IMGS
STEP_IMG_DELAY = int(round(.05 * FPS))
THING_COLOUR = (0, 0, 0)
# end
RANK_BG_COLOUR = (0, 0, 0)
RANK_FONT_COLOUR = (255, 255, 255)
RANK_FONT_SIZE = 70
RANK_PADDING = 50
RANK_LINE_SPACING = 20
RANK_SPACING = 100
# particles
PARTICLE_SPEED = 1.5
PARTICLE_LIFE = .5 * FPS
PARTICLE_SIZE = 2
JUMP_PARTICLES = 100
MOVE_PARTICLES = .0002
