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
from mutagen.mp3 import MP3
import random
import time
import os
import sys
import math
# INITIALISE PYGAME #
pygame.init()

"""
# CONFIGUREABLE PARAMETERS #
Displayed in rough order of how often you'll want to change them
"""
filename = "audio/test.mp3"
loopnumber = 1 #times audio repeats before program finishes
scrollwidth = 3000 #total width of final canvas (in pixels)
FPS = 60 #frames per second (can affect drawing smoothness)
renderspeed = 2 #renderspeed (2 -> 2x as fast) - WORKS BEST WITH INTEGERS
trackbarposition = "above" #accepts "under" or "above"
thickness = 3 #starting thickness of line
pixelsize = 5
fadelength = 250 #in milliseconds
maxshuffletime = 250 #in milliseconds
title = "Listen-And-Draw"
subtitle = 'Click to start // "Esc" to quit'
screeninfo = pygame.display.Info() #get monitor info
(Nx, Ny) = (screeninfo.current_w, screeninfo.current_h) #detected screensize

# COLOURS #
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
transparentgrey = (8,17,23,10)

#set up theme
textcolor = white
pausecolor = transparentgrey
trackbaroutlinecolor = black
trackbaremptycolor = white
trackbarfullcolor = black
canvascolor = lightgreen
maskcolor = darkgreen
linecolor = mediumgreen #initial line color
endcolor = black #maximum possible line color


"""
# FUNCTIONS #
-------------------
Table of Contents:
-------------------
###### DYNAMICS ######|#########################################################
scrollspeedchange     |   Changes the scrolling speed of the canvas (highly configurable)
thicknesschange       |   Changes the thickess of the line (highly configurable)
colorchange           |   Changes the color of the line (highly configurable)
####### SETUP ########|#########################################################                    
windowmeasurements    |   Spits out a whole slew of constants calculated from windowsize
initialdraw           |   Draws the basic shape of the program (canvas, mask, trackbar)
borderdraw            |   Draws the border outlining the canvas
bordershuffle         |   Plays short animation and creates pixellated bevel pattern around border
fadein                |   Fades screen to "pausecolor" over the course of "fadelength" milliseconds
####### RENDER #######|#########################################################
drawsmoothline        |   Draws a line to the canvas
rendertitle           |   Writes title and subtitle over screen
scrollcanvas          |   Advances the canvas depending on the time
updatetrackbar        |   Advances the trackbar's progress
######## MAIN ########|#########################################################
renderplayback        |   Switches to "playback" mode
main                  |   Main program loop
######################|#########################################################
"""
##############################################################################

def scrollspeedchange(TOTALTIME,timepercent):
    """
    This function may be changed depending on artistic effect desired.
    Currently it is set to be a constant such that the canvas finishes scrolling
    just as the audio track finishes.
    """
    scrollspeed = ( scrollwidth - (Nx - 2*offsetx) )/(TOTALTIME*FPS)
    return scrollspeed

def thicknesschange(thickness,timepercent):
    """
    This function may be changed depending on artistic effect desired.
    Currently it does nothing, and the thickness is constant.
    """
    pass
    return thickness

def colorchange(startcolor,endcolor, mousex,mousey,prevmousex,prevmousey,timepercent):
    """
    This function alters the linecolor. It can be changed, but currently operates
    based on mousespeed.
    """
    sensitivity = 2000
    #Find color changes for each RGB value
    Rcolorchange = -startcolor[0] + endcolor[0]
    Gcolorchange = -startcolor[1] + endcolor[1]
    Bcolorchange = -startcolor[2] + endcolor[2]
    distance = math.sqrt( (mousex-prevmousex)**2 + (mousey-prevmousey)**2 )
    colorpercent = min(1,distance*FPS/sensitivity)
    RED = startcolor[0] + Rcolorchange*colorpercent
    GREEN = startcolor[1] + Gcolorchange*colorpercent
    BLUE = startcolor[2] + Bcolorchange*colorpercent 
    #Apply to find current color
    color = (int(RED),int(GREEN),int(BLUE))
    return color

##############################################################################

