import sys
import pygame
import random
pygame.init()
import pygame.mixer
pygame.mixer.init()

from lib.things import *

res = [800,600]
fs = 0
screen = pygame.display.set_mode(res,pygame.FULLSCREEN*fs)

from lib.fight import *

surf = pygame.Surface([320,200])
pygame.mainfont = pygame.font.Font("fonts/lucon.ttf",7)
bg = pygame.image.load("design/mockup.png")

pygame.timer = pygame.time.Clock()

class game_scene(thing):
    make_fight = False
    info_window = None
    def mouse_over(self,pos):
        if self.info_window in self.children:
            self.children.remove(self.info_window)
        self.info_window = None
        super(game_scene,self).mouse_over(pos)
        if self.info_window and self.info_window not in self.children:
            self.children.append(self.info_window)
    def update(self,dt):
        old_window = self.info_window
        super(game_scene,self).update(dt)
        if self.make_fight:
            enemies = [x for x in self.enemies if not x.kill]
            players = [x for x in [pygame.player] if not x.kill]
            obs = [x for x in self.sprites.children if x not in enemies and x not in players and not x.kill]
            self.children = [fight_scene(self.children,players,enemies,pygame.bg,pygame.cur_scene["fight"],obs)]
            self.make_fight = False
    def load_scene(self,scene,char):
        global load_scene
        load_scene(scene,char)

scene = game_scene()
pygame.scene = scene
pygame.gui = thing()
game = thing()
game.children = [pygame.scene,pygame.gui]


def debug_menu():
    main_menu = menu([10,30],60,["New Game","Quit","Fight","Popup","edit fight","edit world"])
    pygame.scene.children.append(main_menu)
    def new_game():
        scene.children = [main_menu]
    def quit():
        sys.exit()
    def fight_test():
        scene.children = [fight_scene(scene.children,[man],pygame.scene.enemies,pygame.bg,pygame.cur_scene["fight"])]
    def popup():
        scene.children.append(popup_text("Some popup text",[150,30]))
    def edit_fight():
        import lib.fight_edit
        scene.children = [lib.fight_edit.edit(scene.children,pygame.cur_scene_name)]
    def edit_world():
        import lib.world_edit
        scene.children = [lib.world_edit.edit(scene.children,pygame.cur_scene_name)]
    main_menu.new_game = new_game
    main_menu.quit = quit
    main_menu.fight = fight_test
    main_menu.popup = popup
    main_menu.edit_fight = edit_fight
    main_menu.edit_world = edit_world

def play_music(x):
    if hasattr(pygame,"cur_music"):
        print x,pygame.cur_music
        if pygame.cur_music==x:
            return
    pygame.cur_music = x
    pygame.mixer.music.load("music/"+x)
    pygame.mixer.music.play(-1)
pygame.play_music = play_music

def load_scene(scene_name,char):
    pygame.cur_scene_name = scene_name
    scene = pygame.cur_scene = pygame.scene_data[scene_name]
    pygame.scene.children = []
    pygame.bg = sprite("art/"+scene["map"]+".png",[0,0])
    pygame.scene.children.append(pygame.bg)
    pygame.scene.sprites = thing()
    pygame.scene.sprites.sort_mode = "y"
    pygame.scene.children.append(pygame.scene.sprites)
    pygame.scene.sprites.children.append(char)
    
    pygame.scene.clickable = []
    
    pygame.scene.enemies = []
    for ob in scene["obs"]:
        if ob.kill:
            continue
        pygame.scene.sprites.children.append(ob)
        if getattr(ob,"is_enemy",False):
            pygame.scene.enemies.append(ob)
            
    #~ if pygame.scene.enemies:
        #~ pygame.scene.children = [fight_scene(pygame.scene.children,[man],pygame.scene.enemies,pygame.bg,pygame.cur_scene["fight"])]
    pygame.scene.children.append(inventory_menu(man,[0,184]))
    debug_menu()
    play_music("chips/YIFFY.IT")

f = open("data/scenes.txt")
pygame.scene_data = eval(f.read())

pygame.all_items = eval(open("data/items.txt").read())
pygame.all_stats = eval(open("data/stats.txt").read())

