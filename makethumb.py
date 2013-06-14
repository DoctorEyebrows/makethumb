#!/usr/bin/python

import pygame, PIL.Image, sys, os
from math import atan2, degrees
from pygame.locals import *

class _globals():
    pass
    
class Cropbox():
    def __init__(self):
        self.on = False
        size = img.size
        self.pos = pygame.Rect(size[0]/4,size[1]/4,size[0]/2,size[1]/2)
        self.update()
        self.grabbed = [0,0,0,0,0,0,0,0,0]
        self.offset = []
        
    def update(self):
        """
        Updates handles
        """
        pos = self.pos
        self.handles = [
                        Rect(pos.left+6,pos.top+6,pos.w-12,pos.h-12), #centre
                        Rect(pos.left-6,pos.top-6,12,12), #top-left
                        Rect(pos.left+6,pos.top-6,pos.w-12,12), #top edge
                        Rect(pos.right-6,pos.top-6,12,12), #top-right
                        Rect(pos.right-6,pos.top+6,12,pos.h-12), #right edge
                        Rect(pos.right-6,pos.bottom-6,12,12), #bottom-right
                        Rect(pos.left+6,pos.bottom-6,pos.w-12,12), #bottom edge
                        Rect(pos.left-6,pos.bottom-6,12,12), #bottom-left
                        Rect(pos.left-6,pos.top+6,12,pos.h-12) #left edge
                        ]
    
    def makesquare(self,move):
        #0--1--2
        #|     |
        #7     3
        #|     |
        #6--5--4
        fix = ((move+3) % 8) + 1
        if fix in (1,3,5,7):
            #user grabbed a corner
            fixpos = self.get_corner(fix)
            movepos = self.get_corner(move)
            angle = degrees(atan2(movepos[1]-fixpos[1],movepos[0]-fixpos[0]))
            if -180 <= angle <= -135 or -45 <= angle <= 0:
                #y=-x
                self.set_corner(move,movepos[0], movepos[1]-abs(self.pos.w)+abs(self.pos.h), True)
            elif -135 <= angle <= -90 or 90 <= angle <= 135:
                #x=-y
                self.set_corner(move, movepos[0]-abs(self.pos.h)+abs(self.pos.w) ,movepos[1], True)
            elif -90 <= angle <= -45 or 45 <= angle <= 90:
                #x=y
                self.set_corner(move, movepos[0]+abs(self.pos.h)-abs(self.pos.w), movepos[1], True)
            elif 0 <= angle <= 45 or 135 <= angle <= 180:
                #y=-x
                self.set_corner(move,movepos[0], movepos[1]+abs(self.pos.w)-abs(self.pos.h), True)
                
        elif fix in (2,6):
            #user grabbed top or bottom edge
            c = self.pos.centerx
            self.pos.w = self.pos.h
            self.pos.centerx = c
        elif fix in (4,8):
            #user grabbed left or right edge
            c = self.pos.centery
            self.pos.h = self.pos.w
            self.pos.centery = c
            
         
    def get_corner(self,corner):
        pos = self.pos
        return [pos.center,pos.topleft,pos.midtop,pos.topright,pos.midright,
                pos.bottomright,pos.midbottom,pos.bottomleft,pos.midleft][corner]
                
