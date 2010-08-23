import pygame
from things import *

class spot(thing):
    """A spot someone can be placed in on the fight screen"""
    def __init__(self,pos,next=[]):
        self.children = []
        self.pos = pos
        self.next = next
        self.contains = None
    def near_enemy(self):
        for n in self.next:
            if n.contains:
                if n.enemy == True:
                    return n
    def can_move(self):
        spots = []
        for n in self.next:
            if not n.contains:
                spots.append(n)
        return spots
    def update(self,dt):
        if not self.children and self.contains:
            self.children = [self.contains]
        if not self.contains and self.children:
            self.children = []
                
class realchar(thing):
    def __init__(self):
        self.pos = [0,0]
        self.spot = None
        self.weapon = None
        self.sprite = char("army",[100,100])
        self.children = []
        self.enemy = False
    def set_spot(self,spot):
        if self.spot:
            self.spot.contains = None
        self.children = []
        if not spot.contains:
            spot.contains = self
            self.spot = spot
            self.children = [self.sprite]
            self.pos = self.sprite.pos = self.spot.pos
        return self
    #~ def mouse_click(self,pos,mode):
        #~ if not self.children:
            #~ return
        #~ x,y = pos
        #~ cx,cy = self.sprite.pos
        #~ cw,ch = self.sprite.surf.get_size()
        #~ if x>=cx and x<=cx+cw and y>=cy and y<=cy+ch:
            #~ pygame.scene.children[0].action_menu(self)
        
class weapon(thing):
    def __init__(self):
        self.type = "gun"

class action_menu(menu):
    """The fighting menu for a person"""
    def __init__(self,character):
        x,y = character.pos
        x+=16
        super(action_menu,self).__init__([x,y],60)
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
    def move(self):
        pygame.fight_scene.menus.children = [move_menu(self.character)]

class move_menu(thing):
    def __init__(self,char):
        self.children = []
        self.char = char
        self.start = self.char.spot
        self.spots = self.char.spot.can_move()
    def draw(self,surf):
        for s in self.spots:
            x = s.pos[0]-10
            y = s.pos[1]-10
            pygame.draw.rect(surf,[255,255,255],[[x,y],[20,20]])
            pygame.draw.line(surf,[255,255,255],self.start.pos,s.pos)
    def mouse_click(self,pos,mode):
        x,y = pos
        for s in self.spots:
            cx = s.pos[0]-10
            cy = s.pos[1]-10
            cw=ch=20
            if x>=cx and x<=cx+cw and y>=cy and y<=cy+ch:
                self.char.set_spot(s)
                pygame.fight_scene.menus.children.remove(self)
                pygame.fight_scene.mode = "wait"
                return True
        
class fight_scene(thing):
    def __init__(self):
        pygame.fight_scene = self
        self.children = []
        self.bg = sprite("art/bunker.png",[0,0])
        self.children.append(self.bg)
        self.spots = {}
        
        self.spots["door"] = spot([176,46])
        self.spots["mid"] = spot([169,94])
        self.spots["right"] = spot([211,96])
        self.spots["left"] = spot([131,82])
        
        self.spots["door"].next = [self.spots["mid"]]
        self.spots["mid"].next = [self.spots["left"],self.spots["right"],self.spots["door"]]
        self.spots["left"].next = [self.spots["mid"]]
        self.spots["right"].next = [self.spots["mid"]]
        for s in self.spots.values():
            self.children.append(s)
        
        enemy = realchar().set_spot(self.spots["door"])
        enemy.weapon = weapon()
        enemy.enemy = True
        player = realchar().set_spot(self.spots["mid"])
        player.weapon = weapon()
        player.sprite.set_facing("n")
        self.participants = [enemy,player]
        
        self.menus = thing()
        self.children.append(self.menus)
        
        self.mode = "wait"
        self.next_mode = 1
    def action_menu(self,char):
        am = action_menu(char)
        self.menus.children = [am]
    def update(self,dt):
        "Update timers if no interface is up"
        if self.mode == "act":
            self.action_menu(self.participants[1])
            self.mode = "actwait"
        if self.mode in ["wait"]:
            self.next_mode -= dt
            if self.next_mode <= 0:
                self.mode = "act"
                self.next_mode = 1