pygame.all_objects = []
for o in eval(open("data/objects.txt").read()):
    ob = None
    if o["pos"] == "random":
        pos = [random.randint(40,140),random.randint(40,140)]
    else:
        pos = o["pos"]
    if o["type"] in pygame.all_stats:
        ob = enemy_char("army",pos)
        ob.stats = pygame.all_stats[o["type"]]
        ob.is_enemy = True
    if o["type"] == "door":
        ob = door("door1",pos,"closed")
    if o["type"] == "doorbars":
        ob = door("doorbars",pos,"closed")
    if o["type"] in pygame.all_items:
        ob = item(o["type"],pos,False,True,pygame.all_items[o["type"]])
    if o["type"] == "crate":
        ob = sprite("art/crate.png",pos)
    if o["type"] == "switch":
        ob = switch("art/redbutton.png",pos)
        ob.tag = "a"
    if o["type"] == "switchb":
        ob = switch("art/switchb.png",pos)
        ob.tag = "b"
    if o["type"].startswith("4waydoor"):
        ob = door(o["type"],pos,"closed")
    if ob:
        ob.data = o
        obs = pygame.scene_data[o["scene"]].get("obs",[])
        obs.append(ob)
        pygame.scene_data[o["scene"]]["obs"] = obs
        pygame.all_objects.append(ob)

bunker = sprite("art/t-junction.png",[0,0])
scene.children.append(bunker)

man = player_char("b",[129,152])
man.stats = pygame.all_stats["player"]
pygame.player = man
pygame.player.update(1)
load_scene("cell",man)
scene.sprites.children.append(man)

scene.children.append(border_textbox("""
Oh no! The green army has caught you sneaking around their base!
You'll have to try and escape. Click on nearby objects to interact
with them. The inventory on the bottom will let you use
healing and equip or unequip items. If the enemy spots you
you will have to fight! First, to escape your prison...

You have heard rumors of a hidden switch inside the brick walls.
(click to exit)""",[0,100],width=300,timeout=10))

bgcolor = (215,196,146)
def col(man):
    for s in pygame.scene.sprites.children:
        if s == man:
            continue
        p = man.pos
        r,ss = s.region()
        if p[0]>=r[0] and p[0]<=r[0]+ss[0] and p[1]>=r[1] and p[1]<=r[1]+ss[1]:
            if s.data.get("destination",None) and s.state=="open":
                if s.data["destination"]["scene"]:
                    load_scene(s.data["destination"]["scene"],man)
                    man.pos = s.data["destination"]["pos"][:]
                    closest_door = None
                    closest_d = 10000
                    for door in pygame.scene.sprites.children:
                        if hasattr(door,"data") and door.data.get("destination",None):
                            d = (man.pos[0]-door.pos[0])**2+(man.pos[1]-door.pos[1])**2
                            if d<closest_d:
                                closest_door = door
                                closest_d = d
                    if closest_door:
                        print closest_door.data["destination"]
                        closest_door.state = "open"
                        closest_door.set_facing()
                return False
            return True
    bg = pygame.bg.surf
    try:
        if bg.get_at([int(x) for x in man.pos])[:3] != bg.get_at([0,0])[:3]:
            return True
    except:
        return True
    return False
        
running = 1
while running:
    dt = pygame.timer.tick(60)/1000.0
    
    surf.fill([0,0,0])
    
    game.update_children(dt)
    game.draw_children(surf)
    
    sc2x = surf#pygame.transform.scale2x(surf)
    screen.blit(pygame.transform.scale(sc2x,res),[0,0])
    pygame.display.flip()
    
    sc = 320.0/res[0],200.0/res[1]
    mp = pygame.mouse.get_pos()
    mp = [int(mp[0]*sc[0]),int(mp[1]*sc[1])]
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running = 0
        if e.type==pygame.KEYDOWN and e.key==pygame.K_x and e.mod | pygame.K_LALT:
            running = 0
        if e.type==pygame.KEYDOWN and e.key==pygame.K_q and e.mod | pygame.K_LCTRL:
            running = 0
        if e.type==pygame.MOUSEBUTTONDOWN:
            game.mouse_click(mp)
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_BACKSPACE:
                game.keypress("backspace")
            else:
                game.keypress(e.unicode)
    
    game.mouse_over(mp)

    keys = pygame.key.get_pressed()
    speed = 40
    
    op = man.pos[:]
    def vert(man,amt):
        man.pos[1]+=amt*dt
        if col(man):
            man.pos[1]-=amt*dt
    def horiz(man,amt):
        man.pos[0]+=amt*dt
        if col(man):
            man.pos[0]-=amt*dt
    if keys[pygame.K_d]:
        man.set_facing("e")
        horiz(man,speed)
        #vert(man,speed/3)
    if keys[pygame.K_a]:
        man.set_facing("w")
        horiz(man,-speed)
        #vert(man,-speed/3)
    if keys[pygame.K_s]:
        man.set_facing("s")
        vert(man,speed)
        #horiz(man,-speed/3)
    if keys[pygame.K_w]:
        man.set_facing("n")
        vert(man,-speed)
        #horiz(man,speed/3)