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
        self.angle = self.target_angle
        self.range = range
        self.half_width = band//2  #half the angle width
        self.min_half_width = 5
        self.shrink_rate = 5
        self.update_stats()
    def random_angle(self):
        """Pick a random firing angle based on our width. Distribution should be somewhat normal,
        center angle should be more common than edges."""
        mean = self.target_angle
        std_dev = self.half_width/3.0
        ang = random.gauss(mean,std_dev)
        self.angle = ang
    def to_line(self):
        """Pick a random firing angle based on our width. Distribution should be somewhat normal,
        center angle should be more common than edges."""
        return make_line(self.start_pos,self.angle,self.range)
    def update_stats(self):
        rise = self.target_pos[0]-self.start_pos[0]
        run = self.target_pos[1]-self.start_pos[1]
        ang = math.atan2(run,rise)
        self.target_angle = ang*180.0/math.pi
        while self.target_angle<0:
            self.target_angle += 360
        self.angle = self.target_angle
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
    hits = []
    for bline in [line1,line2,line3,line4]:
        hp = geometry.calculateIntersectPoint(line[0],line[1],bline[0],bline[1])
        if hp:
            hits.append(hp)
    return hits
        
hr = hit_region(range=200)
hr.start_pos = [155,108]
hr.target_pos = [126,74]
hr.update_stats()
rc = char("army",hr.start_pos)
ec = char("army",hr.target_pos)
hit_points = line_box(hr.to_line(),ec.region())
hr = hit_region(range=200)
assert hit_points
hr = hit_region([155, 108],[185.77732664830461, 56.495086017122986],range=1000)
line = hr.to_line()
assert geometry.calculateIntersectPoint(line[0],line[1],[86, 31], [302, 57])
assert not geometry.calculateIntersectPoint([155, 108], [158, 48],[86, 31], [302, 57])

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
    def __init__(self,tag):
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
        self.stats = {"maxhp":30,"reaction":5,"accuracy":1,"armor":1,"weapon":"hands"}
        self.hp = 30
        self.pos = [0,0]
        self.spot = None
        self.weapon = {"range":50,"damage":2,"accuracy":4,"tag":"hands"}
        self.armor = {"chest":None,"legs":None,"head":None}
        #Chest is up to 0.5 coverage, legs are 0.2 and head is 0.25
        self.sprite = char(tag,[100,100])
        self.health_bar = quick_textbox("",[100,100])
        self.children = []
        self.enemy = False
        self.action = None
        self.target = None
        self.buff = {}
        self.hit_region = hit_region(start=self.pos,end=self.pos,band=30)
        self.hovering = False
        self.display_stats = border_textbox("",self.pos)
    def region(self):
        return self.sprite.region()
    def mouse_over(self,pos):
        self.hovering = False
        cp,s = self.sprite.region()
        if pos[0]>=cp[0] and pos[0]<=cp[0]+s[0] and\
            pos[1]>=cp[1] and pos[1]<=cp[1]+s[1]:
            self.hovering = True
            return True
    def draw(self,surf):
        self.health_bar.pos = [self.sprite.pos[0]+5,self.sprite.pos[1]+5]
        self.health_bar.lines = ["%s/%s"%(self.hp,self.stats["maxhp"])]
        self.health_bar.draw(surf)
        if self.target:
            if not self.enemy or self.hovering:
                self.hit_region.draw(surf)
        if self.hovering:
            text = ""
            if self.buff:
                text += "Gassed!\n"
            text += "hp:%s\n"%self.hp
            for s in sorted(self.stats):
                if s in ["type"]:
                    continue
                cur = self.stats[s]
                real = self.get_stat(s)
                if cur==real:
                    text+="%s: %s\n"%(s,cur)
                else:
                    text+="%s: %s(%s)\n"%(s,cur,real)
            self.display_stats.lines = []
            self.display_stats.to_print = list(text)
            if self.display_stats not in self.children:
                self.children.append(self.display_stats)
        else:
            if self.display_stats in self.children:
                self.children.remove(self.display_stats)
    def set_spot(self,spot):
        if spot.contains:
            return
        if self.spot:
            self.spot.contains = None
            if self.sprite in self.children:
                self.children.remove(self.sprite)
        self.children = []
        if not spot:
            return
        if not spot.contains:
            spot.contains = self
            self.spot = spot
            self.children.append(self.sprite)
            self.pos = self.sprite.pos = self.spot.pos
            self.reset_hit_region()
            self.fight_scene.moving_piece(self)
        return self
    def reset_hit_region(self):
        if not self.weapon:
            self.weapon = {"range":50,"damage":2,"accuracy":4,"tag":"hands"}
        self.hit_region.start_pos = self.pos[:]
        if self.target:
            self.hit_region.target_pos = self.target.pos[:]
        self.hit_region.half_width = 90-self.get_stat("accuracy")*10
        self.hit_region.range = self.weapon["range"]
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
        if key=="coverage":
            return sum([x["coverage"] for x in self.armor.values() if x])
        s = self.stats[key]
        if self.weapon and key in self.weapon:
            s+=self.weapon[key]
        for a in self.armor.values():
            if a and key in a:
                s+=a[key]
        if key in self.buff:
            s+=self.buff[key]
        return s
    def damage(self,amount):
        if random.random()<self.get_stat("coverage"):
            amount *= (0.75**self.get_stat("armor"))
        self.hp -= amount
        return amount

