import pygame
import math

class thing(object):
    kill = 0
    def __init__(self):
        self.children = []
        self.pos = [0,0]
        self.sort_mode = None
    def update_children(self,dt):
        if self.sort_mode == "y":
            self.children.sort(key=lambda o: o.pos[1])
        [x.update_children(dt) for x in self.children]
        self.update(dt)
        self.children = [x for x in self.children if not x.kill]
    def update(self,dt):
        pass
    def draw_children(self,surf):
        self.predraw(surf)
        [x.draw_children(surf) for x in self.children]
        self.draw(surf)
    def draw(self,surf):
        pass
    def predraw(self,surf):
        pass
    def mouse_click(self,pos,mode="default"):
        for c in reversed(self.children):
            if c.mouse_click(pos,mode):
                return True
    def mouse_over(self,pos):
        for c in reversed(self.children):
            if c.mouse_over(pos):
                return True
    def keypress(self,text):
        for c in reversed(self.children):
            if c.keypress(text):
                return True

class textbox(thing):
    def __init__(self,text,pos,width=150,maxy=200,miny=0):
        super(textbox,self).__init__()
        self.lines = []
        self.to_print = list(text)
        self.next = 0.02
        self.pos = pos
        self.font = pygame.mainfont
        self.color = [255,255,255]
        self.width = width
        self.height = 0
        self.maxy = maxy
        self.miny = miny
    def update(self,dt):
        if not self.to_print:
            return
        self.height = 0
        self.next -= dt
        if self.next < 0:
            self.next = 0.02
            a = self.to_print.pop(0)
            if not self.lines:
                self.lines.append("")
            if a=="\n":
                self.lines.append("")
                return
            l = self.lines[-1] + a
            rline = self.render_line(l)
            if rline.get_width()>self.width:
                if " " not in l:
                    left,right = rline[:-1],rline[-1:]
                else:
                    left,right = l.rsplit(" ",1)
                self.lines[-1] = left
                self.lines.append(right)
            else:
                self.lines[-1] = l
    def render_line(self,text):
        return self.font.render(text,1,self.color)
    def draw(self,surf):
        x,y = self.pos
        height = len(self.lines)*10
        if y+height>self.maxy:
            y-=(y+height-self.maxy)
        if y<self.miny:
            y = self.miny
        for line in self.lines:
            rline = self.render_line(line)
            surf.blit(rline,[x,y])
            y+=rline.get_height()+1
            
class quick_textbox(textbox):
    def update(self,dt):
        while self.to_print:
            super(quick_textbox,self).update(5)
            
class border_textbox(quick_textbox):
    def predraw(self,surf):
        x,y=self.pos
        height = len(self.lines)*10
        if y+height>self.maxy:
            y-=(y+height-self.maxy)
        if y<self.miny:
            y = self.miny
        outcol = [124,124,124]
        incol = [70,70,70]
        bgcol = [0,0,0]
        pygame.draw.rect(surf,bgcol,[[x+1,y+1],[self.width-2,height-2]])
        pygame.draw.line(surf,outcol,[x+1,y],[x+self.width-1,y])
        pygame.draw.line(surf,outcol,[x+1,y+height],[x+self.width-1,y+height])
        pygame.draw.line(surf,outcol,[x,y+1],[x,y+height-1])
        pygame.draw.line(surf,outcol,[x+self.width,y+1],[x+self.width,y+height-1])
        pygame.draw.line(surf,incol,[x+1,y+1],[x+self.width-1,y+1])
        pygame.draw.line(surf,incol,[x+1,y+height-1],[x+self.width-1,y+height-1])
        pygame.draw.line(surf,incol,[x+1,y+1],[x+1,y+height-1])
        pygame.draw.line(surf,incol,[x+self.width-1,y+1],[x+self.width-1,y+height-1])
            
class entry_box(quick_textbox):
    def keypress(self,text):
        if text == "backspace":
            self.lines[0] = self.lines[0][:-1]
            return
        try:
            self.lines[0]+=chr(ord(text[0]))
        except:
            pass
            