def windowmeasurements(Nx,Ny):
    """
    This script takes in the window size and centers/arrange the canvas, Rect 
    objects and trackbar, spitting out a whole slew of constants
    """
    (canvaswidth, canvasheight) = (int(0.5*Nx),int(0.6*Ny)) #visible canvas size
    (canvasx, canvasy) = (scrollwidth, canvasheight) #slightly confusing, but this is the REAL canvassize
    #this line rounds the canvas sizes to nearest multiple of 5:
    (canvaswidth, canvasheight) = (5*(canvaswidth//5), 5*(canvasheight//5))       
    (offsetx, offsety) = ( int( (Nx-canvaswidth) /2 ), int( (Ny-canvasheight)/2 )) #define borders (derived from canvas size)
    (trackbarwidth,trackbarheight) = (int(0.8*canvaswidth), int(0.07*canvasheight))
    #define the two updatable areas of the screen - drawscreen and trackbar
    ActiveRect = pygame.Rect(offsetx, offsety,canvaswidth, canvasheight)
    if trackbarposition == "under":
        trackbar = pygame.Rect(int((Nx-trackbarwidth)/2), Ny - trackbarheight - int((offsety-trackbarheight)/2),trackbarwidth,trackbarheight)
    else:
        trackbar = pygame.Rect(int((Nx-trackbarwidth)/2), int((offsety-trackbarheight)/2),trackbarwidth,trackbarheight)
    return(canvasx,canvasy,canvaswidth, canvasheight, offsetx, offsety,trackbarwidth,trackbarheight,ActiveRect,trackbar)

def initialdraw(shuffle_enable=True):
    #color in layers
    window.fill(debugcol)   #fill window with bright pink debug color (should never be visible)
    canvas.fill(canvascolor)      #blank canvas
    #draw corner breaks on canvas    
    corneroffset = 5*pixelsize
    for x in [corneroffset, scrollwidth - 3*pixelsize - corneroffset]:
        for y in [corneroffset, canvasheight - corneroffset - 3*pixelsize]:
                canvas.fill(mediumgreen, pygame.Rect(x, y, 3*pixelsize, 3*pixelsize))
                canvas.fill(canvascolor, pygame.Rect(x+pixelsize, y+pixelsize, pixelsize, pixelsize))
    bordershuffle(maxshuffletime,shuffle_enable)
    return

def borderdraw():
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

def bordershuffle(maxshuffletime,enabled=True):
    if enabled:
        starttime = pygame.time.get_ticks()
        shuffletime = 0
        while shuffletime < maxshuffletime: #keep shuffling border for 250 milliseconds
            mask.fill(maskcolor)         #fill mask
            pygame.draw.rect(mask, transparent,ActiveRect) #cut out hole in mask
            pygame.draw.rect(mask, black,ActiveRect,pixelsize) #outline mask in dark color
            ### BEVEL SCRIPT ###
            borderdraw()
            ####################
            pygame.draw.rect(mask, trackbaremptycolor, trackbar) #draw trackbar
            pygame.draw.rect(mask, trackbaroutlinecolor,trackbar,5) #draw trackbar outline
            #final touches
            pygame.display.set_caption("Listen And Draw - Now Playing: ",filename)
            window.blit(canvas, (offsetx, offsety))
            window.blit(mask, (0,0))
            pygame.display.update() #update whole window
            time.sleep(maxshuffletime/5000)
            shuffletime = pygame.time.get_ticks() - starttime
    else:
        mask.fill(maskcolor)         #fill mask
        pygame.draw.rect(mask, transparent,ActiveRect) #cut out hole in mask
        pygame.draw.rect(mask, black,ActiveRect,pixelsize) #outline mask in dark color
        ### BEVEL SCRIPT ###
        borderdraw()
        ####################
        pygame.draw.rect(mask, trackbaremptycolor, trackbar) #draw trackbar
        pygame.draw.rect(mask, trackbaroutlinecolor,trackbar,5) #draw trackbar outline
        #final touches
        pygame.display.set_caption("Listen And Draw - Now Playing: ",filename)
        window.blit(canvas, (offsetx, offsety))
        window.blit(mask, (0,0))
        pygame.display.update() #update whole window
    return

def fadein(finalcolor,fadelength,startcolor = (0,0,0,0)): #fadelength is in milliseconds
    frames = int(fadelength*FPS/1000)
    #frametime = 1/FPS defunct variable for time.sleep(frametime) functionality
    #this is in case one wants to decouple the animation rate from the frame rate
    for framenumber in range(frames+1):
        colorfraction = framenumber/10
        Rcolorchange = -startcolor[0] + finalcolor[0]
        Gcolorchange = -startcolor[1] + finalcolor[1]
        Bcolorchange = -startcolor[2] + finalcolor[2]
        Acolorchange = -startcolor[3] + finalcolor[3]

        RED = max(int(startcolor[0] + colorfraction*Rcolorchange),0)
        GREEN = max(int(startcolor[1] + colorfraction*Gcolorchange),0)
        BLUE = max(int(startcolor[2] + colorfraction*Bcolorchange),0)
        ALPHA = max(int(startcolor[3] + colorfraction*Acolorchange),0)
        color = (RED,GREEN,BLUE,ALPHA)
        pausescreen.fill(color)
        window.blit(pausescreen, (0,0) )
        pygame.display.update()
    return                  

#############################################################################

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
    color = colorchange(startcolor,endcolor, mousex,mousey,prevmousex,prevmousey,timepercent)
    thickness = thicknesschange(thickness,timepercent)
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

def rendertitle(topstring,topsize,bottomstring,bottomsize,spacer=40,myfont='dfkaisb',verticaloffset=0):
        #(spacer is the spacing between the title and subtitle)
        titlefont = pygame.font.SysFont(myfont,topsize) #"True" makes this title bold
        pausefont = pygame.font.SysFont(myfont, bottomsize)
        titletextsurf = titlefont.render(topstring,True,textcolor)
        (titletextwidth, titletextheight) = (max(titletextsurf.get_width(),1),max(titletextsurf.get_height(),1))
        pausetextsurf = pausefont.render(bottomstring, True, textcolor)
        (pausetextwidth, pausetextheight) = (max(pausetextsurf.get_width(),1),max(pausetextsurf.get_height(),1))
        pausetextposition = int( (Nx-pausetextwidth)/2 ), int( (Ny-pausetextheight)/2 - verticaloffset) #20pix gap between textlines
        titletextposition = int( (Nx-titletextwidth)/2 ), int(pausetextposition[1] - 0.5*(spacer+pausetextheight+titletextheight))
        # BLIT TEXT AND UPDATE SCREEN #
        window.blit(pausetextsurf, pausetextposition)
        window.blit(titletextsurf, titletextposition)
        pygame.display.update()
        return
    
def scrollcanvas(scrollspeed, decimaloffsetx,offsetx):
    """
    This function scrolls the canvas. Its designed to reach the bottom just as
    the song ends, plus or minus a frame.
    """
    decimaloffsetx -= scrollspeed
    offsetx = round(decimaloffsetx) #offset is in pixels, so has to be an integer
    return decimaloffsetx,offsetx

def updatetrackbar(timepercent):
    if trackbarposition == "under":
       pygame.draw.rect(mask, black,pygame.Rect(int((Nx-trackbarwidth)/2),int(Ny - trackbarheight-(offsety-trackbarheight)/2),timepercent*trackbarwidth,trackbarheight) ) 
    else: #otherwise display on top
        pygame.draw.rect(mask, black,pygame.Rect(int((Nx-trackbarwidth)/2),int((offsety-trackbarheight)/2),timepercent*trackbarwidth,trackbarheight) )

#############################################################################
        
"""
##################################################################################################
    MAIN PROGRAM START
################################################################################################## 
"""
(canvasx,canvasy,canvaswidth, canvasheight, offsetx, offsety,trackbarwidth,trackbarheight,ActiveRect,trackbar)\
= windowmeasurements(Nx,Ny) #set some global variables
def main():
    # set up variables again inside function #
    (canvasx,canvasy,canvaswidth, canvasheight, offsetx, offsety,trackbarwidth,trackbarheight,ActiveRect,trackbar)\
= windowmeasurements(Nx,Ny)
    global window,canvas,mask,pausescreen #make surfaces global
    # SET UP SURFACES #
    window = pygame.display.set_mode( (Nx,Ny), pygame.FULLSCREEN )
    canvas = pygame.Surface( (canvasx, canvasy) )
    mask = pygame.Surface( (Nx,Ny), pygame.SRCALPHA ) #this is the mask/trackbar surface
    pausescreen = pygame.Surface( (Nx,Ny), pygame.SRCALPHA ) #pause screen
    # SET UP CLOCK #
    clock = pygame.time.Clock() #set up clock object for FPS limiting
    # SET UP AUDIO PLAYBACK #
    AUDIO = MP3(filename)
    TOTALTIME = math.ceil(AUDIO.info.length)*loopnumber #gets length of track in seconds
    totalframes = TOTALTIME*FPS
    timestep = 1/totalframes #calculate percentage increase per frame (percent goes from 0-1)
    pygame.mixer.music.load(filename) #get ready to stream audio track
    # SET UP SCALING CONSTANTS #
    scalefactor = Nx/max(canvasx,canvasy)
    revealoffset = int((Ny-canvasy*scalefactor)/2)
    revealwidth, revealheight = Nx, int(canvasy*scalefactor)
    # MAIN PROGRAM LOOP #
    """
    In this main program loop, the course of the program depends on which "mode" is active.
    ----------
    PAUSEMODE:
    ----------
        - Shows artially-dimmed "pause" screen with program title overtop
        - Waits statically for a buttonpress
        - Used as starting screen
    -----------
    REVEALMODE:
    -----------
        - Shows full, uncropped canvas scaled to monitor side
        - Displays track info
        - Used when music track finishes
    -----------
    RENDERMODE:
    -----------
        - Shows video playback of previous drawing session
        - Accessed optionally via keypress from REVEALMODE
    --------------
    ELSE (normal):
    --------------
        - Default mode
        - Handles mousedrawing, music playing, canvas scrolling
    
    These different program modes are controlled by various boolean "mode flags"
    """
    pausemode = True
    rendermode = False
    revealmode = False
    while True:
        clock.tick(FPS)
        if pausemode: #this happens at start of program
            global timepercent
            # RESET VARIABLES, DRAW BLANK SCREEN #
            revealmode = False
            revealed = False
            (canvasx,canvasy,canvaswidth, canvasheight, offsetx, offsety,trackbarwidth,trackbarheight,ActiveRect,trackbar)\
    = windowmeasurements(Nx,Ny)
            initialdraw(False)
            # FADE INTO PAUSE #
            fadein(pausecolor,fadelength)
            # SET UP INITIAL CONDITIONS #
            (prevmousex,prevmousey) = (None, None) #default "previousmouse" location
            decimaloffsetx = offsetx #float version of offsetx
            recorder = [] #blank recorder list object
            framecount = 0
            timepercent = 0 #number from 0 to 1 that indicates progress through song
            # RENDER FONT #
            rendertitle(title,50,subtitle,20,40)
            # PAUSE SCREEN LOOP #
            while pausemode:
                clock.tick(FPS)
                for event in pygame.event.get(): #detect events
                    if pygame.mouse.get_pressed()[0] or pygame.key.get_pressed()[32]:
                        pausemode = False
                        initialdraw(True) #shuffle borders
                        #play music after brief pause
                        time.sleep(maxshuffletime/1000)
                        playmusic = True
                    # QUIT DETECT #
                    if event.type == pygame.QUIT or pygame.key.get_pressed()[27]:
                        pygame.quit()
                        sys.exit()
        if playmusic == True:
            pygame.mixer.music.play(loopnumber)
            playmusic = False
        for event in pygame.event.get(): #detect events
            #QUIT DETECTION (Esc key or corner button)
            if event.type == pygame.QUIT or pygame.key.get_pressed()[27]:
                pygame.quit()
                sys.exit()
            #MOUSEDRAW DETECTION
            if pygame.mouse.get_pressed()[0] and not revealmode and not rendermode and not pausemode :
                mousex = int(pygame.mouse.get_pos()[0]) - offsetx
                mousey = int(pygame.mouse.get_pos()[1]) - offsety
                drawsmoothline(mousex,mousey, prevmousex,prevmousey,linecolor,endcolor,thickness)
                #drawline(mousex,mousey, prevmousex,prevmousey,linecolor,thickness)
                (prevmousex,prevmousey) = (mousex,mousey) #update prev values               
            if not pygame.mouse.get_pressed()[0]: #detect mouseUP
                (prevmousex,prevmousey) = (None,None)
            #RESTART DETECTION (clicking on frozen endframe or pressing "r")
            if (pygame.mouse.get_pressed()[0] and revealmode == True) or pygame.key.get_pressed()[114]:
                #restart program all over again
                pygame.mixer.music.stop()
                playmusic = False
                pausemode = True               
            if pygame.mouse.get_pressed()[2]: #DEBUG functionality where rightclicking skips to result
                pygame.mixer.music.stop()
                playmusic = False
                fadein(transparentgrey,500)
                revealmode = True
                revealed = False
            # DETECT RENDERMODE #
            if pygame.key.get_pressed()[13] and revealmode == True:
#                fadein(transparentgrey,500)
                framecount = 0
                rendermode = True
                revealmode = False
                revealed = False
                
        # DO ACTIONS DEPENDING ON MODE #        
        if revealmode: #shows final result screen
            if revealed == False: #do only once
                # STOP THE MUSIC #
                pygame.mixer.music.stop()
                playmusic = False
                # WIPE THE MASK #
                mask.fill(transparent)
                # PAINT THE BACKGROUND #
                window.fill(darkgreen)
                pygame.image.save(canvas,"video/testcanvas.png")             
                # CREATE SCALED CANVAS TO FIT MONITOR #
                pygame.draw.rect(window, black, pygame.Rect(0,revealoffset,revealwidth,revealheight),int(15*scalefactor))
                scaledcanvas = pygame.transform.scale(canvas, (revealwidth, revealheight))
                #RENDER TEXT
                rendertitle("Click to restart // Press 'Enter' for replay", 30, "Audio track: "+filename, 20, 40,'dfkaisb',-revealoffset )
                # BLIT AND UPDATE SCREEN #
                window.blit(scaledcanvas,(0,revealoffset))
                window.blit(mask,(0,0))
                revealed = True
            pygame.display.update()   
        #REVEAL CANVAS WHEN MUSIC FINISHES
        elif not revealmode and not rendermode and timepercent >= 1:
            revealmode = True
            revealed = False
            fadein(transparentgrey,500)
        elif rendermode:
            pausescreen.fill(transparent)
            window.blit(pausescreen, (0,0) )
            pygame.display.update()
            # MINI RENDER LOOP #
            for frame in recorder:
                clock.tick(FPS)
                # DETECT QUIT #
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                currentframe = frame
                window.blit(currentframe,(0,revealoffset))
                pygame.display.update(pygame.Rect(0,revealoffset,revealwidth,revealheight)) #only update relevant Rect               
            # SET FLAGS #
            revealmode = True
            rendermode = False
            revealed = False
        #DEFAULT BEHAVIOUR SCROLL CANVAS + UPDATE TRACKBAR
        elif not revealmode and not rendermode and not pausemode:
            #"Framecount" is the number of frames that have passed in the main animation loop
            framecount += 1
            if framecount % renderspeed == 0:            
                recorder.append( pygame.transform.scale(canvas, (revealwidth, revealheight)) )
            timepercent += timestep
            updatetrackbar(timepercent)
            scrollspeed = scrollspeedchange(TOTALTIME,timepercent)
            decimaloffsetx, offsetx = scrollcanvas(scrollspeed,decimaloffsetx,offsetx)
            window.blit(canvas, (offsetx, offsety) )
            window.blit(mask, (0,0) )
            pygame.display.update(ActiveRect)
            pygame.display.update(trackbar)
        else:
            raise Exception("Mode flags broken!")
if __name__ == "__main__":
    main()
    