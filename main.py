import pygame as pg
import os, json
import random as rnd

# 게임에 필요한 가장 기본적인 변수들입니다.
scale = 4
offset = 0.2 # percent
LightViolet = (0xE4, 0xBB, 0xFF)
padWidth = 800
padHeight = 600
FPS = 30  # frame per second

# pygame.sprite.Sprite 클래스를 상속받아 Player 클래스를 만듭니다.
class Player(pg.sprite.Sprite):
    def __init__(self, game):
        super(Player, self).__init__() # 부모 클래스의 생성자를 호출합니다.
        self.game = game
        self.action = 0 # 움직이는 이미지를 고를 인덱스입니다. 0과 1의 값을 가집니다.
        self.load_image() # 이미지를 로드하는 함수입니다.
        self.image = self.img[self.action] # 기본 동작을 초기 이미지로 합니다.
        self.size = self.image.get_size() # 이미지의 가로와 세로를 튜플형식으로 저장합니다.
        self.pos = (int(padWidth * 0.1), int(padHeight * 0.5)) # 스크린 안에 이미지가 위치할 좌상단 좌표를 줍니다.
        self.rect = pg.Rect(self.pos, self.size) # pygame.Rect 객체로 이미지의 좌표와 크기 데이터를 지정합니다.
        self.vel = -10 # 플레이어의 기본 y축 속도는 -10입니다.
        self.acc = -2 # 플레이어의 기본 y축 가속도는 -2입니다.

    def load_image(self):
        self.w = [self.game.jdata['frames'][i]['sourceSize']['w'] for i in range(2)] # json 데이터에서 player 이미지의 width를 추출합니다.
        self.h = [self.game.jdata['frames'][i]['sourceSize']['h'] for i in range(2)] # json 데이터에서 player 이미지의 height를 추출합니다.
        self.img = [pg.Surface((self.w[i], self.h[i])) for i in range(2)] # 기본 이미지와 움직이는 이미지 두 이미지의 밑배경을 리스트로 저장합니다.
        for i in range(2):
            self.img[i].blit(self.game.resource, (0, 0), (self.game.jdata['frames'][i]['frame']['x'], self.game.jdata['frames'][i]['frame']['y'], self.w[i], self.h[i]))
            self.img[i].set_colorkey(0) # 블랙 픽셀을 모두 투명 픽셀로 바꾸고 이미지 차원을 확장합니다.
            self.img[i] = pg.transform.scale(self.img[i], tuple(x * scale for x in self.img[i].get_size())) # 이미지를 5배로 확대합니다.

    def update(self):
        self.vel += self.acc # 속도에 가속도를 적용합니다.
        self.rect.y -= self.vel # 위치에 속도값을 빼 현재 위치를 만들어 줍니다.
        self.image = self.img[0] if self.vel < 0 else self.img[1] # 속도가 음수라면 기본 이미지를 양수라면 뛰는 이미지로 만듭니다.

    def collide(self, sprites): # 충돌을 검사하여 충돌 객체를 반환하는 메소드입니다.
        for sprite in sprites:
            if pg.sprite.collide_rect(self, sprite):
                return sprite

#바닥을 구성하는 타일 스프라이트 클래스입니다. 서술하지 않은 상세한 내용은 Player 클래스와 같습니다.
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

