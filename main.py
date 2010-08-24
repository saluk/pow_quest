import sys
import pygame
import random
pygame.init()

from lib.things import *
from lib.fight import *

res = [800,600]
fs = 0
screen = pygame.display.set_mode(res,pygame.FULLSCREEN*fs)

surf = pygame.Surface([320,200])
pygame.mainfont = pygame.font.Font("fonts/lucon.ttf",7)
bg = pygame.image.load("design/mockup.png")

pygame.timer = pygame.time.Clock()

scene = thing()
pygame.scene = scene

def load_scene(scene_name,char):
    scene = pygame.cur_scene = pygame.scene_data[scene_name]
    pygame.scene.children = []
    pygame.bg = sprite("art/"+scene["map"]+".png",[0,0])
    pygame.scene.children.append(pygame.bg)
    pygame.scene.sprites = thing()
    pygame.scene.sprites.sort_mode = "y"
    pygame.scene.children.append(pygame.scene.sprites)
    pygame.scene.sprites.children.append(char)
    

f = open("data/scenes.txt")
pygame.scene_data = eval(f.read())

bunker = sprite("art/t-junction.png",[0,0])
scene.children.append(bunker)

man = char("army",[160,100])
load_scene("start",man)

enemies = []
for x in range(5):
    enemy_man = char("army",[random.randint(40,240),random.randint(40,240)])
    scene.sprites.children.append(enemy_man)
    enemies.append(enemy_man)
scene.sprites.children.append(man)
main_menu = menu([10,30],60,["New Game","Quit","Fight","Popup","edit fight"])
scene.children.append(main_menu)
def new_game():
    scene.children = [main_menu]
def quit():
    sys.exit()
def fight_test():
    scene.children = [fight_scene(scene.children,[man],enemies)]
def popup():
    scene.children.append(popup_text("Some popup text",[150,30]))
def edit_fight():
    import lib.fight_edit
    scene.children = [lib.fight_edit.edit(scene.children)]
main_menu.new_game = new_game
main_menu.quit = quit
main_menu.fight = fight_test
main_menu.popup = popup
main_menu.edit_fight = edit_fight


bgcolor = (215,196,146)
def col(man):
    for region in pygame.cur_scene["regions"]:
        if man.pos[0]>=region[0] and man.pos[0]<=region[0]+region[2] and man.pos[1]>=region[1] and man.pos[1]<=region[1]+region[3]:
            r = pygame.cur_scene["regions"][region]
            if r["type"] == "warp":
                load_scene(r["scene"],man)
                man.pos = r["spot"]
                return False
    bg = pygame.bg.surf
    if bg.get_at([int(x) for x in man.pos])[:3] != bg.get_at([0,0])[:3]:
        return True
    return False
        
running = 1
while running:
    dt = pygame.timer.tick(60)/1000.0
    
    surf.fill([0,0,0])
    
    scene.update_children(dt)
    scene.draw_children(surf)
    
    screen.blit(pygame.transform.scale(surf,res),[0,0])
    pygame.display.flip()
    
    
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running = 0
        if e.type==pygame.KEYDOWN and e.key==pygame.K_x and e.mod | pygame.K_LALT:
            running = 0
        if e.type==pygame.KEYDOWN and e.key==pygame.K_q and e.mod | pygame.K_LCTRL:
            running = 0
        if e.type==pygame.MOUSEBUTTONDOWN:
            sc = 320.0/res[0],200.0/res[1]
            p = [int(e.pos[0]*sc[0]),int(e.pos[1]*sc[1])]
            scene.mouse_click(p)
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
    if keys[pygame.K_RIGHT]:
        man.set_facing("e")
        horiz(man,speed)
        #vert(man,speed/3)
    if keys[pygame.K_LEFT]:
        man.set_facing("w")
        horiz(man,-speed)
        #vert(man,-speed/3)
    if keys[pygame.K_DOWN]:
        man.set_facing("s")
        vert(man,speed)
        #horiz(man,-speed/3)
    if keys[pygame.K_UP]:
        man.set_facing("n")
        vert(man,-speed)
        #horiz(man,speed/3)