import os
import sdl2.sdlgfx
from gameconst import *
from rectf import Rectf

class Brick(Rectf):

    values:int = (0,50,60,70,80,90,100,110,120,50,0)
    texture = None

    def __init__(self, x:float, y:float, type:int):
        super().__init__(x+1,y+1,BRICK_WIDTH - 1,BRICK_HEIGHT - 1)
        self.type = type
        if self.type==9:
            self.resistance = 4
        elif self.type==10:
            self.resistance = 8
        else:
            self.resistance = 1

    def contain(self, x, y):
        return  (x>=self.left and x<=self.right and y>=self.top and y<=self.bottom)

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

    @classmethod
    def loadTexture(cls,renderer):
        filepath = os.path.abspath(os.path.dirname(__file__))
        RESOURCES = sdl2.ext.Resources(filepath, "resources")
        image_path = RESOURCES.get_path("Bricks.png")
        surface = sdl2.ext.image.load_image(image_path.encode('utf-8'))
        if not surface:
            print(f"Failed to create texture: {sdl2.SDL_GetError()}")
            exit()

        # Create a texture from the surface
        cls.texture = sdl2.SDL_CreateTextureFromSurface(renderer, surface)
        sdl2.SDL_FreeSurface(surface)  # Free the surface as it's no longer needed
        if not cls.texture:
            print(f"Failed to create texture: {sdl2.SDL_GetError()}")
            exit()

    @classmethod
    def freeTexture(cls):
        sdl2.SDL_DestroyTexture(cls.texture)  # Destroy the texture
