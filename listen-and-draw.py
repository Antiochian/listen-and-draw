# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 22:57:00 2019

@author: user
"""

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
import random

# CONFIGUREABLE PARAMETERS #
filename = "audio/arttest.mp3"
#filename = "audio/bloodhail.mp3"
loopnumber = 1
(Nx,Ny) = (700,400) #windowsize
scrollwidth = 1366 #total height of canvas
FPS = 60
thickness = 3 #starting thickness
trackbarposition = "under"
trackbarposition = "above"
# COLOURS #
#colors
transparent = (0,0,0,0)
white = (255,255,255)
grey = (196, 196, 196)
debugcol = (255, 107, 223)
#themed colors
lightgreen = (137,191,113)
mediumgreen = (49,96,76)
darkgreen = (44,88,89)
black = (8,17,23)
brown = (83,106,74)

#set up theme
trackbaroutlinecolor = black
trackbaremptycolor = white
trackbarfullcolor = black
canvascolor = lightgreen
maskcolor = darkgreen
linecolor = mediumgreen #initial line color
endcolor = black #maximum possible line color


# FUNCTIONS #
def borderdraw(pixelsize=5):
    #generates a random pixellated "bevel" pattern for decorative purposes
    if canvaswidth % pixelsize == 0 and canvasheight % pixelsize == 0:
        #only draw pixel bevel if height is multiple of pixelsize to avoid misalignment
        #DRAW VERTICAL BEVELS
        for y in range(offsety,offsety+canvasheight,pixelsize):
            x = offsetx - 2
            for depth in range(1,6):
                darkchance = -0.2*depth + 0.084*math.sin(2.6*depth) + 1.05 #equation to generate pixel probabilities
                if random.random() < darkchance:
                    mask.fill(black, pygame.Rect(x - depth*pixelsize, y, pixelsize, pixelsize))
                if random.random() < darkchance:
                    mask.fill(black, pygame.Rect(x-2 + canvaswidth + depth*pixelsize, y, pixelsize, pixelsize))
        #DRAW HORIZONTAL BEVELS
        for x in range(offsetx,offsetx+canvaswidth,pixelsize):
            y = offsety - 2
            for depth in range(1,6):
                darkchance = -0.2*depth + 0.084*math.sin(2.6*depth) + 1.05 #equation to generate pixel probabilities
                if random.random() < darkchance:
                    mask.fill(black, pygame.Rect(x, y - depth*pixelsize, pixelsize, pixelsize))
                if random.random() < darkchance:
                    mask.fill(black, pygame.Rect(x, y-2 + canvasheight + depth*pixelsize, pixelsize, pixelsize))    #draw trackbar
    return
                    
def initialdraw():
    pixelsize=5
    #color in layers
    window.fill(debugcol)   #fill window with bright pink debug color (should never be visible)
    canvas.fill(canvascolor)      #blank canvas
    mask.fill(maskcolor)         #fill mask
    pygame.draw.rect(mask, transparent,ActiveRect) #cut out hole in mask
    pygame.draw.rect(mask, black,ActiveRect,pixelsize) #outline mask in dark color
    #FANCY SCRIPT TO DRAW RANDOM PIXEL BEVELS GOES HERE
    borderdraw(pixelsize)
    pygame.draw.rect(mask, trackbaremptycolor, trackbar) #draw trackbar
    pygame.draw.rect(mask, trackbaroutlinecolor,trackbar,5) #draw trackbar outline
    #final touches
    pygame.display.set_caption("Listen And Draw - Now Playing: ",filename)
    window.blit(canvas, (offsetx, offsety))
    window.blit(mask, (0,0))
    pygame.display.update() #update whole window
    return

def windowmeasurements(Nx,Ny):
    """
    This script takes in the window size and centers/arrange the canvas, Rect 
    objects and trackbar, spitting out a whole slew of constants
    """
    (canvasx, canvasy) = (scrollwidth, int(Nx*0.8))
    (canvaswidth, canvasheight) = (int(0.8*Nx),int(0.6*Ny))        
    (offsetx, offsety) = ( int( (Nx-canvaswidth) /2 ), int( (Ny-canvasheight)/2 )) #define borders (derived from canvas size)
    (trackbarwidth,trackbarheight) = (0.5*Nx, 0.04*Ny)
    #define the two updatable areas of the screen - drawscreen and trackbar
    ActiveRect = pygame.Rect(offsetx, offsety,canvaswidth, canvasheight)
    if trackbarposition == "under":
        trackbar = pygame.Rect(int((Nx-trackbarwidth)/2), Ny - trackbarheight - int((offsety-trackbarheight)/2),trackbarwidth,trackbarheight)
    else:
        trackbar = pygame.Rect(int((Nx-trackbarwidth)/2), int((offsety-trackbarheight)/2),trackbarwidth,trackbarheight)
    return(canvasx,canvasy,canvaswidth, canvasheight, offsetx, offsety,trackbarwidth,trackbarheight,ActiveRect,trackbar)

def scrollcanvas(scrollspeed, decimaloffsetx,offsetx):
    """
    This function scrolls the canvas. Its designed to reach the bottom just as
    the song ends, plus or minus a frame.
    """
    decimaloffsetx -= scrollspeed
    offsetx = round(decimaloffsetx) #offset is in pixels, so has to be an integer
    return decimaloffsetx,offsetx

def changeline(timepercent,linecolor,thickness):
    """
    This function may be changed depending on artistic effect desired.
    Currently it does nothing.
    """
    #thickness = round(3 + math.sin(timepercent*4*math.pi))
    #linecolor = (int(timepercent*255),linecolor[1],linecolor[2])
    return linecolor,thickness

def drawsmoothline(mousex,mousey,prevmousex,prevmousey,color,endcolor,thickness):
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
    
    #CHANGE COLOUR BASED ON SPEED
    startcolor = color
    endcolor = endcolor
    Rcolorchange = -startcolor[0] + endcolor[0]
    Gcolorchange = -startcolor[1] + endcolor[1]
    Bcolorchange = -startcolor[2] + endcolor[2]
    
    distance = math.sqrt( (mousex-prevmousex)**2 + (mousey-prevmousey)**2   )
    colorpercent = min(1,distance/60)
    RED = startcolor[0] + Rcolorchange*colorpercent
    GREEN = startcolor[1] + Gcolorchange*colorpercent
    BLUE = startcolor[2] + Bcolorchange*colorpercent 
   
    color = (int(RED),int(GREEN),int(BLUE))
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

def updatetrackbar(timepercent):
    if trackbarposition == "under":
       pygame.draw.rect(mask, black,pygame.Rect(int((Nx-trackbarwidth)/2),int(Ny - trackbarheight-(offsety-trackbarheight)/2),timepercent*trackbarwidth,trackbarheight) ) 
    else: #otherwise display on top
        pygame.draw.rect(mask, black,pygame.Rect(int((Nx-trackbarwidth)/2),int((offsety-trackbarheight)/2),timepercent*trackbarwidth,trackbarheight) )

"""
##################################################################################################
    MAIN PROGRAM START