class action_menu(menu):
    """The fighting menu for a person"""
    def __init__(self,character):
        x,y = [256,142]
        super(action_menu,self).__init__([x,y],60)
        self.character = character
        self.init_options()
    def init_options(self):
        character = self.character
        if character.weapon:
            self.options.append("target")
            if character.target:
                self.options.append("aim")
                self.options.append("shoot")
        self.options.append("use item")
        if character.spot.can_move():
            self.options.append("move")
    def move(self):
        pygame.fight_scene.move_menu(self.character)
    def target(self):
        pygame.fight_scene.target_menu(self.character)
    def shoot(self):
        pygame.fight_scene.shoot_menu(self.character)
    def use_item(self):
        pygame.fight_scene.inv_ok = True
    def aim(self):
        self.character.aim()
        pygame.fight_scene.next()

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
                
class grenade_menu(thing):
    def __init__(self,char,stats):
        super(grenade_menu,self).__init__()
        self.children = []
        self.char = char
        self.stats = stats
        self.drawpos = [0,0]
    def draw(self,surf):
        pygame.draw.circle(surf,[255,50,50],self.drawpos,self.stats["range"],1)
    def mouse_over(self,pos):
        self.drawpos = pos
    def mouse_click(self,pos,mode):
        self.char.inventory.remove(self.stats["tag"])
        pygame.fight_scene.throw_grenade(self.stats,self.char,pos)
        self.kill = 1
        pygame.fight_scene.next()
        return True
                
class target_menu(thing):
    def __init__(self,char,chars):
        super(target_menu,self).__init__()
        self.children = []
        self.char = char
        self.chars = chars
    #~ def draw(self,surf):
        #~ for s in self.chars:
            #~ x = s.pos[0]-10
            #~ y = s.pos[1]-10
            #~ pygame.draw.rect(surf,[255,0,0],[[x,y],[20,20]])
            #~ pygame.draw.line(surf,[255,255,255],self.char.pos,s.pos)
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
    
class shot_line(thing):
    def __init__(self,path,speed,parent,popup_text,after):
        super(shot_line,self).__init__()
        self.start,self.end = path
        self.dx = int((self.end[0]-self.start[0])/(speed))
        self.dy = int((self.end[1]-self.start[1])/(speed))
        self.pen = self.start[:]
        self.speed = speed
        self.block = True
        self.parent = parent
        self.popup_text = popup_text
        self.after = after
    def update(self,dt):
        self.pen[0]+=self.dx*dt
        self.pen[1]+=self.dy*dt
        self.speed -= dt
        if self.speed<=0:
            self.kill = 1
            self.after(self)
            pt = popup_text(self.popup_text,self.pen)
            self.parent.children.append(pt)
            pt.block = True
    def draw(self,surf):
        pygame.draw.line(surf,[255,0,0],self.start,self.pen)
        
