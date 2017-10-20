import pygame, sys
import struct, random, wave
from pygame.locals import *

class xyremap:
    """ use an affine matrix to transform points
    from one cartesian coordinate system to another """
#   a,b,c
#   d,e,f
#   g,h,i

    def __init__(self,matrix):
        self.a = matrix[0][0]
        self.b = matrix[0][1]
        self.c = matrix[0][2]
        self.d = matrix[1][0]
        self.e = matrix[1][1]
        self.f = matrix[1][2]
#       self.g = matrix[2][0]
#       self.h = matrix[2][1]
#       self.i = matrix[2][2]
        return

    #TODO: Decide if this needs rotation
    @classmethod
    def easyInit(self,scalex,scaley,x,y):
        return self(
        [[scalex, 0,      x],
         [0,      scaley, y]])


    def apply(self,pos):
        """Matrix multiply using homogeneous coordinates"""

#        _     _   _ _
#       | a,b,c | | x |
#       | d,e,f | | y | = ret
#       |_g,h,i_| |_1_|

        x = self.a * pos[0] + self.b * pos[1] + self.c # * 1
        y = self.d * pos[0] + self.e * pos[1] + self.f # * 1
#       1 = self.g * pos[0] + self.h * pos[1] + self.i   * 1
        return (int(x),int(y))

    #TODO: Write this
    def applyReverse(self,pos):
        """Reverse the affine coordinate transformation"""
        x = 0
        y = 0
        return (int(x),int(y))

class samples:
    """ All PCM and associated data. """
    def __init__(self,samples,scalx,x,y):
        self.samples = samples
        #TODO: this goes into something that owns the drawstuff for samples

        self.screen2samples = xyremap.easyInit(1/scalx, 1,-x/scalx,-y)
        self.samples2screen = xyremap.easyInit(  scalx, 1, x      , y)
        return

    def __iter__(self):
        for s in self.samples:
            yield s

    def __len__(self):
        return len(self.samples)

    def write(self):
        amplitude=16000//200
        file='what.wav'
        sampleing_rate=24000.0
        nframes=len(self)
        comptype='NONE'
        compname='not compressed'
        nchannels=1
        sampwidth=2

        wav_file=wave.open(file, 'w')

        wav_file.setparams((nchannels, sampwidth, int(sampleing_rate), nframes, comptype, compname))

        i=1
        for s in self.samples:
            wav_file.writeframes(struct.pack('h', int(i*s*amplitude)))
        #    i = -i

        wav_file.close()
        return

    def read(self):
        amplitude=16000//200
        file='what.wav'

        wav_file=wave.open(file, 'r')

        nchannels, sampwidth, framerate, nframes, comptype, compname = wav_file.getparams()
        self.nchannels = nchannels
        self.sampwidth = sampwidth
        self.framerate = framerate
        self.nframes   = nframes
        self.comptype  = comptype
        self.compname  = compname
        tmp_sample = 0

        tmp_bytes = wav_file.readframes(nframes)

        tmp_iter = struct.iter_unpack('h', tmp_bytes)
        for s in range(nframes):
            self.samples.append(next(tmp_iter)[0]//amplitude)

        wav_file.close()
        return

    def draw(self):
        i = 0
        for e in self.samples:
            startpos = self.samples2screen.apply((i,0))
            endpos = self.samples2screen.apply((i,e))

            pygame.draw.polygon(
            windowSurface, green, (startpos, endpos), 1)
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

        print([pos,lastpos,len(samp)])
        if(pos[0]+1 >= len(samp)):
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
samplescale = 9
for i in range(windowSize[0]//samplescale):
    sampletmp.append(random.randint(0,200))
samp = samples([],samplescale,10,100)
samp.read()


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
