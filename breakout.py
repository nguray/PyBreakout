import os
from os import path
from random import randint
import sys
import sdl2.ext
import sdl2.sdlgfx
from sdl2 import (pixels, render, events as sdlevents, surface, error,timer)
from dataclasses import dataclass
import math 
from random import randint
import copy

import sdl2.sdlmixer
import sdl2.sdlttf
from ctypes import c_int, byref

WIN_WIDTH   = 594
WIN_HEIGHT  = 720
BRICK_WIDTH = WIN_WIDTH / 11 # 56 x 24
BRICK_HEIGHT= WIN_HEIGHT / 30


#pip install -U --break-system-packages  git+https://github.com/py-sdl/py-sdl2.git

@dataclass
class Vector2f:
    """Class for 2d vector """
    x: float
    y: float
    def __add__(self, other):
        return self.__class__(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        return self + other


@dataclass
class Rectf:
    """Class for Rectf """
    x: float
    y: float
    w: float
    h: float
    
    def contains(self,x: float,y: float):
        right = self.x + self.w 
        bottom = self.y + self.h
        return (x>=self.x and x<=right and y>=self.y and y<=bottom)
    
    def left(self):
        return self.x
    
    def right(self):
        return self.x + self.w
    
    def top(self):
        return self.y
    
    def bottom(self):
        return self.y + self.h
    

class Brick:

    values:int = (0,50,60,70,80,90,100,110,120,50,0)
    texture = None

    def __init__(self, x:float, y:float, type:int):
        self.left = x+1
        self.top  = y+1
        self.type = type
        self.right = x + BRICK_WIDTH - 1
        self.bottom = y + BRICK_HEIGHT - 1
        if self.type==9:
            self.resistance = 4
        elif self.type==10:
            self.resistance = 8
        else:
            self.resistance = 1

    def contain(self, x, y):
        return  (x>self.left and x<self.right and 
                    y>self.top and y<self.bottom)

    def draw(self, renderer):
        #
        if self.texture!=None:
            src_rect = sdl2.SDL_Rect(x=0, y=self.type*24, w=56, h=24)
            dest_rect = sdl2.SDL_Rect(x=int(self.left), y=int(self.top),
                                       w=int(self.right-self.left), h=int(self.bottom-self.top))
            sdl2.SDL_RenderCopy(renderer,self.texture,src_rect,dest_rect)
        else:
            sdl2.sdlgfx.rectangleRGBA(renderer, int(self.left), int(self.top),
                                       int(self.right), int(self.bottom), 50, 50, 255, 255)

class Ball:
    def __init__(self, x:int =0, y:int =0, r:int = 5):
        self.pos = Vector2f( x, y)
        self.next_pos = copy.copy(self.pos)
        self.fstandby = True
        self.r = r
        self.setVelocity(Vector2f( 0, 0))
        self.fdelete = False
        self.trail = []
        self.trail.append(Vector2f(self.pos.x,self.pos.y))
        self.trail.append(None)
        self.trail.append(None)
        self.trail.append(None)
        self.trail.append(None)

    def setVelocity(self, v: Vector2f):
        self.vel = copy.copy(v)
        if self.vel.x!=0 and self.vel.y!=0:
            self.normal_vel = Vector2f(-self.vel.y, self.vel.x)
            n = math.sqrt(math.pow(-self.vel.y,2)+math.pow(self.vel.x,2))
            self.normal_vel.x /= n 
            self.normal_vel.y /= n
        else:
            self.normal_vel = Vector2f(0,0)

    def draw(self, renderer):
        #
        i = 0
        for p in self.trail:
            if p!=None:
                r = self.r-i
                if r <= 0:
                    r = 1
                sdl2.sdlgfx.filledCircleRGBA(renderer, int(p.x), int(p.y), r, 255, 255, 200, 255-i*40)
            i += 1
        
        #sdl2.sdlgfx.aalineColor(renderer, int(self.pos.x), int(self.pos.y),
        #                        int(self.next_pos.x), int(self.next_pos.y), int('0xFF360AF4',16))
        
        # x1 = self.pos.x + self.normal_vel.x*self.r
        # y1 = self.pos.y + self.normal_vel.y*self.r
        # x2 = x1 + self.vel.x
        # y2 = y1 + self.vel.y
        # sdl2.sdlgfx.aalineColor(renderer, int(x1), int(y1), int(x2), int(y2), int('0xFF360AF4',16))
        # x1 = self.pos.x - self.normal_vel.x*self.r
        # y1 = self.pos.y - self.normal_vel.y*self.r
        # x2 = x1 + self.vel.x
        # y2 = y1 + self.vel.y
        # sdl2.sdlgfx.aalineColor(renderer, int(x1), int(y1), int(x2), int(y2), int('0xFF360AF4',16))

    def updatePosition(self):
        self.pos.x = self.next_pos.x
        self.pos.y = self.next_pos.y
        self.trail.insert(0,Vector2f(self.pos.x,self.pos.y))
        self.trail.pop(4)

    def computeNextPos(self):
        self.next_pos = self.pos + self.vel

    def launch(self, vx):

        if vx==0.0:
            while True:
                ia = randint(80, 100)
                if ia<89 or ia>91:
                    break
            a = -(math.pi*ia)/180.0
            self.setVelocity(Vector2f( 9.5*math.cos(a), 9.5*math.sin(a)))
        else:
            self.setVelocity(Vector2f( vx, 9.0))

        self.computeNextPos()
        self.fstandby = False

    def hitBrick(self, br: Brick, offSetX:float, offSetY:float):

        x1 = self.pos.x + offSetX
        y1 = self.pos.y + offSetY
        x2 = self.next_pos.x + offSetX
        y2 = self.next_pos.y + offSetY

        if br.contain(x2,y2):
            q1 = (x1, y1)
            q2 = (x2, y2)
            
            if br.contain(x1,y1):
                self.setVelocity(Vector2f(-self.vel.x,-self.vel.y))
                self.computeNextPos()
                self.updatePosition()
                return True

            elif x1<br.left and y1<br.top:
                # top left corner

                p1 = (br.left, br.top)
                p2 = (br.right, br.top)
                ptInter = compute_intersection(p1, p2, q1, q2)
                if ptInter!=None:
                    self.setVelocity(Vector2f(self.vel.x,-self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True

                p1 = (br.left, br.top)
                p2 = (br.left, br.bottom)
                ptInter = compute_intersection(p1, p2, q1, q2)
                if ptInter!=None:
                    self.setVelocity(Vector2f(-self.vel.x,self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True

                self.setVelocity(Vector2f(-self.vel.x,-self.vel.y))
                self.computeNextPos()
                self.updatePosition()
                return True

            elif x1>br.right and y1<br.top:
                # top right corner

                p1 = (br.left, br.top)
                p2 = (br.right, br.top)
                ptInter = compute_intersection(p1, p2, q1, q2)
                if ptInter!=None:
                    self.setVelocity(Vector2f(self.vel.x,-self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True

                p1 = (br.right, br.top)
                p2 = (br.right, br.bottom)
                ptInter = compute_intersection(p1, p2, q1, q2)
                if ptInter!=None:
                    self.setVelocity(Vector2f(-self.vel.x,self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True

                self.setVelocity(Vector2f(-self.vel.x,-self.vel.y))
                self.computeNextPos()
                self.updatePosition()
                return True

            elif x1<br.left and y1>br.bottom:
                # bottom left corner

                p1 = (br.left, br.bottom)
                p2 = (br.right, br.bottom)
                ptInter = compute_intersection(p1, p2, q1, q2)
                if ptInter!=None:
                    self.setVelocity(Vector2f(self.vel.x,-self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True

                p1 = (br.left, br.top)
                p2 = (br.left, br.bottom)
                ptInter = compute_intersection(p1, p2, q1, q2)
                if ptInter!=None:
                    self.setVelocity(Vector2f(-self.vel.x,self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True

                self.setVelocity(Vector2f(-self.vel.x,-self.vel.y))
                self.computeNextPos()
                self.updatePosition()
                return True

            elif x1>br.right and y1>br.bottom:
                # bottom right corner

                p1 = (br.right, br.top)
                p2 = (br.right, br.bottom)
                ptInter = compute_intersection(p1, p2, q1, q2)
                if ptInter!=None:
                    self.setVelocity(Vector2f(-self.vel.x,self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True

                p1 = (br.left, br.bottom)
                p2 = (br.right, br.bottom)
                ptInter = compute_intersection(p1, p2, q1, q2)
                if ptInter!=None:
                    self.setVelocity(Vector2f(self.vel.x,-self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True
                
                self.setVelocity(Vector2f(-self.vel.x,-self.vel.y))
                self.computeNextPos()
                self.updatePosition()
                return True

            if y1>br.bottom:
                # Come from bottom

                p1 = (br.left, br.bottom)
                p2 = (br.right, br.bottom)
                ptInter = compute_intersection(p1, p2, q1, q2)
                if ptInter!=None:
                    self.setVelocity(Vector2f(self.vel.x,-self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True
            elif y1<br.top:
                # Come from top
                p1 = (br.left, br.top)
                p2 = (br.right, br.top)
                ptInter = compute_intersection(p1, p2, q1, q2)
                if ptInter!=None:
                    self.setVelocity(Vector2f(self.vel.x,-self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True
                
            if x1<br.left:
                # Come from left
                p1 = (br.left, br.top)
                p2 = (br.left, br.bottom)
                ptInter = compute_intersection(p1, p2, q1, q2)
                if ptInter!=None:
                    self.setVelocity(Vector2f(-self.vel.x,self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True
            elif x1>br.right:
                # Come from right
                p1 = (br.right, br.top)
                p2 = (br.right, br.bottom)
                ptInter = compute_intersection(p1, p2, q1, q2)
                if ptInter!=None:
                    self.setVelocity(Vector2f(-self.vel.x,self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True
                
        return False


class Bonus:

    texture = None

    def __init__(self, type:int, x:int =0, y:int =0, w:int =40, h:int =12):
        self.pos = Vector2f( x, y)
        self.vel = Vector2f( 0, 4.0)
        self.w = w
        self.h = h
        self.type = type
        self.iAnim = 0
        self.startTimeAnim = sdl2.timer.SDL_GetTicks()
        self.fdelete = False
        self.colors = []
        self.colors.append(0x00)
        self.colors.append(int('0xFFEF662E',16))
        self.colors.append(int('0xFFEA0CFA',16))
        self.colors.append(int('0xFF0CFA1D',16))
        self.colors.append(int('0xFFEF662E',16))
        self.colors.append(int('0xFFEA0CFA',16))
        self.colors.append(int('0xFF0CFA1D',16))

    def draw(self, renderer):
        if self.type<=3:
            if self.texture!=None:
                src_rect = sdl2.SDL_Rect(x=(self.type-1)*51, y=(self.iAnim % 3)*20, w=50, h=20)
                dest_rect = sdl2.SDL_Rect(x=int(self.pos.x), y=int(self.pos.y),
                                        w=int(50), h=int(20))
                sdl2.SDL_RenderCopy(renderer,self.texture,src_rect,dest_rect)
        else:
            sdl2.sdlgfx.roundedBoxColor(renderer, int(self.pos.x), int(self.pos.y), 
                        int(self.pos.x+self.w), int(self.pos.y+self.h), int(8), self.colors[self.type])
   
    def updatePosition(self):
        self.pos += self.vel

    def updateAnim(self):
        nbTicks = sdl2.timer.SDL_GetTicks()
        if (nbTicks-self.startTimeAnim)>250:
            self.startTimeAnim = nbTicks
            self.iAnim += 1
        

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

    def setMediumSize(self):
        self.w = 80
        self.h = 14
        self.w_2 = self.w/2
        self.isize = 1

    def setBigSize(self):
        self.w = 104
        self.h = 14
        self.w_2 = self.w/2
        self.isize = 2

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
    
    def left(self):
        return self.pos.x - self.w
    
    def right(self):
        return self.pos.x + self.w

    def top(self):
        return self.pos.y

    def bottom(self):
        return self.pos.y + self.h


class Game:
    
    def __init__(self, renderer, shipTextures=None, mediumFont=None):
        self.frame = Rectf(0,0,WIN_WIDTH,WIN_HEIGHT)
        self.lifes = 3
        self.renderer = renderer
        self.shipTextures = shipTextures
        self.fpause = False
        filepath = os.path.abspath(os.path.dirname(__file__))
        RESOURCES = sdl2.ext.Resources(filepath, "resources")
        font_path = RESOURCES.get_path("sansation.ttf")
        self.mediumFont = sdl2.sdlttf.TTF_OpenFont(font_path.encode("utf8"), 18)
        if self.mediumFont==None:
            err = sdl2.sdlttf.TTF_GetError()
            raise RuntimeError("Error initializing the ttf: {0}".format(err))
        #
        self.score = 0
        self.score_text_w = 0
        self.score_text_h = 0
        self.score_text_x = 0
        self.score_text_y = 0
        self.scoreTexture = None
        self.init()


    def __del__(self):
        # body of destructor
        if self.mediumFont!=None:
            sdl2.sdlttf.TTF_CloseFont(self.mediumFont)
        if self.scoreTexture!=None:
            sdl2.SDL_DestroyTexture(self.scoreTexture)


    def init(self):
        self.lifes = 3
        self.curLevel = 1
        self.loadLevel(1)
        self.tempScore = 0
        self.deleteBrick = None
        self.score = 0
        self.updateScoreTexture()


    def loadLevel(self, iLevel: int =0):
        self.tbl = []
        fileName = "Level{il:02d}.txt".format(il=iLevel)
        with open(fileName, 'r') as inF:
            iLin = 0
            lin = inF.readline()
            while lin:
                if lin != "" and lin != "\n":
                    self.nbColumns = len(lin)-1
                    y = iLin * BRICK_HEIGHT
                    for i,c in enumerate(lin):
                        if c!='\n':
                            x = i * BRICK_WIDTH
                            if c=='A':
                                t = 10
                            else:
                                t = int(c)
                            if t==0:
                                self.tbl.append(None)
                            else:
                                self.tbl.append(Brick( x, y, t))
                    iLin += 1
                lin = inF.readline()
            self.nbRows = iLin

    def nextLevel(self):
        self.curLevel += 1
        self.loadLevel(self.curLevel)

    def updateScoreTexture(self):
        sdl2.sdlttf.TTF_SetFontStyle(self.mediumFont, sdl2.sdlttf.TTF_STYLE_BOLD)
        text = "SCORE : {:06d}".format(self.score)
        text_w, text_h = c_int(0), c_int(0)
        sdl2.sdlttf.TTF_SizeText(self.mediumFont, text.encode("utf-8"), text_w, text_h)
        self.score_text_w = text_w.value
        self.score_text_h = text_h.value
        self.score_text_x = self.frame.right()-self.score_text_w-8
        self.score_text_y = self.frame.bottom()-self.score_text_h-8
        textSurface = sdl2.sdlttf.TTF_RenderText_Solid(self.mediumFont, text.encode("utf-8"), sdl2.SDL_Color(255,255,0,255))
        self.scoreTexture = sdl2.SDL_CreateTextureFromSurface(self.renderer, textSurface)
        sdl2.SDL_FreeSurface(textSurface)

    def draw(self):
        # Bricks
        for l in range(0,self.nbRows):
            for c in range(0,self.nbColumns):
                b = self.tbl[l*self.nbColumns+c]
                if b!=None:
                    b.draw(self.renderer)
                    #sdl2.sdlgfx.roundedBoxColor(renderer, int(b.left+1), int(b.top+1), 
                    #            int(b.right-1), int(b.bottom-1), int(2), self.colors[b.type])
        # Remain lifes
        if self.shipTextures!=None:
            y = WIN_HEIGHT - 20
            for i in range(0,self.lifes):
                src_rect = sdl2.SDL_Rect(x=0, y=0, w=64, h=14)
                x = i * 40 + 10
                dest_rect = sdl2.SDL_Rect(x=int(x), y=int(y), w=32, h=8)
                sdl2.SDL_RenderCopy(self.renderer,self.shipTextures,src_rect,dest_rect)

        if self.scoreTexture!=None:
            src_rect = sdl2.SDL_Rect(x=0, y=0, w=self.score_text_w, h=self.score_text_h)
            dest_rect = sdl2.SDL_Rect(x=int(self.score_text_x), y=int(self.score_text_y), w=self.score_text_w, h=self.score_text_h)
            sdl2.SDL_RenderCopy(self.renderer,self.scoreTexture,src_rect,dest_rect)

    def isLevelCompleted(self)->bool:
        """ Check if current level is completed"""
        for b in self.tbl:
            if b!=None:
                return False
        self.nextLevel()
        return True

    def doBricksHit(self, b: Ball):
        for i,br in enumerate(self.tbl):
            if br!=None:

                offSetX = 0.0
                offSetY = 0.0
                if b.hitBrick(br, offSetX, offSetY):
                    if br.resistance==1:
                        self.tbl[i] = None
                        self.deleteBrick = br
                        self.tempScore += randint(50, 150)
                        self.score += br.values[br.type]
                        self.updateScoreTexture()
                    else:
                        self.tbl[i].resistance -= 1
                    return True

                offSetX = b.normal_vel.x * b.r
                offSetY = b.normal_vel.y * b.r
                if b.hitBrick(br, offSetX, offSetY):
                    if br.resistance==1:
                        self.tbl[i] = None
                        self.deleteBrick = br
                        self.tempScore += randint(50, 150)
                        self.score += br.values[br.type]
                        self.updateScoreTexture()
                    else:
                        self.tbl[i].resistance -= 1
                    return True

                offSetX = -b.normal_vel.x * b.r
                offSetY = -b.normal_vel.y * b.r
                if b.hitBrick(br, offSetX, offSetY):
                    if br.resistance==1:
                        self.tbl[i] = None
                        self.deleteBrick = br
                        self.tempScore += randint(50, 150)
                        self.score += br.values[br.type]
                        self.updateScoreTexture()
                    else:
                        self.tbl[i].resistance -= 1
                    return True

        return False
    
    def doFrameHit(self,b:Ball):
        x1 = b.pos.x
        y1 = b.pos.y
        x2 = b.next_pos.x
        y2 = b.next_pos.y

        if self.frame.contains(x1,y1):

            if not self.frame.contains(x2,y2):
                if x2 <= 0:
                    if y2 >=0 and y2<=WIN_HEIGHT: 
                        q1 = (x1, y1)
                        q2 = (x2, y2)
                        p1 = (0, 0)
                        p2 = (0, WIN_HEIGHT)
                        ptInter = compute_intersection(p1, p2, q1, q2)
                        if ptInter!=None:
                            b.setVelocity(Vector2f(-b.vel.x,b.vel.y))
                            b.next_pos.x = ptInter[0]
                            b.next_pos.y = ptInter[1]
                            b.updatePosition()
                    else:
                        b.setVelocity(Vector2f(-b.vel.x,-b.vel.y))
                    b.computeNextPos()
                    return True
                elif x2 >= WIN_WIDTH:
                    if y2 >=0 and y2<=WIN_HEIGHT: 
                        q1 = (x1, y1)
                        q2 = (x2, y2)
                        p1 = (WIN_WIDTH, 0)
                        p2 = (WIN_WIDTH, WIN_HEIGHT)
                        ptInter = compute_intersection(p1, p2, q1, q2)
                        if ptInter!=None:
                            b.setVelocity(Vector2f(-b.vel.x,b.vel.y))
                            b.next_pos.x = ptInter[0]
                            b.next_pos.y = ptInter[1]
                            b.updatePosition()
                    else:
                        b.setVelocity(Vector2f(-b.vel.x,-b.vel.y))
                    b.computeNextPos()
                    return True
                elif y2 <= 0:
                    if x2 >=0 and x2<=WIN_WIDTH: 
                        q1 = (x1, y1)
                        q2 = (x2, y2)
                        p1 = (0, 0)
                        p2 = (WIN_WIDTH, 0)
                        ptInter = compute_intersection(p1, p2, q1, q2)
                        if ptInter!=None:
                            b.setVelocity(Vector2f(b.vel.x,-b.vel.y))
                            b.next_pos.x = ptInter[0]
                            b.next_pos.y = ptInter[1]
                        b.updatePosition()
                    else:
                        b.setVelocity(Vector2f(-b.vel.x,-b.vel.y))
                    b.computeNextPos()
                    return True
                elif y2 >= WIN_HEIGHT:
                    if x2 >=0 and x2<=WIN_WIDTH: 
                        q1 = (x1, y1)
                        q2 = (x2, y2)
                        p1 = (0, WIN_HEIGHT)
                        p2 = (WIN_WIDTH, WIN_HEIGHT)
                        ptInter = compute_intersection(p1, p2, q1, q2)
                        if ptInter!=None:
                            b.setVelocity(Vector2f(b.vel.x,-b.vel.y))
                            b.next_pos.x = ptInter[0]
                            b.next_pos.y = ptInter[1]
                            b.updatePosition()
                    else:
                        b.setVelocity(Vector2f(-b.vel.x,-b.vel.y))
                    b.computeNextPos()
                    return True
        else:
            if not self.frame.contains(x2,y2):
                b.setVelocity(Vector2f(-b.vel.x,-b.vel.y))
                b.computeNextPos()
                return True

        return  False
    

def loadTexture(filePath, renderer):
    # loads bmp image
    # str.encode() converts string to byte type
    loadedImage = sdl2.SDL_LoadBMP(str.encode(filePath))

    if loadedImage:
        # creates texture from loadedImage
        texture = sdl2.SDL_CreateTextureFromSurface(renderer, loadedImage)
        # free the loadedImage
        sdl2.SDL_FreeSurface(loadedImage)

        if not texture:
            # error check to make sure texture loaded
            print("SDL_CreateTextureFromSurface")
    else:
        print("SDL_LoadBMP failed")
    return texture


def orientation(p, q, r):
    """Returns the orientation of the ordered triplet (p, q, r)."""
    val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
    if val == 0:
        return 0  # collinear
    elif val > 0:
        return 1  # clockwise
    else:
        return 2  # counterclockwise


def on_segment(p, q, r):
    """Checks if point q lies on segment pr."""
    if min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and min(p[1], r[1]) <= q[1] <= max(p[1], r[1]):
        return True
    return False


def compute_intersection(p1, p2, q1, q2):
    """Computes the intersection point of two line segments (if any)."""
    # Compute the orientation of the ordered triplets
    o1 = orientation(p1, p2, q1)
    o2 = orientation(p1, p2, q2)
    o3 = orientation(q1, q2, p1)
    o4 = orientation(q1, q2, p2)

    # General case: the segments straddle each other
    if o1 != o2 and o3 != o4:
        # Solve for the intersection point
        denom = (p1[0] - p2[0]) * (q1[1] - q2[1]) - (p1[1] - p2[1]) * (q1[0] - q2[0])
        num1 = (p1[0] * p2[1] - p1[1] * p2[0])
        num2 = (q1[0] * q2[1] - q1[1] * q2[0])
        
        intersect_x = (num1 * (q1[0] - q2[0]) - (p1[0] - p2[0]) * num2) / denom
        intersect_y = (num1 * (q1[1] - q2[1]) - (p1[1] - p2[1]) * num2) / denom
        
        return (intersect_x, intersect_y)
    
    # Special cases for collinear segments where the intersection lies on the segment
    # p1, p2, q1 are collinear and q1 lies on segment p1p2
    if o1 == 0 and on_segment(p1, q1, p2):
        return q1
    # p1, p2, q2 are collinear and q2 lies on segment p1p2
    if o2 == 0 and on_segment(p1, q2, p2):
        return q2
    # q1, q2, p1 are collinear and p1 lies on segment q1q2
    if o3 == 0 and on_segment(q1, p1, q2):
        return p1
    # q1, q2, p2 are collinear and p2 lies on segment q1q2
    if o4 == 0 and on_segment(q1, p2, q2):
        return p2
    
    return None  # No intersection


def test_not_intersect():
    p1 = (1, 1)
    p2 = (10, 1)
    q1 = (1, 2)
    q2 = (10, 2)
    intersection = compute_intersection(p1, p2, q1, q2)
    if intersection:
        print(f"The segments intersect at: {intersection}")
    else:
        print("The segments do not intersect.")


def test_intersect():
    p1 = (1, 1)
    p2 = (10, 10)
    q1 = (1, 10)
    q2 = (10, 1)
    intersection = compute_intersection(p1, p2, q1, q2)
    if intersection:
        print(f"The segments intersect at: {intersection}")
    else:
        print("The segments do not intersect.")


def run():

    # initialize
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO|sdl2.SDL_INIT_TIMER|sdl2.SDL_INIT_AUDIO)

    filepath = os.path.abspath(os.path.dirname(__file__))
    RESOURCES = sdl2.ext.Resources(filepath, "resources")

    # Initialize a 44.1 kHz 16-bit stereo mixer with a 1024-byte buffer size
    ret = sdl2.sdlmixer.Mix_OpenAudio(44100, sdl2.AUDIO_S16SYS, 2, 2*1024)
    if ret < 0:
        err = sdl2.sdlmixer.Mix_GetError().decode("utf8")
        raise RuntimeError("Error initializing the mixer: {0}".format(err))
    
    sound_path = RESOURCES.get_path("02_-_Arkanoid_-_ARC_-_Game_Start.ogg")
    startSound = sdl2.sdlmixer.Mix_LoadWAV(sound_path.encode("utf8"))
    if startSound!=None:
        sdl2.sdlmixer.Mix_VolumeChunk(startSound,25)
        sdl2.sdlmixer.Mix_PlayChannel(-1, startSound, 0)

    sound_path = RESOURCES.get_path("Arkanoid SFX (1).wav")
    bouncingSound = sdl2.sdlmixer.Mix_LoadWAV(sound_path.encode("utf8"))
    if bouncingSound!=None:
        sdl2.sdlmixer.Mix_VolumeChunk(bouncingSound,5)
        #sdl2.sdlmixer.Mix_PlayChannel(-1, bounceSound, 0)

    sound_path = RESOURCES.get_path("Arkanoid SFX (2).wav")
    laserSound = sdl2.sdlmixer.Mix_LoadWAV(sound_path.encode("utf8"))
    if laserSound!=None:
        sdl2.sdlmixer.Mix_VolumeChunk(laserSound,5)
        #sdl2.sdlmixer.Mix_PlayChannel(-1, bounceSound, 0)


    sound_path = RESOURCES.get_path("Arkanoid SFX (6).wav")
    bonusSound = sdl2.sdlmixer.Mix_LoadWAV(sound_path.encode("utf8"))
    if bonusSound!=None:
        sdl2.sdlmixer.Mix_VolumeChunk(bonusSound,16)
        #sdl2.sdlmixer.Mix_PlayChannel(-1, bonusSound, 0)

    sound_path = RESOURCES.get_path("Arkanoid SFX (8).wav")
    catchSound = sdl2.sdlmixer.Mix_LoadWAV(sound_path.encode("utf8"))
    if catchSound!=None:
        sdl2.sdlmixer.Mix_VolumeChunk(catchSound,20)

    sound_path = RESOURCES.get_path("Arkanoid SFX (9).wav")
    succesSound = sdl2.sdlmixer.Mix_LoadWAV(sound_path.encode("utf8"))
    if succesSound!=None:
        sdl2.sdlmixer.Mix_VolumeChunk(succesSound,20)

    sound_path = RESOURCES.get_path("Arkanoid SFX (10).wav")
    faillureSound = sdl2.sdlmixer.Mix_LoadWAV(sound_path.encode("utf8"))
    if faillureSound!=None:
        sdl2.sdlmixer.Mix_VolumeChunk(faillureSound,20)

    sound_path = RESOURCES.get_path("Arkanoid SFX (11).wav")
    gameOverSound = sdl2.sdlmixer.Mix_LoadWAV(sound_path.encode("utf8"))
    if gameOverSound!=None:
        sdl2.sdlmixer.Mix_VolumeChunk(gameOverSound,20)

    sdl2.sdlttf.TTF_Init()


    # create window
    win = sdl2.SDL_CreateWindow(b"Breakout PySDL",
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            WIN_WIDTH, WIN_HEIGHT, sdl2.SDL_WINDOW_SHOWN)

    # create renderer
    renderer = sdl2.SDL_CreateRenderer(win, -1, sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)

    image_path = RESOURCES.get_path("SpaceShip.png")
    surface = sdl2.ext.image.load_image(image_path.encode('utf-8'))
    if not surface:
        print(f"Failed to create texture: {sdl2.SDL_GetError()}")
        exit()

    # Create a texture from the surface
    textureShip = sdl2.SDL_CreateTextureFromSurface(renderer, surface)
    sdl2.SDL_FreeSurface(surface)  # Free the surface as it's no longer needed
    if not textureShip:
        print(f"Failed to create texture: {sdl2.SDL_GetError()}")
        exit()


    image_path = RESOURCES.get_path("Bricks.png")
    surface = sdl2.ext.image.load_image(image_path.encode('utf-8'))
    if not surface:
        print(f"Failed to create texture: {sdl2.SDL_GetError()}")
        exit()

    # Create a texture from the surface
    textureBrick = sdl2.SDL_CreateTextureFromSurface(renderer, surface)
    sdl2.SDL_FreeSurface(surface)  # Free the surface as it's no longer needed
    if not textureBrick:
        print(f"Failed to create texture: {sdl2.SDL_GetError()}")
        exit()
    Brick.texture = textureBrick

    image_path = RESOURCES.get_path("Bonus.png")
    surface = sdl2.ext.image.load_image(image_path.encode('utf-8'))
    if not surface:
        print(f"Failed to create texture: {sdl2.SDL_GetError()}")
        exit()

    # Create a texture from the surface
    textureBonus = sdl2.SDL_CreateTextureFromSurface(renderer, surface)
    sdl2.SDL_FreeSurface(surface)  # Free the surface as it's no longer needed
    if not textureBonus:
        print(f"Failed to create texture: {sdl2.SDL_GetError()}")
        exit()
    Bonus.texture = textureBonus

    #
    game =Game( renderer, textureShip)

    #
    listBonus = []

    #
    listBalls = []
    listBalls.append(Ball(WIN_WIDTH/2, WIN_HEIGHT-44, 4))

    #
    playerShip = Ship(WIN_WIDTH/2, WIN_HEIGHT-64, textureShip)

    velocityH = 0

    startTimeH = sdl2.timer.SDL_GetTicks()

    lastMouseXrel = 0
    lastMouseX = 0

    # run event loop
    running = True

    while running:

        events = sdl2.ext.get_events()
        for event in events:
            match event.type :
                case sdl2.SDL_QUIT:
                    running = False
                case sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_LEFT and event.key.repeat==False:
                        velocityH = -1
                    elif event.key.keysym.sym == sdl2.SDLK_RIGHT and event.key.repeat==False:
                        velocityH = 1
                    elif event.key.keysym.sym == sdl2.SDLK_ESCAPE and event.key.repeat==False:
                        running = False
                    elif event.key.keysym.sym == sdl2.SDLK_p and event.key.repeat==False:
                        game.fpause ^= True
                    elif event.key.keysym.sym == sdl2.SDLK_a and event.key.repeat==False:
                        listBalls.append(Ball(WIN_WIDTH/2, WIN_HEIGHT-44, 4))
                case sdl2.SDL_KEYUP:
                    if event.key.keysym.sym == sdl2.SDLK_LEFT and event.key.repeat==False:
                        velocityH = 0
                    elif event.key.keysym.sym == sdl2.SDLK_RIGHT and event.key.repeat==False:
                        velocityH = 0
                case sdl2.SDL_MOUSEBUTTONDOWN:
                    bstate = sdl2.ext.mouse.mouse_button_state()
                    if bstate.left==1:
                        for b in listBalls:
                            if b.fstandby:
                                if playerShip.hSpeed<-6:
                                    vx = -2
                                elif playerShip.hSpeed>6:
                                    vx = 2
                                else:
                                    vx = 0.0
                                b.launch(float(vx))
                                break
                case sdl2.SDL_MOUSEMOTION:
                    motion = event.motion
                    lastMouseX = motion.x
                    if lastMouseXrel != motion.xrel:
                        lastMouseXrel = motion.xrel
                        fmouseMove = True
                    else:
                        fmouseMove = False

        #--------------------------------------------------------
        # Update objects states

        # Update ship position
        nbTicks = sdl2.timer.SDL_GetTicks()
        if (nbTicks-startTimeH)>20:
            startTimeH = nbTicks
            if velocityH<0:
                playerShip.moveLeft(8)
            elif velocityH>0:
                playerShip.moveRight(8)
            else:
                playerShip.last_pos.x = playerShip.pos.x
                playerShip.pos.x = lastMouseX

        playerShip.updateState()

        # Update standby balls positions from ship
        for b in listBalls:
            if b.fstandby:
                b.next_pos.x = playerShip.pos.x
                b.next_pos.y = playerShip.pos.y - b.r
                b.updatePosition()


        #
        if not game.fpause:

            # Manage balls
            for b in listBalls:
                if not b.fstandby:
                    #
                    if b.pos.y>(playerShip.pos.y+3*playerShip.h):
                        b.fdelete = True # delete ball
                        continue

                    # Check Ball Ship collision
                    ptIntersection = playerShip.hitBall(b)
                    if ptIntersection!=None:
                        if bouncingSound != None:
                            sdl2.sdlmixer.Mix_PlayChannel(-1, bouncingSound, 0)
                        vx = b.vel.x
                        vy = -b.vel.y
                        dx = 0
                        if playerShip.hSpeed<-6:
                            dx = -2
                        elif playerShip.hSpeed>6:
                            dx = 2
                        if dx!=0:
                            n = math.sqrt(vx*vx+vy*vy)
                            vx += dx
                            n1 = math.sqrt(vx*vx+vy*vy)
                            vx = vx/n1*n
                            vy = vy/n1*n
                        x1 = ptIntersection[0]
                        y1 = ptIntersection[1]
                        # check if next_pos is in frame
                        x2 = x1 + vx
                        y2 = y1 + vy
                        if not game.frame.contains(x2,y2):
                            b.setVelocity(Vector2f(-math.fabs(vx), -math.fabs(vy)))
                        else:
                            b.setVelocity(Vector2f(vx, vy))
                        b.pos.x = x1
                        b.pos.y = y1
                        b.computeNextPos()
                        b.updatePosition()

                    # Check Frame ball collision
                    if not game.doFrameHit(b):
                        b.updatePosition()
                        b.computeNextPos()
                    else:
                        if bouncingSound != None:
                            sdl2.sdlmixer.Mix_PlayChannel(-1, bouncingSound, 0)

                    # generate bonus
                    if game.tempScore>800:
                        if bonusSound != None:
                            sdl2.sdlmixer.Mix_PlayChannel(-1, bonusSound, 0)
                        game.tempScore = 0
                        listBonus.append(Bonus(randint(1, 4),game.deleteBrick.left+10,game.deleteBrick.top+5,
                                                game.deleteBrick.right-game.deleteBrick.left-20,
                                                game.deleteBrick.bottom-game.deleteBrick.top-10
                                                ))

                    #
                    if game.doBricksHit(b):
                        if bouncingSound != None:
                            sdl2.sdlmixer.Mix_PlayChannel(-1, bouncingSound, 0)
                        if game.isLevelCompleted():
                            listBalls = []
                            listBonus = []
                            listBalls.append(Ball(WIN_WIDTH/2, WIN_HEIGHT-44, 4))
                            playerShip.setMediumSize()
                            if succesSound != None:
                                sdl2.sdlmixer.Mix_PlayChannel(-1, succesSound, 0)

            listBalls[:] = [b for b in listBalls if b.fdelete==False]

            # Check for Game Over
            if len(listBalls)==0:
                if game.lifes>0:
                    game.lifes -= 1
                    listBalls.append(Ball(WIN_WIDTH/2, WIN_HEIGHT-44, 4))
                    playerShip.setMediumSize()
                    if faillureSound != None:
                        sdl2.sdlmixer.Mix_PlayChannel(-1, faillureSound, 0)
                else:
                    # Game Over
                    game.init()
                    listBalls = []
                    listBonus = []
                    listBalls.append(Ball(WIN_WIDTH/2, WIN_HEIGHT-44, 4))
                    playerShip.setMediumSize()
                    if gameOverSound != None:
                        sdl2.sdlmixer.Mix_PlayChannel(-1, gameOverSound, 0)

            # Manage Bonus      
            sLeft = playerShip.left()
            sTop = playerShip.top()
            sRight = playerShip.right()
            sBottom = playerShip.bottom()
            for b in listBonus:

                #
                if not game.frame.contains(b.pos.x,b.pos.y):
                    b.fdelete = True
                    continue
                else:
                    b.updatePosition()

                # check ship hit bonus
                if b.pos.y>sTop and b.pos.y<sBottom:
                    bLeft = b.pos.x
                    bRight = bLeft + b.w
                    if ((bLeft>sLeft and bLeft<sRight) or
                        (bRight>sLeft and bRight<sRight)):
                        if catchSound != None:
                            sdl2.sdlmixer.Mix_PlayChannel(-1, catchSound, 0)
                        if b.type==1:
                            playerShip.setBigSize()
                        elif b.type==2:
                            playerShip.setSmallSize()
                        else:
                            playerShip.setMediumSize()
                        b.fdelete = True
                else:
                    b.updateAnim()

            listBonus[:] = [b for b in listBonus if b.fdelete==False]

            
        #---------------------------------------
        # Draw game objects
        sdl2.SDL_SetRenderDrawColor(renderer, 30, 30, 80, sdl2.SDL_ALPHA_OPAQUE)
        sdl2.SDL_RenderClear(renderer)

        #
        game.draw()

        #
        for b in listBalls:
            b.draw(renderer)

        #
        playerShip.draw(renderer)

        #
        for b in listBonus:
            b.draw(renderer)

        #
        sdl2.SDL_RenderPresent(renderer)
        sdl2.SDL_Delay(20)


    # clean up
    sdl2.SDL_DestroyTexture(textureShip)  # Destroy the texture
    sdl2.SDL_DestroyTexture(textureBrick)  # Destroy the texture
    sdl2.SDL_DestroyTexture(textureBonus)  # Destroy the texture
    sdl2.SDL_DestroyRenderer(renderer)
    sdl2.SDL_DestroyWindow(win)
    sdl2.sdlmixer.Mix_CloseAudio()
    sdl2.sdlttf.TTF_Quit()
    sdl2.SDL_Quit()


if __name__ == "__main__":
    sys.exit(run())

