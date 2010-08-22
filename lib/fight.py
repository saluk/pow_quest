import pygame
from things import *

class spot(thing):
    """A spot someone can be placed in on the fight screen"""
    def __init__(self,pos,next=[]):
        self.pos = pos
        self.next = next
        self.contains = None
    def near_enemy(self):
        for n in self.next:
            if n.contains:
                if n.enemy == True:
                    return n
    def can_move(self):
        for n in self.next:
            if not n.contains:
                return True
                
class realchar(thing):
    def __init__(self):
        self.pos = [0,0]
        self.spot = None
        self.weapon = None
        self.sprite = char("army",[100,100])
        self.children = []
        self.enemy = False
    def set_spot(self,spot):
        self.children = []
        if not spot.contains:
            spot.contains = self
            self.spot = spot
            self.children = [self.sprite]
            self.pos = self.sprite.pos = self.spot.pos
        return self
    def mouse_click(self,pos,mode):
        if not self.children:
            return
        x,y = pos
        cx,cy = self.sprite.pos
        cw,ch = self.sprite.surf.get_size()
        if x>=cx and x<=cx+cw and y>=cy and y<=cy+ch:
            pygame.scene.children[0].action_menu(self)
        
class weapon(thing):
    def __init__(self):
        self.type = "gun"

class action_menu(menu):
    """The fighting menu for a person"""
    def __init__(self,character):
        super(action_menu,self).__init__(character.pos,60)
        self.character = character
        self.init_options()
    def init_options(self):
        character = self.character
        if character.weapon:
            self.options.append("aim")
            if character.weapon.type == "gun":
                self.options.append("shoot")
            if character.weapon.type == "knife":
                if character.spot.near_enemy():
                    self.options.append("slice")
        if character.spot.can_move():
            self.options.append("move")
        self.options.append("idle")
        
class fight_scene(thing):
    def __init__(self):
        self.children = []
        self.am = None
        self.bg = sprite("art/bunker.png",[0,0])
        self.children.append(self.bg)
        self.spots = {}
        
        self.spots["door"] = spot([176,46])
        self.spots["mid"] = spot([169,94])
        self.spots["right"] = spot([211,96])
        self.spots["left"] = spot([131,82])
        
        self.spots["door"].next = [self.spots["mid"]]
        self.spots["mid"].next = [self.spots["left"],self.spots["right"]]
        self.spots["left"].next = [self.spots["mid"]]
        self.spots["right"].next = [self.spots["mid"]]
        
        enemy = realchar().set_spot(self.spots["door"])
        enemy.weapon = weapon()
        enemy.enemy = True
        player = realchar().set_spot(self.spots["mid"])
        player.weapon = weapon()
    def update(self,dt):
        for s in self.spots.values():
            if s.contains and s.contains not in self.children:
                self.children.append(s.contains)
    def action_menu(self,char):
        if self.am in self.children:
            self.children.remove(self.am)
        self.am = action_menu(char)
        self.children.append(self.am)
