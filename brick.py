import sdl2.sdlgfx
from gameconst import *

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
