import pygame

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

class textbox(thing):
    def __init__(self,text,pos,width=150):
        super(textbox,self).__init__()
        self.lines = []
        self.to_print = list(text)
        self.next = 0.02
        self.pos = pos
        self.font = pygame.mainfont
        self.color = [255,255,255]
        self.width = width
    def update(self,dt):
        if not self.to_print:
            return
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
        for line in self.lines:
            rline = self.render_line(line)
            surf.blit(rline,[x,y])
            y+=rline.get_height()+1
            
class quick_textbox(textbox):
    def update(self,dt):
        while self.to_print:
            super(quick_textbox,self).update(5)
            
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
        if img not in self.images:
            self.images[img] = pygame.image.load(img).convert()
            self.images[img].set_colorkey([255,0,255])
        self.surf = self.images[img]
        self.pos = pos
        self.center = False
    def draw(self,surf):
        cp = self.pos[:]
        if self.center:
            cp[0]-=self.surf.get_width()//2
            cp[1]-=self.surf.get_height()//2
        surf.blit(self.surf,cp)
        
class char(sprite):
    def __init__(self,tag,pos,facing="s"):
        self.tag = tag
        self.pos = pos
        self.set_facing(facing)
    def set_facing(self,facing):
        super(char,self).__init__("art/%s_%s_idle.png"%(self.tag,facing),self.pos)
        self.center = True
        
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
                command = c.lines[0]
                getattr(self,command.replace(" ","_").lower())()
                return True