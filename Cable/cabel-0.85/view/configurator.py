from xml.dom import minidom
import locale
import string
import wx.lib.colourselect as cSel
import wx.lib.filebrowsebutton as filebrowse
import wx
import tools.config
import os

class CabelConfigDialog(wx.Dialog):
    def __init__(self, parent, cfg):
        """
        """        
        title = 'Preferences'
        wx.Dialog.__init__(self, parent, -1, title,
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonOK = wx.Button(self, wx.ID_OK, "&OK")
        buttonApply = wx.Button(self, wx.ID_APPLY)
        buttonCancel = wx.Button(self, wx.ID_CANCEL, "&Cancel")
        buttonSizer.Add(buttonOK, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        buttonSizer.Add(buttonApply, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        buttonSizer.Add(buttonCancel, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        
        notebookSizer = wx.BoxSizer(wx.HORIZONTAL)
        notebook = wx.Notebook(self, -1, size=(450,300), style = wx.NO_BORDER)
        
        self.configParser = ConfigParser(cfg, notebook, parent)
        self.configParser.fillCategoryNotebook()
        
        notebookSizer.Add(notebook, 1, wx.EXPAND)

        dialog_sizer = wx.BoxSizer(wx.VERTICAL)
        dialog_sizer.Add(notebookSizer, 1, wx.EXPAND | wx.ALL, 2)
        dialog_sizer.Add(buttonSizer, 0, wx.ALL | wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)

        if "__WXMAC__" in wx.PlatformInfo:
           self.SetSizer(dialog_sizer)
        else:
           self.SetSizerAndFit(dialog_sizer)
        self.Centre()

        self.Bind(wx.EVT_BUTTON, self.onOK, id = wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.onApply, id = wx.ID_APPLY)
        self.Bind(wx.EVT_BUTTON, self.onCancel, id = wx.ID_CANCEL)
        
        # Enable ToolTips Globally
        wx.ToolTip_Enable(True)
        wx.ToolTip_SetDelay(10)


    def onCancel(self, evt):
        # Set focus to Cancel button so values in panels are set
        evt.GetEventObject().SetFocus()
        self.EndModal(0)
        
    
    def onOK(self, evt):
        # Set focus to Ok button so values in panels are set
        evt.GetEventObject().SetFocus()
        self.configParser.SaveVars()
        self.Destroy()
        #self.EndModal(0)
        
        
    def onApply(self, evt):
        # Set focus to Apply button so values in panels are set
        evt.GetEventObject().SetFocus()
        self.configParser.SaveVars()
        
    
class ConfigParser(object):
    """
    """
    
    def __init__(self, config, parent, worksp):
        """
        Standardconstructor.
        
        @type  config: tools.config.Config
        @param config: The config model to be parsed.
        """
        self.config = config
        self.parent = parent
        self.workSpace = worksp
        self.varValueDict = {}
    
    
    def fillCategoryNotebook(self):
        """
        """
        csoundCat = self.getCategoryPanel(self.config.csound)
        viewCat = self.getCategoryPanel(self.config.view)
        dirCat = self.getCategoryPanel(self.config.directories)

        self.parent.AddPage(csoundCat, 'Csound')
        self.parent.AddPage(viewCat, 'User Interface')
        self.parent.AddPage(dirCat, 'Directories')
    
    
    def getCategoryPanel(self, category):
        """
        """
        panel = wx.Panel(self.parent)
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        
        groups = {}
        panelList = []
        
        # group configVars
        for configVar in category.vars:
            setting = configVar.setting
            if setting and setting.dialog:
                if setting.group != None:
                    # Group
                    if groups.has_key(setting.group):
                        groups[setting.group].append(configVar)
                    else:
                        groups[setting.group] = [configVar]
                        panelList.append(setting.group)
                else:
                    # None Group
                    panelList.append(configVar)
        
        # get panels
        for i in panelList:
            if isinstance(i, tools.config.ConfigVar) or isinstance(i, tools.config.ListVar):
                # None Group Panel
                ctrlPanel = self.getControl(i, panel)
            else:
                # Group Panel
                ctrlPanel = self.getGroupPanel(groups[i], panel)
            panelSizer.Add(ctrlPanel, 0, wx.EXPAND|wx.ALL, 5)
        
        panel.SetSizer(panelSizer)
        return panel
    
    
    def getGroupPanel(self, vars, parent):
        """
        """
        groupBoxPanel = wx.Panel(parent)
        groupBox = wx.StaticBox(groupBoxPanel, -1, vars[0].setting.group)
        groupBoxSizer = wx.StaticBoxSizer(groupBox, wx.VERTICAL)
        
        for groupVar in vars:
            ctrl = self.getControl(groupVar, groupBoxPanel)
            groupBoxSizer.Add(ctrl, 1, wx.EXPAND|wx.RIGHT, 3)
        
        groupBoxPanelSizer = wx.BoxSizer()
        groupBoxPanelSizer.Add(groupBoxSizer, 1, wx.ALL|wx.EXPAND, 6)
        groupBoxPanel.SetSizer(groupBoxPanelSizer)
        
        return groupBoxPanel
    
    
    def getControl(self, var, parent):
        """
        """
        type = var.valueType
        if type == 'int':
            return self.getIntVarCtrl(parent, var)
        elif type == 'float':
            return self.getFloatVarCtrl(parent, var)
        elif type == 'boolean':
            return self.getBooleanVarCtrl(parent, var)
        elif type == 'colour':
            return self.getColourVarCtrl(parent, var)
        elif type == 'string' and var.nodeType == minidom.Node.TEXT_NODE:
            return self.getStringVarMultiLineCtrl(parent, var)
        elif type == 'string' and var.nodeType == minidom.Node.ATTRIBUTE_NODE:
            return self.getStringVarSingleLineCtrl(parent, var)
        elif type.find('list') >= 0:
            return self.getListVarCtrl(parent, var)
        elif type.find('enum') >= 0:
            return self.getEnumVarCtrl(parent, var)
        else:
            # should never happen!
            return self.getStringVarSingleLineCtrl(parent, var)
        
    
    
    def SaveVars(self):
        """
        """
        # Save each var in the varValDict
        for varValTuple in self.varValueDict.items():
            varValTuple[0].setVal(varValTuple[1])
            if varValTuple[0].setting.updateFunc:
                varValTuple[0].setting.updateView(self.workSpace)
        # Clear varValDict
        self.varValueDict = {}
        
        
    def getColourVarCtrl(self, parent, var, id = -1, size = wx.Size(60,20)):
        """
        """
        colourCtrlSizer = ConfigColourSelect(parent, id, self, var, size)
        return colourCtrlSizer
    
    
    def getListVarCtrl(self, parent, var):
        """
        """
        return wx.Panel(parent)
        
        
    def getEnumVarCtrl(self, parent, var):
        """
        """
        return wx.Panel(parent)
    
    
    def getIntVarCtrl(self, parent, var, id = -1, size = wx.DefaultSize):
        """
        """
        return ConfigInt(parent, id, self, var, size)
            
        
    def getFloatVarCtrl(self, parent, var, id = -1, size = wx.DefaultSize):
        """
        """
        return ConfigFloat(parent, id, self, var, size)
    
    
    def getStringVarSingleLineCtrl(self, parent, var, id = -1, size = wx.DefaultSize):
        """
        """
        len = var.setting.ctrlLength
        if len > 0:
            size = wx.Size(len, wx.DefaultSize.GetHeight())
        return ConfigStringSingleLine(parent, id, self, var, size)
    
    
    def getStringVarMultiLineCtrl(self, parent, var, id = -1, size = wx.DefaultSize):
        """
        """
        len = var.setting.ctrlLength
        if len > 0 and var.setting.ctrlHeight:
            hei = var.setting.ctrlHeight * 16
            size = wx.Size(len, hei)
        return ConfigStringMultiLine(parent, id, self, var, size)
    
    
    def getBooleanVarCtrl(self, parent, var, id = -1, size = wx.DefaultSize):
        """
        """
        return ConfigBooleanCheck(parent, id, self, var, size)
        
    
    
# --------------------------------------------------------------


class ConfigControl(object):
    """
    ConfigControl.
    
    Controller for the configurator input controlls.
    
    It's an 'abstract' class. Inherited classes can implement 'abstract' invalidateVarVal(self, val)
    for validation of the input to the control.
    
    @type parent: wx.Panel
    @ivar parent: The root panel of a wx.Notebook (category) page.
    @type configParser: configurator.ConfigParser
    @ivar configParser: ConfigParser in charge of this control.
    @type configVar: tools.config.ConfigVar
    @ivar configVar: ConfigVarrepresented through this control.
    @type ctrl: wx.Control
    @ivar ctrl: The input control. has to be set in the constructor of inherited class.
    """
    def __init__(self, parent, configParser, var):
        """
        Standardconstructor.
        
        @type parent: wx.Panel
        @param parent: The root panel of a wx.Notebook (category) page.
        @type configParser: configurator.ConfigParser
        @param configParser: ConfigParser in charge of this control.
        @type var: config.ConfigVar
        @param var: ConfigVarrepresented through this control.
        """
        self.parent = parent
        self.configParser = configParser
        self.configVar = var
        self.ctrl = None
        self._defaultCtrlBgrColour = None
        
        
    def updateVarValDict(self, val):
        """
        Checks if the value val for the ConfigVar has changed, if it is valid
        and caches the configVar/value pair in the responsible configParser.
        
        @type val: self.configVar.valueType
        @param val: The value returned by the control.
        """
        # Check if ConfigVar Value has changed
        if self.hasChanged(val):
            # Check Config Var Value input
            warning = self.invalidateVarVal(val)
            # No Warning
            if not warning:
                self.configParser.varValueDict[self.configVar] = val
                if self._defaultCtrlBgrColour:
                    self.paintCtrlWhite(None)
            # Warning
            else:
                # Paint controlls red
                self.paintTheInvalidRed()
                # Register paint the Control White for
                self.ctrl.Bind(wx.EVT_SET_FOCUS, self.paintCtrlWhite)
                # Show warning dialog
                d = wx.MessageDialog(self.parent, str(warning) + "\n Please correct the red marked Config Var.", "ConfigVar Error",
                                     wx.OK | wx.ICON_ERROR)
                d.ShowModal()
                d.Destroy()


    def hasChanged(self, val):
        """
        Checks if the value of the configVarhas changed.
        
        @type val: self.configVar.valueType
        @param val: The value returned by the control.
        """
        oldVal = self.configVar.getVal()
        return not (oldVal == val)
    
        
    def invalidateVarVal(self, val):
        """
        Method for invalidation of the configVar's value.
        
        @rtype: boolean/string
        @return: A warning message if the Value is invalid, else False.
        """
        setting = self.configVar.setting
        # Mustn't a null value
        if setting.notNone:
            if val == None or val == '':
                return "The value can't be empty!"
        return False
    
    
    def paintCtrlWhite(self, event):
        """
        Paints the control as it was originally.
        """
        self.ctrl.SetOwnBackgroundColour(self._defaultCtrlBgrColour)
        self.ctrl.Refresh()
    
    
    def paintTheInvalidRed(self):
        """
        Paints the control red.
        """
        self._defaultCtrlBgrColour = self.ctrl.GetBackgroundColour()
        #self.ctrl.SetValue(str(self.configVar.getVal()))
        self.ctrl.SetOwnBackgroundColour("red")
        self.ctrl.Refresh()
        
        
    def onOK(self, event):
        """
        Calls the callback method of the CabelConfig control if the accelerator for
        the OK or Apply Buttons (ALT-O or ALT-A) are pressed.
        """
        if event.AltDown():
            if event.GetKeyCode() == ord('O') or event.GetKeyCode() == ord('A'):
                self.callback(event)
        event.Skip()
    
        
    def callback(self, event):
        """
        Virtual method of ConfigControl.
        Should call the updateVarValDict with the value of the control in order
        to process the input of the control.
        """
        pass
    
        
# --------------------------------------------------------------


class ConfigFloat(ConfigControl, wx.BoxSizer):
    """
    """
    def __init__(self, parent, id, configParser, configFloatVar, _size):
        """
        """
        # Call superclass constructors
        ConfigControl.__init__(self, parent, configParser, configFloatVar)
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        # Controls
        self.ctrl = wx.TextCtrl(self.parent, id, str(self.configVar.getVal()), size = _size)
        textLabel = wx.StaticText(self.parent, -1, self.configVar.setting.displayName)
        # Tooltip
        textLabel.SetToolTip(wx.ToolTip(self.configVar.setting.description))
        self.ctrl.SetToolTip(wx.ToolTip(self.configVar.setting.description))
        # Add controll to the sizer
        self.Add(textLabel, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.Add(self.ctrl, 1, wx.EXPAND | wx.ALL, 5)
        # Binding
        self.ctrl.Bind(wx.EVT_KILL_FOCUS, self.callback)
        self.ctrl.Bind(wx.EVT_KEY_DOWN, self.onOK)
        
        
    def callback(self, event):
        """
        """
        val = unicode(self.ctrl.GetValue()).strip()
        if val.find(',') >= 0:
            val = val.replace(',', '.')
        if val.find('.') == 0:
            val = '0' + val
        if val != unicode(self.ctrl.GetValue()).strip():
            self.ctrl.SetValue(val)
            self.ctrl.Refresh()
        self.updateVarValDict(val)
        
        
    def invalidateVarVal(self, val):
        """
        """
        superInvalidation = ConfigControl.invalidateVarVal(self, val)
        if not superInvalidation:
            try:
                value = float(val)
                return False
            except ValueError:
                return 'The value must be a float type.'
        else:
            return superInvalidation


# --------------------------------------------------------------
class ConfigInt(ConfigControl, wx.BoxSizer):
    """
    """
    def __init__(self, parent, id, configParser, configIntVar, _size):
        """
        """
        # Call superclass constructors
        ConfigControl.__init__(self, parent, configParser, configIntVar)
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        # Controls
        self.ctrl = wx.TextCtrl(self.parent, id, str(self.configVar.getVal()), size = _size)
        textLabel = wx.StaticText(self.parent, -1, self.configVar.setting.displayName)
        # Tooltip
        textLabel.SetToolTip(wx.ToolTip(self.configVar.setting.description))
        self.ctrl.SetToolTip(wx.ToolTip(self.configVar.setting.description))
        # Add controll to the sizer
        self.Add(textLabel, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        self.Add(self.ctrl, 1, wx.EXPAND | wx.ALL, 5)
        # Binding
        self.ctrl.Bind(wx.EVT_KILL_FOCUS, self.callback)
        self.ctrl.Bind(wx.EVT_KEY_DOWN, self.onOK)
        
        
    def callback(self, event):
        """
        """
        textVal = unicode(self.ctrl.GetValue()).strip()
        self.updateVarValDict(textVal)
        
        
    def invalidateVarVal(self, val):
        """
        """
        superInvalidation = ConfigControl.invalidateVarVal(self, val)
        if not superInvalidation:
            if val.isdigit() or (val[0:1] in ['-', '+'] and val[1:].isdigit()):
                return False
            else:
                return 'The value must be an integer type.'
        else:
            return superInvalidation


# --------------------------------------------------------------
class ConfigStringMultiLine(ConfigControl, wx.BoxSizer):
    """
    """
    def __init__(self, parent, id, configParser, configStringTextNodeVar, _size):
        """
        """
        # Call superclass constructors
        ConfigControl.__init__(self, parent, configParser, configStringTextNodeVar)
        wx.BoxSizer.__init__(self, wx.VERTICAL)
        # Controls
        self.ctrl = wx.TextCtrl(self.parent, id, self.configVar.getVal(), size = _size, style=wx.TE_MULTILINE)
        textLabel = wx.StaticText(self.parent, -1, self.configVar.setting.displayName)
        # Tooltip
        self.ctrl.SetToolTip(wx.ToolTip(self.configVar.setting.description))
        # Add to sizer
        self.Add(textLabel, 0, wx.ALIGN_LEFT, 5)
        self.Add(self.ctrl, 1, wx.EXPAND | wx.ALL, 5)
        # Binding
        self.ctrl.Bind(wx.EVT_KILL_FOCUS, self.callback)
        self.ctrl.Bind(wx.EVT_KEY_DOWN, self.onOK)
                
        
    def callback(self, event):
        """
        """
        textVal = unicode(self.ctrl.GetValue()).strip()
        self.updateVarValDict(textVal)
        

# --------------------------------------------------------------


class ConfigStringSingleLine(ConfigControl, wx.BoxSizer):
    """
    """
    def __init__(self, parent, id, configParser, configStringTextNodeVar, _size):
        """
        """
        # Call superclass constructors
        ConfigControl.__init__(self, parent, configParser, configStringTextNodeVar)
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        # Controls
        if self.configVar.setting.choose == 'file':
            file = self.configVar.getVal()
            #path = file[:file.rfind(os.path.sep)]
            #file = file[file.rfind(os.path.sep):]
            self.ctrl = filebrowse.FileBrowseButton(self.parent, -1, size=_size, labelText='', buttonText='Browse', toolTip=self.configVar.setting.description, startDirectory=file, initialValue=file, changeCallback=self.callback)
            self.ctrl.textControl.Bind(wx.EVT_KILL_FOCUS, self.callback)
        elif self.configVar.setting.choose == 'path':
            self.ctrl = filebrowse.DirBrowseButton(self.parent, -1, size=_size, labelText='', toolTip=self.configVar.setting.description, startDirectory=os.path.join(os.getcwd(), self.configVar.getVal()), changeCallback=self.callback)
            self.ctrl.textControl.Bind(wx.EVT_KILL_FOCUS, self.callback)
            self.ctrl.SetValue(os.path.join(os.getcwd(), self.configVar.getVal()), 0)
        else:
            self.ctrl = wx.TextCtrl(self.parent, id, self.configVar.getVal(), size = _size)
            self.ctrl.Bind(wx.EVT_KILL_FOCUS, self.callback)
        textLabel = wx.StaticText(self.parent, -1, self.configVar.setting.displayName)
        # Tooltip
        textLabel.SetToolTip(wx.ToolTip(self.configVar.setting.description))
        self.ctrl.SetToolTip(wx.ToolTip(self.configVar.setting.description))
        # Add controll to the sizer
        self.Add(textLabel, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTRE_VERTICAL)
        self.Add(self.ctrl, 1, wx.EXPAND | wx.ALL, 5)
        # Binding
        self.ctrl.Bind(wx.EVT_KEY_DOWN, self.onOK)
        
        
    def callback(self, event):
        """
        """
        if not self.ctrl.HasCapture():
            textVal = unicode(self.ctrl.GetValue()).strip()
            self.updateVarValDict(textVal)


# --------------------------------------------------------------

class ConfigBooleanCheck(ConfigControl, wx.BoxSizer):
    """
    """
    def __init__(self, parent, id, configParser, configBooleanVar, size):
        """
        """
        # Call superclass constructors
        ConfigControl.__init__(self, parent, configParser, configBooleanVar)
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        # Controls
        self.ctrl = wx.CheckBox(self.parent, id, self.configVar.setting.displayName, style = wx.ALIGN_RIGHT)
        self.ctrl.SetValue(self.configVar.getVal())
        # ToolTip
        self.ctrl.SetToolTip(wx.ToolTip(self.configVar.setting.description))
        # Binding
        self.ctrl.Bind(wx.EVT_CHECKBOX, self.callback)
        self.ctrl.Bind(wx.EVT_KEY_DOWN, self.onOK)
        # Add controll zo the sizer
        self.Add(self.ctrl, 0, wx.ALIGN_LEFT)
        
    
    def callback(self, event):
        """
        """
        self.updateVarValDict(self.ctrl.GetValue())
        
        
class ConfigColourSelect(ConfigControl, wx.FlexGridSizer):
    """
    """
    def __init__(self, parent, id, configParser, configColourVar, size,
                 label="", pos=wx.DefaultPosition, style=0):
        """
        """
        # Call superclass constructors
        ConfigControl.__init__(self, parent, configParser, configColourVar)
        wx.FlexGridSizer.__init__(self, 1, 2)
        
        # Controls
        self.ctrl = cSel.ColourSelect(self.parent, id, label, self.configVar.Value, \
                                             pos, size, callback = self._callback)
        colourCtrlLabel = wx.StaticText(self.parent, -1, self.configVar.setting.displayName)
        # ToolTips
        self.ctrl.SetToolTip(wx.ToolTip(self.configVar.setting.description))
        colourCtrlLabel.SetToolTip(wx.ToolTip(self.configVar.setting.description))
        # Add Controls to Sizer
        self.Add(colourCtrlLabel, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)
        self.Add(self.ctrl, 0, wx.ALL, 3)
        # Bindings
        self.ctrl.Bind(wx.EVT_KEY_DOWN, self.onOK)
                
                    
    def _callback(self):
        """
        """
        self.updateVarValDict(self.ctrl.GetColour())
        
    
    def callback(self, event):
        """
        """
        self._callback()
