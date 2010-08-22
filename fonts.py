import pygame
pygame.init()

res = [1024,768]
screen = pygame.display.set_mode(res)

surf = pygame.Surface([320,200])


import os
fonts = os.listdir("fonts")
print fonts[0],8
fontsize = 8
fontanti = 1



running = 1
while running:
    
    surf.fill([0,0,0])
    fontname = fonts[0]
    font = pygame.font.Font("fonts/"+fontname,fontsize)
    surf.blit(font.render("This is a test of %s %s %s"%(fontname,fontsize,fontanti),fontanti,[255,255,255]),[50,50])
    
    screen.blit(pygame.transform.scale(surf,res),[0,0])
    pygame.display.flip()
    
    
    for e in pygame.event.get():
        if e.type==pygame.KEYDOWN and e.key==pygame.K_RIGHT:
            a = fonts.pop(0)
            fonts.append(a)
            print fonts[0],fontsize
        if e.type==pygame.KEYDOWN and e.key==pygame.K_LEFT:
            a = fonts.pop(-1)
            fonts.insert(0,a)
            print fonts[0],fontsize
        if e.type==pygame.KEYDOWN and e.key==pygame.K_UP:
            fontsize += 1
            print fonts[0],fontsize
        if e.type==pygame.KEYDOWN and e.key==pygame.K_DOWN:
            fontsize -= 1
            print fonts[0],fontsize
        if e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE:
            fontanti = 1-fontanti
        if e.type==pygame.QUIT:
            running = 0
        