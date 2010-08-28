import pygame
import random
import os
pygame.scrap.init()
from things import *

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
        
class destination_menu(menu):
    def __init__(self):
        super(destination_menu,self).__init__([50,0],150)
        self.options = pygame.scene_data.keys()
    def execute(self,option):
        command = option.lines[0]
        self.ob.data["destination"] = {"scene":command,"pos":[0,0]}
        self.kill = 1
        sm = destination_point(self.ob)
        sm.parent = self.parent
        self.parent.children.append(sm)
        
class destination_point(thing):
    def __init__(self,char):
        super(destination_point,self).__init__()
        self.char = char
    def draw(self,surf):
        bg = sprite("art/"+pygame.scene_data[self.char.data["destination"]["scene"]]["map"]+".png",[0,0])
        bg.draw(surf)
    def mouse_click(self,pos,mode):
        self.char.data["destination"]["pos"] = pos
        self.kill = 1
        return True
        
class place_menu(thing):
    def __init__(self,char):
        super(place_menu,self).__init__()
        self.char = char
    def mouse_click(self,pos,mode):
        self.char.pos = pos
        self.char.data["pos"] = pos
        self.parent.objects.children.append(self.char)
        self.kill = 1
        return True
        
class add_menu(menu):
    def __init__(self,parent):
        super(add_menu,self).__init__([50,0],150)
        self.parent = parent
        self.options = ["door","doorbars","crate","4waydoor_w","4waydoor_e","4waydoor_s","4waydoor_n"]
        self.options.extend(pygame.all_stats.keys())
        self.options.extend(self.parent.items.keys())
    def execute(self,option):
        command = option.lines[0]
        o = {"type":command,"scene":self.parent.scene_name,"pos":"random"}
        ob = self.parent.create_template(o,[0,0])
        pm = place_menu(ob)
        pm.parent = self.parent
        self.parent.interface.children = [pm]
        self.kill = 1

class edit_menu(menu):
    def update(self,dt):
        self.options = ["load scene","new scene","add","save","exit"]
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
    def add(self):
        sm = add_menu(self.parent)
        self.parent.children.append(sm)
        
class object_menu(menu):
    def update(self,dt):
        self.options = ["move","cancel","set destination","----","delete"]
        super(object_menu,self).update(dt)
        setattr(self,"----",lambda: 1)
    def set_destination(self):
        sm = destination_menu()
        sm.parent = self.parent
        sm.ob = self.char
        self.kill = 1
        self.parent.children.append(sm)
    def cancel(self):
        self.kill = 1
    def move(self):
        self.parent.interface.children = [move_object(self.char)]
        self.kill = 1
    def delete(self):
        self.parent.obdat.remove(self.char)
        self.char.kill = 1
        self.kill = 1
        
class move_object(thing):
    def __init__(self,char):
        super(move_object,self).__init__()
        self.char = char
    def mouse_click(self,pos,mode):
        self.char.pos = pos
        self.char.data["pos"] = pos
        self.kill = 1
        return True
        
class editor_ob:
    def mouse_click(self,pos,mode):
        if pos[0]>=self.pos[0] and pos[0]<=self.pos[0]+self.surf.get_width() and pos[1]>=self.pos[1] and pos[1]<=self.pos[1]+self.surf.get_height():
            om = object_menu(pos,100)
            om.parent = self.parent
            om.char = self
            self.parent.children.append(om)
            return True
        
class game_sprite(editor_ob,sprite):
    pass
    
class game_object(editor_ob,char):
    pass

class game_door(editor_ob,door):
    pass
            
class game_item(editor_ob,item):
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
        self.items = eval(open("data/items.txt").read())
        self.obdat = []
        for o in eval(open("data/objects.txt").read()):
            ob = None
            if o["pos"] == "random":
                pos = [random.randint(40,140),random.randint(40,140)]
            else:
                pos = o["pos"]
            self.create_template(o,pos)
        self.load(scene_name)
    def create_template(self,o,pos):
        if o["type"] in pygame.all_stats:
            stats = pygame.all_stats[o["type"]]
            if stats["type"] == "enemy":
                ob = game_object("army",pos)
        if o["type"] == "crate":
            ob = game_sprite("art/crate.png",pos)
        if o["type"] == "door":
            ob = game_door("door1",pos)
            o["destination"] = {"scene":None,"pos":[0,0]}
        if o["type"] == "doorbars":
            ob = game_door("doorbars",pos)
            o["destination"] = {"scene":None,"pos":[0,0]}
        if o["type"] in self.items.keys():
            ob = game_item(o["type"],pos,None,True)
            ob.stats = self.items[o["type"]]
        if o["type"].startswith("4waydoor"):
            ob = game_door(o["type"],pos)
            o["destination"] = {"scene":None,"pos":[0,0]}
        if ob:
            ob.parent = self
            ob.data = o
            self.obdat.append(ob)
        return ob
    def load(self,scene_name):
        self.scene_name = scene_name
        self.scene_data = pygame.scene_data[self.scene_name]
        self.bg.load("art/"+self.scene_data["map"]+".png")
        self.objects.children = []
        for o in self.obdat:
            if o.data["scene"] == self.scene_name:
                self.objects.children.append(o)
        data = eval(open("data/"+self.scene_data["fight"]+".txt").read())
        self.points,self.connections = data["points"],data["connections"]
    def save(self):
        objects = repr([x.data for x in self.obdat])
        f = open("data/objects.txt","w")
        f.write(objects)
        f.close()
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
