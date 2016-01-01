import wx
import wx.py.shell
import os
from view.module import Module
from view.connection import ModuleConnection
from view.connection import Connection
from view.valueframe import CabelValueFrame
from model.observer import Observer
from model.xmlReader import XmlModuleReader
from model.xmlReader import XmlWorkspaceReader
from model.xmlGenerator import XmlGenerator
from model.workspace import ConnectionError
import tools.config
from view.configurator import CabelConfigDialog


class CabelController(Observer):
    """
    CabelController.

    Controller and event handling for CabelFrame.

    @type _model: model.workspace.Workspace
    @ivar _model: Corresponding model for this controller.
    @type _view: view.workspace.CabelFrame
    @ivar _view: Corresponding view for this controller.
    @type _actModule: view.module.Module
    @ivar _actModule: Last touched module.
    @type _lastMousePt: wx.Point
    @ivar _lastMousePt: Last position of mouse pointer.
    @type _lastMousePt: wx.Point
    @ivar _lastMousePt: Last position of mouse pointer.
    @type _lastMouseWorkspaceDragPt: wx.Point
    @ivar _lastMouseWorkspaceDragPt: Point of mouse when starting to drag workspace.
    @type _connectOutput: int
    @ivar _connectOutput: If in "connection mode" index of module output, else -1.
    @type _idToModules: dict
    @ivar _idToModules: Dictionary to get view modules by wx.id of the modules menu.
    @type _idToRecent: dict
    @ivar _idToRecent: Dictionary to get recent Cabel workspace file by its wx.id recent menu entry.
    @type _configDirs: tools.config.Config.Directories
    @ivar _configDirs: relevant config Params
    @type _openValueFrames: list
    @ivar _openValueFrames: List of opened valueframes.
    @type _saved: bool
    @ivar _saved: Flag, if this patch is unchanged and saved.
    """

    def __init__(self, model, view):
        """
        Standard constructor.

        @type  model: model.workspace.Workspace
        @param model: Corresponding model for this controller.
        @type  view: view.workspace.CabelFrame
        @param view: Corresponding view for this controller.
        """
        Observer.__init__(self)
        
        self._configDirs = model.config.directories
        
        self._model = model
        self._view = view
        
        # Add controller and view to observers of model
        self._model.addObserver(self)
        self._model.addObserver(view)

        # Diverse help variables
        self._actModule = None             # Actual module
        self._lastMousePt = wx.Point()     # Last position of mouse on workspace
                                           # saved for move modules
        self._lastMouseWorkspaceDragPt = wx.Point()  # Last position of mouse when starting to drag with middle button
        self._connectOutput = -1           # Output number of module while
                                           # dragging a cable
        self._idToModules = {}             # Remeber corresponding module name to id in popup
        self._idToRecent = {}              # Remeber corresponding Cabel workspace file.
        self._openValueFrames = []

        self._saved = True                 # Set empty workspace as saved


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
            self._callFunc(self, arg[1])

        if arg[0] != "play" and arg[0] != "stop" and arg[0] != 'funCall':
            self._saved = False


    def onKey(self, event):
        """
        Respond to key events.

        @type  event: wx.Event
        @param event: Event associated with this function.        
        """
        # Focus zoom factor for CTRL-Z
        if event.ControlDown() and event.GetKeyCode() == ord('Z'):
            self._view.statusbar.zoomTxtCtrl.SetFocus()
    

    def onMenuExit(self, event):
        """
        Respond to the "Exit" menu command.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        # Close Window
        self._view.Close()


    def onMenuExportToCsd(self, event):
        """
        Respond to "Export to CSD" menu command.

        @type  event: wx.Event
        @param event: Event associated with this function.        
        """
        fileDlg = wx.FileDialog(self._view,
                                defaultDir=self._view.filePath,
                                defaultFile=self._view.fileName + ".csd",
                                wildcard="Csound Unified File (*.csd)|*.csd",
                                style=wx.SAVE|wx.OVERWRITE_PROMPT)
        if fileDlg.ShowModal() == wx.ID_OK:
            fileName = fileDlg.GetPath()
            self._model._csoundGenerator.exportToCsd(fileName)
        fileDlg.Destroy()


    def onClose(self, event):
        """
        Respond to the Frame close event.
        
        @type  event:
        @param event:
        """
        if self._askSave(event):
            # Stop csound
            self._model.stop()
        
            # Remove observers
            self._model.removeObserver(self)
            self._model.removeObserver(self._view)
        
            # Save FrameSize
            frameSize = self._view.GetSize()
            self._model.config.view.setVal(tools.config.View.FRAMEHEIGHT, frameSize.height)
            self._model.config.view.setVal(tools.config.View.FRAMEWIDTH, frameSize.width)
            # Destroy the frame
            self._view.Destroy()


    def onNew(self, event):
        """
        Respond to the "New" menu command.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        if self._askSave(event):
            self._opening = True
            self._createWorkspace()
            self._saved = True # Set empty workspace as saved
        
        
    def onOpen(self, event):
        """
        Respond to the "Open" menu command.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        if self._askSave(event):
            fileDialog = wx.FileDialog(self._view, \
                                       defaultDir = self._view.filePath, \
                                       defaultFile = self._view.fileName + '.cw', \
                                       wildcard = 'Cabel Workspace Files (*.cw)|*.cw', \
                                       style = wx.OPEN | wx.FILE_MUST_EXIST)
            if fileDialog.ShowModal() == wx.ID_OK:
                fileLocation = fileDialog.GetPath()
                self._createWorkspace(fileLocation)
                self._saved = True
            
    
    def onRecent(self, event):
        """
        Open file from recent open files menu.

        @type  event: wx.Event
        @param event: Event associated with this function.        
        """
        if self._askSave(event):
            path = self._idToRecent[event.GetId()]
            self._createWorkspace(path)
            self._saved = True
    
    
    def onSave(self, event):
        """
        Respond to the "Save" menu command.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        if self._view.fileName == '':
            self.onSaveAs(event)
        else:
            fileLocation = os.path.join(self._view.filePath, self._view.fileName + '.cw')
            generator = XmlGenerator(fileLocation)
            erg = generator.writeWorkspace(self._view)
            self._saved = erg[0]
            if not self._saved:
                d = wx.MessageDialog(self._view, 
                                 "Error while writing File " + fileLocation + ".\n\nException text:\n" + str(erg[1]),
                                 "Writing Error",
                                 wx.OK | wx.ICON_ERROR)
                d.ShowModal()
                d.Destroy()
    
    
    def onSaveAs(self, event):
        """
        Respond to the "Save As" menu command.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        fileDialog = wx.FileDialog(self._view,
                                   defaultDir=self._view.filePath,
                                   defaultFile=self._view.fileName + '.cw',
                                   wildcard='Cabel Workspace Files (*.cw)|*.cw',
                                   style=wx.SAVE|wx.OVERWRITE_PROMPT)
        if fileDialog.ShowModal() == wx.ID_OK:
            fileLocation = fileDialog.GetPath()
            generator = XmlGenerator(fileLocation)
            erg = generator.writeWorkspace(self._view)
            if erg[0]:
                self._saved = True
                self._pushToRecentFiles(fileLocation)
            else:
                d = wx.MessageDialog(self._view, 
                                 "Error while writing File " + fileLocation + ".\n\nException text:\n" + str(erg[1]),
                                 "Writing Error",
                                 wx.OK | wx.ICON_ERROR)
                d.ShowModal()
                d.Destroy()
        fileDialog.Destroy()


    def onMouseLeftDown(self, event):
        """
        Respond to left mouse button down on workspace.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        mousePt = self._getEventCoordinates(event)
        self.setModuleFocus(self._view.getModuleAt(mousePt))

        # Mouse is on module
        if self._actModule:
            self._connectOutput = self._actModule.isOnOutput(mousePt)


    def onMouseLeftDclick(self, event):
        """
        Respond to left mouse button double click on workspace.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        mousePt = self._getEventCoordinates(event)
        self.setModuleFocus(self._view.getModuleAt(mousePt))

        # Mouse is on module show value edit frame
        if self._actModule:
            if len(self._actModule.module.inVars) > 0:
                f = CabelValueFrame(self._actModule.module, self._view.workspace,
                                    self._model, self, (event.GetX(), event.GetY()))
                self._openValueFrames.append(f)
                f.Show()


    def onMouseRightDown(self, event):
        """
        Respond to right mouse button down on workspace.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        mousePt = self._getEventCoordinates(event)
        self.setModuleFocus(self._view.getModuleAt(mousePt))

        # Test if mouse is on module
        if self._actModule:
            # Create on-module-contextmenu
            modulemenu = self._view.getModuleMenu()
            
            # Popup on-module-contextmenu
            self._view.PopupMenu(modulemenu, wx.Point(event.GetX(), event.GetY()))
        else:
            # Show modules popup menu at point relative to workspace origin
            self._view.PopupMenu(self._view._modulesMenu,
                                 wx.Point(event.GetX(), event.GetY()))


    def onMouseMotion(self, event):
        """
        Respond to mouse motion on workspace.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        mousePt = self._getEventCoordinates(event)
        if event.LeftIsDown():

            # If in "connection mode" create visual feedback for connection
            if self._connectOutput > -1:
                startPt = self._actModule.getOutput(self._connectOutput)
                self._view.createDraggedCable(startPt, mousePt)
                self._view.workspace.Refresh()

            # Disconnect or move a module
            if self._actModule and not self._connectOutput > -1:
                inputNum = self._actModule.isOnInput(mousePt)

                # Is on input and there's a connection to input
                if inputNum > -1 \
                       and self._actModule.module.inVars[inputNum].connection:
                    # Disconnect and show dragged cable
                    connection = self._actModule.module.inVars[inputNum].connection
                    fromVar = connection.fromVar
                    outputNum = fromVar.module.outVars.index(fromVar)
                    self._connectOutput = outputNum
                    self._actModule = self._view._modulesDict[fromVar.module.id]
                    startPt = self._actModule.getOutput(outputNum)

                    self._model.disconnect(connection)
                    self._view.createDraggedCable(startPt, mousePt)

                else:
                    # Move module
                    moveVecPt = mousePt - self._lastMousePt
                    self._actModule.setRelativePosition(moveVecPt)
                    self._saved = False

                self._view.workspace.Refresh()

            # If on workspace border move scroll workspace
            self._view.scrollWorkspaceOnBorder(mousePt)

        # Over Module
        module = self._view.getModuleAt(mousePt)
        if module:
            # Show Module description in Statusbar
            self._view.SetStatusText(module.getName() + ': ' \
                                     + module.module.description, 0)

            # Show module instrument number in Statusbar
            instrNum = self._model.instruments.index(module.module.instrument) + 1
            self._view.SetStatusText("instr " + str(instrNum), 1)

            # Over output
            output = module.isOnOutput(mousePt)
            input = module.isOnInput(mousePt)

            if output > -1:
                # Change cursor to hand if over output and not in connection mode
                if self._connectOutput == -1:
                    self._view.workspace.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

                # Show output description in Statusbar
                outVar = module.getOutVar(output)
                self._view.SetStatusText(outVar.name + ': ' \
                                         + outVar.description, 0)
            elif input > -1:
                # Change cursor to hand if in connection mode
                if self._connectOutput > -1 \
                       or module.module.inVars[input].connection:
                    self._view.workspace.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

                # Show input description in Statusbar
                inVar = module.getInVar(input)
                range = ' [' + str(inVar.min) + ', ' + str(inVar.max) + ']'
                if inVar.connection:
                    inVarName = inVar.name + ': '
                else:
                    inVarName = inVar.name + ' = ' + str(inVar.value) + ':  '
                inVarDescription = inVarName + inVar.description + range
                self._view.SetStatusText(inVarDescription, 0)
            else:
                self._view.workspace.SetCursor(wx.STANDARD_CURSOR)
        else: # Not on module
            # Change cursor to standard cursor
            self._view.workspace.SetCursor(wx.STANDARD_CURSOR)
            self._view.SetStatusText('', 0)

            # Clear instrument number in statusbar
            self._view.SetStatusText("", 1)

        # Drag workspace with middle keys
        if event.MiddleIsDown():            
            originX, originY = self._view.workspace.GetViewStart()
            unitX, unitY = self._view.workspace.GetScrollPixelsPerUnit()
            moveVecPt = wx.Point(event.GetX() - self._lastMouseWorkspaceDragPt.x,
                                 event.GetY() - self._lastMouseWorkspaceDragPt.y)
            if moveVecPt.x >= unitX:
                self._view.workspace.Scroll(originX - 1, -1)
                self._lastMouseWorkspaceDragPt = wx.Point(event.GetX(), event.GetY())
            elif moveVecPt.x <= -unitX:
                self._view.workspace.Scroll(originX + 1, -1)
                self._lastMouseWorkspaceDragPt = wx.Point(event.GetX(), event.GetY())
            if moveVecPt.y >= unitY:
                self._view.workspace.Scroll(-1, originY - 1)
                self._lastMouseWorkspaceDragPt = wx.Point(event.GetX(), event.GetY())
            elif moveVecPt.y <= -unitY:
                self._view.workspace.Scroll(-1, originY + 1)
                self._lastMouseWorkspaceDragPt = wx.Point(event.GetX(), event.GetY())

        self._lastMousePt = mousePt


    def onMouseMiddleDown(self, event):
        """
        Respond to middle mouse button down on workspace.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        self._lastMouseWorkspaceDragPt = wx.Point(event.GetX(), event.GetY())


    def onMouseLeftUp(self, event):
        """
        Respond to left mouse button up on workspace.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        # Connect two modules?
        if self._connectOutput > -1:
            inModule = self._view.getModuleAt(self._lastMousePt)
            if inModule:
                connectInput = inModule.isOnInput(self._lastMousePt)
                if connectInput > -1: # Mouse is on Input
                    try:
                        self._model.connect(self._actModule.module.outVars[self._connectOutput],
                                            inModule.module.inVars[connectInput])
                    except ConnectionError, txt:
                        d = wx.MessageDialog(self._view, str(txt), "Connection error",
                                             wx.OK | wx.ICON_ERROR)
                        d.ShowModal()
                        d.Destroy()

            # Reset connection mode
            self._connectOutput = -1
            self._view.removeDraggedCable()
            self._view.workspace.SetCursor(wx.STANDARD_CURSOR)
            self._view.workspace.Refresh()


    def onModulesMenu(self, event):
        """
        Listener for the Module menu.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        moduleName = self._idToModules[event.GetId()]
        module = self._model.addXmlModule(moduleName)


    def onRemoveActModule(self, event):
        """
        Remove a module. If VIEW_MODULEDELETEWARNING is enabled ask
        before removing.

        @type  event: wx.Event
        @param event: Event associated with this function.
        """
        # Get corresponding open valueframes for actmodule
        deleteValueFrames = []
        for f in self._openValueFrames:
            if f._module == self._actModule.module:
                deleteValueFrames.append(f)

        # Ask if we should delete this module
        if self._view.config.getVal(tools.config.View.MODULEDELETEWARNING):
            shureDialog = wx.MessageDialog(self._view,
                                           'Delete module ' \
                                           + self._actModule.getName() \
                                           + ' (ID: ' + str(self._actModule.module.id) + ')?',
                                           'Delete',
                                           wx.YES_NO | wx.ICON_QUESTION)
            if shureDialog.ShowModal() == wx.ID_YES:
                self._model.removeModule(self._actModule.module)
            shureDialog.Destroy()
        else:
            self._model.removeModule(self._actModule.module)

        # Delete/Close corresponding ValueFrame
        for f in deleteValueFrames:
            f.Close()
            
    
    def onShowModuleXML(self, event):
        """
        Opens the Module Xml file in editor.
        
        @type event: wx.Event
        @param event: Menu Event associated with this method in view.workspace.CabelFrame.getModuleMenu
        """
        xmlModulePath = os.path.join(os.getcwd(), self._configDirs.getVal(tools.config.Directories.MODULES), self._actModule.module.fullName + '.xml')
        editorPath = self._configDirs.getVal(tools.config.Directories.EDITOR)
        if os.path.exists(xmlModulePath):
            cmd = editorPath + ' \"' + xmlModulePath + '\"'
            if not wx.Execute(cmd):
                print('The editor executable (' + editorPath + ') as specified ' + \
                       'in the Preferences dialog wasn\'t found.')
        else:
            #TODO: Modal Dialog: Can not find Module Xml. Definition of module is from cw file. Open cw file?
            print('The module xml file defining the current Module ' + \
                  self._actModule.module.fullName + ' wasn\'t found in the directory ' + \
                  os.path.join(os.getcwd(), self._configDirs.getVal(tools.config.Directories.MODULES)))
               

    def setModuleFocus(self, module):
        """
        Sets the actual Module, gives it a focus and removes the focus
        on the old actual module if there was any.

        @type  module: view.module.Module
        @param module: The new actual Module.
        """
        if module == self._actModule:
            return
        if module:
            if self._actModule:           
                self._actModule = module
            else:
                self._actModule = module
        else:
            self._actModule = module


    def onOptionsOpen(self, event):
        """
        Open the Options Dialog.
        
        @type event: wx.Event
        @param event: Event.
        """
        optionsDialog = CabelConfigDialog(self._view, self._model.config)
        optionsDialog.ShowModal()


    def onValueFrameClosed(self, valueframe):
        """
        Called when a value frame is closed.

        @type  valueframe: model.view.valueframe.CabelValueFrame
        @param valueframe: Closed value frame.
        """
        self._openValueFrames.remove(valueframe)

    
    def setIoTextCtrl(self, control = None):
        """
        """
        # Set the ioTextControll in the model
        if control:
            self._view.ioTextCtrl = control
        self._model.setIoTextCtrl(self._view.ioTextCtrl)        


    def onScaleInActModule(self, event):
        """
        Scales into (Zoom In) the selected Module with default zoom from preferences.
        
        @type event: wx.Event
        @param event: Menu Event associated with this method in view.workspace.CabelFrame.getModuleMenu
        """
        viewConfig = self._model.config.view
        defaultZoom = viewConfig.getVal(tools.config.View.ZOOM_FACTOR_DEFAULT)
        self._actModule.scaleIt(defaultZoom / 100)
        self._view.workspace.Refresh()
        
    
    def onScaleOutActModule(self, event):
        """
        Scales out of (Zoom Out) the selected Module with default zoom from preferences.
        
        @type event: wx.Event
        @param event: Menu Event associated with this method in view.workspace.CabelFrame.getModuleMenu
        """
        viewConfig = self._model.config.view
        defaultZoom = viewConfig.getVal(tools.config.View.ZOOM_FACTOR_DEFAULT)
        self._actModule.scaleIt(0.0 - (defaultZoom / 100))
        self._view.workspace.Refresh()


    def zoom(self, zoom):
        """
        Set Zoom percent-value on the workspace, scales every module on the workspace
        and repaints the workspace.
        
        @type zoom: int
        @param zoom: Percent value of the zoom
        """
        self._view.zoom = zoom
        self._view.config.setVal(tools.config.View.ZOOM_LASTVALUE, zoom)
        for mod in self._view._modulesDict.values():
            mod.zoom()
        self._view.workspace.Refresh()
        
    
    def onPlayStop(self, event):
        """
        EventHandler for start/stop csound process from the file menu or with shortcut ctrl-y
        
        @type event: wx.Event
        @param event: Menu Event associated with this method in view.workspace.CabelFrame.__init__
        """
        #TODO: CabelStatusBar method for starting/stoping csound should call this method.
        # Check wether Cabel is in playing state or not
        if self._model.isPlaying():
            self._model.stop()
        else:
            self._model.play()
        self._refreshPlayStopMenuEntry()
            
            
    def onSize(self, event):
        """
        Saves wether view.workspace.CabelFrame is maximized or not in the config.xml
                
        @type event: wx.Event
        @param event: Menu Event associated with this method in view.workspace.CabelFrame.__init__
        """
        # If frame is maximized, save it in config.xml
        if self._view.IsMaximized():
            self._view.config.setVal(tools.config.View.FRAME_MAXIMIZED, True)
        else:
            self._view.config.setVal(tools.config.View.FRAME_MAXIMIZED, False)
        event.Skip()


    def _callFunc(self, obj, method):
        """
        Calls the method on obj.
        Exceptions caused by 'dummy' method names are caught.
        
        @type obj: object
        @param obj: The object on which this func is defined.        
        @type method: string
        @param method: Name of a method without parameters to call on the self object.
        """
        try:
            function = getattr(obj, method)
            function()
        except AttributeError:
            pass
    
    
    def _refreshPlayStopMenuEntry(self):
        """
        Refresh the Filemenu entry for start/stop csound process.
        Warning: This method works with absolut menu entry position.
        """
        self._view._filemenu.RemoveItem(self._view._filemenu.FindItemById(self._view._playStopId))
        self._view._filemenu.Insert(7, self._view._playStopId, self._model.isPlaying() and 'Stop Csound\tCTRL-Y' or 'Start Csound\tCTRL-Y')
        
    
    def _refreshModulesMenu(self, event=None):
        """
        Read the xml-modules and refresh their corresponding menu entries.
        
        @type event: wx.Event
        @param event: Event. (per default: None)
        """
        self._idToModules = {}
        modulesMenu = self._view.getModulesMenu(self._getXmlModuleList())
        self._view.GetMenuBar().Replace(1, modulesMenu, "&Modules")
        self._view._modulesMenu = modulesMenu
    
    
    def _createWorkspace(self, fileLocation = ''):
        """
        Read a CabelWorkspace file into a XmlWorkspaceReader and 
        create the model- and view- workspace representations of it.
        
        @type fileLocation: string
        @param fileLocation: Full qualified path to a cabelworkspace file. 
                             (per default: '', serves for clean workspace)
        """
        # Read the given File if it exists
        if fileLocation != '':
            workspaceReader = XmlWorkspaceReader(fileLocation, self)
        else:
            workspaceReader = None
        # create the model
        self._model = self._model.createWorkspace(workspaceReader)
        self._pushToRecentFiles(fileLocation)
        # The view
        self._closeOpenValueFrames()
        self._view = self._view.createWorkspace(workspaceReader)
        # Reset lastMousePoint
        self._actualModule = None
        self._lastMousePt = wx.Point()
        
        
    def _getEventCoordinates(self, event):
        """
        Return the coordinates associated with the given mouse event.

        The coordinates have to be adjusted to allow for the current
        scroll position.

        @type  event: wx.Event
        @param event: Event associated with this function.
        @rtype : wx.Point
        @return: Coordinates of event.
        """
        originX, originY = self._view.workspace.GetViewStart()
        unitX, unitY = self._view.workspace.GetScrollPixelsPerUnit()
        return wx.Point(event.GetX() + (originX * unitX),
                        event.GetY() + (originY * unitY))


    def _getXmlModuleList(self):
        """
        Returns list of module names.
        """
        mr = XmlModuleReader()
        return mr.getModulesObjects()


    def _pushToRecentFiles(self, location):
        """
        Add the given filePath to recentfiles list if it is not yet in it or
        move it to the top else.
        
        @type location: string
        @param location: Full qualified fileName.
        """
        if location != '':
            recents = self._configDirs.getVal(tools.config.Directories.RECENTFILES)
            if location not in recents:
                recents.insert(0, os.path.normpath(location))
                if (len(recents)) > 10:
                    recents = recents[0:10]
            else:
                del recents[recents.index(location)]
                recents.insert(0, location)
            
            self._configDirs.setVal(tools.config.Directories.RECENTFILES, recents)
            self._view.reloadRecentMenu()


    def _closeOpenValueFrames(self):
        """
        Close all open ValueFrames.
        """
        while self._openValueFrames:
            f = self._openValueFrames[0]
            f.Close()


    def _askSave(self, event):
        """
        Ask if patch should be saved if it was changed.

        @type  event: wx.Event
        @param event: Event from calling event handler function.
        @rtype: bool
        @return: True if user decided to save or not so save, False if user
                 canceled action.
        """
        if not self._saved:
            fileName = "New File"
            if self._view.fileName:
                fileName = self._view.fileName + ".cw"
            dlg = wx.MessageDialog(self._view,
                                   "Save changes to " + fileName \
                                   + " before closing?",
                                   "Close " + fileName,
                                   wx.YES_NO|wx.CANCEL|wx.NO_DEFAULT|wx.ICON_EXCLAMATION)
            result = dlg.ShowModal()
            if result == wx.ID_YES:
                self.onSave(event)
                dlg.Destroy()
                if self._saved:
                    return True
                return False
            if result == wx.ID_NO:
                dlg.Destroy()
                return True
            else:
                dlg.Destroy()
                return False
        return True
