# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 00:41:22 2019
MSPaint clone
@author: user
"""

import pygame
import sys
import math
from mutagen.mp3 import MP3
# CONFIGUREABLE PARAMETERS #
#filename = "audio/shorttest.mp3"
filename = "audio/longtest.mp3"
(Nx,Ny) = (600,400) #windowsize
scrollheight = 700 #total height of canvas
FPS = 30
thickness = 1 #starting thickness

# COLOURS #
black = (0,0,0)
transparent = (0,0,0,0)
white = (255,255,255)
grey = (196, 196, 196)
debugcol = (255, 107, 223)
linecolor = black #initial line colour

# SET UP WINDOW #
(canvasx, canvasy) = (int(Nx*0.6),scrollheight) #define canvas size
(offsetx, offsety) = (int(Nx*0.2),int(Ny*0.1)) #define borders (derived from canvas size)
#define the two updatable areas of the screen - drawscreen and trackbar
ActiveRect = pygame.Rect(offsetx, offsety, Nx - 2*offsetx, Ny - 2*offsety)
trackerbar = pygame.Rect(0.25*Nx,0.28*offsety,0.5*Nx,0.04*Ny)


# SET UP PYGAME #
pygame.init()
#make 3 layers
window = pygame.display.set_mode( (Nx,Ny), pygame.RESIZABLE )
canvas = pygame.Surface( (canvasx, canvasy) )
mask = pygame.Surface( (Nx,Ny), pygame.SRCALPHA ) #this is the mask/musicplayer surface
#color in layers
window.fill(debugcol)   #decorate window (should never be visible)
canvas.fill(white)      #blank canvas
mask.fill(grey)         #border colors
pygame.draw.rect(mask, transparent,ActiveRect) #cut out hole in mask
pygame.draw.rect(mask, white, trackerbar) #draw trackerbar
pygame.draw.rect(mask, black,trackerbar,5) #draw trackerbar outline
#final touches
pygame.display.set_caption("Listen And Draw - Now Playing: ",filename)
clock = pygame.time.Clock() #set up clock object for FPS limiting
#initial blitting (order is important!)
window.blit(canvas, (offsetx, offsety))
window.blit(mask, (0,0))
pygame.display.update() #update whole window

# SET UP AUDIO PLAYBACK #
AUDIO = MP3(filename)
pygame.mixer.music.load(filename) #get ready to stream audio track
TOTALTIME = math.ceil(AUDIO.info.length) #gets length of track in seconds
totalframes = TOTALTIME*FPS
timestep = 1/totalframes #calculate percentage increase per frame (percent goes from 0-1)

# INITIALISE CONSTANTS #
(prevmousex,prevmousey) = (None, None) #default "previousmouse" location
revealmode = False
decimaloffsety = offsety
timepercent = 0 #number from 0 to 1
initialoffsety = offsety
#calculate scrollspeed required
scrollspeed = ( scrollheight - (Ny - 2*offsety) )/(TOTALTIME*FPS) #in pixels/frame

# FUNCTIONS #
def scrollcanvas(scrollspeed, decimaloffsety,offsety):
    """
    This function scrolls the canvas. Its designed to reach the bottom just as
    the song ends, plus or minus a frame.
    """
    decimaloffsety -= scrollspeed
    offsety = round(decimaloffsety) #offset is in pixels, so has to be an integer
    return decimaloffsety,offsety

def changeline(timepercent,linecolor,thickness):
    """
    This function may be changed depending on artistic effect desired.
    CURRENTLY:
        - Thickness increases linearly from 1 - 5
        - Line color changes linearly from (0,0,0) to (255,0,0)
    """
    thickness = round(1 + 4*timepercent)
    linecolor = (int(timepercent*255),linecolor[1],linecolor[2])
    print(linecolor)
    return linecolor,thickness

def drawsmoothline(mousex,mousey,prevmousex,prevmousey,color,thickness):
    """
    This smoothline is split into 3 drawing methods
    1. For thickness from 0 - 1.99, it draws a single aliased pixel line
    2. For thickness from 2 - 3.99 it draws a single line surrounded by 4 aliased lines and ended with a circle
    3. For thickness from 4 + it draws a fat single line bookended by circles at both ends
    """
    if prevmousex == None or prevmousey == None: #if its the first frame of a linedraw
        (prevmousex,prevmousey) = (mousex,mousey)
        if int(thickness) > 1:
            pygame.draw.circle(canvas, color, (mousex,mousey), int(thickness))
    #idea: draw multiple smooth lines to simulate thickness
    if int(thickness) == 1:
        pygame.draw.aaline(canvas, color, (prevmousex,prevmousey), (mousex,mousey))
    elif thickness < 4:    
        for offset in range(1,int(thickness)):
            #centerline
            pygame.draw.line(canvas, color, (prevmousex,prevmousey), (mousex,mousey),int(thickness))
            #four cardinal points
            pygame.draw.aaline(canvas, color, (prevmousex+offset,prevmousey), (mousex+offset,mousey))  
            pygame.draw.aaline(canvas, color, (prevmousex-offset,prevmousey), (mousex-offset,mousey))  
            pygame.draw.aaline(canvas, color, (prevmousex,prevmousey+offset), (mousex,mousey+offset))  
            pygame.draw.aaline(canvas, color, (prevmousex,prevmousey-offset), (mousex,mousey-offset)) 
    else:
        pygame.draw.line(canvas, color, (prevmousex,prevmousey), (mousex,mousey), int(thickness)*2)
        pygame.draw.circle(canvas, color, (mousex,mousey), int(thickness)-1)
        pygame.draw.circle(canvas, color, (prevmousex,prevmousey), int(thickness)-1)
    return

def drawtrackbar(timepercent):
    pygame.draw.rect(mask, black,pygame.Rect(0.25*Nx,0.28*offsety,timepercent*0.5*Nx,0.04*Ny) )

pygame.mixer.music.play()
while True:
    clock.tick(FPS)
    timepercent += timestep
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
        pygame.mixer.music.stop()
        offsety = 0
        Nx,Ny = Nx,scrollheight
        window = pygame.display.set_mode((Nx, scrollheight), pygame.RESIZABLE)
        mask.fill(transparent)
        window.fill(grey)
        window.blit(canvas,(offsetx,0)) #NB offsety is now 0
        window.blit(mask,(offsetx,0))
        pygame.display.update()
        pygame.image.save(canvas,"video/testcanvas.png")
    elif not revealmode and offsety < -340:
        revealmode = True
    else:
        decimaloffsety, offsety = scrollcanvas(scrollspeed,decimaloffsety,offsety)
        linecolor,thickness = changeline(timepercent,linecolor,thickness)
        window.blit(canvas, (offsetx, offsety) )
        window.blit(mask, (0,0) )
        pygame.display.update(ActiveRect)
        pygame.display.update(trackerbar)
    
    #add an if-statement to shunt program into revealmode when ticker reaches bottom
    
    
    