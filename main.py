import pygame
pygame.init()

from lib.things import *

res = [640,400]
fs = 1
screen = pygame.display.set_mode(res,pygame.FULLSCREEN*fs)

surf = pygame.Surface([320,200])
pygame.mainfont = pygame.font.Font("fonts/lucon.ttf",7)
bg = pygame.image.load("design/mockup.png")

pygame.timer = pygame.time.Clock()

scene = thing()
scene.children.append(sprite("art/bunker.png",[0,0]))
scene.children.append(textbox_chain("50,50,150,2;This is a test of speech. \n\
It should wrap at the right time, and go on and on and on. \
Just a basic textbox module really.;0,0,150,2;This is another textbox.;"))
man = char("army",[100,100])
scene.children.append(man)
        
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
    keys = pygame.key.get_pressed()
    speed = 40
    if keys[pygame.K_DOWN]:
        man.set_facing("s")
        man.pos[1]+=speed*dt
    if keys[pygame.K_RIGHT]:
        man.set_facing("e")
        man.pos[0]+=speed*dt
    if keys[pygame.K_LEFT]:
        man.set_facing("w")
        man.pos[0]-=speed*dt
    if keys[pygame.K_UP]:
        man.set_facing("n")
        man.pos[1]-=speed*dt