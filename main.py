import pygame as pg
import os, json
import random as rnd

scale = 4
offset = 0.2 # percent
LightViolet = (0xE4, 0xBB, 0xFF)
padWidth = 800
padHeight = 600
FPS = 30  # frame per second

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        super(Player, self).__init__()
        self.game = game
        self.groups = self.game.all_sprites
        self.action = 0
        self.load_image()
        self.image = self.img[self.action]
        self.size = self.image.get_size()
        self.pos = (int(padWidth * 0.1), int(padHeight * 0.5))
        self.rect = pg.Rect(self.pos, self.size)
        self.vel = -10
        self.acc = -2
    def load_image(self):
        self.w = [self.game.jdata['frames'][i]['sourceSize']['w'] for i in range(2)]
        self.h = [self.game.jdata['frames'][i]['sourceSize']['h'] for i in range(2)]
        self.img = [pg.Surface((self.w[i], self.h[i])) for i in range(2)]
        for i in range(2):
            self.img[i].blit(self.game.resource, (0, 0), (self.game.jdata['frames'][i]['frame']['x'], self.game.jdata['frames'][i]['frame']['y'], self.w[i], self.h[i]))
            self.img[i].set_colorkey(self.img[i].get_at((0, 0)))
            self.img[i] = pg.transform.scale(self.img[i], tuple(x * scale for x in self.img[i].get_size()))

    def update(self):
        self.vel += self.acc
        self.rect.y -= self.vel
        self.image = self.img[0] if self.vel < 0 else self.img[1]

    def collide(self, sprites):
        for sprite in sprites:
            if pg.sprite.collide_rect(self, sprite):
                return sprite


class Tile(pg.sprite.Sprite):
    def __init__(self, game, x):
        super(Tile, self).__init__()
        self.game = game
        self.groups = self.game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_image()
        self.size = self.image.get_size()
        self.pos = (int(x), int(padHeight - self.size[1]))
        self.rect = pg.Rect(self.pos, self.size)

    def load_image(self):
        self.w = self.game.jdata['frames'][2]['sourceSize']['w']
        self.h = self.game.jdata['frames'][2]['sourceSize']['h']
        self.image = pg.Surface((self.w, self.h))
        self.image.blit(self.game.resource, (0,0), (self.game.jdata['frames'][2]['frame']['x'], self.game.jdata['frames'][2]['frame']['y'], self.w, self.h))
        self.image = pg.transform.scale(self.image, tuple(x * scale for x in self.image.get_size()))

    def collide(self, sprites):
        for sprite in sprites:
            if pg.sprite.collide_rect(self, sprite):
                return sprite


class Pipe(pg.sprite.Sprite):
    def __init__(self, game, x, level, isTop):
        super(Pipe, self).__init__()
        self.game = game
        self.x = x
        self.level = level
        self.isTop = isTop
        self.groups = self.game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.load_image()
        self.size = self.image.get_size()
        self.pos = (x,50*level - self.image.get_height() if self.isTop else int(padHeight*0.9 - 50*level))
        self.rect = pg.Rect(self.pos, self.size)

    def load_image(self):
        # 0 index is bottom, 1 index is top
        self.w = [self.game.jdata['frames'][i]['sourceSize']['w'] for i in range(3,5)]
        self.h = [self.game.jdata['frames'][i]['sourceSize']['h'] for i in range(3,5)]
        self.img = [pg.Surface((self.w[i], self.h[i])) for i in range(2)]
        for i in range(2):
            self.img[i].blit(self.game.resource, (0, 0), (self.game.jdata['frames'][i+3]['frame']['x'], self.game.jdata['frames'][i+3]['frame']['y'], self.w[i], self.h[i]))
            self.img[i] = pg.transform.scale(self.img[i], tuple(x * scale for x in self.img[i].get_size()))

        self.image = pg.Surface((self.w[0] * scale, self.h[0] * (self.level+1) * scale))
        self.image.blit(self.img[1], (0,0), self.img[1].get_rect())
        [self.image.blit(self.img[0], (0,self.h[0]*i*scale), self.img[0].get_rect()) for i in range(1,5)]
        self.image = pg.transform.rotate(self.image, 180) if self.isTop else self.image
        self.image.set_colorkey(0)  # make black pixel to transparent

    def update(self,vel=-10):
        self.rect.x += vel
        if self.rect.x < - padWidth *offset:
            self.kill()
            if not self.game.died:
                self.game.score += 5
                self.game.get_score.play()

    def collide(self, sprites):
        for sprite in sprites:
            if pg.sprite.collide_rect(self, sprite):
                return sprite

