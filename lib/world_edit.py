import pygame
import random
import os
pygame.scrap.init()
from things import *

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

class file_menu(menu):
    def update(self,dt):
        self.options = os.listdir(self.dir)
        super(file_menu,self).update(dt)
    def execute(self,option):
        command = option.lines[0]
        self.parent.bg.load("art/"+command)
        self.kill = 1

class scene_menu(menu):
    def __init__(self):
        super(scene_menu,self).__init__([50,0],150)
        self.options = pygame.scene_data.keys()
    def execute(self,option):
        command = option.lines[0]
        self.parent.load(command)
        self.kill = 1

class edit_menu(menu):
    def update(self,dt):
        self.options = ["load scene","new scene","exit"]
        super(edit_menu,self).update(dt)
    def load_scene(self):
        sm = scene_menu()
        sm.parent = self.parent
        self.parent.children.append(sm)
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
    def clear(self):
        self.parent.points = []
        self.parent.connections = []
    def exit(self):
        self.parent.finish()
        
class game_object(char):
    pass

class edit(thing):
    def __init__(self,children,scene_name):
        super(edit,self).__init__()
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
        self.objects = thing()
        self.children.append(self.objects)
        self.load(scene_name)
    def load(self,scene_name):
        self.scene_name = scene_name
        self.scene_data = pygame.scene_data[self.scene_name]
        self.bg.load("art/"+self.scene_data["map"]+".png")
        self.objects.children = []
        for o in eval(open("data/objects.txt").read()):
            ob = None
            if o["pos"] == "random":
                pos = [random.randint(40,140),random.randint(40,140)]
            else:
                pos = o["pos"]
            if o["type"] == "enemy":
                ob = game_object("army",pos)
            if ob:
                self.objects.children.append(ob)
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
