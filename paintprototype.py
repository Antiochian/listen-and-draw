# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 00:41:22 2019
MSPaint clone
@author: user
"""

import pygame
import sys

TOTALTIME = 10 #(in seconds)
(Nx,Ny) = (600,400)
scrollheight = 700
FPS = 60
black = (0,0,0)
transparent = (0,0,0,0)
white = (255,255,255)
grey = (196, 196, 196)
debugcol = (255, 107, 223)
thickness = 2

speed = 0.2
(canvasx, canvasy) = (int(Nx*0.6),scrollheight)
(offsetx, offsety) = (int(Nx*0.2),int(Ny*0.1))
initialoffsety = offsety
ActiveRect = pygame.Rect(offsetx, offsety, Nx - 2*offsetx, Ny - 2*offsety)

def scrollcanvas(speed,offsety):
    if speed == 0:
        return offsety
    elif pygame.time.get_ticks() % (1/speed) == 0:
        offsety -= 1
    return offsety

def changeline(speed,linecolor,thickness):
    if speed == 0:
        return offsety
    elif pygame.time.get_ticks() % (1/speed) == 0:
        linecolor = (linecolor[0]+1,linecolor[1],linecolor[2])
        #thickness += 0.08
    if linecolor[0] > 255:
        linecolor = (255,0,0)
    return linecolor,thickness
def reveal(alternator):
    pass
    """
    This function first needs to act a canvas reveal, resizing the main window
    and uncovering all of the so-far hidden canvas layers
    """
    return

def drawsmoothline(mousex,mousey,prevmousex,prevmousey,color,thickness): 
    if prevmousex == None or prevmousey == None: #if its the first frame of a linedraw
        (prevmousex,prevmousey) = (mousex,mousey)
        pygame.draw.circle(canvas, color, (mousex,mousey), int(thickness))
    #idea: draw multiple smooth lines to simulate thickness
    for offset in range(1,int(thickness)):
        #centerline
        pygame.draw.line(canvas, color, (prevmousex,prevmousey), (mousex,mousey),thickness)
        #four cardinal points
        pygame.draw.aaline(canvas, color, (prevmousex+offset,prevmousey), (mousex+offset,mousey))  
        pygame.draw.aaline(canvas, color, (prevmousex-offset,prevmousey), (mousex-offset,mousey))  
        pygame.draw.aaline(canvas, color, (prevmousex,prevmousey+offset), (mousex,mousey+offset))  
        pygame.draw.aaline(canvas, color, (prevmousex,prevmousey-offset), (mousex,mousey-offset))    
    return
    
def drawline(mousex,mousey,prevmousex,prevmousey,color,thickness):
    if prevmousex == None or prevmousey == None: #if its the first frame of a linedraw
        (prevmousex,prevmousey) = (mousex,mousey)
        pygame.draw.circle(canvas, color, (mousex,mousey), int(thickness))
    #draw line connecting two points, then 2 circles at each end
    else:
        pygame.draw.line(canvas, color, (prevmousex,prevmousey), (mousex,mousey), int(thickness)*3)
        pygame.draw.circle(canvas, color, (mousex,mousey), int(thickness))
        pygame.draw.circle(canvas, color, (prevmousex,prevmousey), int(thickness))
    return

def drawlinesimple(mousex,mousey,prevmousex,prevmousey,color,thickness):
    pygame.draw.circle(canvas, color, (mousex,mousey), thickness)
    return

pygame.init()

window = pygame.display.set_mode( (Nx,Ny), pygame.RESIZABLE )
pygame.display.set_caption("Paint prototype")

canvas = pygame.Surface( (canvasx, canvasy) )
mask = pygame.Surface( (Nx,Ny), pygame.SRCALPHA ) #this is the mask/musicplayer surface


clock = pygame.time.Clock()

window.fill(debugcol)
canvas.fill(white)

mask.fill(grey)
pygame.draw.rect(mask, transparent,ActiveRect)

#initial blitting
window.blit(canvas, (offsetx, offsety))
window.blit(mask, (0,0))
pygame.display.update() #update whole window

(prevmousex,prevmousey) = (None, None) #default "prev" value
revealmode = False
linecolor = black
while True:
    clock.tick(FPS)

    for event in pygame.event.get(): #detect events
        if event.type == pygame.QUIT: #detect attempted exit
            pygame.quit()
            sys.exit()
        if pygame.mouse.get_pressed()[0]:
            mousex = int(pygame.mouse.get_pos()[0]) - offsetx
            mousey = int(pygame.mouse.get_pos()[1]) - offsety
            drawsmoothline(mousex,mousey, prevmousex,prevmousey,linecolor,thickness)
            #drawline(mousex,mousey, prevmousex,prevmousey,linecolor,thickness)
            (prevmousex,prevmousey) = (mousex,mousey) #update prev values               
        if not pygame.mouse.get_pressed()[0]:
            (prevmousex,prevmousey) = (None,None)
        if pygame.mouse.get_pressed()[2]: #DEBUG REVEAL FUNCTIONALITY
            revealmode = True
            
    if revealmode:
        offsety = 0
        Nx,Ny = Nx,scrollheight
        window = pygame.display.set_mode((Nx, scrollheight), pygame.RESIZABLE)
        mask.fill(transparent)
        window.fill(grey)
        window.blit(canvas,(offsetx,0)) #NB offsety is now 0
        pygame.display.update()
        pygame.image.save(canvas,"video/testcanvas2.png")
    elif not revealmode and offsety < -340:
        revealmode = True
    else:
        offsety = scrollcanvas(speed,offsety)
        linecolor,thickness = changeline(speed,linecolor,thickness)
        window.blit(canvas, (offsetx, offsety) )
        window.blit(mask, (0,0) )
        pygame.display.update(ActiveRect)
    
    #add an if-statement to shunt program into revealmode when ticker reaches bottom
    
    
    