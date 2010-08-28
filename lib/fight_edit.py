import pygame
import os
pygame.scrap.init()
from things import *

class scene_menu(menu):
    def __init__(self):
        super(scene_menu,self).__init__([50,0],150)
        self.options = pygame.scene_data.keys()
    def execute(self,option):
        command = option.lines[0]
        self.parent.load(command)
        self.kill = 1

class point_add(thing):
    def mouse_click(self,pos,mode):
        if pos in self.parent.points:
            self.parent.points.remove(pos)
        else:
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
        
class wall_point_add(thing):
    def mouse_click(self,pos,mode):
        if pos in self.parent.wall_points:
            self.parent.wall_points.remove(pos)
        else:
            self.parent.wall_points.append(pos)
        
class wall_point_connect(thing):
    def __init__(self):
        super(wall_point_connect,self).__init__()
        self.mode = "first"
    def mouse_click(self,pos,mode):
        if self.mode == "first":
            for p in self.parent.wall_points:
                if abs(p[0]-pos[0])<5 and abs(p[1]-pos[1])<5:
                    self.start = p
                    self.mode = "second"
                    return True
        elif self.mode == "second":
            for p in self.parent.wall_points:
                if abs(p[0]-pos[0])<5 and abs(p[1]-pos[1])<5:
                    self.parent.add_connection([self.start,p],"wall_")
                    self.mode = "first"
                    return True
        return True

class file_menu(menu):
    def update(self,dt):
        self.options = os.listdir(self.dir)
        super(file_menu,self).update(dt)
    def execute(self,option):
        command = option.lines[0]
        self.parent.bg.load("art/"+command)
        self.kill = 1

class edit_menu(menu):
    def update(self,dt):
        self.options = ["load","save","add point","connect points","add wall point","connect wall","clear","bg","exit"]
        super(edit_menu,self).update(dt)
    def load(self):
        pa = scene_menu()
        pa.parent = self.parent
        self.parent.children.append(pa)
    def add_point(self):
        pa = point_add()
        pa.parent = self.parent
        self.parent.interface.children = [pa]
    def connect_points(self):
        pc = point_connect()
        pc.parent = self.parent
        self.parent.interface.children = [pc]
    def add_wall_point(self):
        pa = wall_point_add()
        pa.parent = self.parent
        self.parent.interface.children = [pa]
    def connect_wall(self):
        pc = wall_point_connect()
        pc.parent = self.parent
        self.parent.interface.children = [pc]
    def save(self):
        self.parent.save()
    def bg(self):
        fm = file_menu([0,0],150)
        fm.dir = "art"
        fm.parent = self.parent
        self.parent.children.append(fm)
    def clear(self):
        self.parent.points = []
        self.parent.connections = []
    def exit(self):
        self.parent.finish()

class edit(thing):
    def __init__(self,children,scene_name):
        super(edit,self).__init__()
        self.old_children = children
        self.bg = sprite("art/door1_closed.png",[0,0])
        self.children = [self.bg]
        self.em = edit_menu([0,0],80)
        self.em.parent = self
        self.data = {"points":[],"connections":[],"wall_points":[],"wall_connections":[]}
        if self.em not in self.children:
            self.children.append(self.em)
            self.em.kill = 0
        self.interface = thing()
        self.children.insert(0,self.interface)
        self.load(scene_name)
        #~ try:
            #~ self.load(pygame.scrap.get(pygame.SCRAP_TEXT).strip().replace("\x00","").replace("\r\n","\n"))
        #~ except:
            #~ pass
    connections = property(lambda self: self.data["connections"])
    points = property(lambda self: self.data["points"])
    wall_connections = property(lambda self: self.data["wall_connections"])
    wall_points = property(lambda self: self.data["wall_points"])
    def load(self,scene_name):
        scene = pygame.scene_data[scene_name]
        self.bg.load("art/"+scene["map"]+".png")
        fn = self.fn = "data/%s.txt"%scene["fight"]
        self.data = {"points":[],"connections":[],"wall_points":[],"wall_connections":[]}
        text = open(fn).read()
        self.data.update(eval(text))
    def save(self):
        f = open(self.fn,"w")
        f.write(repr(self.data))
        f.close()
    def finish(self):
        pygame.scene.children = self.old_children
    def add_connection(self,points,mode=""):
        s = sorted(points)
        lo = self.data[mode+"connections"]
        if s in lo:
            lo.remove(s)
        else:
            lo.append(s)
    #~ def mouse_over(self,pos):
        #~ print pos
    def draw(self,surf):
        for c in self.connections:
            pygame.draw.line(surf,[155,0,155],c[0],c[1])
        for p in self.points:
            pygame.draw.line(surf,[255,0,255],p,p)
        for c in self.wall_connections:
            pygame.draw.line(surf,[155,0,55],c[0],c[1])
        for p in self.wall_points:
            pygame.draw.line(surf,[255,50,55],p,p)
