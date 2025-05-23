import os
import sdl2

from vector2f import Vector2f

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
        if self.type<=4:
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
        
    @classmethod
    def loadTexture(cls,renderer):
        filepath = os.path.abspath(os.path.dirname(__file__))
        RESOURCES = sdl2.ext.Resources(filepath, "resources")
        image_path = RESOURCES.get_path("Bonus.png")
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
