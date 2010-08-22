import pygame
pygame.init()

from lib.things import *

res = [800,600]
fs = 0
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
scene.children.append(sprite("art/army_s_idle.png",[100,100]))
        
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