class popup_text(quick_textbox):
    direction = -1
    time = 0.3
    def update(self,dt):
        super(popup_text,self).update(dt)
        self.time -= dt
        self.pos[1] += self.direction
        if self.time<0:
            if self.direction == -1:
                self.direction = 1
                self.time = 0.3
            elif self.direction == 1:
                self.direction = 0
                self.time = 0.3
            else:
                self.kill = 1
            
class textbox_chain(thing):
    def __init__(self,text):
        super(textbox_chain,self).__init__()
        self.text = text
        self.next_box = 4.0
    def update(self,dt):
        if not self.children:
            self.add_textbox()
        else:
            self.wait_children(dt)
    def add_textbox(self):
        """Get next command from self.text about a textbox and build it."""
        if not self.text:
            return
        pos,text,rest = self.text.split(";",2)
        x,y,width,self.next_box = [int(x) for x in pos.split(",")]
        self.text = rest
        tb = textbox(text,[x,y],width)
        self.children.append(tb)
    def wait_children(self,dt):
        if self.children[0].to_print:
            return
        self.next_box -= dt
        if self.next_box<0:
            del self.children[0]
            
class sprite(thing):
    images = {}
    def __init__(self,img,pos):
        super(sprite,self).__init__()
        self.load(img)
        self.pos = pos
        self.center = False
    def load(self,img):
        if img not in self.images:
            self.images[img] = pygame.image.load(img).convert()
            self.images[img].set_colorkey([255,0,255])
        self.img_name = img
        self.surf = self.images[img]
    def draw(self,surf):
        cp = self.pos[:]
        if self.center:
            cp[0]-=self.surf.get_width()//2
            cp[1]-=self.surf.get_height()//2
        surf.blit(self.surf,cp)
    def region(self):
        cp = self.pos[:]
        s = self.surf.get_size()
        if self.center:
            cp[0]-=s[0]//2
            cp[1]-=s[1]//2
        return cp,s
        
class char(sprite):
    def __init__(self,tag,pos,facing="s"):
        self.tag = tag
        self.pos = pos
        self.set_facing(facing)
        self.weapon = None
        self.armor = {"chest":None,"legs":None,"head":None}
        self.actions = ["talk"]
    def set_facing(self,facing):
        self.facing = facing
        super(char,self).__init__("art/%s_%s_idle.png"%(self.tag,facing),self.pos)
        self.center = True
        
class enemy_char(char):
    def perception(self,obs):
        for o in obs:
            if self.can_see(o):
                return True
    def can_see(self,ob):
        rise = self.pos[0]-ob.pos[0]
        run = self.pos[1]-ob.pos[1]
        ang = math.atan2(run,rise)*180.0/math.pi
        curang = {"e":0,"n":90,"w":180,"s":270}[self.facing]
        while ang<0:
            ang+=360
        if ang<curang:
            ang,curang = curang,ang
        if ang-curang<60:
            return True
    def update(self,dt):
        super(enemy_char,self).update(dt)
        if self.kill:
            return
        if self.can_see(pygame.player):
            pygame.scene.make_fight = True
        
        