#   def unnormalize(self,axis):
#       if axis == 0:
#           #flip horizontally
            
        
    def set_corner(self,corner,x,y,ignoreshift=False):
        """
        Corners labeled 0,1,2,3 from top-left, clockwise
        """
        rel = (x-self.handles[corner].centerx , y-self.handles[corner].centery)
        if corner == 0:
            self.pos.center = (x,y)
            self.pos.clamp_ip(blitbox)
        if corner == 1:
            self.pos.w -= rel[0]
            self.pos.h -= rel[1]
            self.pos.topleft = (x,y)
        elif corner == 2:
            self.pos.h -= rel[1]
            self.pos.top = y
        elif corner == 3:
            self.pos.w += rel[0]
            self.pos.h -= rel[1]
            self.pos.topright = (x,y)
        elif corner == 4:
            self.pos.w += rel[0]
            self.pos.right = x
        elif corner == 5:
            self.pos.w += rel[0]
            self.pos.h += rel[1]
            self.pos.bottomright = (x,y)
        elif corner == 6:
            self.pos.h += rel[1]
            self.pos.bottom = y
        elif corner == 7:
            self.pos.w -= rel[0]
            self.pos.h += rel[1]
            self.pos.bottomleft = (x,y)
        elif corner == 8:
            self.pos.w -= rel[0]
            self.pos.left = x
        
        #clip doesn't work with invalid rectangles
        if self.pos.w < 0:
            self.pos.normalize()
            self.swap_corners()
            
        self.pos = self.pos.clip(blitbox)
        self.update()
        if pygame.key.get_pressed()[K_RSHIFT] and not ignoreshift:
            #make the box square
            self.makesquare(corner) #passing move
            self.update()
                
    def draw(self):
        pygame.draw.rect(screen,(0,0,0),self.pos,2)
        for i in range(1,9):
            visible = self.handles[i].clip(blitbox)
            visible.normalize()
            temp = pygame.Surface( (visible.width, visible.height),  SRCALPHA)
            colour = pygame.Color(("red","blue","green","cyan","pink","purple","black","orange","yellow")[i])
            colour.a = 100
            temp.fill(colour)
            r = self.handles[i]; r.normalize()
            screen.blit(temp,  visible)




#GLOBALS
clock = pygame.time.Clock()
g = _globals()
g.doblit = True

if len(sys.argv) == 2:
    img = PIL.Image.open(sys.argv[1])
    imgG = pygame.image.load(sys.argv[1])
else:
    img = PIL.Image.open(r"/home/philip/prog/python/cat-carrier.jpg")
    imgG = pygame.image.load(r"/home/philip/prog/python/cat-carrier.jpg")
imgG.set_colorkey(None)
blitbox = pygame.Rect(0,0,img.size[0],img.size[1])

#PYGAME SETUP----------------------------------
pygame.init()
screen = pygame.display.set_mode(img.size)
pygame.display.set_caption("MakeThumb")
#----------------------------------------------
cropbox = Cropbox()



############################## - MAINLOOP - ##############################

_END = False
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            _END = True
            break
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            #PRESS
            cropbox.on = True
            for i in range(9):
                if cropbox.handles[i].collidepoint(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
                    cropbox.grabbed[i] = 1
                    cropbox.offset = [cropbox.handles[i].center[j] - pygame.mouse.get_pos()[j] for j in (0,1)]
            g.doblit = True
        elif event.type == MOUSEMOTION and cropbox.grabbed != [0,0,0,0,0,0,0,0,0]:
            #MOVE
            for i in range(9):
                if cropbox.grabbed[i]:
                    cropbox.set_corner(i,event.pos[0]+cropbox.offset[0],
                                        event.pos[1]+cropbox.offset[1])
                    break
            g.doblit = True
        elif event.type == MOUSEBUTTONUP:
            #RELEASE
            cropbox.grabbed = [0,0,0,0,0,0,0,0,0]
            cropbox.pos.normalize()
            cropbox.update()
            g.doblit = True
        elif event.type == KEYDOWN:
            if event.key == K_c:
                cropbox.pos.move_ip(-blitbox.left,-blitbox.top)
                img = img.crop(cropbox.pos.topleft+cropbox.pos.bottomright)
                print cropbox.pos.w, cropbox.pos.h
                temp = pygame.Surface((cropbox.pos.w,cropbox.pos.h))
                temp.blit(imgG,(0,0),cropbox.pos)
                imgG = temp
                blitbox = pygame.Rect( (screen.get_width()-cropbox.pos.w)/2, (screen.get_height()-cropbox.pos.h)/2, img.size[0], img.size[1])
                
                screen.fill((0,0,0))
                cropbox.pos = blitbox
                cropbox.update()
                g.doblit = True
            elif event.key == K_s:
                #img.save("cropped.jpg")
                extention = sys.argv[1][sys.argv[1].rfind("."):]
                print extention
                i = 0
                folder = os.path.split(sys.argv[1])[0]
                while "cropped"+str(i)+extention in os.listdir(folder):
                    i += 1
                img.save(os.path.join(folder,"cropped"+str(i)+extention))
    if _END:
        break

    if g.doblit:
        #draw image
        screen.blit(imgG, blitbox)
        if cropbox.on:
            cropbox.draw()
        pygame.display.flip()
        g.doblit = False
    clock.tick(40)

pygame.quit()
