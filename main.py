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
bunker = sprite("art/t-junction.png",[0,0])
scene.children.append(bunker)
scene.children.append(textbox_chain("50,50,150,2;This is a test of speech. \n\
It should wrap at the right time, and go on and on and on. \
Just a basic textbox module really.;0,0,150,2;This is another textbox.;"))
man = char("army",[160,100])
scene.sprites = thing()
scene.sprites.sort_mode = "y"
scene.children.append(scene.sprites)
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
def col(man,bg):
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
            p = [e.pos[0]*sc[0],e.pos[1]*sc[1]]
            scene.mouse_click(p)
    keys = pygame.key.get_pressed()
    speed = 40
    
    op = man.pos[:]
    def vert(man,amt):
        man.pos[1]+=amt*dt
        if col(man,bunker.surf):
            man.pos[1]-=amt*dt
    def horiz(man,amt):
        man.pos[0]+=amt*dt
        if col(man,bunker.surf):
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