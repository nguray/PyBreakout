from vector2f import Vector2f
import sdl2.ext
import sdl2.sdlgfx
from sdl2 import (pixels, render, events as sdlevents, surface, error,timer)
import copy

from gameconst import *
from utils import compute_intersection
from ball import Ball

class Ship:
    def __init__(self, x:int =0, y:int =0, texture = None):
        self.pos = Vector2f( x, y)
        self.last_pos = copy.copy(self.pos)
        self.setMediumSize()
        self.texture = texture
        self.startTimeS = sdl2.timer.SDL_GetTicks()
        self.startTimeAnim = sdl2.timer.SDL_GetTicks()
        self.startXMouse = 0
        self.hSpeed = 0
        self.iflash = 0
        self.fmagnet = False

    def updateState(self):
        nbTicks = sdl2.timer.SDL_GetTicks()
        if (nbTicks-self.startTimeS)>20:
            self.startTimeS = nbTicks
            self.hSpeed = self.pos.x - self.startXMouse
            self.startXMouse = self.pos.x
        if (nbTicks-self.startTimeAnim)>200:
            self.startTimeAnim = nbTicks
            self.iflash += 1

    def setSmallSize(self):
        self.w = 64
        self.h = 14
        self.w_2 = self.w/2
        self.isize = 0
        self.fmagnet = False

    def setMediumSize(self):
        self.w = 80
        self.h = 14
        self.w_2 = self.w/2
        self.isize = 1
        self.fmagnet = False

    def setBigSize(self):
        self.w = 104
        self.h = 14
        self.w_2 = self.w/2
        self.isize = 2
        self.fmagnet = False

    def setMagnet(self,f=True):
        self.setMediumSize()
        self.fmagnet = f

    def draw(self, renderer):
        #
        x1 = self.pos.x - self.w/2
        x2 = self.pos.x + self.w/2
        y1 = self.pos.y
        y2 = y1 + self.h
        if self.texture!=None:
            src_rect = sdl2.SDL_Rect(x=0, y=(self.iflash % 2)*self.h + 2*self.isize*self.h, w=self.w, h=self.h)
            dest_rect = sdl2.SDL_Rect(x=int(x1), y=int(y1), w=self.w, h=self.h)
            sdl2.SDL_RenderCopy(renderer,self.texture,src_rect,dest_rect)
        else:
            sdl2.sdlgfx.rectangleRGBA(renderer, int(x1), int(y1), int(x2), int(y2), 50, 50, 255, 255)

    def moveLeft(self, dx: int):
        if (self.pos.x-self.w_2)>0 :
            self.last_pos.x = self.pos.x
            self.pos.x -= dx

    def moveRight(self, dx: int):
        if (self.pos.x+self.w_2) < WIN_WIDTH:
            self.last_pos.x = self.pos.x
            self.pos.x += dx

    def hitBall(self, b: Ball):
        p1 = (self.pos.x - self.w_2, self.pos.y)
        p2 = (self.pos.x + self.w_2, self.pos.y)
        q1 = (b.pos.x, b.pos.y)
        q2 = (b.next_pos.x, b.next_pos.y)
        return compute_intersection(p1, p2, q1, q2)
    @property
    def left(self):
        return self.pos.x - self.w
    
    @property
    def right(self):
        return self.pos.x + self.w

    @property
    def top(self):
        return self.pos.y

    @property
    def bottom(self):
        return self.pos.y + self.h

