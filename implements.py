import math
import random
import time
import config
import pygame
from pygame.locals import Rect, K_LEFT, K_RIGHT


class Basic:
    def __init__(self, color: tuple, speed: int = 0, pos: tuple = (0, 0), size: tuple = (0, 0)):
        self.color = color
        self.rect = Rect(pos[0], pos[1], size[0], size[1])
        self.center = (self.rect.centerx, self.rect.centery)
        self.speed = speed
        self.start_time = time.time()
        self.dir = 270

    def move(self):
        dx = math.cos(math.radians(self.dir)) * self.speed
        dy = -math.sin(math.radians(self.dir)) * self.speed
        self.rect.move_ip(dx, dy)
        self.center = (self.rect.centerx, self.rect.centery)


class Block(Basic):
    def __init__(self, color: tuple, pos: tuple = (0,0), on_collide = None , alive = True):
        super().__init__(color, 0, pos, config.block_size)
        self.pos = pos
        self.alive = alive
        self.on_collide = on_collide

    def draw(self, surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)
    
    def collide(self):
        self.alive = False  # 블록이 없어짐
        self.rect.topleft = (-100, -100)  # 블록을 화면 밖으로 이동
        self.on_collide(self)


class Paddle(Basic):
    def __init__(self):
        super().__init__(config.paddle_color, 0, config.paddle_pos, config.paddle_size)
        self.start_pos = config.paddle_pos
        self.speed = config.paddle_speed
        self.cur_size = config.paddle_size

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def move_paddle(self, event: pygame.event.Event):
        if event.key == K_LEFT and self.rect.left > 0:
            self.rect.move_ip(-self.speed, 0)
        elif event.key == K_RIGHT and self.rect.right < config.display_dimension[0]:
            self.rect.move_ip(self.speed, 0)


class Ball(Basic):
    def __init__(self, dir: int = 0, pos: tuple = config.ball_pos):
        super().__init__(config.ball_color, config.ball_speed, pos, config.ball_size)
        self.power = 1
        if(dir == 0):
            self.dir = 90 + random.randint(-45, 45)
        else:
            self.dir = dir

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)

    def collide_block(self, blocks: list):
         for block in blocks:
            if self.rect.colliderect(block.rect) and block.alive:  # 블록이 살아있는 상태에서만 충돌 처리
                # 벽돌을 깨고 제거
                block.collide()

                # 충돌 방향을 정확히 반대로 변경
                self.dir = (self.dir + 180) % 360  
                break  # 첫 번째로 충돌한 블록만 처리하고 종료

    def collide_paddle(self, paddle: Paddle) -> None:
        if self.rect.colliderect(paddle.rect):
            self.dir = 360 - self.dir + random.randint(-5, 5)

    def hit_wall(self):
        if self.rect.left <= 0 or self.rect.right >= config.display_dimension[0]:
            self.dir = 180 - self.dir  # 좌우 벽에 부딪히면 방향 반전

        # 상단 벽 충돌
        if self.rect.top <= 0:
            self.dir = 360 - self.dir  # 상단 벽에 부딪히면 방향 반전
    
    def alive(self):
         # 공이 패들 아래로 떨어졌는지 확인
        if self.rect.top > config.display_dimension[1]:
            return False  # 공이 화면 아래로 나갔음
        return True  # 공이 여전히 살아있음
    
# 모든 Item은 이 객체를 사용함  - Kyonami
class Item(Basic):
    def __init__(self, pos: tuple = (0, 0), color: tuple = config.item_default_color, on_collide_paddle = None):
        super().__init__(color, config.item_speed, pos, config.item_size)
        self.on_collide_paddle = on_collide_paddle

    def move(self):
        self.rect.move_ip(0, self.speed)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def collide_paddle(self, paddle: Paddle):
        if self.rect.colliderect(paddle.rect):
            self.activate_effect(paddle)
            self.rect.topleft = (-100, -100)    # 패들과 충돌시 아이템을 화면 밖으로 보냄 (사라지게)  - Kyonami

    def activate_effect(self, paddle: Paddle):
        if self.on_collide_paddle != None:
            self.on_collide_paddle(paddle)   # 콜백 함수가 존재하면 호출  - Kyonami

    def is_out_of_screen(self): 
        return self.rect.top > config.display_dimension[1]  # 화면 하단 보다 내려가면 화면 밖으로 나갔다고 판단  - Kyonami