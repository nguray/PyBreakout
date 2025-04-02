
from dataclasses import dataclass

@dataclass
class Rectf:
    """Class for Rectf """
    x: float
    y: float
    w: float
    h: float
    
    def contains(self,x: float,y: float):
        return (x>=self.x and x<=(self.x + self.w) and y>=self.y and y<=(self.y + self.h))
    
    def deflate(self,l:float,t:float,r:float,b:float):
        self.x += l
        self.y += t
        self.w -= (r+l)
        self.h -= (t+b)
    
    @property
    def left(self):
        return self.x
    
    @left.setter
    def lef(self, value):
        self.x = value

    @property
    def right(self):
        return self.x + self.w
    
    @right.setter
    def right(self, value):
        self.w = value - self.x

    @property
    def top(self):
        return self.y
    
    @top.setter
    def top(self, value):
        self.y = value
    
    @property
    def bottom(self):
        return self.y + self.h
    
    @bottom.setter
    def bottom(self, value):
        self.h = value - self.y
    