# 장애물인 파이프 스프라이트 클래스입니다.
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
        # 레벨만큼 스크린의 y좌표를 유동적으로 지정합니다.
        self.pos = (x,50*level - self.image.get_height() if self.isTop else int(padHeight*0.9 - 50*level))
        self.rect = pg.Rect(self.pos, self.size)

    def load_image(self):
        # 0 index is bottom, 1 index is top
        self.w = [self.game.jdata['frames'][i]['sourceSize']['w'] for i in range(3,5)]
        self.h = [self.game.jdata['frames'][i]['sourceSize']['h'] for i in range(3,5)]
        self.img = [pg.Surface((self.w[i], self.h[i])) for i in range(2)]
        for i in range(2): # 합성에 필요한 기본 이미지인 파이프 상단 굴뚝 이미지와 파이프 하단 봉 이미지를 불러옵니다.
            self.img[i].blit(self.game.resource, (0, 0), (self.game.jdata['frames'][i+3]['frame']['x'], self.game.jdata['frames'][i+3]['frame']['y'], self.w[i], self.h[i]))
            self.img[i] = pg.transform.scale(self.img[i], tuple(x * scale for x in self.img[i].get_size()))

        self.image = pg.Surface((self.w[0] * scale, self.h[0] * (self.level+1) * scale)) # 클래스의 생성자 인수로 받은 level에 따라 이미지의 크기를 조정합니다.
        self.image.blit(self.img[1], (0,0), self.img[1].get_rect()) # 파이프 상단 굴뚝 이미지를 우선 그립니다.
        [self.image.blit(self.img[0], (0,self.h[0]*i*scale), self.img[0].get_rect()) for i in range(1,5)] # 레벨만큼 파이프 하단부를 붙여줍니다.
        self.image = pg.transform.rotate(self.image, 180) if self.isTop else self.image # 만약 파이프가 아래쪽에 붙어있다면 이미지를 180도 회전합니다.
        self.image.set_colorkey(0)

    def update(self,vel=-10):
        self.rect.x += vel
        if self.rect.x < - padWidth *offset: # 이미지가 화면을 벗어난다면
            self.kill() # 객체를 제거하고
            if not self.game.died:
                self.game.score += 5 # 점수를 10점 올립니다. (하단 상단 두 개의 객체가 작동하여 10점이 올라감)
                self.game.get_score.play() # 점수를 따는 것과 동시에 효과음을 냅니다.

    def collide(self, sprites):
        for sprite in sprites:
            if pg.sprite.collide_rect(self, sprite):
                return sprite

