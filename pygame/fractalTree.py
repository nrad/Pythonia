import pygame, math
 
pygame.init()
window = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Fractal Tree")
screen = pygame.display.get_surface()

colorDict=pygame.colordict.THECOLORS
color=[colorDict['rosybrown'],colorDict['darkgreen'],colorDict['lightgreen'],colorDict['lightgreen'],colorDict['lightgreen']]
 
def drawTree(x1, y1, angle, depth):
    if depth:
        print depth
        x2 = x1 + int(math.cos(math.radians(angle)) * depth * 10.0)
        y2 = y1 + int(math.sin(math.radians(angle)) * depth * 10.0)
        pygame.draw.line(screen, (255,255,255), (x1, y1), (x2, y2), depth)
        drawTree(x2, y2, angle - 20, depth - 1)
        drawTree(x2, y2, angle + 20, depth - 1)
 
def input(event):
    if event.type == pygame.QUIT:
        exit()
 
drawTree(300, 550, -80, 10)
pygame.display.flip()
while True:
    input(pygame.event.wait())