class player_char(char):
    frob_range = 15
    def __init__(self,*args):
        super(player_char,self).__init__(*args)
        self.inventory = ["bandaid","smg"]
        self.display_stats = border_textbox("",self.pos)
    def update(self,dt):
        if self.stats and not hasattr(self,"hp"):
            self.hp = self.stats["maxhp"]
    def mouse_over(self,pos):
        self.hovering = False
        cp,s = self.region()
        if pos[0]>=cp[0] and pos[0]<=cp[0]+s[0] and\
            pos[1]>=cp[1] and pos[1]<=cp[1]+s[1]:
            text = "hp:%s\n"%self.hp
            for s in sorted(self.stats):
                if s in ["type"]:
                    continue
                cur = self.stats[s]
                text+="%s: %s\n"%(s,cur)
            self.display_stats.lines = []
            self.display_stats.to_print = list(text)
            self.display_stats.update(5)
            self.display_stats.pos = self.pos
            pygame.scene.info_window = self.display_stats
            return True
    def draw(self,surf):
        super(player_char,self).draw(surf)
        pygame.scene.clickable = []
        for ob in pygame.scene.sprites.children:
            if ob == self:
                continue
            if not hasattr(ob,"actions"):
                continue
            cp,s = ob.region()
            center = cp[0]+s[0]//2,cp[1]+s[1]//2
            size = max(s)
            if (center[0]-self.pos[0])**2+(center[1]-self.pos[1])**2<self.frob_range**2:
                #pygame.draw.circle(surf,[0,0,0],center,size//2,1)
                pygame.draw.line(surf,[255,250,240],[cp[0]-1,cp[1]-1],[cp[0]+3,cp[1]-1])
                pygame.draw.line(surf,[255,250,240],[cp[0]+s[0]-3,cp[1]-1],[cp[0]+s[0]+1,cp[1]-1])
                pygame.draw.line(surf,[255,250,240],[cp[0]-1,cp[1]+s[1]],[cp[0]+3,cp[1]+s[1]])
                pygame.draw.line(surf,[255,250,240],[cp[0]+s[0]-3,cp[1]+s[1]],[cp[0]+s[0]+1,cp[1]+s[1]])
                pygame.scene.clickable.append(ob)

        
class door(sprite):
    def __init__(self,tag,pos,state="closed"):
        self.tag = tag
        self.pos = pos
        self.state = state
        self.set_facing()
        self.actions = ["open","close"]
    def set_facing(self):
        super(door,self).__init__("art/%s_%s.png"%(self.tag,self.state),self.pos)
    def mouse_click(self,pos,mode):
        if not self in pygame.scene.clickable:
            return
        c = self
        w,h = self.surf.get_size()
        if pos[0]>=c.pos[0] and pos[0]<=c.pos[0]+w and pos[1]>=c.pos[1] and pos[1]<=c.pos[1]+h:
            if self.state == "closed":
                self.state = "open"
            elif self.state == "open":
                self.state = "closed"
            self.set_facing()
            
class item(sprite):
    def __init__(self,tag,pos,char,world=False,stats={}):
        super(item,self).__init__("art/"+tag+".png",pos)
        self.tag = tag
        self.char = char
        self.hover = False
        self.world = world   #In the scene or on the interface
        self.stats = stats
        self.actions = ["pickup"]
    def mouse_click(self,pos,mode):
        if pos[0]>=self.pos[0] and pos[0]<=self.pos[0]+14 and pos[1]>=self.pos[1] and pos[1]<=self.pos[1]+16:
            if not self.world:
                return self.execute()
            else:
                return self.pickup()
    def mouse_over(self,pos):
        self.children = []
        if pos[0]>=self.pos[0] and pos[0]<=self.pos[0]+14 and pos[1]>=self.pos[1] and pos[1]<=self.pos[1]+16:
            t = self.tag
            for s in sorted(self.stats):
                t+="\n"+s+": "+str(self.stats[s])
            self.children = [border_textbox(t,[self.pos[0],self.pos[1]],maxy=self.pos[1])]
    def execute(self):
        d = {}
        d.update(self.stats)
        d["tag"] = self.tag
        if d["type"]=="weapon":
            if not self.char.weapon or self.char.weapon["tag"]!=self.tag:
                self.char.weapon = d
            else:
                self.char.weapon = None
            return "changed weapon"
        if d["type"]=="armor":
            if not self.char.armor[d["position"]] or self.char.armor[d["position"]]["tag"] != self.tag:
                self.char.armor[d["position"]] = d
            else:
                self.char.armor[d["position"]] = None
            return "changed armor"
    def pickup(self):
        if not self in pygame.scene.clickable:
            return
        if not self.kill:
            self.kill = 1
            pygame.player.inventory.append(self.tag)
        return "picked up"
    def predraw(self,surf):
        self.draw_box(surf)
        self.draw_item(surf)
    def draw_box(self,surf):
        if self.world:
            return
        color = [0,0,0]
        if self.char and self.char.weapon and self.weapon_stats()["tag"] == self.tag:
            color = [0,0,100]
        if self.char and "position" in self.stats and self.char.armor[self.stats["position"]] and self.armor_stats(self.stats["position"])["tag"] == self.tag:
            color = [0,0,100]
        pygame.draw.rect(surf,color,[self.pos,[14,16]])
    def draw_item(self,surf):
        super(item,self).draw(surf)
    def draw(self,surf):
        pass
    def weapon_stats(self):
        if hasattr(self.char.weapon,"stats"):
            return self.char.weapon.stats
        return self.char.weapon
    def armor_stats(self,position):
        ar = self.char.armor[position]
        if hasattr(ar,"stats"):
            return ar.stats
        return ar
            
