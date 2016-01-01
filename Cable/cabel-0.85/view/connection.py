import wx
import tools.config
import model.workspace

class Connection(object):
    """
    Connection.
    
    Graphic class for connection from start point to end point.

    @type startPt: wx.Point
    @ivar startPt: Start point of connection.
    @type endPt: wx.Point
    @ivar endPt: End Point of connection.
    @type config: tools.config.View
    @ivar config: View related config vars.
    """


    def __init__(self, startPt, endPt):
        """
        Standard constructor.

        @type  startPt: wx.Point
        @param startPt: Start point of connection.
        @type  endPt: wx.Point
        @param endPt: End point of connection.
        """
        self.startPt = startPt
        self.endPt = endPt
        self.config = model.workspace.Workspace.config.view


    def getColours(self):
        """
        Calculates the 3 colours of a cabel connection out of the basic value in config.xml
        
        @rtype: dict of wx.colour
        @return: A dictionary with the entries: 'shade', 'midtone' and 'highlight'
        """
        basicColour = self.config.getVal(tools.config.View.CABLECOLOUR)
        red = basicColour.Red()
        green = basicColour.Green()
        blue = basicColour.Blue()
        
        colourShade = wx.Colour((int(red * 0.33) <= 255 and [int(red * 0.33)] or [255])[0], \
                                      (int(green * 0.33) <= 255 and [int(green * 0.33)] or [255])[0], \
                                      (int(blue * 0.33) <= 255 and [int(blue * 0.33)] or [255])[0])
        colourMidtone = wx.Colour((int(red * 1.0) <= 255 and [int(red * 1.0)] or [255])[0], \
                                        (int(green * 1.0) <= 255 and [int(green * 1.0)] or [255])[0], \
                                        (int(blue * 1.0) <= 255 and [int(blue * 1.0)] or [255])[0])
        colourHighlight = wx.Colour((int(red * 1.33) <= 255 and [int(red * 1.33)] or [255])[0], \
                                        (int(green * 1.33) <= 255 and [int(green * 1.33)] or [255])[0], \
                                        (int(blue * 1.33) <= 255 and [int(blue * 1.33)] or [255])[0])
                                        
        return {'shade': colourShade, 'midtone': colourMidtone, 'highlight': colourHighlight}
        

    def getSagging(self):
        """
        Get the sagging of connection cables as saved in config.xml.
        
        @rtype: int
        @return: Sagging of cable connections.
        """
        return self.config.getVal(tools.config.View.CABLESAGGING)


    def draw(self, dc, zoom = 100):
        """
        Draw this connection in our workspace.

        @type  dc: wx.DC
        @param dc: Device conetext on which to draw.
        @type zoom: int
        @param zoom: Zoom of Connection; default = 100.
        """
        self.drawRelative(dc, wx.Point(0, 0), zoom)
        

    def drawRelative(self, dc, origin, zoom = 100):
        """
        Draw this connection relative to origin in our workspace.

        @type  dc: wx.DC
        @param dc: Device context on which to draw.
        @type  origin: wx.Point
        @param origin: Actual orgin of workspace.
        @type zoom: int
        @param zoom: Zoom of Connection; default = 100.
        """
        startX = self.startPt.x - origin.x
        startY = self.startPt.y - origin.y
        endX = self.endPt.x - origin.x
        endY = self.endPt.y - origin.y
        colours = self.getColours()
        sagging = self.getSagging()
        scale = float(zoom) / 100.0
        dc.SetPen(wx.Pen(colours['shade'], 6.0 * scale, wx.SOLID))
        dc.DrawSpline([wx.Point(startX, startY),
                       wx.Point((startX + endX)/2,
                                (startY + endY)/2 + sagging),
                       wx.Point(endX, endY)])
        dc.SetPen(wx.Pen(colours['midtone'], 3.0 * scale, wx.SOLID))
        dc.DrawSpline([wx.Point(startX, startY),
                       wx.Point((startX + endX)/2,
                                (startY + endY)/2 + sagging),
                       wx.Point(endX, endY)])
        dc.SetPen(wx.Pen(colours['highlight'], 1.0 * scale, wx.SOLID))
        dc.DrawSpline([wx.Point(startX, startY),
                       wx.Point((startX + endX)/2,
                                (startY + endY)/2 + sagging),
                       wx.Point(endX, endY)])


#---------------------------------------------------------------------------

class ModuleConnection(Connection):
    """
    Graphic class for module connections.

    @type outModule: view.module.Module
    @ivar outModule: Start module of connection.
    @type inModule: view.module.Module
    @ivar inModule: End module of connection.
    @type outputNum: int
    @ivar outputNum: Output number of start plug on outModule.
    @type inputNum: int
    @ivar inputNum: Input number of end plug on inModule.
    """

    def __init__(self, outModule, outputNum, inModule, inputNum):
        """
        Standard constructor.

        @type  outModule: view.module.Module
        @param outModule: Start module of connection.
        @type  inModule: view.module.Module
        @param inModule: End module of connection.
        @type  outputNum: int
        @param outputNum: Output number of start plug on outModule.
        @type  inputNum: int
        @param inputNum: Input number of end plug on inModule.
        """
        self.outModule = outModule
        self.inModule = inModule
        self.outputNum = outputNum
        self.inputNum = inputNum
        Connection.__init__(self, self.outModule.getOutput(self.outputNum),
                            self.inModule.getInput(self.inputNum))


    def __eq__(self, other):
        """
        Overwritten equal operator.
        
        @type  other: view.connection.ModuleConnection
        @param other: the ModuleConnection to compare with
        """
        return (self.outModule == other.outModule) \
            and (self.inModule == other.inModule) \
            and (self.outputNum == other.outputNum) \
            and (self.inputNum == other.inputNum)
            
            
    def __ne__(self, other):
        """
        Overwritten not equal operator.
        
        @type  other: view.connection.ModuleConnection
        @param other: the ModuleConnection to compare with
        """
        return not self.__eq__(other)
            
    
    def draw(self, dc, zoom):
        """
        Draw this connection in our workspace.

        @type  dc: wx.DC
        @param dc: Device conetext on which to draw.
        @type zoom: int
        @param zoom: Zoom of Connection; default = 100.
        """
        # Update startPt and endPt for outModule and inModule
        self.startPt = self.outModule.getOutput(self.outputNum)
        self.endPt = self.inModule.getInput(self.inputNum)
        Connection.draw(self, dc, zoom)


    def drawRelative(self, dc, origin, zoom):
        """
        Draw this connection relative to origin in our workspace.

        @type  dc: wx.DC
        @param dc: Device context on which to draw.
        @type  origin: wx.Point
        @param origin: Actual orgin of workspace.
        @type zoom: int
        @param zoom: Zoom of Connection; default = 100.
        """
        # Update startPt and endPt for outModule and inModule
        self.startPt = self.outModule.getOutput(self.outputNum)
        self.endPt = self.inModule.getInput(self.inputNum)
        Connection.drawRelative(self, dc, origin, zoom)


    def getOutModule(self):
        """
        Return output module of connection.
        """
        return self.outModule


    def getInModule(self):
        """
        Return input moduleof connection.
        """
        return self.inModule


    def getOutputNumber(self):
        """
        Return output number of outModule.
        """
        return self.outputNum


    def getInputNumber(self):
        """
        Return input number of inModule.
        """
        return self.inputNum
