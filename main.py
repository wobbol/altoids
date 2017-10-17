import pygame, sys
import struct, random, wave 
from pygame.locals import *

def write_sample(samples,num_samples):
    amplitude=16000//200
    file='what.wav'
    sampleing_rate=24000.0
    nframes=num_samples
    comptype='NONE'
    compname='not compressed'
    nchannels=1
    sampwidth=2

    wav_file=wave.open(file, 'w')

    wav_file.setparams((nchannels, sampwidth, int(sampleing_rate), nframes, comptype, compname))


    i=-1
    for s in samples:
        i = -i
        wav_file.writeframes(struct.pack('h', int(i*s*amplitude)))
    
    wav_file.close()


def draw_sample(pix_div,sample):
    i = 0
    for e in sample:

        pygame.draw.polygon(windowSurface,
                green,
                ((i*pix_div, 0), (i*pix_div, e)),
                1
                )
        i = i + 1

pygame.init()

windowSize = (1360, 200)
#pygame.display.get_surface().get_size()

windowSurface = pygame.display.set_mode(windowSize, 0, 32)
pygame.display.set_caption('Hello, world!')

black = (0, 0, 0)
white = (255, 255, 255)
red   = (255, 0, 0)
green = (0, 255, 0)
blue  = (0, 0, 255)


print(pygame.display.get_surface().get_size())

div = 200
#use div like 1/windowSize[0]
# or use antialiasing
i = 0
sampleAmplitude = []
num_samples = windowSize[0]

while(i < num_samples):
    sampleAmplitude.append(random.randint(0,200))
    i += 1


#pygame.display.update()
pygame.display.flip()

spaceing = 1
mouseClick = False
pos = (1,1)
lastpos = pos
while True:
    windowSurface.fill(black)
    if(mouseClick):
        lastpos = pos
        pos = pygame.mouse.get_pos()
        if(pos[0] != lastpos[0]):
             if(pos[0] >= len(sampleAmplitude)):
                 sampleAmplitude[-1] = pos[1]
             elif(pos[0] < 0):
                 sampleAmplitude[0] = pos[1]
             else:
             #form a straight line from lastpos to pos
                 dy = pos[1] - lastpos[1]
                 dx = pos[0] - lastpos[0]
                 print([pos, lastpos, dy, dx])
                 slope = dy/dx
                 if(lastpos[0] < pos[0]):
                     start = lastpos[0]
                     end = pos[0]
                 else:
                     start = pos[0]
                     end = lastpos[0]
                 for x in range(start,end):

                     y = slope * x - slope * lastpos[0] + lastpos[1]
                     print(y)
                     sampleAmplitude[x//spaceing] = y

        
    draw_sample(spaceing,sampleAmplitude)
    #pygame.draw.polygon(windowSurface,
    #                green,
    #                ((0,0),pos),1)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                write_sample(sampleAmplitude,num_samples) 
                pygame.quit()
                sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            mouseClick = True
        if event.type == MOUSEBUTTONUP:
            mouseClick = False
    pygame.display.update()