class inventory_menu(thing):
    def __init__(self,char,pos):
        super(inventory_menu,self).__init__()
        self.pos = pos
        self.char = char
        self.last_invlist = []
    def update(self,dt):
        if self.char.inventory != self.last_invlist:
            self.children = []
            x,y = self.pos
            for o in self.char.inventory:
                self.children.append(item(o,[x,y+3],self.char,False,pygame.all_items[o]))
                x+=14
            self.last_invlist = self.char.inventory[:]
            
class fight_inventory_menu(inventory_menu):
    def __init__(self,char,pos,fight_scene):
        super(fight_inventory_menu,self).__init__(char,pos)
        self.fight_scene = fight_scene
    def mouse_click(self,pos,mode):
        if self.fight_scene.inv_ok:
            pickup = super(fight_inventory_menu,self).mouse_click(pos,mode)
            if pickup:
                self.char.reset_hit_region()
                self.fight_scene.next()
    def draw(self,surf):
        if self.fight_scene.inv_ok:
            pygame.draw.line(surf,[255,255,255],[0,183],[320,183])
        super(fight_inventory_menu,self).draw(surf)
    
        
class menu(thing):
    def __init__(self,pos,width,options=None):
        super(menu,self).__init__()
        self.pos = pos
        self.width = width
        self.options = []
        self.last_options = None
        if options:
            self.options = options
    def predraw(self,surf):
        x,y=self.pos
        height = len(self.options)*10
        outcol = [124,124,124]
        incol = [70,70,70]
        bgcol = [0,0,0]
        pygame.draw.rect(surf,bgcol,[[x+1,y+1],[self.width-2,height-2]])
        pygame.draw.line(surf,outcol,[x+1,y],[x+self.width-1,y])
        pygame.draw.line(surf,outcol,[x+1,y+height],[x+self.width-1,y+height])
        pygame.draw.line(surf,outcol,[x,y+1],[x,y+height-1])
        pygame.draw.line(surf,outcol,[x+self.width,y+1],[x+self.width,y+height-1])
        pygame.draw.line(surf,incol,[x+1,y+1],[x+self.width-1,y+1])
        pygame.draw.line(surf,incol,[x+1,y+height-1],[x+self.width-1,y+height-1])
        pygame.draw.line(surf,incol,[x+1,y+1],[x+1,y+height-1])
        pygame.draw.line(surf,incol,[x+self.width-1,y+1],[x+self.width-1,y+height-1])
    def update(self,dt):
        if self.options != self.last_options:
            self.children = []
            x,y = self.pos
            for o in self.options:
                self.children.append(quick_textbox(o,[x+3,y+2],self.width-5))
                y+=10
            self.last_options = self.options
    def mouse_click(self,pos,mode):
        for c in self.children:
            if pos[0]>=c.pos[0] and pos[0]<=c.pos[0]+c.width and pos[1]>=c.pos[1] and pos[1]<=c.pos[1]+10:
                self.execute(c)
                return True
    def execute(self,option):
        try:
            command = option.lines[0]
            getattr(self,command.replace(" ","_").lower())()
        except:
            import traceback
            traceback.print_exc()