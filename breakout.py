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
import ctypes
from ctypes import c_int, byref

from enum import Enum

from gameconst import *

from utils import compute_intersection
from vector2f import Vector2f
from rectf import Rectf
from ball import Ball
from brick import Brick
from ship import Ship
from bonus import Bonus

from dataclasses import dataclass

#pip install -U --break-system-packages  git+https://github.com/py-sdl/py-sdl2.git

class GameMode(Enum):
    STAND_BY = 1
    PLAY = 2
    HIGH_SCORE = 3
    GAME_OVER = 4


@dataclass
class HighScore:
    player: str
    score: int


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
        self.bigFont = sdl2.sdlttf.TTF_OpenFont(font_path.encode("utf8"), 20)
        if self.bigFont==None:
            err = sdl2.sdlttf.TTF_GetError()
            raise RuntimeError("Error Loading font: {0}".format(err))
        self.bigBigFont = sdl2.sdlttf.TTF_OpenFont(font_path.encode("utf8"), 24)
        if self.bigBigFont==None:
            err = sdl2.sdlttf.TTF_GetError()
            raise RuntimeError("Error Loading font: {0}".format(err))

        self.standbyTexture = None
        self.creStandbyTexMsg()

        self.gameOverTexture = None
        self.creGameOverTexMsg()

        #
        self.score = 0
        self.score_text_w = 0
        self.score_text_h = 0
        self.score_text_x = 0
        self.score_text_y = 0
        self.scoreTexture = None
        self.init()

        self.velocityH = 0
        self.lastMouseX = WIN_WIDTH/2

        self.processEvent = self.processStandby
        self.drawGame = self.drawStandbyMode

        #
        self.listBonus = []

        #
        self.listBalls = []
        self.listBalls.append(Ball(WIN_WIDTH/2, WIN_HEIGHT-44, 4))
        
        self.playerShip = Ship(WIN_WIDTH/2, WIN_HEIGHT-64, shipTextures)

        self.mode = GameMode.STAND_BY

        #
        self.player = ''
        self.ihighScore = -1
        self.ihighScoreColorText = 0
        self.highScoreTimer = sdl2.timer.SDL_GetTicks()
        self.listHighScores = [
            HighScore('',0),
            HighScore('',0),
            HighScore('',0),
            HighScore('',0),
            HighScore('',0),
            HighScore('',0),
            HighScore('',0),
            HighScore('',0),
            HighScore('',0),
            HighScore('',0)
        ]

        self.tblKeys =	{
                sdl2.SDLK_a : 'A',
                sdl2.SDLK_b : 'B',
                sdl2.SDLK_c : 'C',
                sdl2.SDLK_d : 'D',
                sdl2.SDLK_e : 'E',
                sdl2.SDLK_f : 'F',
                sdl2.SDLK_g : 'G',
                sdl2.SDLK_h : 'H',
                sdl2.SDLK_i : 'I',
                sdl2.SDLK_j : 'J',
                sdl2.SDLK_k : 'K',
                sdl2.SDLK_l : 'L',
                sdl2.SDLK_m : 'M',
                sdl2.SDLK_n : 'N',
                sdl2.SDLK_o : 'O',
                sdl2.SDLK_p : 'P',
                sdl2.SDLK_q : 'Q',
                sdl2.SDLK_r : 'R',
                sdl2.SDLK_s : 'S',
                sdl2.SDLK_t : 'T',
                sdl2.SDLK_u : 'U',
                sdl2.SDLK_v : 'V',
                sdl2.SDLK_x : 'X',
                sdl2.SDLK_y : 'Y',
                sdl2.SDLK_z : 'Z',
                sdl2.SDLK_0 : '0',
                sdl2.SDLK_1 : '1',
                sdl2.SDLK_2 : '2',                
                sdl2.SDLK_3 : '3',
                sdl2.SDLK_4 : '4',
                sdl2.SDLK_5 : '5',
                sdl2.SDLK_6 : '6',
                sdl2.SDLK_7 : '7',
                sdl2.SDLK_8 : '8',
                sdl2.SDLK_9 : '9'
                }

    def __del__(self):
        # body of destructor
        if self.mediumFont!=None:
            sdl2.sdlttf.TTF_CloseFont(self.mediumFont)
        if self.bigFont!=None:
            sdl2.sdlttf.TTF_CloseFont(self.bigFont)
        if self.bigBigFont!=None:
            sdl2.sdlttf.TTF_CloseFont(self.bigBigFont)
        if self.scoreTexture!=None:
            sdl2.SDL_DestroyTexture(self.scoreTexture)
        if self.standbyTexture!=None:
            sdl2.SDL_DestroyTexture(self.standbyTexture)
        if self.gameOverTexture!=None:
            sdl2.SDL_DestroyTexture(self.gameOverTexture)


    def init(self):
        self.lifes = 3
        self.curLevel = 1
        self.loadLevel(1)
        self.tempScore = 0
        self.deleteBrick = None
        self.score = 0
        self.updateScoreTexture()

    def loadHighScores(self,fileName):
        with open(fileName, 'r') as inF:
            iLin = 0
            lin = inF.readline()
            while lin and iLin<len(self.listHighScores):
                if lin != "" and lin != "\n":
                    lin.rstrip()
                    words = lin.split(';')
                    self.listHighScores[iLin].player = words[0]
                    self.listHighScores[iLin].score = int(words[1])
                iLin += 1
                lin = inF.readline()

    def saveHighScores(self,fileName):
        with open(fileName, 'w') as outF:
            for h in self.listHighScores:
                strLin = '{};{}\n'.format(h.player,h.score)
                outF.write(strLin)

    def isNewHighScore(self, newScore: int)->bool:
        for i,h in enumerate(self.listHighScores):
            if newScore>=h.score:
                return i
        return -1

    def insertHighScore(self,iscore: int,player: str,score: int):
        i = len(self.listHighScores)-1
        while i>iscore:
            self.listHighScores[i] = self.listHighScores[i-1]
            i -= 1
        self.listHighScores[iscore] = HighScore(player,score)
        
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
        self.score_text_x = self.frame.right-self.score_text_w-8
        self.score_text_y = self.frame.bottom-self.score_text_h-8
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
                        self.score += 50
                        self.updateScoreTexture()
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
                        self.score += 50
                        self.updateScoreTexture()
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
                        self.score += 50
                        self.updateScoreTexture()
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
                        if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
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
                        if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
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
                        if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
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
                        if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
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
    
    def processStandby(self):
        events = sdl2.ext.get_events()
        for event in events:
            match event.type :
                case sdl2.SDL_QUIT:
                    self.running = False
                    return False
                case sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_ESCAPE and event.key.repeat==False:
                        self.running = False
                        return False
                case sdl2.SDL_MOUSEBUTTONDOWN:
                    bstate = sdl2.ext.mouse.mouse_button_state()
                    if bstate.left==1:
                        self.processEvent = self.processPlay
                        self.drawGame = self.drawPlayMode
                        self.mode = GameMode.PLAY
                        return False
        return True


    def processGameOver(self):
        events = sdl2.ext.get_events()
        for event in events:
            match event.type :
                case sdl2.SDL_QUIT:
                    self.running = False
                    return False
                case sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_ESCAPE and event.key.repeat==False:
                        self.running = False
                        return False
                case sdl2.SDL_MOUSEBUTTONDOWN:
                    bstate = sdl2.ext.mouse.mouse_button_state()
                    if bstate.left==1:
                        self.processEvent = self.processStandby
                        self.drawGame = self.drawStandbyMode
                        self.mode = GameMode.STAND_BY
                        return False
        return True

    def processPlay(self):

        #
        def launchBall():
            for b in self.listBalls:
                if b.vel.y==0.0:
                    if self.playerShip.hSpeed<-6:
                        vx = -2
                    elif self.playerShip.hSpeed>6:
                        vx = 2
                    else:
                        vx = 0.0
                    b.launch(float(vx))
                    break

        events = sdl2.ext.get_events()
        for event in events:
            match event.type :
                case sdl2.SDL_QUIT:
                    self.running = False
                case sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_LEFT and event.key.repeat==False:
                        self.velocityH = -1
                    elif event.key.keysym.sym == sdl2.SDLK_RIGHT and event.key.repeat==False:
                        self.velocityH = 1
                    elif event.key.keysym.sym == sdl2.SDLK_ESCAPE and event.key.repeat==False:
                        self.running = False
                    elif event.key.keysym.sym == sdl2.SDLK_p and event.key.repeat==False:
                        self.fpause ^= True
                    #elif event.key.keysym.sym == sdl2.SDLK_a and event.key.repeat==False:
                    #    listBalls.append(Ball(WIN_WIDTH/2, WIN_HEIGHT-44, 4))
                    elif event.key.keysym.sym == sdl2.SDLK_SPACE and event.key.repeat==False:
                        launchBall()
                case sdl2.SDL_KEYUP:
                    if event.key.keysym.sym == sdl2.SDLK_LEFT and event.key.repeat==False:
                        self.velocityH = 0
                    elif event.key.keysym.sym == sdl2.SDLK_RIGHT and event.key.repeat==False:
                        self.velocityH = 0
                case sdl2.SDL_MOUSEBUTTONDOWN:
                    bstate = sdl2.ext.mouse.mouse_button_state()
                    if bstate.left==1:
                        launchBall()
                case sdl2.SDL_MOUSEMOTION:
                    motion = event.motion
                    self.lastMouseX = motion.x

    def creStandbyTexMsg(self):
        sdl2.sdlttf.TTF_SetFontStyle( self.bigFont, sdl2.sdlttf.TTF_STYLE_NORMAL)
        text = "PRESS KEY TO START"
        # ctext_w, ctext_h = c_int(0), c_int(0)
        # sdl2.sdlttf.TTF_SizeText(self.bigFont, text.encode("utf-8"), ctext_w, ctext_h)
        # text_w = ctext_w.value
        # text_h = ctext_h.value
        textSurface = sdl2.sdlttf.TTF_RenderText_Solid(self.bigFont, text.encode("utf-8"), sdl2.SDL_Color(255,255,0,255))
        self.standbyTexture = sdl2.SDL_CreateTextureFromSurface(self.renderer, textSurface)
        sdl2.SDL_FreeSurface(textSurface)

    def creGameOverTexMsg(self):
        sdl2.sdlttf.TTF_SetFontStyle( self.bigFont, sdl2.sdlttf.TTF_STYLE_NORMAL)
        text = "Game Over"
        # ctext_w, ctext_h = c_int(0), c_int(0)
        # sdl2.sdlttf.TTF_SizeText(self.bigFont, text.encode("utf-8"), ctext_w, ctext_h)
        # text_w = ctext_w.value
        # text_h = ctext_h.value
        textSurface = sdl2.sdlttf.TTF_RenderText_Solid(self.bigFont, text.encode("utf-8"), sdl2.SDL_Color(255,255,0,255))
        self.gameOverTexture = sdl2.SDL_CreateTextureFromSurface(self.renderer, textSurface)
        sdl2.SDL_FreeSurface(textSurface)

    def drawStandbyMode(self):
        #
        self.draw()

        #
        for b in self.listBalls:
            b.draw(self.renderer)

        #
        self.playerShip.draw(self.renderer)

        #
        for b in self.listBonus:
            b.draw(self.renderer)

        #
        if self.standbyTexture!=None:
            w, h = ctypes.c_int32(0), ctypes.c_int32(0)
            format = ctypes.c_uint32(0)
            access = ctypes.c_int32(0)
            result = sdl2.SDL_QueryTexture(self.standbyTexture, ctypes.byref(format), ctypes.byref(access),
                                            ctypes.byref(w), ctypes.byref(h))
            if result == 0:
                text_w = w.value
                text_h = h.value
                src_rect = sdl2.SDL_Rect(x=0, y=0, w=text_w, h=text_h)
                dest_rect = sdl2.SDL_Rect(x=int((WIN_WIDTH-text_w)/2), y=int(WIN_HEIGHT/2-text_h), w=text_w, h=text_h)
                sdl2.SDL_RenderCopy(self.renderer,self.standbyTexture,src_rect,dest_rect)

    def drawGameOverMode(self):
        #
        self.draw()

        #
        for b in self.listBalls:
            b.draw(self.renderer)

        #
        self.playerShip.draw(self.renderer)

        #
        for b in self.listBonus:
            b.draw(self.renderer)

        if self.gameOverTexture!=None:
            w, h = ctypes.c_int32(0), ctypes.c_int32(0)
            format = ctypes.c_uint32(0)
            access = ctypes.c_int32(0)
            result = sdl2.SDL_QueryTexture(self.gameOverTexture, ctypes.byref(format), ctypes.byref(access),
                                            ctypes.byref(w), ctypes.byref(h))
            if result == 0:
                text_w = w.value
                text_h = h.value
                src_rect = sdl2.SDL_Rect(x=0, y=0, w=text_w, h=text_h)
                dest_rect = sdl2.SDL_Rect(x=int((WIN_WIDTH-text_w)/2), y=int(WIN_HEIGHT/2-text_h), w=text_w, h=text_h)
                sdl2.SDL_RenderCopy(self.renderer,self.gameOverTexture,src_rect,dest_rect)

    def drawPlayMode(self):
        #
        self.draw()

        #
        for b in self.listBalls:
            b.draw(self.renderer)

        #
        self.playerShip.draw(self.renderer)

        #
        for b in self.listBonus:
            b.draw(self.renderer)

    def processHighScore(self):
        #
        events = sdl2.ext.get_events()
        for event in events:
            match event.type :
                case sdl2.SDL_QUIT:
                    self.running = False
                case sdl2.SDL_KEYDOWN:
                    if event.key.keysym.sym == sdl2.SDLK_ESCAPE and event.key.repeat==False:
                        self.running = False
                    elif (event.key.keysym.sym == sdl2.SDLK_RETURN or event.key.keysym.sym == sdl2.SDLK_KP_ENTER) and event.key.repeat==False:
                        self.processEvent = self.processStandby
                        self.drawGame = self.drawStandbyMode
                    elif event.key.keysym.sym == sdl2.SDLK_BACKSPACE and event.key.repeat==False:
                        curPlayer = self.listHighScores[self.ihighScore].player
                        if (l:=len(curPlayer))>0:
                            curPlayer = curPlayer[0:len(curPlayer)-1]
                            self.listHighScores[self.ihighScore].player = curPlayer
                    elif (((event.key.keysym.sym >= sdl2.SDLK_a and event.key.keysym.sym <= sdl2.SDLK_z) or
                            (event.key.keysym.sym >= sdl2.SDLK_0 and event.key.keysym.sym <= sdl2.SDLK_9))
                                    and event.key.repeat==False):
                        self.listHighScores[self.ihighScore].player += self.tblKeys[event.key.keysym.sym]

    def drawHighScoreMode(self):
        #
        rect = copy.copy(self.frame)
        rect.deflate(15,15,15,15)
        sdl2.sdlgfx.boxRGBA(self.renderer, int(rect.left),int(rect.top),
                                    int(rect.right), int(rect.bottom), 20, 20, 70, 255)
        #
        ctext_w, ctext_h = c_int(0), c_int(0)
        yLin = 50
        text = "HIGH SCORES"
        sdl2.sdlttf.TTF_SizeText(self.bigBigFont, text.encode("utf-8"), ctext_w, ctext_h)
        text_w = ctext_w.value
        text_h = ctext_h.value
        textSurface = sdl2.sdlttf.TTF_RenderText_Solid(self.bigBigFont, 
                                                       text.encode("utf-8"), sdl2.SDL_Color(255,255,0,255))
        texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, textSurface)
        sdl2.SDL_FreeSurface(textSurface)
        src_rect = sdl2.SDL_Rect(x=0, y=0, w=text_w, h=text_h)
        dest_rect = sdl2.SDL_Rect(x=int((WIN_WIDTH-text_w)/2), y=int(yLin), w=text_w, h=text_h)
        sdl2.SDL_RenderCopy(self.renderer,texture,src_rect,dest_rect)
        sdl2.SDL_DestroyTexture(texture)
        #
        dx = WIN_WIDTH/12
        xCol1 = 3*dx
        xCol2 = 7*dx
        yLin += 80
        sdl2.sdlttf.TTF_SetFontStyle( self.bigFont, sdl2.sdlttf.TTF_STYLE_NORMAL)
        sdl2.sdlttf.TTF_SetFontKerning(self.bigFont, 0)
        for i,h in enumerate(self.listHighScores):
            if h.player=='':
                text = '--------' 
            else:
                text = h.player
            sdl2.sdlttf.TTF_SizeText(self.bigFont, text.encode("utf-8"), ctext_w, ctext_h)
            text_w = ctext_w.value
            text_h = ctext_h.value

            # For blinking highdcore
            nbTicks = sdl2.timer.SDL_GetTicks()
            if (nbTicks-self.highScoreTimer) > 300:
                self.highScoreTimer = nbTicks
                self.ihighScoreColorText += 1

            if i==self.ihighScore:
                if (self.ihighScoreColorText % 2 ==1):
                    textColor = sdl2.SDL_Color(255,255,0,255)
                else:
                    textColor = sdl2.SDL_Color(155,155,0,255)
            else:
                textColor = sdl2.SDL_Color(255,255,0,255)

            textSurface = sdl2.sdlttf.TTF_RenderText_Solid(self.bigFont, text.encode("utf-8"), textColor)
            texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, textSurface)
            sdl2.SDL_FreeSurface(textSurface)
            src_rect = sdl2.SDL_Rect(x=0, y=0, w=text_w, h=text_h)
            dest_rect = sdl2.SDL_Rect(x=int(xCol1), y=int(yLin), w=text_w, h=text_h)
            sdl2.SDL_RenderCopy(self.renderer,texture,src_rect,dest_rect)
            sdl2.SDL_DestroyTexture(texture)

            text = "{:06d}".format(h.score)
            sdl2.sdlttf.TTF_SizeText(self.bigFont, text.encode("utf-8"), ctext_w, ctext_h)
            text_w = ctext_w.value
            text_h = ctext_h.value
            textSurface = sdl2.sdlttf.TTF_RenderText_Solid(self.bigFont, text.encode("utf-8"), sdl2.SDL_Color(255,255,0,255))
            texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, textSurface)
            sdl2.SDL_FreeSurface(textSurface)
            src_rect = sdl2.SDL_Rect(x=0, y=0, w=text_w, h=text_h)
            dest_rect = sdl2.SDL_Rect(x=int(xCol2), y=int(yLin), w=text_w, h=text_h)
            sdl2.SDL_RenderCopy(self.renderer,texture,src_rect,dest_rect)
            sdl2.SDL_DestroyTexture(texture)

            yLin += (text_h+8)


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

    font_path = RESOURCES.get_path("sansation.ttf")
    bigFont = sdl2.sdlttf.TTF_OpenFont(font_path.encode("utf8"), 20)
    if bigFont==None:
        err = sdl2.sdlttf.TTF_GetError()
        raise RuntimeError("Error Loading font: {0}".format(err))

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
    game = Game( renderer, textureShip)


    game.loadHighScores('highscores.txt')


    # run event loop
    game.running = True

    while game.running:

        game.processEvent()

        #------------------------------------------------------------
        # Update objects states

        # Update ship position
        if game.velocityH<0:
            game.playerShip.moveLeft(10)
            game.lastMouseX = game.playerShip.pos.x
        elif game.velocityH>0:
            game.playerShip.moveRight(10)
            game.lastMouseX = game.playerShip.pos.x
        else:
            dx = int(math.fabs(game.playerShip.pos.x-game.lastMouseX))
            if dx>12:
                if game.playerShip.pos.x<game.lastMouseX:
                    game.playerShip.moveRight(12)
                elif game.playerShip.pos.x>game.lastMouseX:
                    game.playerShip.moveLeft(12)

        game.playerShip.updateState()

        #
        if not game.fpause:

            # Manage balls
            for b in game.listBalls:
                if b.vel.y==0:
                    # Update standby balls positions from ship
                    b.next_pos = Vector2f(game.playerShip.pos.x, game.playerShip.pos.y - b.r)
                    b.updatePosition()
                else:
                    #
                    if b.pos.y>(game.playerShip.pos.y+3*game.playerShip.h):
                        b.fdelete = True # delete ball
                        continue

                    # Check Ball Ship collision
                    if (ptInter:=game.playerShip.hitBall(b))!=None:
                        if bouncingSound != None:
                            sdl2.sdlmixer.Mix_PlayChannel(-1, bouncingSound, 0)

                        if game.playerShip.fmagnet:
                            b.vel = Vector2f(0.0,0.0)
                            continue
                        else:
                            vx = b.vel.x
                            vy = -b.vel.y
                            dx = 0
                            if game.playerShip.hSpeed<-6:
                                dx = -2
                            elif game.playerShip.hSpeed>6:
                                dx = 2
                            if dx!=0:
                                n = math.sqrt(vx*vx+vy*vy)
                                vx += dx
                                n1 = math.sqrt(vx*vx+vy*vy)
                                vx = vx/n1*n
                                vy = vy/n1*n
                            x1 = ptInter[0]
                            y1 = ptInter[1]
                            # check if next_pos is in frame
                            x2 = x1 + vx
                            y2 = y1 + vy
                            if not game.frame.contains(x2,y2):
                                b.setVelocity(Vector2f(-vx, -vy))
                            else:
                                b.setVelocity(Vector2f(vx, vy))
                            b.pos = Vector2f(x1,y1)
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
                    if game.tempScore>400:
                        if bonusSound != None:
                            sdl2.sdlmixer.Mix_PlayChannel(-1, bonusSound, 0)
                        game.tempScore = 0
                        game.listBonus.append(Bonus(randint(1, 5),game.deleteBrick.left+10,game.deleteBrick.top+5,
                                                game.deleteBrick.right-game.deleteBrick.left-20,
                                                game.deleteBrick.bottom-game.deleteBrick.top-10
                                                ))

                    #
                    if game.doBricksHit(b):
                        if bouncingSound != None:
                            sdl2.sdlmixer.Mix_PlayChannel(-1, bouncingSound, 0)
                        if game.isLevelCompleted():
                            game.listBalls = []
                            game.listBonus = []
                            game.listBalls.append(Ball(WIN_WIDTH/2, WIN_HEIGHT-44, 4))
                            game.playerShip.setMediumSize()
                            if succesSound != None:
                                sdl2.sdlmixer.Mix_PlayChannel(-1, succesSound, 0)

            game.listBalls[:] = [b for b in game.listBalls if b.fdelete==False]

            # Check for Game Over
            if len(game.listBalls)==0:
                if game.lifes>0:
                    game.lifes -= 1
                    game.listBalls.append(Ball(WIN_WIDTH/2, WIN_HEIGHT-44, 4))
                    game.playerShip.setMediumSize()
                    if faillureSound != None:
                        sdl2.sdlmixer.Mix_PlayChannel(-1, faillureSound, 0)
                else:
                    # Game Over
                    if gameOverSound != None:
                        sdl2.sdlmixer.Mix_PlayChannel(-1, gameOverSound, 0)
                    # 
                    game.ihighScore = game.isNewHighScore(game.score)
                    if game.ihighScore>=0:
                        game.insertHighScore(game.ihighScore,game.player,game.score)
                        game.processEvent = game.processHighScore
                        game.drawGame = game.drawHighScoreMode
                        game.mode = GameMode.HIGH_SCORE
                    else:
                        game.processEvent = game.processGameOver
                        game.drawGame = game.drawGameOverMode
                        game.mode = GameMode.GAME_OVER
                    game.init()
                    game.listBalls = []
                    game.listBonus = []
                    game.listBalls.append(Ball(WIN_WIDTH/2, WIN_HEIGHT-44, 4))
                    game.playerShip.setMediumSize()
 
            # Manage Bonus hit     
            sLeft = game.playerShip.left
            sTop = game.playerShip.top
            sRight = game.playerShip.right
            sBottom = game.playerShip.bottom
            for b in game.listBonus:

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
                            game.playerShip.setBigSize()
                        elif b.type==2:
                            game.playerShip.setSmallSize()
                        elif b.type==4:
                            game.playerShip.setMagnet(True)
                        else:
                            game.playerShip.setMediumSize()
                        b.fdelete = True
                else:
                    b.updateAnim()

            game.listBonus[:] = [b for b in game.listBonus if b.fdelete==False]

            
        #------------------------------------------------------------------
        # Draw Game

        #
        sdl2.SDL_SetRenderDrawColor(renderer, 30, 30, 80, sdl2.SDL_ALPHA_OPAQUE)
        sdl2.SDL_RenderClear(renderer)

        #
        game.drawGame()

        #
        sdl2.SDL_RenderPresent(renderer)
        sdl2.SDL_Delay(20)

    game.saveHighScores('highscores.txt')

    # clean up
    sdl2.SDL_DestroyTexture(textureShip)  # Destroy the texture
    sdl2.SDL_DestroyTexture(textureBrick)  # Destroy the texture
    sdl2.SDL_DestroyTexture(textureBonus)  # Destroy the texture
    sdl2.SDL_DestroyRenderer(renderer)
    sdl2.SDL_DestroyWindow(win)
    sdl2.sdlmixer.Mix_CloseAudio()
    if bigFont!=None:
        sdl2.sdlttf.TTF_CloseFont(bigFont)
    sdl2.sdlttf.TTF_Quit()
    sdl2.SDL_Quit()



if __name__ == "__main__":
    sys.exit(run())

