




peed = 10 # how many iterations per second
squares = 1 # size of squares: 0 = 8X8, 1 = 16X16, 2 = 32X32, 3 = 64X64
map_size = 32 # the width and height


if squares == 0:
  imgs = ["res/alive_8.png","res/dead_8.png",8]
if squares == 1:
  imgs = ["res/alive_16.png","res/dead_16.png",16]
if squares == 2:
  imgs = ["res/alive_32.png","res/dead_32.png",32]
if squares == 3:
  imgs = ["res/alive_64.png","res/dead_64.png",64]

#-----CONFIG-----

width       = map_size*imgs[2]
height      = map_size*imgs[2]
screen_size = width,height
screen      = pygame.display.set_mode(screen_size)
clock       = pygame.time.Clock()
#alive       = pygame.image.load(imgs[0]).convert()
#dead        = pygame.image.load(imgs[1]).convert()
done        = False



class cell:
  def __init__(self,location,alive=False):
    self.to_be = None
    self.alive = alive
    self.pressed = False
    self.location = location




class board:

  def __init__(self):
    self.map = []

  def fill(self,ran):
    for i in xrange(map_size):
      self.map.append([])
      for g in xrange(map_size):
        if ran == True:
          a = random.randint(0,4)
          if a == 0: self.map[i].insert(g,cell((i,g),True))
          else: self.map[i].insert(g,cell((i,g)))
        else: self.map[i].insert(g,cell((i,g)))
  
