#############################
# Group Name: Bird Brains
# Group Members: 
#  Elijah Payton
#  Xandria Kline
#  Fisher Hall
# Purpose: Flappy Bird Game where player controls 3 inputs
#############################
import math
import pygame
import os
from pygame.locals import *
from random import randint
from collections import deque

FPS = 60
pixelSpeed = 0.15       # Speed at which the game plays
windowWidth = 284 * 2
windowHeight= 512

# Bird class that controls all attributes associated with the bird
class Bird(pygame.sprite.Sprite):
    WIDTH = 32              # Width of bird image
    HEIGHT = 32             # Height of Bird image
    sinkSpeed = 0.14        # How fast the bird falls
    climbSpeed = 0.2        # How much the bird climbs from one 'flap'
    climbDuration = 300.0   # How long it takes bird to complete one 'flap'

    def __init__(self, x, y, climbMsec, images):
        super(Bird,self).__init__()
        self.x = x
        self.y = y
        self.climbMsec = climbMsec
        self.birdimage = images
        self.maskbird = pygame.mask.from_surface(self.birdimage)

    def updatePos(self, deltaFrames = 1):
        if self.climbMsec > 0:
            fracOfclimb = 1 - self.climbMsec/Bird.climbDuration
            self.y -= (Bird.climbSpeed * ((deltaFrames/FPS)*1000) * 
                    (1- math.cos(fracOfclimb * math.pi)))
            self.climbMsec -= ((deltaFrames/FPS)*1000)
        else:
            self.y += Bird.sinkSpeed * (1000*(deltaFrames/FPS))
    
    @property
    def image(self):
        return self.birdimage

    @property
    def mask(self):
        return self.maskbird
    
    @property
    def rect(self):
        return Rect(self.x, self.y, Bird.WIDTH, Bird.HEIGHT)

class Pipes(pygame.sprite.Sprite):
    width = 80
    pieceheight = 32
    addInterval = 3000

    def __init__(self, pipeEndImage, pipeBodyImage):
        self.x = float(windowWidth - 1)
        self.scoreCounted = False

        self.image = pygame.Surface((Pipes.width, windowHeight), SRCALPHA)
        self.image.convert()
        self.image.fill((0,0,0,0))
        totalPipeBodyPieces = int(
            (windowHeight - 
            3 * Bird.HEIGHT -
            3 * Pipes.pieceheight) / Pipes.pieceheight)

        self.bottomPieces = randint(1, totalPipeBodyPieces)
        self.topPieces = totalPipeBodyPieces - self.bottomPieces

        # Bottom Pipe
        for i in range(1, self.bottomPieces + 1):
            piecePos = (0, windowHeight - i*Pipes.pieceheight)
            self.image.blit(pipeBodyImage, piecePos)
        bottomPipeY = windowHeight - (self.bottomPieces * Pipes.pieceheight)
        bottomPiecePos = (0, bottomPipeY - Pipes.pieceheight)
        self.image.blit(pipeEndImage, bottomPiecePos)

        # Top Pipe
        for i in range(self.topPieces):
            self.image.blit(pipeBodyImage, (0, i * Pipes.pieceheight))
        topPipeY = (self.topPieces * Pipes.pieceheight)
        self.image.blit(pipeEndImage, (0, topPipeY))

        # Compensate for End Pieces
        self.topPieces += 1
        self.bottomPieces += 1

        # Collision Detection
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def visible(self):
        return -Pipes.width < self.x < windowWidth
    @property
    def rect(self):
        return Rect(self.x, 0, Pipes.width, Pipes.pieceheight)

    def update(self, deltaFrames = 1):
        self.x -= pixelSpeed * ((deltaFrames / FPS)*1000)
        
    def collisionCheck(self, bird):
        return pygame.sprite.collide_mask(self, bird)

def loadImages():   
    def loadImage(imageFileName):
        fileName = os.path.join(os.path.dirname(__file__),'images',imageFileName)
        image = pygame.image.load(fileName)
        image.convert()
        return image
    return {'birdimage': loadImage('birdimage.png'),
            'pipeBodyImage': loadImage('pipebodyimage.png'),
            'pipeEndImage': loadImage('pipeendimage.png'),
            'background': loadImage('background.png')}

def main():
    pygame.init()
    displaySurface = pygame.display.set_mode((windowWidth, windowHeight))
    pygame.display.set_caption('Pygame Flappy Bird')

    clock = pygame.time.Clock()
    scoreFont = pygame.font.SysFont(None, 32, bold=True)
    images = loadImages()

    bird = Bird(50, int(windowHeight/2 - Bird.HEIGHT/2), 2, (images['birdimage']))
    pipes = deque()

    frameClock = 0
    score = 0
    done = paused = False
    while not done:
        clock.tick(FPS)

        if not (paused or frameClock % ((FPS * Pipes.addInterval)/1000)):
            pipeImages = Pipes(images['pipeEndImage'], images['pipeBodyImage'])
            pipes.append(pipeImages)
        
        for i in pygame.event.get():
            if i.type == QUIT or (i.type == KEYUP and i.key == K_ESCAPE):
                done = True
                break
            elif i.type == KEYUP and i.key in (K_PAUSE, K_p):
                paused = not paused
            elif i.type == MOUSEBUTTONUP or (i.type == KEYUP and i.key in (k_UP, K_RETURN, K_SPACE)):
                bird.climbMsec = Bird.climbDuration
            
        if paused:
                continue

        # check for collisions
        pipeCollision = any(k.collisionCheck(bird) for k in pipes)
        if pipeCollision or 0 >= bird.y or bird.y >= windowHeight - Bird.HEIGHT:
            done = True
            
        for x in (0, windowWidth / 2):
            displaySurface.blit(images['background'], (x,0))

        while pipes and not pipes[0].visible:
            pipes.popleft()

        for i in pipes:
            i.update()
            displaySurface.blit(i.image, i.rect)
        
        bird.updatePos()
        displaySurface.blit(bird.image, bird.rect)

        # update and display score
        for k in pipes :
            if k.x + Pipes.width < bird.x and not k.scoreCounted:
                score += 1
                k.scoreCounted = True
        
        scoreSurface = scoreFont.render(str(score), True, (255, 255, 255))
        scoreX = windowWidth/2 - scoreSurface.get_width()/2
        displaySurface.blit(scoreSurface, (scoreX, Pipes.pieceheight))

        pygame.display.flip()
        frameClock += 1
    print('Game Over! Score: %i' % score)
    pygame.quit()

if __name__ == '__main__':
    main()

    
            

