import pygame, sys
import struct, random, wave 
from pygame.locals import *




class transform:
#a,b
#c,d
    def __init__(self,matrix):
        self.a = matrix[0][0]
        self.b = matrix[0][1]
        self.c = matrix[1][0]
        self.d = matrix[1][1]
        return

    def apply(self,pos):
        x = self.a * pos[0] + self.b * pos[1]
        y = self.c * pos[0] + self.d * pos[1]
        return (int(x),int(y))

class samples:
    """ All PCM and associated data. """
    def __init__(self,samples,startpos,pixpitch):
        self.samples = samples
        #TODO: this goes into something that owns the drawstuff for samples
        self.pixpitch = pixpitch
        self.spos = startpos
        self.screen2samples = transform([[1/pixpitch, 0],[0,1]])

        self.samples2screen = transform([[pixpitch, 0],[0,1]])
        return

    def __iter__(self):
        for s in self.samples:
            yield s

    def write(self):
        amplitude=16000//200
        file='what.wav'
        sampleing_rate=24000.0
        nframes=len(self.samples)
        comptype='NONE'
        compname='not compressed'
        nchannels=1
        sampwidth=2
    
        wav_file=wave.open(file, 'w')

        wav_file.setparams((nchannels, sampwidth, int(sampleing_rate), nframes, comptype, compname))

        i=1
        for s in self.samples:
            wav_file.writeframes(struct.pack('h', int(i*s*amplitude)))
            i = -i

        wav_file.close()
        return

    def draw(self):
        i = 0
        for e in self.samples:
            pygame.draw.polygon(windowSurface,
                    green,
                    ((i*self.pixpitch, 0), (i*self.pixpitch, e)),
                    1
                    )
            i = i + 1
        return


class pcmMouse:
    """ Functions for modifying Samples, using the mouse. """
    def __init__(self):
        self.position = pygame.mouse.get_pos()
        self.lastPosition = self.position
        return

    def pencil(self,samp):

        self.lastPosition = self.position
        self.position = pygame.mouse.get_pos()

        # Do all operations in sample's coordinates.
        pos = samp.screen2samples.apply(self.position)
        lastpos = samp.screen2samples.apply(self.lastPosition)

        print([pos,lastpos,len(samp.samples)])
        if(pos[0]+1 >= len(samp.samples)):
            samp.samples[-1] = pos[1]
            return
        elif(pos[0] == 0):
            samp.samples[0] = pos[1]
            return
        if(pos[0] == lastpos[0]):
            return

        #TODO: fix for loop below to work even if start < end
        if(lastpos[0] < pos[0]):
            start = lastpos[0]
            end = pos[0]
        else:
            start = pos[0]
            end = lastpos[0]

        #form a straight line from lastpos to pos
        dy = pos[1] - lastpos[1]
        dx = pos[0] - lastpos[0]
        #print([pos, lastpos, dy, dx])
        slope = dy/dx
        for x in range(start,end):
            # point slope equation
            y = slope * x - slope * lastpos[0] + lastpos[1]
            #print(y)
            samp.samples[x] = y
        return

class signal:
    def __init__(self):
        self.mouseClick = False
        self.writeQuit = False
        self.quit = False
        return

    def poll(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.writeQuit = True
            elif event.type == MOUSEBUTTONDOWN:
                self.mouseClick = True
            elif event.type == MOUSEBUTTONUP:
                self.mouseClick = False
        return


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

sampletmp = []
samplepitch = 5
for i in range(windowSize[0]//samplepitch):
    sampletmp.append(random.randint(0,200))
samp = samples(sampletmp,(0,100),samplepitch)


mouse = pcmMouse()
input = signal()

#pygame.display.update()
pygame.display.flip()

while True:
    windowSurface.fill(black)

    input.poll()

    if input.quit:
        pygame.quit()
        sys.exit()
    if input.writeQuit:
        samp.write()
        pygame.quit()
        sys.exit()
    if input.mouseClick:
        mouse.pencil(samp)

    samp.draw()
    pygame.display.update()
