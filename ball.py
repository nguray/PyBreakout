import math 
from vector2f import Vector2f
import sdl2.sdlgfx
import copy

from brick import Brick
from random import randint
from utils import compute_intersection

class Ball:
    def __init__(self, x:int =0, y:int =0, r:int = 5):
        self.pos = Vector2f( x, y)
        self.next_pos = copy.copy(self.pos)
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
        self.pos = copy.copy(self.next_pos)
        self.trail.insert(0,Vector2f(self.pos.x,self.pos.y))
        self.trail.pop(4)

    def computeNextPos(self):
        self.next_pos = self.pos + self.vel

    def launch(self, vx):

        if vx==0.0:
            while True:
                ia = randint(85, 95)
                if ia<89 or ia>91:
                    break
            a = -(math.pi*ia)/180.0
            self.setVelocity(Vector2f( 9.5*math.cos(a), 9.5*math.sin(a)))
        else:
            self.setVelocity(Vector2f( vx, -9.5))

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
                if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
                    self.setVelocity(Vector2f(self.vel.x,-self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True

                p1 = (br.left, br.top)
                p2 = (br.left, br.bottom)
                if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
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
                if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
                    self.setVelocity(Vector2f(self.vel.x,-self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True

                p1 = (br.right, br.top)
                p2 = (br.right, br.bottom)
                if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
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
                if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
                    self.setVelocity(Vector2f(self.vel.x,-self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True

                p1 = (br.left, br.top)
                p2 = (br.left, br.bottom)
                if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
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
                if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
                    self.setVelocity(Vector2f(-self.vel.x,self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True

                p1 = (br.left, br.bottom)
                p2 = (br.right, br.bottom)
                if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
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
                if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
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
                if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
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
                if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
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
                if (ptInter:=compute_intersection(p1, p2, q1, q2))!=None:
                    self.setVelocity(Vector2f(-self.vel.x,self.vel.y))
                    self.next_pos.x = ptInter[0]
                    self.next_pos.y = ptInter[1]
                    self.updatePosition()
                    self.computeNextPos()
                    return True
                
        return False