class ending(textbox):
    def __init__(self,text,after):
        self.cooldown = 2
        super(ending,self).__init__(text,[0,0])
        self.after = after
    def update(self,dt):
        super(ending,self).update(dt)
        if self.to_print:
            return
        self.cooldown -= dt
        if self.cooldown<=0:
            self.kill = 1
            self.after()
    #~ def draw(self,surf):
        #~ surf.fill([0,0,0])
        #~ super(ending,self).draw(surf)
        
class fight_scene(thing):
    def __init__(self,restore_children,goodies,enemies,bg,fight,objects,play_music=True):
        
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
            
        self.participants = []
        
        self.goodies = goodies
        for good in goodies:
            if good.kill:
                return
            spot = choose_closest_to(good,[x for x in self.spots.values() if not x.contains])
            player = realchar("b")
            if hasattr(good,"stats"):
                player.stats = good.stats
            player.fight_scene = self
            player.set_spot(spot)
            if good.weapon:
                player.weapon = good.weapon
                player.stats["weapon"] = good.weapon["tag"]
            for p in good.armor:
                player.armor[p] = good.armor[p]
            player.hp = good.hp
            player.sprite.set_facing("n")
            player.inventory = good.inventory
            self.participants = [player]
        
        self.enemies = enemies
        for enemy in enemies:
            if enemy.kill:
                return
            spot = choose_closest_to(enemy,[x for x in self.spots.values() if not x.contains])
            stats = enemy.stats
            enemy = realchar("army")
            enemy.fight_scene = self
            enemy.set_spot(spot)
            enemy.stats = stats
            enemy.hp = stats["maxhp"]
            enemy.weapon = pygame.all_items[enemy.stats["weapon"]]
            enemy.enemy = True
            self.participants.append(enemy)
        
        self.debris = []
        for o in objects:
            if "crate" in o.img_name:
                self.debris.append(o)
                self.children.append(o)
                
        self.inv_ok = False
        self.inv_gui = fight_inventory_menu(self.players()[0],[0,184],self)
        self.children.append(self.inv_gui)
        
        self.menus = thing()
        self.children.append(self.menus)
        self.turns = []
        if play_music:
            pygame.play_music("chips/rontomo.s3m")
        self.finished = False
        self.calc_turns()
        self.collide_points = []
    def load_spots_from_file(self,file):
        self.spots = {}
        self.walls = []
        data = eval(open(file).read())
        points,connections = data["points"],data["connections"]
        for p in points:
            self.spots[tuple(p)] = spot(list(p))
        for c in connections:
            a,b = c
            self.spots[tuple(a)].next.append(self.spots[tuple(b)])
            self.spots[tuple(b)].next.append(self.spots[tuple(a)])
        wp,wc = data["wall_points"],data["wall_connections"]
        for c in wc:
            a,b = c
            self.walls.append([a,b])
    def calc_turns(self):
        self.turn_start = True
        for p in self.participants:
            if p.buff:
                p.buff["turns"] -= 1
                if p.buff["turns"] <= 0:
                    p.buff = {}
            self.turns.append(p)
        self.next_mode = 1
    def next(self):
        self.turn_start = True
        self.inv_ok = False
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
    def grenade_menu(self,char,stats):
        self.menus.children = [grenade_menu(char,stats)]
    def shoot_menu(self,char):
        self.collide_points = []
        self.menus.children = []
        self.shoot(char)
        self.next()
    def shot_line(self,path,speed,text,after=lambda self:0):
        self.children.append(shot_line(path,speed,self,text,after))
    def hit_wall(self,line):
        p = line[0]
        hit = None
        hitd = 0
        for wall in self.walls:
            hp = geometry.calculateIntersectPoint(line[0],line[1],wall[0],wall[1])
            if hp:
                d = (p[0]-hp[0])**2+(p[1]-hp[1])**2
                if not hit or d<hitd:
                    hitd = d
                    hit = hp
        return hit,hitd
    def shoot(self,char):
        p = char.pos
        tp = char.target.pos
        char.hit_region.update_stats()
        shoot_angle = char.hit_region.target_angle
        for shot in range(char.weapon.get("shots",1)):
            target = None
            char.hit_region.random_angle()
            hit = self.hit_region_collide(char.hit_region,ignore=[char])
            shoot_path = char.hit_region.to_line()
            if not hit:
                self.shot_line(shoot_path,0.5,"Miss")
                continue
            if hit and hit[0] in ["debris","wall"]:
                self.shot_line([char.pos,hit[2]],0.5,"Blocked!")
                continue
            target = hit[1]
            angle = hit_region(char.pos,target.pos).target_angle
            diff = angle-shoot_angle
            if angle<shoot_angle:
                diff = shoot_angle-angle
            damage = char.weapon["damage"]
            if diff>3:
                damage*=0.5
            tp = target.pos
            def after(sl,damage=damage,target=target,self=self):
                damage = target.damage(damage)
                sl.popup_text = str(damage)
                if target.hp<=0:
                    target.set_spot(None)
                    if target in self.participants:
                        self.participants.remove(target)
                    for p in self.participants:
                        if p.target == target:
                            p.target = None
                    while target in self.turns:
                        self.turns.remove(target)
            self.shot_line([char.pos,hit[2]],0.5,"",after)
    def throw_grenade(self,stats,char,pos):
        p = char.pos[:]
        e = pos[:]
        d = math.sqrt((p[0]-e[0])**2+(p[1]-e[1])**2)
        hr = hit_region(p,e,range=min(d,150))
        hit_thing = self.hit_region_collide(hr,ignore=[char])
        if hit_thing:
            pos = hit_thing[2]
        def gg(sl,scene=self,stats=stats,pos=pos):
            scene.grenade(stats,pos)
        self.shot_line([p,pos],1,"boom!",gg)
    def hit_region_collide(self,hr,participants=True,walls=True,debris=True,ignore=[]):
        shoot_angle = hr.angle
        shoot_path = hr.to_line()
        hits = []
        if participants:
            for part in self.participants:
                if part in ignore:
                    continue
                hit_points = line_box(shoot_path,part.region())
                for hp in hit_points:
                    hits.append(("part",part,hp))
        if debris:
            for part in self.debris:
                if part in ignore:
                    continue
                hit_points = line_box(shoot_path,part.region())
                for hp in hit_points:
                    hits.append(("debris",part,hp))
        if walls:
            hit_wall,hitd = self.hit_wall(shoot_path)
            if hit_wall:
                hits.append(("wall",None,hit_wall))
        shortest = None
        p = hr.start_pos[:]
        for hit in hits:
            self.collide_points.append(("miss",hit[2]))
            hit_pos = hit[2]
            if not shortest or ((p[0]-hit_pos[0])**2+(p[1]-hit_pos[1])**2)<((p[0]-shortest[2][0])**2+(p[1]-shortest[2][1])**2):
                shortest = list(hit)
        if shortest:
            r = math.sqrt((p[0]-shortest[2][0])**2+(p[1]-shortest[2][1])**2)
            v = hit_region(p,shortest[2],range=r-2)
            line = v.to_line()
            shortest[2] = line[1]
            self.collide_points.append(("hit",shortest[2]))
        self.collide_points.append(("hit",hr.start_pos))
        return shortest
    def grenade(self,stats,pos):
        p = pos
        hit = []
        for aim_for in self.participants:
            target = None
            hr = hit_region(p,aim_for.pos,range=stats["range"])
            h = self.hit_region_collide(hr)
            if h:
                hit.append(h)
        if not hit:
            self.shot_line(hr.to_line(),0.5,"Miss")
            return
        for h in hit:
            target = h[1]
            tp = h[2]
            angle = hit_region(p,tp).target_angle
            if h[0] in ["debris",'wall']:
                self.shot_line([p,tp],0.5,"Blocked!")
                continue
            damage = stats["damage"]
            def after(sl,damage=damage,target=target,self=self,stats=stats):
                if stats["damage"]:
                    damage = target.damage(damage)
                    sl.popup_text = str(damage)
                    if target.hp<=0:
                        target.set_spot(None)
                        if target in self.participants:
                            self.participants.remove(target)
                        for p in self.participants:
                            if p.target == target:
                                p.target = None
                        while target in self.turns:
                            self.turns.remove(target)
                if stats.get("buff",None):
                    target.buff = stats["buff"].copy()
                    sl.popup_text = "Gassed!"
            self.shot_line([p,tp],0.5,"",after)
    def update(self,dt):
        "Update timers if no interface is up"
        super(fight_scene,self).update(dt)
        if [x for x in self.children if getattr(x,"block",False)]:
            return
        if self.finished:
            return
        self.finish()
        if not self.turns:
            self.calc_turns()
            return
        nt = self.turns[0]
        if hasattr(nt,"startswith") and nt.startswith("wait"):
            self.turn_start = False
            self.finish()
            self.next_mode -= dt
            if self.next_mode <= 0:
                self.next()
                self.next_mode = float(nt.split(":")[1])
        elif self.turn_start:
            self.turn_start = False
            p = nt
            if p.enemy:
                self.ai(p)
            else:
                self.action_menu(self.players()[0])
    #~ def draw(self,surf):
        #~ for p in self.participants:
            #~ pygame.draw.rect(surf,[100,100,100],p.region())
        #~ for p in reversed(sorted(self.collide_points,key=lambda x: x[0])):
            #~ if p[0]=="miss":
                #~ pygame.draw.line(surf,[255,0,255],p[1],p[1])
            #~ else:
                #~ pygame.draw.line(surf,[255,0,0],p[1],p[1])
    def moving_piece(self,x):
        for p in self.participants:
            if p.target == x:
                p.reset_hit_region()
    def clear_targets(self):
        for p in self.participants:
            if p.target not in self.participants:
                p.target = None
    def finish(self):
        if not [x for x in self.participants if not x.enemy]:
            self.finished = True
            player = self.goodies[0]
            player.pos = [129,152]
            pygame.scene.load_scene("cell",player)
        if not [x for x in self.participants if x.enemy]:
            for e in self.enemies:
                e.kill = 1
            player = self.goodies[0]
            player.pos = self.participants[0].pos
            player.hp = self.participants[0].hp
            player.weapon = self.participants[0].weapon
            player.armor = self.participants[0].armor
            pygame.play_music("chips/kupla.it")
            def after():
                pygame.scene.children = self.restore_children
                print "playing yiffy...."
                pygame.play_music("chips/YIFFY.IT")
            text = "You have killed the opposition... For now.\n"
            xp = sum([x.stats["xp"] for x in self.enemies])
            text += "You have earned %s xp.\n"%xp
            levels = player.levelup(xp)
            for l in levels:
                text += "You have gained a level!\n"
                for c in l:
                    text += "%s: %s -> %s\n"%(c)
            for e in self.enemies:
                if random.randint(0,10)>7:
                    item = random.choice(["bandaid"]*5 + ["bulletvest"]*1 + ["grenade"]*1 + ["smokegrenade"]*1)
                    text += "You also found an %s!\n"%item
                    player.inventory.append(item)
            self.children = [ending(text,after)]
            self.finished = True

    def players(self):
        return [x for x in self.participants if not x.enemy]
    def ai(self,char):
        if not char.target:
            p = self.players()
            if p:
                char.choose_target(p[0])
        if not char.target:
            self.next()
            return
        need_near = False
        result = [None]
        if char.hit_region.half_width>char.hit_region.min_half_width:
            if random.randint(0,10)>5:
                char.hit_region.shrink()
                return self.next()
        options = char.spot.can_move()
        if random.randint(0,100)>85:
            char.set_spot(choose_closest_to(char.target,options))
            return self.next()
        if need_near:
            if char.target not in char.spot.near():
                if options:
                    char.set_spot(choose_closest_to(char.target,options))
            else:
                result = self.shoot(char)
        else:
            result = self.shoot(char)
        self.next()