class Game:
    def __init__(self):
        pg.init() # pyGame's initializer
        pg.mixer.init() # to use background music
        self.scr = pg.display.set_mode((padWidth, padHeight)) # Screen Object
        self.TITLE = 'Fluppy Crabby'
        self.resource = pg.image.load(os.path.join('resources', 'texture_atlas.png'))
        self.clock = pg.time.Clock()
        self.onGame = True

        self.dir = os.path.dirname(__file__)
        pg.mixer.music.load(os.path.join(self.dir, 'resources', 'Retro_Platforming-David_Fesliyan.mp3'))
        self.stx_sound = pg.mixer.Sound(os.path.join(self.dir, 'resources','begin_game.wav'))
        self.get_score = pg.mixer.Sound(os.path.join(self.dir, 'resources','score_point.wav'))
        self.ouch = pg.mixer.Sound(os.path.join(self.dir, 'resources','ouch.wav'))
        with open(os.path.join('resources', 'texture_atlas.json')) as f:
            self.jdata = json.load(f) # json meta data


        pg.display.set_caption(self.TITLE)
        self.newGame()

    def newGame(self):
        self.start = False
        self.score = 0
        self.died = False
        self.level = 'Level 1'
        self.all_sprites = pg.sprite.Group()
        self.pipes = pg.sprite.Group()
        self.pipe_vel = -20
        self.tiles = [Tile(self, x=i) for i in range(0,padWidth, self.jdata['frames'][2]['sourceSize']['w']*scale)]
        self.player = Player(self)
        self.all_sprites.add([self.player, self.tiles, self.pipes])
        self.start_tick = pg.time.get_ticks()
        self.second = (pg.time.get_ticks() - self.start_tick) / 1000
        if not os.path.isfile('high_score.txt'):
            with open(os.path.join(self.dir, 'high_score.txt'), 'w') as f:
                f.write('0')
        with open(os.path.join(self.dir, 'high_score.txt'), 'r') as f:
            try:
                self.high_score = int(f.read())
            except:
                self.high_score = 0

        self.stx_sound.play()

        while self.onGame:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
            pg.display.update()

    def update(self):
        self.pre_second = self.second
        self.second = (pg.time.get_ticks() - self.start_tick)/1000 if self.start else 0

        if self.start and (int(self.pre_second) != int(self.second)):
            _level1 = rnd.randint(0, 8)
            _level2 = rnd.randint(0,max(0,6-_level1))
            _isTop = rnd.randint(0, 1)
            self.pipes.add(Pipe(self, x=padWidth, level=_level1, isTop=_isTop))
            self.pipes.add(Pipe(self, x=padWidth, level=_level2, isTop=int(not _isTop)))

        if (not self.died) and (self.player.collide(self.tiles) or self.player.collide(self.pipes)):
            self.died = True
            self.player.vel = -50
            self.ouch.play()
            self.high_score = self.score if self.score > self.high_score else self.high_score
            with open(os.path.join(self.dir, 'high_score.txt'), 'w') as f:
                try:
                    f.write(str(self.high_score))
                except:
                    pass


        if self.score == 100:
            self.pipe_vel = -15
            self.level = 'Level 2'
        elif self.score == 200:
            self.pipe_vel = -10
            self.level = 'Level 3'
        elif self.score == 300:
            self.pipe_vel = -5
            self.level = 'Level 4'

        if self.start: self.player.update()
        if self.start: self.pipes.update(self.pipe_vel)


    def events(self):
        event = pg.event.poll()
        if event.type == pg.QUIT:
            self.onGame = False
        elif self.died and event.type == pg.KEYDOWN:
            self.newGame()
        elif not self.died and event.type == pg.MOUSEBUTTONDOWN:
            if not self.start:
                self.start_tick = pg.time.get_ticks()
                pg.mixer.music.play(-1)
            self.start = True
            self.player.vel = 15


    def draw(self):
        self.scr.fill(LightViolet)
        self.all_sprites.draw(self.scr)
        if not self.start:
            self.draw_text('Click Mouse button to start', 60, padWidth * 0.5, padHeight * 0.5, (255, 255, 0), True)
        if self.died:
            self.draw_text('Game Over', 100,  padWidth*0.5, padHeight*0.5, (255,255,0), True)
            self.draw_text('Press any Key to restart', 40, padWidth*0.5, padHeight*0.6, (180,255,200), True)
        self.draw_text('Time: '+str(int(self.second))+'s', 28,0,0, (0, 0, 0), False)
        self.draw_text('Score: '+str(self.score), 28, padWidth*0.73, 0, (0,0,0), False)
        self.draw_text('High Score: '+str(self.high_score), 28, padWidth*0.73, 30, (0,0,0), False)
        self.draw_text(self.level, 34, padWidth*0.5, padHeight*0.03, (0,0,0), True)
        pg.display.flip()

    def draw_text(self, text, font_size, x, y, color, isCenter):
        font = pg.font.Font(os.path.join(self.dir, 'resources', 'NanumBarunGothic.ttf'), font_size)
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if isCenter:
            text_rect.centerx = int(x)
            text_rect.centery = int(y)
        else:
            text_rect.x = int(x)
            text_rect.y = int(y)
        self.scr.blit(text_obj, text_rect)


if __name__ == '__main__':
    game = Game()
    #print(json.dumps(game.jdata,indent='    '))
