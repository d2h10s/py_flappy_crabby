import pygame as pg
import sys, os, json
from time import sleep
vec = pg.math.Vector2




class Player(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.groups = self.game.all_sprites
        self.load_image()
        self.image = self.img_crab0
        self.rect = self.image.get_rect()
        self.pos = vec(self.game.padWidth * 0.1, self.game.padHeight * 0.5)
        self.vel = vec(0,0)
        self.acc = vec(0, -9.8)

    def load_image(self):
        self.w0 = self.game.jdata['frames'][0]['sourceSize']['w']
        self.h0 = self.game.jdata['frames'][0]['sourceSize']['h']
        self.img_crab0 = pg.Surface((self.w0*3, self.h0*3))
        self.img_crab0.blit(self.game.resource, (0, 0),
                            (self.game.jdata['frames'][0]['frame']['x'],
                             self.game.jdata['frames'][0]['frame']['y'], self.w0, self.h0))
        self.img_crab0.set_colorkey(self.img_crab0.get_at((0, 0)))
        self.w1 = self.game.jdata['frames'][1]['sourceSize']['w']
        self.h1 = self.game.jdata['frames'][1]['sourceSize']['h']
        self.img_crab1 = pg.Surface((self.w1, self.h1))
        self.img_crab1.blit(self.game.resource, (0, 0),
                            (self.game.jdata['frames'][1]['frame']['x'],
                             self.game.jdata['frames'][1]['frame']['y'], self.w1, self.h1))

class tiles(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.groups = self.game.all_sprites, self.game.tiles

        self.w = self.game.jdata['frames'][2]['sourceSize']['w']
        self.h = self.game.jdata['frames'][2]['sourceSize']['h']
        self.img = pg.Surface(self.w, self.h)
        self.img.blit(self.game.resource, (0,0),
                      self.game.jdata['frames'][2]['frame']['x'],
                      self.game.jdata['frames'][2]['frame']['y'], self.w, self.h)
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = self.game

    def new(self):
        self.tile = pg.sprite.Group()

class Game:
    def __init__(self):
        pg.init() # pyGame's initializer
        pg.mixer.init() # to use background music
        self.LightViolet = (200, 220, 230)
        self.padWidth = 800
        self.padHeight = 600
        self.scr = pg.display.set_mode((self.padWidth, self.padHeight)) # Screen Object
        self.TITLE = 'Fluppy Crabby'
        self.resource = pg.image.load(os.path.join('resources', 'texture_atlas.png')).convert_alpha() # binded texture
        self.resource.set_colorkey(self.resource.get_at((0,0)))
        self.clock = pg.time.Clock()
        self.onGame = False
        self.FPS = 30 # 60 frame per second

        self.dir = os.path.dirname(__file__)
        self.stx_sound = pg.mixer.Sound(os.path.join('resources','begin_game.wav'))
        self.get_score = pg.mixer.Sound(os.path.join('resources','score_point.wav'))
        self.ouch = pg.mixer.Sound(os.path.join('resources','ouch.wav'))
        with open(os.path.join('resources', 'texture_atlas.json')) as f:
            self.jdata = json.load(f) # json meta data

        pg.display.set_caption(self.TITLE)


    def run(self):
        self.stx_sound.play()

        while not self.onGame:
            for event in pg.event.get():
                if event.type in [pg.QUIT]:
                    pg.quit()
                    sys.exit()
            self.clock.tick(self.FPS)
            self.events()
            self.update()
            self.draw()
            pg.display.update()

    def newGame(self):
        self.score = 0
        self.speed_x = 1
        self.speed_y = 5

        self.all_sprites = pg.sprite.Group()
        self.pipes = pg.sprite.Group()
        self.floors = pg.sprite.Group()
        self.player = Player(self)
        self.all_sprites.add(self.player)

        self.start_tick = pg.time.get_ticks()
        if not os.path.isfile('high_score.txt'):
            with open(os.path.join(self.dir, 'high_score.txt'), 'w') as f:
                f.write('0')
        with open(os.path.join(self.dir, 'high_score.txt'), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

        self.run()

    def update(self):
        self.all_sprites.update()
        self.second = (pg.time.get_ticks() - self.start_tick)/1000

        if self.score == 10:
            self.speed_x = 5
        elif self.score == 20:
            self.speed_x = 10
        elif self.score == 30:
            self.speed_x = 20


    def events(self):
        pass


    def draw(self):
        self.scr.fill(self.LightViolet)
        self.all_sprites.draw(self.scr)
        pg.display.flip()

if __name__ == '__main__':
    with open('./resources/texture_atlas.json') as f:
        jdata = json.load(f)
    print(json.dumps(jdata,indent='    '))
    print(jdata['frames'][2]['frame']['x'])
    game = Game()
    game.newGame()
