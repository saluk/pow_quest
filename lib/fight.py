import pygame
import random
import math
import sys
import geometry
from things import *


"""
Aiming.
hit region:
    defines range of angles that are picked at random for a shot
    also at a wide angle shots have a chance to miss even if the line of sight actually hits (based on how far off true angle)
Each time target is changed
    hit region defined by base aim skill for character and weapon
    each time aim is picked, hit region narrows based on character aim speed skill and weapon
    hit region has a minimum narrow defined by character and weapon aim stats
When changing targets, hit region expands but not all the way
when hit, hit region expands based on focus statistic
"""
class hit_region(thing):
    def __init__(self):
        super(hit_region,self).__init__()
        self.start_pos = [0,0]
        self.target_pos = [100,100]
        self.target_angle = 60
        self.half_width = 10  #half the angle width
    def get_angle(self):
        """Pick a random firing angle based on our width. Distribution should be somewhat normal,
        center angle should be more common than edges."""
        mean = self.target_angle
        std_dev = self.half_width/3.0
        ang = random.gauss(mean,std_dev)
        return ang
    def update_stats(self):
        rise = self.target_pos[0]-self.start_pos[0]
        run = self.target_pos[1]-self.start_pos[1]
        ang = math.atan2(run,rise)
        self.target_angle = ang*180.0/math.pi

def line_box(line,box):
    x,y = box[0]
    w,h = box[1]
    line1 = [x,y],[x+w,y]
    line2 = [x+w,y],[x+w,y+h]
    line3 = [x,y+h],[x+w,y+h]
    line4 = [x,y],[x,y+h]
    for bline in [line1,line2,line3,line4]:
        if geometry.calculateIntersectPoint(line[0],line[1],bline[0],bline[1]):
            return True
        
hr = hit_region()
hr.update_stats()
print hr.get_angle()

class spot(thing):
    """A spot someone can be placed in on the fight screen"""
    def __init__(self,pos,next=None):
        super(spot,self).__init__()
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
        super(realchar,self).__init__()
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
        super(weapon,self).__init__()
        self.set_stats()
    def set_stats(self):
        self.type = "gun"
        self.damage = 10
        self.far = 100
        self.range = 50
        self.close = 20
        self.accuracy_close = 0.7
        self.accuracy = 0.5
        self.accuracy_far = 0.2

class gun(weapon):
    def set_stats(self):
        self.type = "gun"
        self.damage = 10
        self.far = 200
        self.range = 150
        self.close = 50
        self.accuracy_close = 0.7
        self.accuracy = 0.5
        self.accuracy_far = 0.2
        
class knife(weapon):
    def set_stats(self):
        self.type = "knife"
        self.damage = 3
        #Knife types can only attack from one space over anyway
        self.far = 150
        self.range = 150
        self.close = 150
        self.accuracy_close = 0.9
        self.accuracy = 0.9
        self.accuracy_far = 0.9

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
            self.options.append("target")
            if character.target:
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
        pygame.fight_scene.move_menu(self.character)
    def target(self):
        pygame.fight_scene.target_menu(self.character)
    def shoot(self):
        pygame.fight_scene.shoot_menu(self.character)

class move_menu(thing):
    def __init__(self,char):
        super(move_menu,self).__init__()
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
                
class target_menu(thing):
    def __init__(self,char,chars):
        super(target_menu,self).__init__()
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
                #pygame.fight_scene.next()
                pygame.fight_scene.action_menu(self.char)
                self.kill = 1
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
    def __init__(self,restore_children,goodies,enemies,bg,fight):
        super(fight_scene,self).__init__()
        pygame.fight_scene = self
        self.restore_children = restore_children
        self.children = []
        self.bg = bg
        self.children.append(self.bg)
        self.spots = {}
        
        self.load_spots_from_file("data/%s.txt"%fight)
        for s in self.spots.values():
            self.children.append(s)
        
        self.goodies = goodies
        for good in goodies:
            spot = choose_closest_to(good,[x for x in self.spots.values() if not x.contains])
            player = realchar().set_spot(spot)
            player.weapon = gun()
            player.sprite.set_facing("n")
            self.participants = [player]
        
        self.enemies = enemies
        for enemy in enemies:
            spot = choose_closest_to(enemy,[x for x in self.spots.values() if not x.contains])
            enemy = realchar().set_spot(spot)
            enemy.weapon = gun()
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
    def target_menu(self,char):
        self.menus.children = [target_menu(char,self.participants)]
    def shoot_menu(self,char):
        self.menus.children = []
        self.shoot(char)
        self.next()
    def shoot(self,char):
        p = char.pos
        #Sort participants by range
        for part in self.participants:
            tp = part.pos
            d = (p[0]-tp[0])**2+(p[1]-tp[1])**2
            part.dist = d
        #Iterate through participants in order of distance until we hit it
        target = None
        for part in sorted(self.participants,key=lambda x: x.dist):
            w,h = [15,20]
            x = part.pos[0]-w//2
            y = part.pos[1]-h//2
            if line_box([p,part.pos],[[x,y],[w,h]]):
                target = part
                break
        tp = target.pos
        if not target or target.dist>char.weapon.far**2:
            print target.dist,char.weapon.far
            self.children.append(popup_text("Miss",tp[:]))
            return
        target.hp-=char.weapon.damage
        self.children.append(popup_text(str(char.weapon.damage),tp[:]))
        if target.hp<=0:
            target.set_spot(None)
            self.participants.remove(target)
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
                self.next_mode = 0.25
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
        if not [x for x in self.participants if x.enemy]:
            for e in self.enemies:
                e.kill = 1
            self.goodies[0].pos = self.participants[0].pos
            pygame.scene.children = self.restore_children
        if not [x for x in self.participants if not x.enemy]:
            print "you lose"
            sys.exit()

    def players(self):
        return [x for x in self.participants if not x.enemy]
    def ai(self,char):
        if char.weapon.type=="knife":
            if not char.target:
                p = self.players()
                if p:
                    char.target = p[0]
            elif char.target not in char.spot.near():
                options = char.spot.can_move()
                if options:
                    char.set_spot(choose_closest_to(char.target,options))
            else:
                self.shoot(char)
        elif char.weapon.type=="gun":
            if not char.target:
                p = self.players()
                if p:
                    char.target = p[0]
            else:
                self.shoot(char)
        self.next()