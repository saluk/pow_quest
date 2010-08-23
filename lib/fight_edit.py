import pygame
pygame.scrap.init()
from things import *

class point_add(thing):
    def mouse_click(self,pos,mode):
        self.parent.points.append(pos)
        
class point_connect(thing):
    def __init__(self):
        super(point_connect,self).__init__()
        self.mode = "first"
    def mouse_click(self,pos,mode):
        if self.mode == "first":
            for p in self.parent.points:
                if abs(p[0]-pos[0])<5 and abs(p[1]-pos[1])<5:
                    self.start = p
                    self.mode = "second"
                    return True
        elif self.mode == "second":
            for p in self.parent.points:
                if abs(p[0]-pos[0])<5 and abs(p[1]-pos[1])<5:
                    self.parent.add_connection([self.start,p])
                    self.mode = "first"
                    return True
        return True

class edit_menu(menu):
    def update(self,dt):
        self.options = ["save","add point","connect points"]
        super(edit_menu,self).update(dt)
    def add_point(self):
        pa = point_add()
        pa.parent = self.parent
        self.parent.interface.children = [pa]
    def connect_points(self):
        pc = point_connect()
        pc.parent = self.parent
        self.parent.interface.children = [pc]
    def save(self):
        self.parent.save()

class edit(thing):
    def __init__(self,children):
        self.old_children = children
        self.bg = sprite("art/bunker.png",[0,0])
        self.children = [self.bg]
        self.em = edit_menu([0,0],80)
        self.em.parent = self
        self.points = []
        self.connections = []
        if self.em not in self.children:
            self.children.append(self.em)
            self.em.kill = 0
        self.interface = thing()
        self.children.insert(0,self.interface)
        self.load(pygame.scrap.get(pygame.SCRAP_TEXT))
    def load(self,text):
        points,connections = text.split("\n")
        self.points = eval(points)
        self.connections = eval(connections[:-1])
    def save(self):
        print repr(self.points)
        print repr(self.connections)
    def finish(self):
        pygame.scene.children = self.old_children
    def add_connection(self,points):
        s = sorted(points)
        if s in self.connections:
            self.connections.remove(s)
        else:
            self.connections.append(s)
    def draw(self,surf):
        for c in self.connections:
            pygame.draw.line(surf,[155,0,155],c[0],c[1])
        for p in self.points:
            pygame.draw.line(surf,[255,0,255],p,p)