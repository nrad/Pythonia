import wx
import tools.config
import os
import model.workspace

class Module(object):
    """
    Module.

    Graphic class for a module on the workspace.

    @type x: wx.Coord
    @ivar x: X coordintate of module on workspace.
    @type y: wx.Coord
    @ivar y: Y coordintate of module on workspace.
    @type module: model.module.Module
    @ivar module: Corresponding model.module.Module.
    @type config: tools.config.Config
    @ivar config: Config for some vars.
    @type controller: view.controller.CabelController
    @ivar controller: CabelController.
    @type numInputs: int
    @ivar numInputs: Number of inputs.
    @type numOutputs: int
    @ivar numOutputs: Number of outputs.
    @type height: int
    @ivar height: Height in pixels.
    @type width: int
    @ivar width: Width in pixels.
    @type scale: float
    @ivar scale: Scale factor of module; Read-only property; considers zoom.
    @type _bitmap: wx.Bitmap
    @ivar _bitmap: Stores a bitmap of the module representation for faster
                   drawing.
    @type _plugDistance: int
    @cvar _plugDistance: Distance between two output or input plugs in
                         pixels.
    @type _plugIndentation: int
    @cvar _plugIndentation: Indentation from module border for in- and outputs.
    @type _plugNameIndentation: int
    @cvar _plugNameIndentation: Indentation from module border for in- and
                                output names.
    @type _plugRadius: int
    @cvar _plugRadius: Size of in- and output plugs in pixels.
    @type _aColour: wx.Colour
    @cvar _aColour: Colour for a-rate plugs.
    @type _kColour: wx.Colour
    @cvar _kColour: Colour for k-rate plugs.
    @type _iColour: wx.Colour
    @cvar _iColour: Colour for i-rate plugs.
    @type _unknownColour: wx.Colour
    @cvar _unknownColour: Colour for unknown plugs.
    """
    _aColour = wx.Colour(255, 0, 0)
    _kColour = wx.Colour(0, 255, 0)
    _iColour = wx.Colour(0, 0, 255)
    _unknownColour = wx.Colour(150, 150, 150)
    

    def __init__(self, x, y, module, controller):
        """
        Standard constructor.

        @type  x: wx.Point
        @param x: X coordintate of module on workspace.
        @type  y: wx.Point
        @param y: Y coordintate of module on workspace.
        @type  module: model.module.Module
        @param module: Corresponding model.module.Module.
        @type controller: view.controller.CabelController
        @param controller: CabelController.
        """
        # Controller
        self.controller = controller
        
        # Config for some vars
        self.config = model.workspace.Workspace.config
        
        # Set position
        self.x = x
        self.y = y

        # Connect to corresponding model.module.Module
        self.module = module
        
        # Scale factor
        self._scale = 1.0
        
        # Get height/width
        self.numInputs = len(self.module.inVars)
        self.numOutputs = len(self.module.outVars)
        self.height = self._getHeight()
        self.width = self._getWidth()
        
        # Make new bitmap buffer for module image
        self._drawBitmap()

    
    def _getPlugDistance(self):
        """
        @rtype: float
        @return: The distance between two plugs considering the scale
                 factor self.scale.
        """
        return self._getCharHeight() + float(4 * self.scale)
    _plugDistance = property(_getPlugDistance)
       
    
    def _getPlugIndentation(self):
        """
        @rtype: float
        @return: The indentation of a plug from the border of a module
                 considering the scale factor self.scale.
        """
        return self._getPlugRadius() + float(2 * self.scale)
    _plugIndentation = property(_getPlugIndentation)
    
    
    def _getPlugNameIndentation(self):
        """
        @rtype: float
        @return: The indentation of the name of an in-/outVar from the
                 plugdistance considering the scale factor self.scale.
        """
        return self._getCharWidth() + float(11 * self.scale)
    _plugNameIndentation = property(_getPlugNameIndentation)
    
    
    def _getPlugRadius(self):
        """
        @rtype: float
        @return: The radius of plugs considering the scale factor self.scale.
        """
        return self._getCharHeight() - float(9 * self.scale)
    _plugRadius = property(_getPlugRadius)
    
    
    def _getCharHeight(self):
        """
        @rtype: float
        @return: The height of a font character considering the scale factor
                 self.scale.
        """
        dc = wx.MemoryDC()
        dc.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        return float(dc.GetCharHeight() * self.scale)
    
    
    def _getCharWidth(self):
        """
        @rtype: float
        @return: The width of a font character considering the scale factor
                 self.scale.
        """
        dc = wx.MemoryDC()
        dc.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        return float(dc.GetCharWidth() * self.scale)
    
    
    def _getScale(self):
        """
        @rtype: float
        @return: Factor to scale module.
        """
        return self._scale * float(self.controller._view.zoom) / 100.0
    scale = property(_getScale)


    def zoom(self):
        """
        Repaint module zoomed.
        """
        self.refresh()
    
    
    def scaleIt(self, scaleFactor):
        """
        """
        self._scale = self._scale + scaleFactor
        self.refresh()
     
    
    def refresh(self):
        """
        """
        self.width = self._getWidth()
        self.height = self._getHeight()
        self._drawBitmap()
    
     
    def draw(self, dc):
        """
        Draw this module on workspace.

        @type  dc: wx.DC
        @param dc: Device context on which to draw the module bitmap.
        """
        dc.DrawBitmap(self._bitmap, self.x, self.y)


    def drawRelative(self, dc, origin):
        """
        Draw this module relative to origin in our workspace.

        @type  dc: wx.DC
        @param dc: Device context on which to draw the module bitmap.
        @type  origin: wx.Point
        @param origin: Actual origin of workspace.
        """
        dc.DrawBitmap(self._bitmap, self.x - origin.x, self.y - origin.y)


    def setPosition(self, pt):
        """
        Set position of module.

        @type  pt: wx.Point
        @param pt: New position of module.
        """
        self.x = pt.x
        self.y = pt.y


    def setRelativePosition(self, vecPt):
        """
        Move module in vector direction.

        @type  vecPt: wx.Point
        @param vecPt: Direction vector for movement of module.
        """
        self.x = self.x + vecPt.x
        self.y = self.y + vecPt.y


    def getOutput(self, num):
        """
        Returns point of output plug.

        @type  num: int
        @param num: Number of output.
        @rtype : wx.Point
        @return: Point of output.
        """
        return wx.Point(self.x + self.width - self._plugIndentation,
                        self.y + (num+1) * self._plugDistance + 0.4 * self._plugDistance)
                        
    
    def getOutVar(self, num):
        """
        Returns OutVar of output num.

        @type  num: int
        @param num: Number of output.
        @rtype : model.var.OutVar
        @return: OutVar.
        """
        return self.module.outVars[num]
        

    def getInput(self, num):
        """
        Returns point of input plug.

        @type  num: int
        @param num: Number of input.
        @rtype : wx.Point
        @return: Point of input.
        """
        return wx.Point(self.x + self._plugIndentation,
                        self.y + (num+1) * self._plugDistance + 0.4 * self._plugDistance)


    def getInVar(self, num):
        """
        Returns inVar of input num.

        @type  num: int
        @param num: Number of output.
        @rtype : model.var.InVar
        @return: InVar.
        """
        return self.module.inVars[num]


    def isOnModule(self, pt):
        """
        Returns True if this module contains given point.

        @type  pt: wx.Point
        @param pt: Test if pt is included in module.
        @rtype : bool
        @return: Is pt on module?
        """
        if pt.x < self.x or pt.x > self.x + self.width or \
           pt.y < self.y or pt.y > self.y + self.height:
            return False
        return True


    def isOnOutput(self, pt):
        """
        If point is on an output returns the output number. Otherwise
        it returns -1.

        @type pt: wx.Point
        @param pt: Test if pf is on an output.
        @rtype : int
        @return: Number of output on which pt is (0 indexed). Otherwise -1.
        """
        for i in range(0, self.numOutputs):
            plugPt = self.getOutput(i)
            if pt.x < plugPt.x + self._plugRadius and \
               pt.x > plugPt.x - self._plugRadius and \
               pt.y < plugPt.y + self._plugRadius and \
               pt.y > plugPt.y - self._plugRadius:
                return i
        return -1


    def isOnInput(self, pt):
        """
        If point is on an input returns the input number. Otherwise it
        returns -1.

        @type  pt: wx.Point
        @param pt: Test if pf is on an input.
        @rtype : int
        @return: Number of input on which pt is (0 indexed). Otherwise -1.        
        """
        for i in range(0, self.numInputs):
            plugPt = self.getInput(i)
            if pt.x < plugPt.x + self._plugRadius and \
               pt.x > plugPt.x - self._plugRadius and \
               pt.y < plugPt.y + self._plugRadius and \
               pt.y > plugPt.y - self._plugRadius:
                return i
        return -1
        
      
    def getName(self):
        """
        Return name of module.
        
        @rtype: string
        @return: Name of module.
        """
        if self.config.view.getVal(tools.config.View.FULLMODULENAMES):
            return self.module.fullName
        else:
            return self.module.name


    def _getWidth(self):
        """
        Return width of module.

        @rtype: float
        @return: Width of module.
        """
        dc = wx.MemoryDC()
        title = self.getName() + ' ' + str(self.module.id)
        dc.SetFont(wx.Font(8.0 * self.scale , wx.DEFAULT, wx.NORMAL, wx.BOLD))
        titleWidth, titleHeight = dc.GetTextExtent(title)

        inVarWidth, outVarWidth = 0, 0
        dc.SetFont(wx.Font(8.0 * self.scale, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        for i in self.module.inVars:
            w, h = dc.GetTextExtent(i.name)
            if w > inVarWidth:
                inVarWidth = w
        for o in self.module.outVars:
            w, h = dc.GetTextExtent(o.name)
            if w > outVarWidth:
                outVarWidth = w
        if (inVarWidth + outVarWidth + 2 * self._plugNameIndentation) > titleWidth:
            return (inVarWidth + outVarWidth) + 2 * self._plugNameIndentation + 5 * self.scale
        return titleWidth + self._plugNameIndentation
    
    
    def _getHeight(self):
        """
        Return height of module.
        
        @rtype: float
        @return Height of module.
        """
        if self.numInputs > self.numOutputs:
            return (self.numInputs + 1) * self._plugDistance
        else:
            return (self.numOutputs + 1) * self._plugDistance

        
    def _drawBitmap(self):
        """
        Draw image of module on module bitmap.
        """
        skin = None
        border= 3 # Width of black border

        # Set skin if skin jpg exists
        # TODO: Change to absolute path
        skinPath = os.path.join(os.getcwd(),
                                self.config.directories.getVal(self.config.directories.MODULES),
                                self.module.fullName + ".jpg")
        if os.path.exists(skinPath):
            imgSkin = wx.Image(skinPath, wx.BITMAP_TYPE_JPEG)
            # scale the skin image
            imgSkin.Rescale(imgSkin.GetWidth() * self.scale, imgSkin.GetHeight() * self.scale)
            skin = wx.BitmapFromImage(imgSkin)
            if skin.GetWidth() + border > self.width:
                self.width = skin.GetWidth() + border
            if skin.GetHeight() + border > self.height:
                self.height = skin.GetHeight() + border

        # Create empty bitmap for drawing
        self._bitmap = wx.EmptyBitmap(self.width, self.height)

        # Start Drawing
        dc = wx.MemoryDC()
        #dc.SetUserScale(self.scale, self.scale)
        dc.SelectObject(self._bitmap)

        dc.BeginDrawing()

        # Draw outline
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.SetPen(wx.Pen(wx.BLACK, border, wx.SOLID))
        dc.DrawRectangle(0, 0, self.width, self.height)

        # Draw skin
        if skin:
            dc.DrawBitmap(skin,
                          self.width / 2 - skin.GetWidth() / 2,
                          self.height / 2 - skin.GetHeight() / 2, False)

        # Draw title
        title = self.getName() + ' ' + str(self.module.id)
        dc.SetFont(wx.Font(8.0 * self.scale, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        dc.DrawText(title, 2 * self._plugRadius, 2)

        # Draw inputs
        dc.SetFont(wx.Font(int(8 * self.scale), wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        for i in range(0, self.numInputs):
            # Get coordinates
            plugPt = self.getInput(i) # Absolute coordinates
            plugX = plugPt.x - self.x # Relative coordinates
            plugY = plugPt.y - self.y # Relative coordinates
            
            # Draw input name
            dc.SetPen(wx.Pen(wx.BLACK, 1, wx.SOLID))
            dc.SetBrush(wx.WHITE_BRUSH)
            dc.DrawText(self.module.inVars[i].name,
                        self._plugNameIndentation,
                        plugY - self._plugIndentation)

            # Draw plug backgroup
            dc.SetPen(wx.BLACK_PEN)
            dc.SetBrush(wx.BLACK_BRUSH)
            dc.DrawCircle(plugX, plugY, self._plugRadius + 1)

            # Draw plug foreground
            colour = Module._unknownColour
            if self.module.inVars[i].type == 'a':
                colour = Module._aColour
            elif self.module.inVars[i].type == 'k':
                colour = Module._kColour
            elif self.module.inVars[i].type == 'i':
                colour = Module._iColour
            dc.SetPen(wx.Pen(colour, 1, wx.SOLID))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawCircle(plugX, plugY, self._plugRadius)

        # Draw outputs
        dc.SetFont(wx.Font(int(8.0 * self.scale), wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        for i in range(0, self.numOutputs):
            # Get coordinates
            plugPt = self.getOutput(i) # Absolute coordinates
            plugX = plugPt.x - self.x  # Relative coordinates
            plugY = plugPt.y - self.y  # Relative coordinates

            # Draw output name
            dc.SetPen(wx.Pen(wx.BLACK, 1, wx.SOLID))
            dc.SetBrush(wx.WHITE_BRUSH)
            width, height = dc.GetTextExtent(self.module.outVars[i].name)
            dc.DrawText(self.module.outVars[i].name,
                        self.width - self._plugNameIndentation - width,
                        plugY - self._plugIndentation,)

            # Draw plug background
            dc.SetPen(wx.BLACK_PEN)
            dc.SetBrush(wx.BLACK_BRUSH)
            dc.DrawCircle(plugX, plugY, self._plugRadius + 1)

            # Draw plug foreground
            colour = Module._unknownColour
            if self.module.outVars[i].type == 'a':
                colour = Module._aColour
            elif self.module.outVars[i].type == 'k':
                colour = Module._kColour
            elif self.module.outVars[i].type == 'i':
                colour = Module._iColour
            dc.SetPen(wx.Pen(colour, 1, wx.SOLID))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawCircle(plugX, plugY, self._plugRadius)

        dc.EndDrawing()
