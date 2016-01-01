import wx
import wx.py.shell
import os
import sys
import tools.config
from view.controller import CabelController
from view.module import Module
from view.connection import ModuleConnection
from view.connection import Connection
from model.observer import Observer
from model.xmlReader import XmlWorkspaceReader
from model.xmlGenerator import XmlGenerator
from model.workspace import ConnectionError


class CabelFrame(wx.Frame, Observer):
    """
    CabelFrame.

    A frame showing the contents of a single Cabel session.

    @type _controller: view.workspace.CabelController
    @ivar _controller: Corresponding controller for this view.
    @type _modules: list
    @ivar _modules: List of modules to paint on workspace.
    @type _connections: list
    @ivar _connections: List of connections to paint on workspace.
    @type _draggedCable: model.view.connection.Connection
    @ivar _draggedCable: Visual feedback when connection two modules.
    @type _modulesDict: dict
    @ivar _modulesDict: Dictionary to map ids to their
                        corresponding view modules.
    @type __fileMenu: wx.Menu
    @ivar __fileMenu: File Menu.
    @type _modulesMenu: wx.Menu
    @ivar _modulesMenu: Menu with all in th modules- searchpath
                        defined xml modules
    @type __recentMenuId: id
    @ivar __recentMenuId: Id of RecentMenu Entry.
    @type _splitter: CabelSplitterWindow
    @ivar _splitter: Splitter Window.
    @type _shell: wx.py.shell.Shell
    @ivar _shell: Python shell for command input.
    @type config: tools.config.Config.View
    @ivar config: relevant config Vars
    @type statusbar: wx.StatusBar
    @ivar statusbar: Statusbar of CabelFrame
    @type workspace: view.workspace.CabelScrolledWindow
    @ivar workspace: Workspace for synth building.
    @type ioTextCtrl: wx.TextCtrl
    @ivar ioTextCtrl: Gets the stdout and stderr output of the app
    @type fileName: string
    @ivar fileName: Name of the workspace
    @type filePath: string
    @ivar filePath: Save-Path of the workspace.
    @type zoom: int
    @ivar zoom: Zoom.
    """


    def __init__(self, model):
        """
        Standard constructor.

        @type  model: model.workspace.Workspace
        @param model: Corresponding model for this view.
        """
        # Initialize Observer
        Observer.__init__(self)
        
        parent = None

        # View related config vars
        self.config = model.config.view
        
        # Filename, etcetera
        self.fileName = ''
        self.filePath = os.path.join(os.getcwd(), 'examples')
        self._cwFileNewCount = 1
        
        size = wx.Size(self.config.getVal(tools.config.View.FRAMEWIDTH), \
                       self.config.getVal(tools.config.View.FRAMEHEIGHT))
        wx.Frame.__init__(self, parent, -1, self.GetTitle(), size = size)
        
        # Remember Maximized Frame; Only works on MSW
        if sys.platform in ("win32") and self.config.getVal(tools.config.View.FRAME_MAXIMIZED):
            self.Maximize(True)
            
        # Zoom
        self.zoom = self.config.getVal(tools.config.View.ZOOM_LASTVALUE)

        # initialize controller
        self._controller = CabelController(model, self)

        # List of modules and connections
        self._modules = []
        self._connections = []
        self._draggedCable = None
        self._modulesDict = {}

        # Create menus
        menubar = wx.MenuBar()
        # File
        self._filemenu = wx.Menu()
        self._filemenu.Append(wx.ID_NEW, "&New\tCTRL-N", "New..")
        self._filemenu.Append(wx.ID_OPEN, "&Open\tCTRL-O", "Open a Workspace")
        # RecentMenu
        self._recentMenuId = wx.NewId()
        recentMenu = self._getRecentMenu()
        self._filemenu.AppendMenu(self._recentMenuId, "Open Recent...", recentMenu)
        if recentMenu.GetMenuItemCount() == 0:
            self._filemenu.Enable(self._recentMenuId, False)
        self._filemenu.AppendSeparator()
        # Save
        self._filemenu.Append(wx.ID_SAVE, "&Save\tCTRL-S", "Save Workspace")
        self._filemenu.Append(wx.ID_SAVEAS, "S&ave As\tALT-S", "Save Workpsace As...")
        self._filemenu.AppendSeparator()
        # Csound start/stop
        self._playStopId = wx.NewId()
        self._filemenu.Append(self._playStopId, self._controller._model.isPlaying() and 'Stop Csound\tCTRL-Y' or 'Start Csound\tCTRL-Y')
        idExportToCsd = wx.NewId()
        self._filemenu.Append(idExportToCsd, "&Export to CSD\tCTRL-E",
                              "Export workspace to CSD (Csound Unified File Format)")
        self._filemenu.AppendSeparator()
        # Exit
        self._filemenu.Append(wx.ID_EXIT, "E&xit\tCTRL-Q", "Exit Cabel")
        menubar.Append(self._filemenu, "&File")
        
        # Modules
        self._modulesMenu = self.getModulesMenu(self._controller._getXmlModuleList())
        menubar.Append(self._modulesMenu, "&Modules")
        
        # Options
        self._optionsmenu = wx.Menu()

        # bottom Pane
        # -> properties
        if self.config.getVal(tools.config.View.BOTTOMWINDOW_REMEMBERPROPERTIES):
            showBottomPane = self.config.getVal(tools.config.View.BOTTOMWINDOW_SHOW)
        else:
            showBottomPane = self.config.getDefault(tools.config.View.BOTTOMWINDOW_SHOW)
        # -> menu entry
        self.id_bottomPane = wx.NewId()
        self._optionsmenu.AppendCheckItem(self.id_bottomPane, "Show &Bottom Pane\tALT-X",
                                    "Show Bottom Pane")
        self._optionsmenu.Check(self.id_bottomPane, showBottomPane)
        
        id_refreshMods = wx.NewId()
        self._optionsmenu.Append(id_refreshMods, "&Refresh Module List\tALT-R", "Refresh the Xml-Module List")
        
        self._optionsmenu.AppendSeparator()
        
        # Preferences
        id_options = wx.NewId()
        self._optionsmenu.Append(id_options, "Preferences\tALT-P", "Preferences")
                
        menubar.Append(self._optionsmenu, "&Options")

        self.SetMenuBar(menubar)

        # Associate menu events to handler functions
        self.Bind(wx.EVT_MENU, self._controller.onNew, id = wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self._controller.onOpen, id = wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self._controller.onSave, id = wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self._controller.onSaveAs, id = wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self._controller.onPlayStop, id = self._playStopId)
        self.Bind(wx.EVT_MENU, self._controller.onMenuExportToCsd, id = idExportToCsd)
        self.Bind(wx.EVT_MENU, self._controller.onMenuExit, id = wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.onToggleBottomPane, id = self.id_bottomPane)
        self.Bind(wx.EVT_MENU, self._controller._refreshModulesMenu, id = id_refreshMods)
        self.Bind(wx.EVT_MENU, self._controller.onOptionsOpen, id = id_options)
        self.Bind(wx.EVT_CLOSE, self._controller.onClose)

        # Create Statusbar
        self.statusbar = CabelStatusBar(self)
        self.SetStatusBar(self.statusbar)
        self.SetStatusBarPane(0)
        
        # Create splitted window
        self._splitter = CabelSplitterWindow(self, wx.ID_ANY)
        
        # Add workspace for synth building
        self.workspace = CabelScrolledWindow(self._splitter, -1, self)

        # wxTextCtrl which gets the stdout and stderr output of the app
        self.ioTextCtrl = None

        # Initialize Splitter
        self._splitter.initialize(self.workspace)

        # Associate mouse events to handler functions
        self.workspace.Bind(wx.EVT_LEFT_DOWN, self._controller.onMouseLeftDown)
        self.workspace.Bind(wx.EVT_LEFT_UP, self._controller.onMouseLeftUp)
        self.workspace.Bind(wx.EVT_LEFT_DCLICK, self._controller.onMouseLeftDclick)
        self.workspace.Bind(wx.EVT_RIGHT_DOWN, self._controller.onMouseRightDown)
        self.workspace.Bind(wx.EVT_MIDDLE_DOWN, self._controller.onMouseMiddleDown)
        self.workspace.Bind(wx.EVT_MOTION, self._controller.onMouseMotion)
        self.Bind(wx.EVT_SIZE, self._controller.onSize)

        # Add additional key events
        self.Bind(wx.EVT_KEY_DOWN, self._controller.onKey)

        self.update(None, None)


    def createWorkspace(self, workspaceReader):
        """
        """
        # Open workspace from worksp
        if workspaceReader:
            # Set view modules
            self._modules = workspaceReader.viewModules.values()
            self._modulesDict = workspaceReader.viewModules
            
            # Set connections
            self._connections = []
            for c in workspaceReader.connections:
                outModule = self._modulesDict[c['fromModuleId']]
                inModule = self._modulesDict[c['toModuleId']]
                self._connections.append(ModuleConnection(outModule, \
                                            c['fromVarId'], \
                                            inModule, \
                                            c['toVarId']))
            # Set file location                                
            self.fileName = workspaceReader.fileName
            self.filePath = workspaceReader.filePath
            
        # Delete old workspace and create new one
        else:
            self._modules = []
            self._modulesDict = {}
            self._connections = []
            
            self.fileName = ''
            self._cwFileNewCount += 1
            
            self._controller._actModule = None
        
        self.workspace.Refresh()
        return self            
        

    def update(self, observable, arg):
        """
        This method is called whenever the observed object is
        changed. An application calls an observable object's
        notifyObservers method to have all the object's observers
        notified of the change.

        @type  o: Observable
        @param o: The observable object.
        @type  arg: object
        @param arg: An argument passed to the notifyObservers method.
        """
        # Refresh the workspace?
        refresh = True
        # Read arg gand do what has to be done.
        if arg:
            # model.workspace.addModule;
            # arg[1] module to add
            if arg[0] == 'add':
                newModule = arg[1]
                self.addModule(newModule, self._controller._lastMousePt)
            # model.workspace.removeModule;
            # arg[1] module to remove, arg[2] in- & outgoing connections to remove
            elif arg[0] == 'remove':
                rmModule = arg[1]
                rmConnections = arg[2]
                self.removeModule(rmModule, rmConnections)
            # model.workspace.connect;
            # arg[1] new connection
            elif arg[0] == 'connect':
                newConnection = arg[1]
                self.addConnection(newConnection)
            # model.workspace.disconnect;
            # arg[1] connection to be removed
            elif arg[0] == 'disconnect':
                rmConnections = arg[1]
                self.removeConnection(rmConnections)
            # model.workspace.setValue:
            # arg[1] input variable which changed, arg[2] new value of input var
            elif arg[0] == 'set':
                inVar = arg[1]
                newValue = arg[2]
            # gets triggered by the config.setting.updateView method:
            # arg[1] in view workspace defined method without parameters.
            elif arg[0] == 'funCall':
                self._controller._callFunc(self, arg[1])
            
        # Repaints the workspace
        if refresh:
            self.workspace.Refresh()


    def onToggleBottomPane(self, event):
        """
        Toggle bottom pane in the splitter window.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        if not self.config.getVal(tools.config.View.BOTTOMWINDOW_SHOW):
            self._splitter.split()
        else:
            self._splitter.unSplit()


    def addModule(self, module, pt):
        """
        Adds module to view workspace.

        @type  module: model.module.Module
        @param module: module to add to view workspace
        @type  pt: wx.Point
        @param pt: Position on the workspace of module to add
        """
        # Module is not yet on the view.workspace
        if not self._modulesDict.has_key(module.id):
            viewModule = Module(pt.x, pt.y, module, self._controller)
            # if lastToAddPosition not changes, this helps
            pt.x += 25
            pt.y += 20
            self._modulesDict[module.id] = viewModule
        # Yet it is
        else:
            viewModule = self._modulesDict[module.id]
        # If it is not yet in the internal list of view.Modules
        if viewModule not in self._modules:
            # then add it
            self._modules.append(viewModule)
        # Set added module to actModule
        self._controller.setModuleFocus(viewModule)
        return viewModule


    def removeModule(self, module, connections):
        """
        Removes module from workspace.

        @type  module: model.module.Module
        @param module: module to be removed from view workspace.
        @type  connections: list
        @param connections: list of model.connection.Connection to delete.
        """
        # remove modules connections
        for c in connections:
            self.removeConnection(c)

        # remove module
        if self._modulesDict.has_key(module.id):

            viewModule = self._modulesDict[module.id]
            self._modules.remove(viewModule)

            if self._controller._actModule == viewModule:
                self._controller.setModuleFocus(None)

            del self._modulesDict[module.id]


    def addConnection(self, connection):
        """
        Add connection to view workspace.

        @type  connection: model.connection.Connection
        @param connection: Model connection to add to view workspace.
        """
        outputNum = connection.fromVar.module.outVars.index(connection.fromVar)
        inputNum = connection.toVar.module.inVars.index(connection.toVar)
        newConnection = ModuleConnection(self._modulesDict[connection.fromVar.module.id],
                                         outputNum,
                                         self._modulesDict[connection.toVar.module.id],
                                         inputNum)
        if newConnection not in self._connections:
            self._connections.append(newConnection)


    def removeConnection(self, connection):
        """
        Remove connection from view workspace.

        @type  connection: model.connection.Connection
        @param connection: Connection to remove from view workspace.
        """
        # Create corresponding view connection
        outputNum = connection.fromVar.module.outVars.index(connection.fromVar)
        inputNum = connection.toVar.module.inVars.index(connection.toVar)
        fromModule = connection.fromVar.module
        toModule = connection.toVar.module
        rmConnection = ModuleConnection(self._modulesDict[fromModule.id],
                                        outputNum,
                                        self._modulesDict[toModule.id],
                                        inputNum)
        # If in _connections list remove it
        if rmConnection in self._connections:
            self._connections.remove(rmConnection)


    def getModuleAt(self, pt):
        """
        Return the first module found at given point.

        @type  pt: wx.Point
        @param pt: Point to test if on a module.
        @rtype : view.module.Module
        @return: Module at point or None.
        """
        # Search from last added module to first
        for i in range(len(self._modules) - 1, -1, -1):
            if self._modules[i].isOnModule(pt):
                return self._modules[i]
        return None


    def scrollWorkspaceOnBorder(self, pt):
        """
        If pt is on workspace border scrolls workspace.

        @type  pt: wx.Point
        @param pt: Point to test if on worspace border.
        """
        unitX, unitY = self.workspace.GetScrollPixelsPerUnit()
        sizeX, sizeY = self.workspace.GetClientSize()
        originX, originY = self.workspace.GetViewStart()
        distanceLeft = pt.x - originX * unitX
        distanceRight = originX * unitX + sizeX - pt.x
        distanceTop = pt.y - originY * unitY
        distanceBottom = originY * unitY + sizeY - pt.y
        if distanceLeft < 10:
            self.workspace.Scroll(originX - 1, -1)
        if distanceRight < 10:
            self.workspace.Scroll(originX + 1, -1)
        if distanceTop < 10:
            self.workspace.Scroll(-1, originY - 1)
        if distanceBottom < 10:
            self.workspace.Scroll(-1, originY + 1)


    def getModulesMenu(self, xmlModuleList):
        """
        Gets the Menu for all the defined Xml Modules.

        @type  xmlModuleList: list
        @param xmlModuleList: List of tuples which represents the
                              structure of the modules folder.
        @rtype:  wx.Menu
        @return: Menu
        """
        modulesmenu = wx.Menu()
        for xmlModuleListItem in xmlModuleList:
            newId = wx.NewId()
            if isinstance(xmlModuleListItem[1], list):
                modulesmenu.AppendMenu(newId, xmlModuleListItem[0],
                                       self.getModulesMenu(xmlModuleListItem[1]))
            else:
                self._controller._idToModules[newId] = xmlModuleListItem[1].fullName
                modulesmenu.Append(newId, xmlModuleListItem[0],
                                   xmlModuleListItem[1].description)
                self.Bind(wx.EVT_MENU, self._controller.onModulesMenu, id = newId)

        return modulesmenu


    def getModuleMenu(self):
        """
        Return menu when right clicking on a module.
        """
        modulemenu = wx.Menu()
        
        # "Remove Module" Entry
        delId = wx.NewId()
        modulemenu.Append(delId, 'Remove Module')
        self.Bind(wx.EVT_MENU, self._controller.onRemoveActModule, id = delId)
        
        # "Zoom Module" Entries
        if self.config.getVal(tools.config.View.ZOOM_INDIVIDUAL_ACTIVE):
            # Zoom Entry
            modulemenu.AppendSeparator()        
            # Zoom Entry Ids
            zoomInId = wx.NewId()
            zoomOutId = wx.NewId()
            # Zooms
            zoomDefault = self.config.getVal(tools.config.View.ZOOM_FACTOR_DEFAULT)
            # Scales
            scaleInFactor = scaleOutFactor = zoomDefault / 100
            # Zoom Menu Entries
            modulemenu.Append(zoomInId, 'zoom +' + str(zoomDefault) + '%')
            modulemenu.Append(zoomOutId, 'zoom -' + str(zoomDefault) + '%')
            # Bindings
            self.Bind(wx.EVT_MENU, self._controller.onScaleInActModule, id = zoomInId)
            self.Bind(wx.EVT_MENU, self._controller.onScaleOutActModule, id = zoomOutId)
            
        if self.config.getVal(tools.config.Directories.EDITOR):
            modulemenu.AppendSeparator()
            viewXmlId = wx.NewId()
            modulemenu.Append(viewXmlId, 'Show Module Xml')
            self.Bind(wx.EVT_MENU, self._controller.onShowModuleXML, id = viewXmlId)

        return modulemenu


    def _getRecentMenu(self):
        """
        """
        configDir = self._controller._configDirs
        recentList = []
        recentList = configDir.getVal(tools.config.Directories.RECENTFILES)
        
        recentMenu = wx.Menu()
        
        for i in xrange (0, len(recentList)):
            recentId = wx.NewId()
            recentMenu.Append(recentId, '&' + str(i) + ' ' + str(os.path.normpath(recentList[i])))
            self._controller._idToRecent[recentId] = str(recentList[i])
            self.Bind(wx.EVT_MENU, self._controller.onRecent, id = recentId)
            
        return recentMenu
        
        
    def reloadRecentMenu(self):
        """
        """
        self._filemenu.Remove(self._recentMenuId)
        recentMenu = self._getRecentMenu()
        self._filemenu.InsertMenu(2, self._recentMenuId, 'Open Recent...', recentMenu)
        
        # Depending if there are Items in the RecentMenu Disable / Enable it
        if self._filemenu.IsEnabled(self._recentMenuId):
            if recentMenu.GetMenuItemCount() == 0:
                self._filemenu.Enable(self._recentMenuId, False)
        else:
            if recentMenu.GetMenuItemCount() > 0:
                self._filemenu.Enable(self._recentMenuId, True)
        

    def createDraggedCable(self, startPt, endPt):
        """
        Create connection between startPt and endPt as visual feedback
        for connection mode.

        @type  startPt: wx.Point
        @param startPt: Start point of dragged cable.
        @type  endPt: wx.Point
        @param endPt: End point of dragged cable.
        """
        self._draggedCable = Connection(startPt, endPt)


    def removeDraggedCable(self):
        """
        Remove dragged cable from workspace.
        """
        self._draggedCable = None
        self.workspace.Refresh()


    def getModules(self):
        """
        Return list of view modules.

        @rtype: List
        @return: List of view modules.
        """
        return self._modules


    def getConnections(self):
        """
        Return list of view connections.

        @rtype: List
        @return: List of view connections.
        """
        return self._connections


    def getDraggedCable(self):
        """
        Return dragged cable object.

        @rtype: model.view.connection.Connection
        @return: Visual feedback when connection two modules.
        """
        return self._draggedCable
        
        
    def GetTitle(self):
        """
        Return Title string for the CabelFrame.
        
        @rtype: string
        @return: Title string for the CabelFrame.
        """
        try:
            star = (self._controller._saved and [''] or ['*'])[0]
        except AttributeError:
            # self._controller isn't defined yet
            star = ''
        
        if self.fileName == '':
            documentName = 'new' + str(self._cwFileNewCount) + '.cw'
        else:
            documentName = self.fileName + '.cw'
        
        return 'Cabel - [' + documentName + ']' + star

    
#---------------------------------------------------------------------------


class CabelScrolledWindow(wx.ScrolledWindow):
    """
    CabelScrolledWindow.

    Scrolled window to represent the Cabel GUI workspace for placing
    and connecting modules with double buffered painting.

    @type _WORKSPACE_WIDTH: int
    @cvar _WORKSPACE_WIDTH: Maximal width for this scrolled window.
    @type _WORKSPACE_HEIGHT: int
    @cvar _WORKSPACE_HEIGHT: Maximal height for this scrolled window.
    @type _BACKGROUND_COLOUR: wx.Colour
    @cvar _BACKGROUND_COLOUR: Default background colour for this scrolled window.
    @type _view: view.workspace.CabelFrame
    @ivar _view: Corresponding view.
    """

    _WORKSPACE_WIDTH = 3000
    _WORKSPACE_HEIGHT = 3000


    def __init__(self, parent, id, view):
        """
        Standard constuctor.

        @type  parent: wx.Object
        @param parent: Parent of this scrolled window.
        @type  id: int
        @param id: ID of this scrolled window.
        @type  view: view.workspace.CabelFrame
        @param view: Corresponding view.
        """
        wx.ScrolledWindow.__init__(self, parent, id)
        self._view = view
        self.SetBackgroundColour(self._view.config.getVal(tools.config.View.BACKGROUNDCOLOUR))
        self.EnableScrolling(True, True)
        self.SetScrollbars(20, 20, self._view.config.getVal(tools.config.View.WORKSPACEWIDTH) / 20,
                           self._view.config.getVal(tools.config.View.WORKSPACEHEIGHT) / 20)

        # Bind events for double buffered painting
        self.Bind(wx.EVT_PAINT, self._onPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self._onEraseBackground)


    def GetBackgroundColour(self):
        """
        Overwrites wx.ScrolledWindow.GetBackgroundColour() with the in config.xml
        defined Colour.
        
        @rtype: wx.Colour
        @return: Background colour for workspace.
        """
        return self._view.config.getVal(tools.config.View.BACKGROUNDCOLOUR)


    def _onPaint(self, event):
        """
        Respond to repaint request.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        width, height = self.GetClientSizeTuple()
        bitmap = wx.EmptyBitmap(width, height) # Buffer bitmap
        memdc = wx.MemoryDC()
        memdc.SelectObject(bitmap)

        memdc.BeginDrawing()

        memdc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        memdc.Clear()     # Clear the bitmap

        originX, originY = self.GetViewStart()
        unitX, unitY = self.GetScrollPixelsPerUnit()
        originX, originY = originX * unitX, originY * unitY

        for module in self._view.getModules():
            module.drawRelative(memdc, wx.Point(originX, originY))
        for connection in self._view.getConnections():
            connection.drawRelative(memdc, wx.Point(originX, originY), self._view.zoom)
        if self._view.getDraggedCable():
            self._view.getDraggedCable().drawRelative(memdc,
                                                      wx.Point(originX, originY), self._view.zoom)
        self._view.SetTitle(self._view.GetTitle())
        
        memdc.EndDrawing()

        wx.PaintDC(self).Blit(0, 0, width, height, memdc, 0, 0)


    def _onEraseBackground(self, event):
        """
        Don't alter the background.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        pass


#---------------------------------------------------------------------------


class CabelSplitterWindow(wx.SplitterWindow):
    """
    CabelSplitterWindow.

    Horizontal splitter window which expands its top window when resized.

    @type _bottomWindowHeight: int
    @ivar _bottomWindowHeight: Height in pixels for bottom window.
    @type _parent: view.workspace.CabelFrame
    @ivar _parent: CabelFrame as parent window of CabelSplitterWindow.
    @type _topPane: wx.ScrolledWindow
    @ivar _topPane: Top Frame of SplitteredWindow. Set after initialize call, before that it is None.
    @type _bottomPane: wx.Notebook
    @ivar _bottomPane: Bottom Frame of SplitteredWindow. Set after initialize call, before that it is None.
    """

    # Maximum height of bottom Window
    MAX_HEIGHT_RELATIVE = 0.75
    

    def __init__(self, parent, id):
        """
        Standard constructor.

        @type  parent: view.workspace.CabelFrame
        @param parent: Parent of this splitter window.
        @type  id: int
        @param id: ID of this splitter window.
        @type  bottomWindowSize: int
        @param bottomWindowSize: Size of bottom window in pixels.
        """
        wx.SplitterWindow.__init__(self, parent, id, style = wx.SP_ARROW_KEYS)
        
        # view CabelFrame
        self._parent = parent
        # The 2 Panes
        self._topPane = None
        self._bottomPane = None

        # Bottom Height
        self._bottomWindowHeight = 0
        
        # Frame ClientSize
        self._parentClientSize = 0
        
        # Bindings
        # If the Position of the sash is changing / has changed
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self._onSashChanging)
        self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self._onSashChanged)
        self.Bind(wx.EVT_SPLITTER_DOUBLECLICKED, self._onDblClick)


    def initialize(self, topPane):
        """
        Inizialize Splitter.
        Decide wether to show both (top and bottom) panes, or only the first one.
        
        @type  topPane: wx.Pane
        @param topPane: The top pane.
        """
        # Initialize Panes
        self._topPane = topPane
        #self._bottomPane = bottomPane
        
        # Split or Unsplit?
        if self._parent.config.getVal(tools.config.View.BOTTOMWINDOW_REMEMBERPROPERTIES):
            split = self._parent.config.getVal(tools.config.View.BOTTOMWINDOW_SHOW)
            self._bottomWindowHeight = self._parent.config.getVal(tools.config.View.BOTTOMWINDOW_HEIGHT)
        else:
            split = self._parent.config.getDefault(tools.config.View.BOTTOMWINDOW_SHOW)
            self._bottomWindowHeight = self._parent.config.getVal(tools.config.View.BOTTOMWINDOW_HEIGHT)
        
        # get frame clientSize
        self._parentClientSize = self._parent.GetClientSize()
        
        # set bottomWindow size
        self._bottomPane = CabelBottomWindow(self,
                                             (self._parentClientSize.width,
                                              self.getBottomWindowHeight() \
                                              - self.GetSashSize()))
        #self._bottomPane.SetSize((self._parentClientSize.width, self.getBottomWindowHeight()))
        
        # split or only initialize?
        if split:
            self.split()
        else:
            self._bottomPane.Hide()
            self.Initialize(self._topPane)
            self._topPane.Show(True)
            self.UpdateSize() # Fix Linux bug
            self._topPane.SetFocus()
        
        # Bindings
        # If the CabelApp Window's size changed
        self.Bind(wx.EVT_SIZE, self._onSize)
        

    def getBottomWindowHeight(self):
        """
        Return height of bottom window in pixels.

        @rtype: int
        @return: Size of bottom window.
        """
        allowedHeight = self._bottomWindowHeightNotAllowed(self._bottomWindowHeight)
        if allowedHeight:
            if allowedHeight <= 40:
                self._bottomWindowHeight = 40
            else:
                self._bottomWindowHeight = allowedHeight
                
        return self._bottomWindowHeight
        
        
    def setBottomWindowHeight(self, height):
        """
        Set the height of the Bottom Window and 
        unsplit if new bottomWindowHeight is <= 10
        
        @type height: int
        @param height: Height of the bottom window.
        """
        # Is height allowed?
        allowedHeight = self._bottomWindowHeightNotAllowed(height)
        if allowedHeight:
            if allowedHeight <= 40:
                self.unSplit()
            else:
                self._bottomWindowHeight = allowedHeight
        else:
            self._bottomWindowHeight = height            
        
        # Save height
        if self.IsSplit():
            if self._parent.config.getVal(tools.config.View.BOTTOMWINDOW_REMEMBERPROPERTIES):
                self._parent.config.setVal(tools.config.View.BOTTOMWINDOW_HEIGHT,
                                           self._bottomWindowHeight)


    def split(self):
        """
        Split top and bottom pane of splitter window.
        Sets the config.xml Var and checks the options-menubar entry
        """
        if not self.IsSplit():
            self._topPane.Show(True)
            self._bottomPane.Show(True)
            self.SplitHorizontally(self._topPane, self._bottomPane,
                                   - self.getBottomWindowHeight())
            self._parent.config.setVal(tools.config.View.BOTTOMWINDOW_SHOW, True)
            self._parent._optionsmenu.Check(self._parent.id_bottomPane, True)
            self._bottomPane.SetFocus()


    def unSplit(self):
        """
        Unsplit. Only self._topPane visible.
        Sets the config.xml Var and unchecks the options-menubar entry
        """
        if self.IsSplit():
            self._bottomPane.Hide()
            self.Unsplit(self._bottomPane)
            self._parent.config.setVal(tools.config.View.BOTTOMWINDOW_SHOW, False)
            self._parent._optionsmenu.Check(self._parent.id_bottomPane, False)
            self._topPane.SetFocus()
        

    def _bottomWindowHeightNotAllowed(self, height):
        """
        Check if height is Not allowed.
        
        @rtype: int
        @return: 0 if bottom window height is allowed, else the allowed height.
        """
        maxHeight= int(self._parent.GetClientSize().GetHeight() \
                       * CabelSplitterWindow.MAX_HEIGHT_RELATIVE)
        if height > maxHeight:
            return maxHeight
        elif height < 40:
            return 39
        else:
            return 0
        
        
    def _onSashChanging(self, event):
        """
        React on the Event Sash Position changing.
        Prevents closing of workspace (self._topPane).

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        frameHeight = self._parent.GetClientSize().height
        allowedHeight = self._bottomWindowHeightNotAllowed(frameHeight \
                                                           - event.GetSashPosition())
        if allowedHeight:
            event.SetSashPosition(frameHeight - allowedHeight)
            event.Skip(False)      


    def _onSashChanged(self, event):
        """
        React on the Event Sash Position has changed.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        sashPos = event.GetSashPosition()
        frameHeight = self._parent.GetClientSize().height
        self.setBottomWindowHeight(frameHeight - sashPos)
        self.SetSashPosition(frameHeight - self.getBottomWindowHeight(), False)
        
        
    def _onDblClick(self, event):
        """
        """
        self.unSplit()
        
        
    def _onSize(self, event):
        """
        """
        self._reposition(event)
        
        
    def _reposition(self, event):
        """
        """
        old_csz = self._parentClientSize
        if not old_csz == self._parent.GetClientSize():
            if self.getBottomWindowHeight() > 9:
                self._parentClientSize = self._parent.GetClientSize()
                old_height = self.getBottomWindowHeight()
                old_relativeheight = float(old_csz.height) / float(old_height)
                new_height = int(self._parentClientSize.height / old_relativeheight)
                                
                self.setBottomWindowHeight(new_height)
                self.SetSashPosition(self._parentClientSize.height \
                                     - self.getBottomWindowHeight(), False)                
        
#---------------------------------------------------------------------------


class CabelIOTextCtrl(wx.TextCtrl, Observer):
    """
    CabelIOTextCtrl.
    
    TextControl to which all the stderr/stdout messages will be written.
    
    @type loggingConfig: tools.config.Directories
    @ivar loggingConfig: The directory category of config.xml in which the logging properties are saved.
    @type log: File
    @ivar log: The logging file to which the logging messages are written or Null.
    @type loggingOn: boolean
    @ivar loggingOn: State of logging.
    @type loggingPath: string
    @ivat loggingPath: Logging directory.
    @type controller: view.controller.CabelController
    @ivar controller: Cabel controller with link to the instances of model/view.workspace.
    """
    
    
    def __init__(self, parent, controller):
        """
        Standardconstructor.
        
        @type parent: wx.Panel
        @param parent: Parent on which the textControl should be put on.
        @type controller: view.controller.CabelController
        @param controller: Cabel controller with link to the instances of model/view.workspace.
        """
        wx.TextCtrl.__init__(self, parent, wx.NewId(), style = \
                             wx.NO_BORDER | wx.TE_AUTO_SCROLL | wx.TE_AUTO_URL \
                             | wx.TE_MULTILINE | wx.TE_READONLY)
        self.loggingConfig = controller._model.config.directories
        self.controller = controller
        self.controller._model.addObserver(self)
        self.log = None
        self.loggingOn = self.loggingConfig.getVal(tools.config.Directories.LOGGING_ON)
        self.loggingPath = self.loggingConfig.getVal(tools.config.Directories.LOGGING_DIR)
        
        
    def write(self, txt):
        """
        Write given text to the TextControl and to a logging file, if logging is set on.
        
        @type txt: string
        @param txt: Text to be written.
        """
        # Write message to the TextControl
        self.WriteText(txt)
        # If logging is on, write it aswell to a logfile with timestamp
        if self.loggingConfig.getVal(tools.config.Directories.LOGGING_ON):
            if self.log == None:
                # logPath
                logPath = self.loggingConfig.getVal(tools.config.Directories.LOGGING_DIR)
                if not(os.path.exists(logPath)):
                    os.makedirs(logPath)
                # logFile
                import time
                logfileName = os.path.join(logPath, 'log ' + time.strftime('%Y%m%d_%H-%M-%S') + '.txt')
                self.log = open(logfileName, 'w')
                
            self.log.write(txt)
            self.log.flush()
            
            
    def update(self, observable, arg):
        """
        This method is called whenever the observed object is
        changed. An application calls an observable object's
        notifyObservers method to have all the object's observers
        notified of the change.

        @type  o: Observable
        @param o: The observable object.
        @type  arg: object
        @param arg: An argument passed to the notifyObservers method.
        """
        if arg[0] == 'funCall':
            self.controller._callFunc(self, arg[1])
            
            
    def _updateLogging(self):
        """
        Check if logging properties have changed and set the CabelIOTextCtrl properties if it is so.
        """
        logpath = self.loggingConfig.getVal(tools.config.Directories.LOGGING_DIR)
        # Check wether loggingOn Value changed
        if self.loggingOn != self.loggingConfig.getVal(tools.config.Directories.LOGGING_ON):
            self.loggingOn = self.loggingConfig.getVal(tools.config.Directories.LOGGING_ON)
            print ('Logging properties changed: Logging just switched ' + (self.loggingOn and 'on' or 'off') + '!')
        
        # Check wether the logfile path changed
        if self.loggingPath != logpath:
            self.loggingPath = logpath            
            print ('Logging properties changed: New path for logfiles: ' + logpath)
            if self.log != None:
                self.log.close()
                self.log = None
        
        
#---------------------------------------------------------------------------


class CabelBottomWindow(wx.Notebook):
    """
    Cabel's bootom area.
    """
    
    def __init__(self, parent, size):
        """
        Standardconstructor.
        
        @type parent: view.workspace.CabelSplitterWindow
        @param parent: Parent frame.
        @type size: wx.Size
        @param size: The initial size of the bottom window pane
        """
        self.parent = parent
        self.config = parent._parent.config
        wx.Notebook.__init__(self, parent, -1, style = wx.NB_TOP, size = size)
        
        shell1 = self._getShellPane()
        self.AddPage(shell1, 'Python Shell')
        
        messages = self._getIOTextCtrl()
        self.AddPage(messages, 'Messages')
        
        self.SetSelection(self.config.getEnumIndex(tools.config.View.BOTTOMWINDOW_ACTIVEPAGE))
        
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged)
        
               
    def _getIOTextCtrl(self):
        """
        Creates a CabelIOTextCtrl, sets it as the stdout and stderr
        of the calling app and fits it in a Panel...
        
        @rtype: wx.Panel
        @return: Returns a TextCtrl connected to the stdout/stderr streams.
        """
        p = wx.Panel(self, -1)
        txtctrl = CabelIOTextCtrl(p, self.parent._parent._controller)
        p = self.__getNotebookPanel(p, txtctrl)
        sys.stdout = sys.stderr = txtctrl
        self.parent._parent._controller.setIoTextCtrl(txtctrl)
        return p
        

    def _getShellPane(self):
        """
        Creates a Python shell and fits it in a Panel..
        
        @rtype: wx.Panel
        @return: Interactive Python Shell Panel.
        """
        p = wx.Panel(self, -1)
        shell = wx.py.shell.Shell(p, wx.NewId(), style = wx.NO_BORDER)
        return self.__getNotebookPanel(p, shell)


    def __getNotebookPanel(self, panel, window):
        """
        Creates a Panel and a sizer for the given window
        
        @type panel: wx.Panel
        @param panel: The Panel to manipulate.
        @type window: wx.Window
        @param window: Tindow to fit in Panel for the wx.Notebook.
        @rtype: wx.Panel
        @return: The Panel fitted for integration in the CabelBottomWindow.
        """
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizer.Add(window, 1, wx.GROW)
        panel.SetSizer(panelSizer)
        panel.win = window
        return panel


    def onPageChanged(self, event):
        """
        Save actual Page.
        """
        pageIndex = event.GetSelection()
        self.config.setEnumIndex(tools.config.View.BOTTOMWINDOW_ACTIVEPAGE, pageIndex)
        event.Skip(True)
        
        
#---------------------------------------------------------------------------


class CabelStatusBar(wx.StatusBar, Observer):
    """
    Cabel's own StatusBar.
    
    @type workspace: view.workspace.CabelFrame
    @ivar workspace: View workspace.
    """

    def __init__(self, parent):
        """
        Standardconstructor.
        
        @type parent: view.workspace.CabelFrame
        @param parent: Parent frame.
        """
        wx.StatusBar.__init__(self, parent, -1)
        Observer.__init__(self)
        
        # Config Vars Csound
        self.config = parent._controller._model.config.csound
        
        # View workspace
        self.workspace = parent
        self.workspace._controller._model.addObserver(self)
        
        # Number of Fields and it's widths
        self.SetFieldsCount(4)
        self.SetStatusWidths([-3, 80, 60, 115])

        self.Bind(wx.EVT_SIZE, self.onSize)
        
        #play button
        self.playBmp = wx.Bitmap(os.path.join(os.getcwd(), 'stuff', 'play.jpg'), wx.BITMAP_TYPE_JPEG)
        playMask = wx.Mask(self.playBmp, wx.LIGHT_GREY)
        self.stopBmp = wx.Bitmap(os.path.join(os.getcwd(), 'stuff', 'stop.jpg'), wx.BITMAP_TYPE_JPEG)
        stopMask = wx.Mask(self.stopBmp, wx.LIGHT_GREY)
        
        self.playBmp.SetMask(playMask)
        self.stopBmp.SetMask(stopMask)
        
        self.playBtn = wx.BitmapButton(self, wx.NewId(), self.playBmp)
        self.playBtn.SetToolTipString("Start Csound. [CTRL-Y]")
        self.Bind(wx.EVT_BUTTON, self.onPlayStopButton, self.playBtn)
        
        #autoplay checkbox
        self.autoplayCb = wx.CheckBox(self, wx.NewId(), "autoplay")
        self.Bind(wx.EVT_CHECKBOX, self.onAutoplayCheckBox, self.autoplayCb)
        self.autoplayCb.SetValue(self.config.getVal(tools.config.Csound.AUTOPLAY))
        
        #zoom combobox
        self.zoomTxtCtrl = wx.TextCtrl(self, wx.NewId(), str(self.workspace.zoom) + ' %', style = wx.TE_PROCESS_ENTER|wx.TE_RIGHT)
        self.zoomTxtCtrl.SetToolTipString("Zoom the Modules on the Workspace.")
        self.Bind(wx.EVT_TEXT_ENTER, self.onZoomEntered, self.zoomTxtCtrl)
        
        self._reposition()
        
        self._play = False
        
    
    def _reposition(self):
        """
        Reposition the button within the statusbar.
        """
        rect = self.GetFieldRect(3)
        # Reposition Button
        btnPosX = rect.x + rect.width - (self.playBmp.GetWidth() + 4)
        self.playBtn.SetPosition((btnPosX, rect.y + 2))
        self.playBtn.SetSize((self.playBmp.GetWidth() + 2, rect.height - 4))
        # Reposition Checkbox
        self.autoplayCb.SetPosition((rect.x + 2, rect.y + 2))
        self.autoplayCb.SetSize((rect.width - (self.playBmp.GetWidth() + 4), rect.height - 4))
        # Reposition Zoom TextControl
        rect2 = self.GetFieldRect(2)
        self.zoomTxtCtrl.SetPosition(wx.Point(rect2.x + 5, rect2.y + 2))
        zoomWidth = (50 > rect2.width and [rect2.width -10] or [50])[0]
        self.zoomTxtCtrl.SetSize(wx.Size(zoomWidth, rect2.height - 4))

    
    def onPlayStopButton(self, event):
        if self._play:
            self.workspace._controller._model.stop()
        else:
            self.workspace._controller._model.play()
    
    
    def onAutoplayCheckBox(self, event):
        cbValue = self.autoplayCb.GetValue()
        self.config.setVal(tools.config.Csound.AUTOPLAY, cbValue)
    
    
    def onSize(self, event):
        self._reposition()
    
    
    def onZoomEntered(self, event):
        """
        """
        zoom = self.zoomTxtCtrl.GetValue()
        pi = zoom.find('%')
        if pi >= 0:
            zoom = zoom[:pi]
        zoom = zoom.strip()
        if zoom.isdigit():
            self.workspace._controller.zoom(int(zoom))
        self.zoomTxtCtrl.SetValue(str(self.workspace.zoom) + ' %')       
            
    
    def update(self, observable, arg):
        if arg:
            if arg[0] == 'play':
                self._play = True
                self.playBtn.SetBitmapLabel(self.stopBmp)
                self.playBtn.SetToolTipString("Stop playing. [CTRL-Y]")
                self.workspace._controller._refreshPlayStopMenuEntry()
            elif arg[0] == 'stop':
                self._play = False
                self.playBtn.SetBitmapLabel(self.playBmp)
                self.playBtn.SetToolTipString("Start Csound. [CTRL-Y]")
                self.workspace._controller._refreshPlayStopMenuEntry()
            elif arg[0] == 'funCall':
                # gets triggered by the config.setting.updateView method:
                # arg[1] in view workspace defined method without parameters.
                self.workspace._controller._callFunc(self, arg[1])

                
    def _updateAutoplayCb(self):
        """
        """
        self.autoplayCb.SetValue(self.config.getVal(tools.config.Csound.AUTOPLAY))
        self.autoplayCb.Refresh()
