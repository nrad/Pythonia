#!/usr/bin/python
from PIL import Image, ImageDraw
import math, colorsys
import random
import os




class Mandel():
    

    def __init__(self, z=0, scale=1.0, iterate_max = 1000):

        self.z = z
        self.dimensions = (800, 800)
        #self.dimensions = (200, 200)
        self.scale = scale/(self.dimensions[0]/3)
        self.center_point = (2.2, 1.5)       # Use this for Mandelbrot set
        #center = (1.5, 1.5)       # Use this for Julia set
        self.iterate_max = iterate_max
        self.colors_max = iterate_max
        
        # Calculate a tolerable palette
        self.palette = [0] * self.colors_max
        self.center = lambda  x,y : (x * self.scale - self.center_point[0], y * self.scale - self.center_point[1]) 
    
        for i in xrange(self.colors_max):
            #f = 1-abs((float(i)/colors_max-1)**15)
            f = 1-abs( math.log((i+0.00001)/self.colors_max) / math.log((0.00001)/self.colors_max) )
            r, g, b = colorsys.hsv_to_rgb(.66+f/3, 1-f/2, f)
            #palette[i] = (int(r*255), int(g*255), int(b*255))
            self.palette[i] = (int(r*random.randrange(0,255) ), int(g*random.randrange(0,255)), int(b* random.randrange(0,255)))

    def output_path(self, output_name="results"):
        """ Create an output filename: look into folder dreams,
            return lowest INTEGER.jpg with leading zeros, e.g. 00020.jpg """
        index=0 
        output_file = "%s.png"%output_name#%index
        while os.path.exists(output_file):
            index += 1
            output_file = "{output_name}_{index}.png".format(output_name = output_name, index=index)
        return output_file


    
    
    def rand_rgb(self, ): 
        r = random.randrange
        return tuple([r(0,255) for x in range(3)])
    
    
    # Calculate the mandelbrot sequence for the point c with start value z
    def iterate_mandelbrot(self, c, z = None):
        if z == None: z=self.z
        for n in xrange(self.iterate_max + 1):
            z = z*z +c
            if abs(z) > 2:
                return n
        return None
    
    # Draw our image
    def draw_image(self, output_postfix=""):

        img = Image.new("RGB", self.dimensions)
        d = ImageDraw.Draw(img)

        for y in xrange(self.dimensions[1]):
            for x in xrange(self.dimensions[0]):
                #c = complex(x * scale - center_point[0], y * scale - center_point[1])
                c = complex( * self.center(x,y) )
                n = self.iterate_mandelbrot(c)            # Use this for Mandelbrot set
        
                #n = iterate_mandelbrot(complex(0.3, 0.6), c)  # Use this for Julia set
                #print n
                if n is None:
                    v = 1
                else:
                    v = n/self.colors_max
        
                d.point((x, y), fill = self.palette[int(v * (self.colors_max-1))])
                #d.point( (x, y) , fill = self.palette[int( v < 20 )])
                #if v==1:
                #    d.point((x, y), fill = rand_rgb() )
                #else:
                #    d.point((x, y), fill = palette[ int( v * (colors_max-1))])
                #d.point((x, y), fill = palette[x%colors_max])
            #img.save("result_%s.png"%y)
        
        del d
        output_file = self.output_path("results_%s"%output_postfix)
        img.save(output_file)



    def draw_palette(self ):

        img = Image.new("RGB", self.dimensions)
        d = ImageDraw.Draw(img)

        for y in xrange(self.dimensions[1]):
            for x in xrange(self.dimensions[0]): 
                rel_x =  float(x)/self.dimensions[0]
                rel_y =  float(y)/self.dimensions[1]
                #print rel_x, rel_y
                d.point((x, y), fill = self.palette[int( (rel_x+rel_y)/2. * (self.colors_max-1))])
        
        del d
        output_file = self.output_path()
        img.save(output_file)





















if __name__=="__main__":
    m = Mandel()
    m.draw_image()