class Game:
    def __init__(self):
        pg.init() # pyGame's initializer
        pg.mixer.init() # to use background music
        self.scr = pg.display.set_mode((padWidth, padHeight)) # Screen Object
        self.TITLE = 'Flappy Crabby'
        self.resource = pg.image.load(os.path.join('resources', 'texture_atlas.png')) # 한 장에 저장된 이미지 리소스를 불러옵니다.
        self.clock = pg.time.Clock() # Clock 객체를 생성합니다.
        self.onGame = True # onGame이 False가 되면 프로그램이 종료됩니다.

        self.dir = os.path.dirname(__file__) # 이 프로그램의 절대경로 위치를 저장합니다.
        pg.mixer.music.load(os.path.join(self.dir, 'resources', 'Retro_Platforming-David_Fesliyan.mp3')) # 기본 bgm을 불러옵니다.
        self.stx_sound = pg.mixer.Sound(os.path.join(self.dir, 'resources','begin_game.wav')) # 시작 효과음을 불러옵니다.
        self.get_score = pg.mixer.Sound(os.path.join(self.dir, 'resources','score_point.wav')) # 점수 효과음을 불러옵니다.
        self.ouch = pg.mixer.Sound(os.path.join(self.dir, 'resources','ouch.wav')) # 사망 효과음을 불러옵니다.
        with open(os.path.join('resources', 'texture_atlas.json')) as f:
            self.jdata = json.load(f) # json 형식의 데이터 파일을 불러와 저장합니다.

        pg.display.set_caption(self.TITLE) # 타이틀을 지정합니다.
        self.newGame()  # 새 게임을 시작하는 함수입니다.

    def newGame(self):
        self.start = False # 마우스 이벤트가 발생하기 전까진 게임을 임의로 시작하지 않습니다.
        self.score = 0
        self.died = False # 죽으면 재시작이 가능하게 판별할 수 있도록 하는 플래그입니다.
        self.level = 'Level 1'
        self.all_sprites = pg.sprite.Group() # 스프라이트들의 집합을 만드는 객체입니다.
        self.pipes = pg.sprite.Group() # 파이프 집합을 저장하는 객체입니다.
        self.pipe_vel = -20 # 파이프의 기본 속도입니다.
        self.tiles = [Tile(self, x=i) for i in range(0,padWidth, self.jdata['frames'][2]['sourceSize']['w']*scale)] # 화면 크기만큼 타일을 생성합니다.
        self.player = Player(self) # 플레이어 객체를 생성합니다.
        self.all_sprites.add([self.player, self.tiles, self.pipes]) # 생성한 객체들을 관리가 편하게 한 객체에 넣습니다.
        self.start_tick = pg.time.get_ticks() # 시작 시간을 기록합니다.
        self.second = (pg.time.get_ticks() - self.start_tick) / 1000 # 시작 시간에서 현재 시간을 빼어 second 단위의 시간을 저장합니다.
        if not os.path.isfile('high_score.txt'): # 최고 점수 파일이 없다면 생성합니다.
            with open(os.path.join(self.dir, 'high_score.txt'), 'w') as f:
                f.write('0')
        with open(os.path.join(self.dir, 'high_score.txt'), 'r') as f: # 최고 점수를 읽어옵니다. 실패한다면 0점이 기본 점수입니다.
            try:
                self.high_score = int(f.read())
            except:
                self.high_score = 0

        self.stx_sound.play() # 시작 효과음을 냅니다.

        while self.onGame:
            self.clock.tick(FPS) # frame per second를 지정합니다.
            self.events() # 이벤트를 처리합니다.
            self.update() # 게임 데이터를 업데이트 합니다.
            self.draw() # 화면 데이터를 업데이트 합니다.
            pg.display.update() # 변경사항을 화면에 적용합니다.

    def update(self):
        self.pre_second = self.second # 이전 시간을 기록합니다.
        self.second = (pg.time.get_ticks() - self.start_tick)/1000 if self.start else 0 # 현재 시간입니다. (게임을 시작했을 때만 작동)

        if self.start and (int(self.pre_second) != int(self.second)):
            _level1 = rnd.randint(0, 8) # 0에서 8까지의 레벨을 가질 수 있습니다.
            _level2 = rnd.randint(0,max(0,6-_level1)) # 6레벨(300픽셀) 정도의 상하 여유간격을 두고 랜덤으로 레벨을 생성합니다.
            _isTop = rnd.randint(0, 1) # 생성하는 파이프가 위로갈지 아래로 갈지 결정하는 변수입니다.
            self.pipes.add(Pipe(self, x=padWidth, level=_level1, isTop=_isTop))
            self.pipes.add(Pipe(self, x=padWidth, level=_level2, isTop=int(not _isTop))) # 위의 파이의와 반대방향으로 객체를 생성합니다.

        if (not self.died) and (self.player.collide(self.tiles) or self.player.collide(self.pipes)): # 죽지 않았다면 충돌검사를 합니다.
            self.died = True # 충돌 하였다면 died 변수를 True로 바꿔줍니다.
            self.player.vel = -50 # 플레이어의 속도를 크게 바꾸어 떨어지는 모션을 취해줍니다.
            self.ouch.play() # 사망 효과음을 냅니다.
            self.high_score = self.score if self.score > self.high_score else self.high_score # 하이스코어보다 점수가 높다면 하이스코어에 반영합니다.
            with open(os.path.join(self.dir, 'high_score.txt'), 'w') as f: # 최고 점수를 파일에 기록합니다.
                try:
                    f.write(str(self.high_score))
                except:
                    pass

        # 스코어가 100점 단위로 바뀔때마다 파이프의 속도를 늦추어 난이도를 높입니다.
        if self.score == 100:
            self.pipe_vel = -15
            self.level = 'Level 2'
        elif self.score == 200:
            self.pipe_vel = -10
            self.level = 'Level 3'
        elif self.score == 300:
            self.pipe_vel = -5
            self.level = 'Level 4'

        # 게임이 시작되었을 때만 플레이어와 파이프의 상태를 업데이트 합니다.
        if self.start: self.player.update()
        if self.start: self.pipes.update(self.pipe_vel)


    def events(self):
        event = pg.event.poll() # 이벤트를 처리하는 객체를 만듭니다.
        if event.type == pg.QUIT: # 이벤트 타입이 종료(닫기를 누르거나 ctrl+c 키를 입력)라면 프로그램을 종료합니다.
            self.onGame = False
        elif self.died and (event.type == pg.MOUSEBUTTONDOWN or event.type == pg.KEYDOWN): # 죽은 상태에서 키를 누르면 게임을 초기화합니다.
            self.newGame()
        elif (not self.died) and (event.type == pg.MOUSEBUTTONDOWN or event.type == pg.K_SPACE): # 죽지 않은 상태에서 마우스를 클릭하면
            if not self.start: # 게임이 시작되지 않은 상태라면
                self.start_tick = pg.time.get_ticks() # 시작 시간을 지정하고
                pg.mixer.music.play(-1) # bgm을 재생합니다.
            self.start = True
            self.player.vel = 15 #플레이어의 속도를 15로 만들어 일시적으로 상승하다가 가속도로 인해 떨어지도록 만듭니다./


    def draw(self):
        self.scr.fill(LightViolet) # 기본 배경색을 칠합니다.
        self.all_sprites.draw(self.scr) # 모든 스프라이트 객체의 draw 함수를 호출합니다.
        if not self.start: # 시작하지 않은 상태라면 시작 메세지를 보여줍니다.
            self.draw_text('Click Mouse button to start', 60, padWidth * 0.5, padHeight * 0.5, (255, 255, 0), True)
        if self.died: # 죽은 상태라면 재시작이 가능하도록 안내 메세지를 보여줍니다.
            self.draw_text('Game Over', 100,  padWidth*0.5, padHeight*0.5, (255,255,0), True)
            self.draw_text('Press any Key to restart', 40, padWidth*0.5, padHeight*0.6, (180,255,200), True)
        self.draw_text('Time: '+str(int(self.second))+'s', 28,0,0, (0, 0, 0), False) # 플레이 시간입니다.
        self.draw_text('Score: '+str(self.score), 28, padWidth*0.73, 0, (0,0,0), False) # 점수입니다.
        self.draw_text('High Score: '+str(self.high_score), 28, padWidth*0.73, 30, (0,0,0), False) # 최고점수입니다.
        self.draw_text(self.level, 34, padWidth*0.5, padHeight*0.03, (0,0,0), True) # 현재 레벨을 표시합니다.
        pg.display.flip() # 화면을 업데이트합니다.

    def draw_text(self, text, font_size, x, y, color, isCenter):
        font = pg.font.Font(os.path.join(self.dir, 'resources', 'NanumBarunGothic.ttf'), font_size) # 인수로 받은 font size에 따라 font 객체를 생성합니다.
        text_obj = font.render(text, True, color) # font를 사용해 텍스트 객체를 만듭니다.
        text_rect = text_obj.get_rect() # 텍스트가 위치와 크기를 저장하는 객체입니다.
        if isCenter: # isCenter 변수가 True라면 좌표를 텍스트의 중심으로 삼습니다.
            text_rect.centerx = int(x)
            text_rect.centery = int(y)
        else: # isCenter 변수가 False라면 좌표를 텍스트의 좌상단점으로 삼습니다.
            text_rect.x = int(x)
            text_rect.y = int(y)
        self.scr.blit(text_obj, text_rect) # 화면에 업데이트합니다.


if __name__ == '__main__': # 이 파일이 import된 경우에는 실행되지 않도록 합니다.
    game = Game() # 게임객체를 생성하면 자동으로 게임이 시작됩니다.
    #print(json.dumps(game.jdata,indent='    ')) # json 데이터를 사용자가 보기 좋은 모습으로 출력해줍니다.
