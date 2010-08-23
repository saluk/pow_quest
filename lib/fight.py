import pygame
import sys
from things import *

class spot(thing):
    """A spot someone can be placed in on the fight screen"""
    def __init__(self,pos,next=None):
        self.children = []
        self.pos = pos
        self.next = []
        if next:
            self.next = next
        self.contains = None
    def near_enemy(self):
        for n in self.next:
            if n.contains:
                if n.contains.enemy == True:
                    return n
    def near(self):
        near = []
        for n in self.next:
            if n.contains:
                near.append(n.contains)
        return near
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
        self.hp = 30
        self.pos = [0,0]
        self.spot = None
        self.weapon = None
        self.sprite = char("army",[100,100])
        self.health_bar = quick_textbox("",[100,100])
        self.children = []
        self.enemy = False
        self.action = None
        self.target = None
    def draw(self,surf):
        self.health_bar.pos = [self.sprite.pos[0]+5,self.sprite.pos[1]+5]
        self.health_bar.lines = ["%s/30"%self.hp]
        self.health_bar.draw(surf)
        if self.target:
            pygame.draw.line(surf,[100,100,100],self.pos,self.target.pos)
    def set_spot(self,spot):
        if self.spot:
            self.spot.contains = None
        self.children = []
        if not spot:
            return
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
        self.damage = 10

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
            if character.target:
                if character.weapon.type == "gun":
                    self.options.append("shoot")
                if character.weapon.type == "knife":
                    if character.spot.near_enemy():
                        self.options.append("slice")
        if character.spot.can_move():
            self.options.append("move")
        self.options.append("idle")
    def move(self):
        pygame.fight_scene.move_menu(self.character)
    def aim(self):
        pygame.fight_scene.aim_menu(self.character)
    def shoot(self):
        pygame.fight_scene.shoot_menu(self.character)

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
                pygame.fight_scene.next()
                return True
                
class aim_menu(thing):
    def __init__(self,char,chars):
        self.children = []
        self.char = char
        self.chars = chars
    def draw(self,surf):
        for s in self.chars:
            x = s.pos[0]-10
            y = s.pos[1]-10
            pygame.draw.rect(surf,[255,0,0],[[x,y],[20,20]])
            pygame.draw.line(surf,[255,255,255],self.char.pos,s.pos)
    def mouse_click(self,pos,mode):
        x,y = pos
        for s in self.chars:
            cx = s.pos[0]-10
            cy = s.pos[1]-10
            cw=ch=20
            if x>=cx and x<=cx+cw and y>=cy and y<=cy+ch:
                self.char.target = s
                pygame.fight_scene.next()
                return True
                
def choose_closest_to(ob,spots):
    closest = None
    cd = None
    p = ob.pos
    for s in spots:
        sp = s.pos
        d = (sp[0]-p[0])**2+(sp[1]-p[1])**2
        if not closest or d<cd:
            cd = d
            closest = s
    return closest
        
class fight_scene(thing):
    def __init__(self,restore_children,goodies,enemies):
        pygame.fight_scene = self
        self.restore_children = restore_children
        self.children = []
        self.bg = sprite("art/bunker.png",[0,0])
        self.children.append(self.bg)
        self.spots = {}
        
        self.load_spots_from_file("data/fight1.txt")
        for s in self.spots.values():
            self.children.append(s)
        
        self.goodies = goodies
        for good in goodies:
            spot = choose_closest_to(good,[x for x in self.spots.values() if not x.contains])
            player = realchar().set_spot(spot)
            player.weapon = weapon()
            player.sprite.set_facing("n")
            self.participants = [player]
        
        self.enemies = enemies
        for enemy in enemies:
            spot = choose_closest_to(enemy,[x for x in self.spots.values() if not x.contains])
            enemy = realchar().set_spot(spot)
            enemy.weapon = weapon()
            enemy.weapon.type = "knife"
            enemy.weapon.damage = 3
            enemy.enemy = True
            self.participants.append(enemy)
        
        self.menus = thing()
        self.children.append(self.menus)
        self.turns = ["wait"]
        self.calc_turns()
    def load_spots_from_file(self,file):
        self.spots = {}
        points,connections = open(file).read().split("\n")
        points = eval(points)
        connections = eval(connections)
        for p in points:
            self.spots[tuple(p)] = spot(list(p))
        for c in connections:
            a,b = c
            self.spots[tuple(a)].next.append(self.spots[tuple(b)])
            self.spots[tuple(b)].next.append(self.spots[tuple(a)])
    def calc_turns(self):
        self.turn_start = True
        for p in self.participants:
            self.turns.append(p)
            self.turns.append("wait")
        self.next_mode = 1
    def next(self):
        self.turn_start = True
        self.menus.children = []
        if self.turns:
            del self.turns[0]
        if not self.turns:
            self.calc_turns()
    def action_menu(self,char):
        self.menus.children = [action_menu(char)]
    def move_menu(self,char):
        self.menus.children = [move_menu(char)]
    def aim_menu(self,char):
        self.menus.children = [aim_menu(char,self.participants)]
    def shoot_menu(self,char):
        self.menus.children = []
        self.shoot(char)
        self.next()
    def shoot(self,char):
        char.target.hp-=char.weapon.damage
        tp = char.target.pos
        self.children.append(popup_text(str(char.weapon.damage),tp[:]))
        if char.target.hp<=0:
            char.target.set_spot(None)
            self.participants.remove(char.target)
            self.clear_targets()
    def update(self,dt):
        "Update timers if no interface is up"
        nt = self.turns[0]
        if nt == "wait":
            self.turn_start = False
            self.finish()
            self.next_mode -= dt
            if self.next_mode <= 0:
                self.next()
                self.next_mode = 1
        elif self.turn_start:
            self.turn_start = False
            p = nt
            if p.enemy:
                self.ai(p)
            else:
                self.action_menu(self.players()[0])
    def clear_targets(self):
        for p in self.participants:
            if p.target not in self.participants:
                p.target = None
    def finish(self):
        if len(self.participants)==1:
            pygame.scene.children = self.restore_children
            if self.participants[0].enemy:
                print "you lose"
                sys.exit()
            for e in self.enemies:
                e.kill = 1
            self.goodies[0].pos = self.participants[0].pos
    def players(self):
        return [x for x in self.participants if not x.enemy]
    def ai(self,char):
        if char.weapon.type=="knife":
            if not char.target:
                char.target = self.players()[0]
            elif char.target not in char.spot.near():
                options = char.spot.can_move()
                if options:
                    char.set_spot(choose_closest_to(char.target,options))
            else:
                self.shoot(char)
        self.next()