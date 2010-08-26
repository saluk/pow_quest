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
def rad(x):
    return x*math.pi/180.0
def deg(x):
    return x*180.0*math.pi
def make_line(point,ang,length):
    x = length*math.cos(ang*math.pi/180.0)
    y = length*math.sin(ang*math.pi/180.0)
    return [point,[point[0]+x,point[1]+y]]
class hit_region(thing):
    def __init__(self,start=[0,0],end=[100,100],band=30,range=300):
        super(hit_region,self).__init__()
        self.start_pos = start
        self.target_pos = end
        self.target_angle = 60
        self.range = range
        self.half_width = band//2  #half the angle width
        self.min_half_width = 5
        self.shrink_rate = 5
        self.update_stats()
    def get_angle(self):
        """Pick a random firing angle based on our width. Distribution should be somewhat normal,
        center angle should be more common than edges."""
        mean = self.target_angle
        std_dev = self.half_width/3.0
        ang = random.gauss(mean,std_dev)
        print ang,mean
        return ang
    def random_line(self):
        """Pick a random firing angle based on our width. Distribution should be somewhat normal,
        center angle should be more common than edges."""
        ang = self.get_angle()
        length = self.range
        return make_line(self.start_pos,ang,length)
    def update_stats(self):
        rise = self.target_pos[0]-self.start_pos[0]
        run = self.target_pos[1]-self.start_pos[1]
        ang = math.atan2(run,rise)
        self.target_angle = ang*180.0/math.pi
        while self.target_angle<0:
            self.target_angle += 360
    def shrink(self):
        self.half_width -= self.shrink_rate
        if self.half_width < self.min_half_width:
            self.half_width = self.min_half_width
    def draw(self,surf):
        center = self.start_pos[:]
        left_ang = self.target_angle-self.half_width
        right_ang = self.target_angle+self.half_width
        l1 = make_line(self.start_pos,left_ang,self.range)
        l2 = make_line(self.start_pos,right_ang,self.range)
        l3 = make_line(self.start_pos,self.target_angle,self.range)
        for l in [l1,l2,l3]:
            pygame.draw.line(surf,[0,255,0],*l)
        
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
print hr.random_line()

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
        """Stats info:
        maxhp - maximum hit points
        accuracy - starting band and minimum band
                    accuracy of 0 starts at 180 and min band is 110
                    each point decreases these values by 10
        reaction - affects aim speed and other speeds of things
                    each point of reaction adds 5 degrees to aim speed
        focus - how many degrees are lost when things make you lose degrees,
                   how long to charge spells"""
        super(realchar,self).__init__()
        self.stats = {"maxhp":30,"reaction":5,"accuracy":1}
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
        self.hit_region = hit_region(start=self.pos,end=self.pos,band=30)
    def draw(self,surf):
        self.health_bar.pos = [self.sprite.pos[0]+5,self.sprite.pos[1]+5]
        self.health_bar.lines = ["%s/30"%self.hp]
        self.health_bar.draw(surf)
        if self.target:
            pygame.draw.line(surf,[100,100,100],self.pos,self.target.pos)
            self.hit_region.draw(surf)
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
    def reset_hit_region(self):
        self.hit_region.start_pos = self.pos[:]
        if self.target:
            self.hit_region.target_pos = self.target.pos[:]
        self.hit_region.half_width = 90-self.get_stat("accuracy")*10
        self.hit_region.update_stats()
    def choose_target(self,char):
        self.target = char
        self.reset_hit_region()
    def aim(self):
        self.hit_region.shrink_rate = self.get_stat("reaction")*5
        self.hit_region.min_half_width = 60-self.get_stat("accuracy")*10
        self.hit_region.shrink()
    def get_stat(self,key):
        """Gets a stat, including modifications"""
        s = self.stats[key]
        if self.weapon and key in self.weapon.stats:
            s+=self.weapon.stats[key]
        return s
    #~ def mouse_click(self,pos,mode):
        #~ if not self.children:
            #~ return
        #~ x,y = pos
        #~ cx,cy = self.sprite.pos
        #~ cw,ch = self.sprite.surf.get_size()
        #~ if x>=cx and x<=cx+cw and y>=cy and y<=cy+ch:
            #~ pygame.scene.children[0].action_menu(self)
        
class weapon(thing):
    def __init__(self,stats=None):
        super(weapon,self).__init__()
        self.set_stats()
        if stats:
            self.stats.update(stats)
    def set_stats(self):
        """Stats that match player stats are added to that stat"""
        self.stats = {"type":"gun","damage":10,"accuracy":0,"reaction":0}

class gun(weapon):
    def set_stats(self):
        self.stats = {"type":"gun","damage":10,"accuracy":-1}
        
class knife(weapon):
    def set_stats(self):
        self.stats = {"type":"knife","damage":3,"accuracy":100}

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
                if character.weapon.stats["type"] == "gun":
                    self.options.append("shoot")
                if character.weapon.stats["type"] == "knife":
                    if character.spot.near_enemy():
                        self.options.append("slice")
        if character.spot.can_move():
            self.options.append("move")
        self.options.append("inacurate gun")
        self.options.append("accurate gun")
    def move(self):
        pygame.fight_scene.move_menu(self.character)
    def target(self):
        pygame.fight_scene.target_menu(self.character)
    def shoot(self):
        pygame.fight_scene.shoot_menu(self.character)
    def aim(self):
        self.character.aim()
        pygame.fight_scene.next()
    def inacurate_gun(self):
        self.character.weapon = gun({"accuracy":-2})
        self.character.reset_hit_region()
    def accurate_gun(self):
        self.character.weapon = gun({"accuracy":2})
        self.character.reset_hit_region()

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
                self.char.choose_target(s)
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
        self._debug_line = None
        
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
    def draw(self,surf):
        if self._debug_line:
            pygame.draw.line(surf,[255,0,0],*self._debug_line)
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
        tp = char.target.pos
        i = 0
        shoot_path = char.hit_region.random_line()
        self._debug_line = shoot_path
        for part in sorted(self.participants,key=lambda x: x.dist):
            if part == char:
                continue
            i+=1
            w,h = [10,10]
            x = part.pos[0]-w//2
            y = part.pos[1]-h//2
            print [p,char.target.pos],[[x,y],[w,h]]
            if line_box(shoot_path,[[x,y],[w,h]]):
                target = part
                print "found target"
                break
        if not target or target.dist>char.hit_region.range**2:
            self.children.append(popup_text("Miss",tp[:]))
            return
        angle = hit_region(char.pos,target.pos).target_angle
        width = char.hit_region.half_width
        print width
        diff = abs(char.hit_region.target_angle-angle)+width/3.0
        print diff
        r = abs(random.randint(int(angle-diff),int(angle+diff))-angle)
        if r>10:
            self.children.append(popup_text("Near miss",target.pos[:]))
            return
        damage = char.weapon.stats["damage"]
        tp = target.pos
        target.hp-=damage
        self.children.append(popup_text(str(damage),tp[:]))
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
                self.next_mode = 0.01
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
        #~ if char.weapon.stats["type"]=="knife":
            #~ if not char.target:
                #~ p = self.players()
                #~ if p:
                    #~ char.target = p[0]
            #~ elif char.target not in char.spot.near():
                #~ options = char.spot.can_move()
                #~ if options:
                    #~ char.set_spot(choose_closest_to(char.target,options))
            #~ else:
                #~ self.shoot(char)
        #~ elif char.weapon.stats["type"]=="gun":
            #~ if not char.target:
                #~ p = self.players()
                #~ if p:
                    #~ char.target = p[0]
            #~ else:
                #~ self.shoot(char)
        self.next()