################################################################################################## 
"""
# SET UP WINDOW USING windowmeasurements FUNCTION#
(canvasx,canvasy,canvaswidth, canvasheight, offsetx, offsety,trackbarwidth,trackbarheight,ActiveRect,trackbar)\
= windowmeasurements(Nx,Ny)

# INITIALISE PYGAME #
pygame.init()

# DRAW UI #
#make 3 layers
window = pygame.display.set_mode( (Nx,Ny), pygame.RESIZABLE )
canvas = pygame.Surface( (canvasx, canvasy) )
mask = pygame.Surface( (Nx,Ny), pygame.SRCALPHA ) #this is the mask/musicplayer surface
#INITIALDRAW FUNCTION
initialdraw()
clock = pygame.time.Clock() #set up clock object for FPS limiting

# SET UP AUDIO PLAYBACK #
AUDIO = MP3(filename)
pygame.mixer.music.load(filename) #get ready to stream audio track
TOTALTIME = math.ceil(AUDIO.info.length)*loopnumber #gets length of track in seconds
totalframes = TOTALTIME*FPS
timestep = 1/totalframes #calculate percentage increase per frame (percent goes from 0-1)

# INITIALISE CONSTANTS #
(prevmousex,prevmousey) = (None, None) #default "previousmouse" location
revealmode = False
decimaloffsetx = offsetx
timepercent = 0 #number from 0 to 1
initialoffsetx = offsetx
#calculate scrollspeed required
scrollspeed = ( scrollwidth - (Nx - 2*offsetx) )/(TOTALTIME*FPS) #in pixels/frame

pygame.mixer.music.play(loopnumber)
while True:
    clock.tick(FPS)
    #print(int(clock.get_fps()))
    timepercent += timestep
    for event in pygame.event.get(): #detect events
        if event.type == pygame.QUIT: #detect attempted exit
            pygame.quit()
            sys.exit()
        if pygame.mouse.get_pressed()[0]:
            mousex = int(pygame.mouse.get_pos()[0]) - offsetx
            mousey = int(pygame.mouse.get_pos()[1]) - offsety
            drawsmoothline(mousex,mousey, prevmousex,prevmousey,linecolor,endcolor,thickness)
            #drawline(mousex,mousey, prevmousex,prevmousey,linecolor,thickness)
            (prevmousex,prevmousey) = (mousex,mousey) #update prev values               
        if not pygame.mouse.get_pressed()[0]:
            (prevmousex,prevmousey) = (None,None)
        if (pygame.mouse.get_pressed()[0] and revealmode == True) or pygame.mouse.get_pressed()[2]: #DEBUG RESTART FUNCTIONALITY
            (canvasx,canvasy,canvaswidth, canvasheight, offsetx, offsety,trackbarwidth,trackbarheight,ActiveRect,trackbar)\
= windowmeasurements(Nx,Ny)
            initialdraw()
            (prevmousex,prevmousey) = (None, None) #default "previousmouse" location
            revealmode = False
            decimaloffsetx = offsetx
            timepercent = 0 #number from 0 to 1
            initialoffsetx = offsetx
            #calculate scrollspeed required
            scrollspeed = ( scrollwidth - (Nx - 2*offsetx) )/(TOTALTIME*FPS) #in pixels/frame
            
            pygame.mixer.music.play(loopnumber)
            
    if revealmode:
        pygame.mixer.music.stop()
        offsety = 0
        Nx,Ny = scrollwidth,Ny
        window = pygame.display.set_mode((Nx, Ny), pygame.RESIZABLE)
        mask.fill(transparent)
        window.fill(grey)
        window.blit(canvas,(0,offsety)) #NB offsety is now 0
        window.blit(mask,(0,offsety))
        pygame.display.update()
        pygame.image.save(canvas,"video/testcanvas.png")
    elif not revealmode and timepercent >= 1:
        revealmode = True
    else:
        updatetrackbar(timepercent)
        decimaloffsetx, offsetx = scrollcanvas(scrollspeed,decimaloffsetx,offsetx)
        linecolor,thickness = changeline(timepercent,linecolor,thickness)
        window.blit(canvas, (offsetx, offsety) )
        window.blit(mask, (0,0) )
        pygame.display.update(ActiveRect)
        pygame.display.update(trackbar)
    
    #add an if-statement to shunt program into revealmode when ticker reaches bottom
    
    
    