import pygame

class thing(object):
    def __init__(self):
        self.children = []
        self.pos = [0,0]
    def update_children(self,dt):
        [x.update_children(dt) for x in self.children]
        self.update(dt)
    def update(self,dt):
        pass
    def draw_children(self,surf):
        [x.draw_children(surf) for x in self.children]
        self.draw(surf)
    def draw(self,surf):
        pass

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