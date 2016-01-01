import StringIO
import codecs
import xml
from xml.dom import minidom
from xml.dom.minidom import getDOMImplementation
import wx
import os
import sys


class Config:
    """
    Config.
    
    Encapsulates all Categories in the config file.
    
    @type configXmlLocation: string
    @ivar configXmlLocation: Path to config.xml.
    @type configDoc: minidom.Document
    @ivar configDoc: config.xml DOM.
    """
        
    def __init__(self):
        """
        Standardconstructor.
        """
        self.configXmlLocation = self._getConfigXmlLocation()
        self.configDoc = self._getOrCreateConfigXml()
        
        self.csound = Csound(self.configDoc, self.configXmlLocation)
        self.directories = Directories(self.configDoc, self.configXmlLocation)
        self.view = View(self.configDoc, self.configXmlLocation)
        

    def _getConfigXmlLocation(self):
        """
        getConfigXmlLocation. Where is the config.xml?

        @rtype:  string
        @return: Path of the config.xml File (without Filename).)
        """
        if os.getenv("HOME"):
            configXmlLocation = os.getenv("HOME") + os.path.sep \
                                + '.Cabel' + os.path.sep
            if not(os.path.exists(configXmlLocation)):
                os.makedirs(configXmlLocation)
        else:
            configXmlLocation = ""
            
        return configXmlLocation
    

    def _getOrCreateConfigXml(self):
        """
        If config.xml exists in the configXmlLocation it gets parsed to DOM,
        else it is created.
        
        @rtype: xml.dom.minidom.Document
        @return: DOM representation of config.xml.
        """
        configDoc = None
        try:
            configDoc = minidom.parse(self.configXmlLocation + 'config.xml')
        except (IOError, xml.parsers.expat.ExpatError):
            impl = getDOMImplementation()
            configDoc = impl.createDocument(None, 'config', None)
        return configDoc


class Category(object):
    """
    Category.

    Abstract superclass for all Config Categories. If you want a
    coherent config.xml File do NOT use the Config_Var objects of
    vars[] directly!!!  setVal/getVal are the methods to use!!

    @type vars: list
    @ivar  vars: List of ConfigVar objects. setVal/getVal are the
                methods to use for access to its Values!!
    @type name: string
    @ivar name: Name of Category.
    @type configXmlLocation: string
    @ivar configXmlLocation: Path to config.xml.
    @type configDoc: minidom.Document
    @ivar configDoc: config.xml DOM.
    @type categoryNode: minidom.Element
    @ivar categoryNode: Node of the Category in config.xml DOM.
    """

    def __init__(self, name, configDoc, configXmlLocation):
        """
        Standardconstructor.

        @type  name: string
        @param name: Name of Category.
        @type configXmlLocation: string
        @param configXmlLocation: Path to config.xml.
        @type configDoc: minidom.Document
        @param configDoc: config.xml DOM.
        """
        self.vars = []
        self.configXmlLocation = configXmlLocation
        self.configDoc = configDoc
        self.categoryNode = None
        self.name = name

        try:
            # Find categoryNode
            if isinstance(self, ListVar):
                # If its a ListVar, the categoryNode looks like <<self._varNodeName | 'var'> name='self.name'>
                for varNode in self._parentNode.getElementsByTagName(self._varNodeName):
                    if varNode.getAttribute('name') == self.name:
                        self.categoryNode = varNode
                        break
                if not self.categoryNode:
                    raise IndexError
            else:
                # A 'pure' categoryNode looks like <name>
                self.categoryNode = self.configDoc.documentElement.getElementsByTagName(self.name)[0]
            
            self.fillWithDefaultVars()
        except IndexError:
            self._createCategoryNode()


    def fillWithDefaultVars(self):
        """
        Fills vars[] with its Config_Var Objects. Has to be
        implemented by the non abstract inherited classes.
        """
        pass


    def getVar(self, var):
        """
        """
        return self.vars[var]


    def getDefault(self, var):
        """
        Gets the default of the Config_Var object in vars[var].
        
        @type  var: int
        @param var: index of Config_Var object in vars[]. Get it from
                    the instance-constants of the implemented Category.
        @rtype:  object
        @return: Default value of var.
        """
        return self.vars[var].Default
    
    
    def getVal(self, var):
        """
        Gets the Value of the Config_Var object in vars[var]. If it
        isn't already in the config.xml DOM, it is added and
        config.xml saved.

        @type  var: int
        @param var: index of Config_Var object in vars[]. Get it from
                    the static-constants of the implemented Category.
        @rtype:  object
        @return: Value of var.
        """
        val = self.vars[var].Value
        if not self.vars[var].nodeFound:
            self._save()
            self.vars[var].nodeFound = False
        return val


    def setVal(self, var, val):
        """
        Sets the Value of the Config_Var object in vars[var] and saves
        the config.xml DOM.

        @type  var: int
        @param var: index of Config_Var object in vars[]. Get it from
                    the instance-constants of the implemented Category.
        @type  val: string
        @param val: Value to which it should be set.
        """
        self.vars[var].Value = val
        self._save()


    def setEnumIndex(self, var, index):
        """
        Sets the enum index of the enumVar vars[var] and saves it to the config.xml.
        
        @type  var: int
        @param var: index of Config_Var object in vars[]. Get it from
                    the instance-constants of the implemented Category.
        @type  index: int
        @param index: Index to which it should be set.
        @raise IndexError: If the ConfigVar vars[var] isn't a ConfigEnumVar.
        """
        configVar = self.vars[var]
        if isinstance(configVar, ConfigEnumVar):
            configVar.Index = index
            self._save()
        else:
            raise IndexError, 'The configVar is not a enumeration Var!'
            
            
    def getEnumIndex(self, var):
        """
        Gets the enum index of the enumVar vars[var].
        
        @type  var: int
        @param var: index of Config_Var object in vars[]. Get it from
                    the instance-constants of the implemented Category.
        @raise IndexError: If the ConfigVar vars[var] isn't a ConfigEnumVar.
        """
        configVar = self.vars[var]
        if isinstance(configVar, ConfigEnumVar):
            return configVar.Index
        else:
            raise IndexError, 'The configVar is not a enumeration Var!'
        

    def insertVar(self, index, var):
        """
        Sets the ConfigVar var at the specified position in self.vars and fills
        the still unset vars with its index number.
        
        @type index: int
        @param index: 0 based index of the var to add.
        @type var: config.ConfigVar
        @param var: The ConfigVar to be added.
        """
        if len(self.vars) == index:
            self.vars.append(var)
        elif len(self.vars) < index:
            for i in xrange(len(self.vars), index):
                self.vars.append(i)
            self.vars.append(var)
        else:
            self.vars[index] = var
    
    
    def _createCategoryNode(self):
        """
        Adds a Category Node in the config.xml DOM fills it with its
        vars and saves it.
        """
        self.categoryNode = self.configDoc.createElement(self.name)
        self.configDoc.documentElement.appendChild(self.categoryNode)
        self.fillWithDefaultVars()
        self._write()


    def _write(self):
        """
        Writes all Config_Var objects in self.vars to the config.xml
        DOM and saves it.
        """
        for var in self.vars:
            var.write()
        self._save()


    def _save(self):
        """
        Saves config.xml DOM (configDoc) in configXmlLocation/config.xml
        """
        configFile = codecs.open(self.configXmlLocation + 'config.xml', 'w', encoding='utf8')
        # linesep workaround
        stringBuf = StringIO.StringIO()
        self.configDoc.writexml(stringBuf, encoding='utf-8', newl='\n', addindent='\t')
        lines = []
        for line in stringBuf.getvalue().split('\n'):
            if not line.isspace():
                lines.append(line + '\n')
        configFile.writelines(lines)
        configFile.close()


#---------------------------------------------------------------------------

class Csound(Category):
    """
    config.Csound.

    Category for Csound specific Information. (See documentation of
    superclass Category!)
    """

    SAMPLERATE = 0
    KONTROLRATE = 1
    KSMPS = 2
    NCHNLS = 3
    SCORE = 4
    PARAMS = 6
    AUTOPLAY = 7
    CSOUNDPATH = 5
    FEEDBACK_TIMEOUT = 8


    def __init__(self, configDoc, configXmlLocation):
        """
        Standardconstructor.
        
        @type configXmlLocation: string
        @param configXmlLocation: Path to config.xml.
        @type configDoc: minidom.Document
        @param configDoc: config.xml DOM.
        """
        Category.__init__(self, 'csound', configDoc, configXmlLocation)


    def fillWithDefaultVars(self):
        """
        Fills classvar vars[] with its Config_Var Objects.
        """
        setting = Setting('Sample Rate.', 'Sample Rate')
        setting.group = 'Instrument Header'
        self.insertVar(Csound.SAMPLERATE, ConfigVar(self, 'sampleRate', '48000', setting))

        setting = Setting('Control Rate', 'Control Rate')
        setting.group = 'Instrument Header'
        self.insertVar(Csound.KONTROLRATE, ConfigVar(self, 'kontrolRate', '6000', setting))

        setting = Setting('Number of samples in a control period (Should be [Sample Rate] / [Control Rate]!)', 'KSMPS')
        setting.group = 'Instrument Header'
        self.insertVar(Csound.KSMPS, ConfigVar(self, 'ksmps', '8', setting))

        setting = Setting('Number of channels of audio output.', 'Channels')
        setting.group = 'Instrument Header'
        self.insertVar(Csound.NCHNLS, ConfigVar(self, 'nchnls', '1', setting))
        
        setting = Setting('Csound score.', 'Score')
        setting.ctrlHeight = 5
        self.insertVar(Csound.SCORE, ConfigVar(self, 'score', 'f0 6000', setting, nodeType = minidom.Node.TEXT_NODE))
        
        setting = Setting('Start Parameters (Flags) for Csound', 'Csound Parameters')
        setting.group = 'Csound Preferences'
        setting.hint = 'pref_csoundparams'
        self.insertVar(Csound.PARAMS, ConfigVar(self, 'params',
                                    '-d -b256 -B2048 -W -+rtmidi=mme -+rtaudio=mme -o dac0 -M0 -m0', setting))
        
        setting = Setting('Automatically restart csound when workspace changed?', 'Autoplay')
        setting.updateFunc = '_updateAutoplayCb'
        self.insertVar(Csound.AUTOPLAY, ConfigVar(self, 'autoplay', False, setting))

        setting = Setting('Path to csound binary file.', 'Csound path')
        setting.group = 'Csound Preferences'
        setting.choose = 'file'
        if sys.platform in ("win32"):
            self.insertVar(Csound.CSOUNDPATH, ConfigVar(self, 'Csoundpath', 'c:\\Program Files\\Csound\csound.exe', setting))
        else:
            self.insertVar(Csound.CSOUNDPATH, ConfigVar(self, 'Csoundpath', '/usr/local/bin/csound', setting))
            
        setting = Setting('Timeout (in milliseconds) for success- feedback of the csound compilation process', 'Compilation Feedback Timeout')
        setting.group = 'Csound Preferences'
        setting.hint = 'pref_csoundcompilationtimeout'
        self.insertVar(Csound.FEEDBACK_TIMEOUT, ConfigVar(self, 'feedbacktimeout', 150, setting))

 #---------------------------------------------------------------------------

class Directories(Category):
    """
    Directories.

    Category for Directories. (See documentation of superclass Category!)
    """

    MODULES = 0
    RECENTFILES = 1
    LOGGING_DIR = 2
    LOGGING_ON = 3
    EDITOR = 4


    def __init__(self, configDoc, configXmlLocation):
        """
        Standardconstructor.
        
        @type configXmlLocation: string
        @param configXmlLocation: Path to config.xml.
        @type configDoc: minidom.Document
        @param configDoc: config.xml DOM.
        """
        Category.__init__(self, 'directories', configDoc, configXmlLocation)


    def fillWithDefaultVars(self):
        """
        Fills classvar vars[] with its Config_Var Objects.
        """
        setting = Setting('Path to the Xml Modules', 'Module Path')
        setting.choose = 'path'
        setting.notNone = False
        setting.updateFunc = '_refreshModulesMenu'
        self.insertVar(Directories.MODULES, ConfigVar(self, 'Modules', 'modules', setting))
        
        setting = Setting('Recently loaded CabelWorkspace files.', 'Recent Files')
        setting.dialog = False
        self.insertVar(Directories.RECENTFILES, ConfigVar(self, 'RecentFiles', [], setting))
        
        setting = Setting('Path to the Logging Files', 'Logfiles')
        setting.choose = 'path'
        setting.notNone = False
        setting.group = 'Logging'
        setting.updateFunc = '_updateLogging'
        self.insertVar(Directories.LOGGING_DIR, ConfigVar(self, 'LogfilesPath', self.configXmlLocation + 'log', setting))
        
        setting = Setting('Write Log Messages in Logfiles?', 'Logging on?')
        setting.group = 'Logging'
        setting.updateFunc = '_updateLogging'
        self.insertVar(Directories.LOGGING_ON, ConfigVar(self, 'Logging', True, setting))
        
        setting = Setting('The Editor to start from within Cabel', 'Editor')
        setting.choose = 'file'
        setting.notNone = False
        self.insertVar(Directories.EDITOR, ConfigVar(self, 'Editor', '', setting))


#---------------------------------------------------------------------------

class View(Category):
    """
    View.

    Category for graphic representations. (See documentation of superclass Category!)
    """

    BACKGROUNDCOLOUR = 0
    WORKSPACEWIDTH = 1
    WORKSPACEHEIGHT = 2
    FRAMEWIDTH = 3
    FRAMEHEIGHT = 4
    FULLMODULENAMES = 5
    MODULEDELETEWARNING = 6
    CABLECOLOUR = 7
    CABLESAGGING = 12
    BOTTOMWINDOW_SHOW = 8
    BOTTOMWINDOW_REMEMBERPROPERTIES = 9
    BOTTOMWINDOW_HEIGHT = 11
    BOTTOMWINDOW_ACTIVEPAGE = 10
    ZOOM_INDIVIDUAL_ACTIVE = 13
    ZOOM_FACTOR_DEFAULT = 14
    FRAME_MAXIMIZED = 15
    ZOOM_LASTVALUE = 16


    def __init__(self, configDoc, configXmlLocation):
        """
        Standardconstructor.
        
        @type configXmlLocation: string
        @param configXmlLocation: Path to config.xml.
        @type configDoc: minidom.Document
        @param configDoc: config.xml DOM.
        """
        Category.__init__(self, 'view', configDoc, configXmlLocation)


    def fillWithDefaultVars(self):
        """
        Fills classvar vars[] with its Config_Var Objects.
        """
        setting = Setting('Colour of Workspace Background', 'Workspace Colour')
        setting.group = 'Workspace'
        setting.updateFunc = 'dummy'
        self.insertVar(View.BACKGROUNDCOLOUR, ConfigVar(self, 'BackgroundColour', wx.Colour(80, 55, 0), setting))
        
        setting = Setting('Width of the Workspace (Scroll-area)', 'Workspace Width')
        setting.group = 'Workspace'
        setting.updateFunc = 'dummy'
        self.insertVar(View.WORKSPACEWIDTH, ConfigVar(self, 'WorkspaceWidth', 3000, setting))
        
        setting = Setting('Height of the Workspace (Scroll-area)', 'Workspace Height')
        setting.group = 'Workspace'
        setting.updateFunc = 'dummy'
        self.insertVar(View.WORKSPACEHEIGHT, ConfigVar(self, 'WorkspaceHeight', 3000, setting))
        
        setting = Setting('Width of the Cabel Application Window', 'Window Width')
        setting.dialog = False
        self.insertVar(View.FRAMEWIDTH, ConfigVar(self, 'FrameWidth', 1024, setting))
        
        setting = Setting('Height of the Cabel Application Window', 'Window Height')
        setting.dialog = False
        self.insertVar(View.FRAMEHEIGHT, ConfigVar(self, 'FrameHeight', 800, setting))
        
        setting = Setting('Show full module names (including pathnames)?', 'Full Module Names')
        setting.updateFunc = 'dummy'
        #setting.group = 'etc.'
        self.insertVar(View.FULLMODULENAMES, ConfigVar(self, 'FullModuleNames', False, setting))
        
        setting = Setting('Warn before removing modules from workspace?', 'Warning on Removing Modules')
        #setting.group = 'etc.'
        self.insertVar(View.MODULEDELETEWARNING, ConfigVar(self, 'ModuleDeleteWarning', True, setting))
        
        setting = Setting('Basic colour of Connection Cables', 'Cable Colour')
        setting.updateFunc = 'dummy'
        setting.group = 'Cable Connection'
        self.insertVar(View.CABLECOLOUR, ConfigVar(self, 'CableColour', wx.Colour(0, 150, 0), setting))
        
        setting = Setting('Show the bottom pane?', 'Show Bottom Pane')
        setting.dialog = False
        self.insertVar(View.BOTTOMWINDOW_SHOW, ConfigVar(self, 'ShowBottomWindow', False, setting))
        
        setting = Setting('Remember properties of the bottom pane?', 'Save Bottom Pane Settings')
        #setting.group = 'etc.'
        self.insertVar(View.BOTTOMWINDOW_REMEMBERPROPERTIES, ConfigVar(self, 'RememberBottomWindowProperties', True, setting))
        
        setting = Setting('Height of the bottom pane', 'Bottom Pane Height')
        setting.dialog = False
        self.insertVar(View.BOTTOMWINDOW_HEIGHT, ConfigVar(self, 'HeightBottomWindow', 100, setting))
        
        setting = Setting('Active Page of the Bottom Pane', 'Active Bottom Pane Page')
        setting.dialog = False
        bottomPages = ['Python Shell', 'Messages']
        self.insertVar(View.BOTTOMWINDOW_ACTIVEPAGE, ConfigEnumVar(self, 'ActiveBottomPage', 0, setting, enum = bottomPages))
        
        setting = Setting('Sagging of Connection Cables', 'Cable Sagging')
        setting.updateFunc = 'dummy'
        setting.group = 'Cable Connection'
        self.insertVar(View.CABLESAGGING, ConfigVar(self, 'CableSagging', 30, setting))
        
        setting = Setting('Enable individual zooming of Modules?', 'Module Zoom Enabled')
        setting.group = 'Zoom'
        self.insertVar(View.ZOOM_INDIVIDUAL_ACTIVE, ConfigVar(self, 'ModuleZoomEnabled', False, setting))
        
        setting = Setting('Zoom Factor for standard step zooms', 'Default Zoom Factor')
        setting.group = 'Zoom'
        self.insertVar(View.ZOOM_FACTOR_DEFAULT, ConfigVar(self, 'ZoomDefFactor', 25.0, setting))
        
        setting = Setting('Frame maximized?', 'Frame Maximized?')
        setting.dialog = False
        self.insertVar(View.FRAME_MAXIMIZED, ConfigVar(self, 'FrameMaximized', False, setting))
        
        setting = Setting('Zoom Value', 'Zoom Value')
        setting.dialog = False
        self.insertVar(View.ZOOM_LASTVALUE, ConfigVar(self, 'ZoomValue', 100, setting))
        


class ListVar(Category):
    """
    List.
    
    Helper category for internal use only. Serves as a meta category for list vars.
    """
    
    
    def __init__(self, configVar, list = [], name = '', parentNode = None, setting = 'take the 1 in configVar', varNodeName = 'var'):
        """
        Standardconstructor.
        
        @type name: string
        @param name: Name of the list var.
        @type list: list
        @param list: The list of initial values.
        @type parentNode: xml.dom.Node
        @param parentNode: Parent Node for the ListVar to save.
        @type setting: config.Setting
        @param setting: Setting for the ListVar.
        @type configVar: config.ConfigVar
        @param configVar: ConfigVar of ListVar.
        @type varNodeName: string
        @param varNodeName: Name of the Node in which the ListVar is stored. 'var' per default!
        """
        self._varNodeName = varNodeName
        self._parentNode = (parentNode == None and [configVar.category.categoryNode] or [parentNode])[0]
        self._list = list
        self.setting = (setting == 'take the 1 in configVar' and [configVar._setting] or [setting])[0]
        Category.__init__(self, (name == '' and [configVar.name] or [name])[0],
                                 configVar.category.configDoc, 
                                 configVar.category.configXmlLocation)
        
        
    def fillWithDefaultVars(self):
        """
        Fills classvar vars[] with its Config_Var Objects.
        """
        valType = self.categoryNode.getAttribute('valueType')
        listLength = int(valType[valType.index('-') + 1:])
        
        # all read list elements
        for i in xrange(0, len(self._list)):
            self.vars.append(ConfigVar(self, 'index-' + str(i), self._list[i]))
        # list in config.xml is larger than the internal _list
        if listLength > len(self._list):
            for j in xrange(len(self._list), listLength):
                self.vars.append(ConfigVar(self, 'index-' + str(j), 'dummy-' + str(j)))
            
            
    def _createCategoryNode(self):
        """
        Adds a Category Node in the config.xml DOM fills it with its
        vars and saves it.
        """
        # Create Var Node
        self.categoryNode = self.configDoc.createElement(self._varNodeName)
        self.categoryNode.setAttribute('name', self.name)
        self.categoryNode.setAttribute('valueType', 'list-' + str(len(self._list)))
        # Create Setting Node
        if self.setting:
            settingNode = self.configDoc.createElement('setting')
            self.categoryNode.appendChild(settingNode)
            self.setting.writeNode(settingNode)
        self._parentNode.appendChild(self.categoryNode)
        self.fillWithDefaultVars()
        self._write()
    
    
    def read(self):
        """
        Read the listVar from config.xml and return the obtained list.
        
        @rtype: list
        @return: The listVar saved in config.xml
        """
        retList = []
        # Read List params
        valType = self.categoryNode.getAttribute('valueType')
        listLength = int(valType[valType.index('-') + 1:])
        
        for i in xrange(0, listLength):
             retList.append(self.getVal(i))
             
        # Read setting info
        if self.setting and len(self.categoryNode.getElementsByTagName('setting')) > 0:
            self.setting.readNode(self.categoryNode.getElementsByTagName('setting')[0])
            
        return retList
        
        
    def write(self, _list = None):
        """
        Writes the as argument passed list to the config.xml.
        Therefore it deletes the actual Nodes and creates it new from self._list.
        """
        if _list:
            if self._list == _list:
                # Nothing has changed
                return
            else:
                self._list = _list
        
        # Delete old childNodes/values
        self.categoryNode.childNodes = []
        self.vars = []
        # Doesn't work due to bug in xml.dom implementation, use workaround
        #for valNode in self.categoryNode.childNodes:
        #   valNode = self.categoryNode.childNodes[v]
        #    removedNode = self.categoryNode.removeChild(valNode)
        #    removedNode.unlink()
        
        # Write new values
        self.categoryNode.setAttribute('valueType', 'list-' + str(len(self._list)))
        # Write list values
        for i in xrange(0, len(self._list)):
            listVar = ConfigVar(self, 'index-' + str(i), self._list[i])
            self.vars.append(listVar)
            listVar.write()
            
        # Write setting Infos
        self._writeSetting()
        
    
    def _writeSetting(self):
        """
        If there is a setting for the listVar, write it to the config.xml DOM.
        """
        if self.setting:
            settingNode = self.configDoc.createElement('setting')
            self.setting.writeNode(settingNode)
            self.categoryNode.appendChild(settingNode)
            
    
#---------------------------------------------------------------------------

class ConfigVar(object):
    """
    ConfigVar.

    Encapsulates information of a Config Variable and the
    functionality to write and read it.

    !!! Always use the Property Value for accesing and setting the
    Value of ConfigVar!!!

    @type category: config.Category
    @ivar category: Category to which ConfigVar belongs to.
    @type nodeType: int (minidom.Node.nodeType)
    @ivar nodeType: Is the ConfigVar stored as a ATTRIBUTE_NODE or
                    TEXT_NODE in config.xml.
    @type name: string
    @ivar name: Name of ConfigVar.
    @type valueType: string
    @ivar valueType: Type of Value; 'string'
    @type _value: string
    @ivar _value: Value of ConfigVar.
    @type _default: string
    @ivar _default: Default-Value of ConfigVar.
    @type description: string
    @ivar description: Describes ConfigVar.
    @type nodeFound: boolean
    @ivar nodeFound: Set by read method. If it is set to None after
                     read method, the category in charge will save
                     config.xml. Else it stores the varNode.
    """


    def __init__(self, category, name, default, setting = None, 
                 nodeType = minidom.Node.ATTRIBUTE_NODE):
        """
        Standardconstructor.

        @type  category: config.Category
        @param category: Category to which ConfigVar belongs to.
        @type  name: string
        @param name: Name of ConfigVar.
        @type  default: string
        @param default: Default-Value of ConfigVar.
        @type  setting: config.Setting
        @param setting: Describes ConfigVar.
        @type  nodeType: int (minidom.Node.nodeType)
        @param nodeType: Is the ConfigVar stored as a ATTRIBUTE_NODE
                         (=Standard) or TEXT_NODE in config.xml.
        """
        self.category = category
        self.nodeType = nodeType
        self.name = name
        self._setting = setting
        if setting:
            setting._var = self
        self._value = ''
        self.nodeFound = None
        

        if isinstance(default, bool):
            self.valueType = 'boolean'
            self._default = str(default)
        elif isinstance(default, int):
            self.valueType = 'int'
            self._default = str(default)
        elif isinstance(default, float):
            self.valueType = 'float'
            self._default = str(default)
        elif isinstance(default, wx.Colour):
            self.valueType = 'colour'
            self._default = self.__colour2String(default)
        elif isinstance(default, list):
            self.valueType = 'list'
            self._default = ListVar(self, default)
        else:
            self.valueType = 'string'
            try:
                self._default = str(default)
            except UnicodeEncodeError:
                self._default = unicode(default).encode("utf-8")
            

    def _readNode(self):
        """
        """
        varNode = self.nodeFound
        # Value
        valNode = varNode.getElementsByTagName('val')[0]
        # Get Node in which value is stored
        if self.nodeType == valNode.ATTRIBUTE_NODE:
            # Stored as Attribute
            storedValue = valNode.getAttribute('value')
            self._value = storedValue
        elif self.nodeType == valNode.TEXT_NODE:
            # Stored as TextNode
            for textNodeKid in valNode.childNodes:
                if textNodeKid.nodeType == valNode.TEXT_NODE:
                    self._value = textNodeKid.nodeValue.strip()
        # Value Type
        self.valueType = valNode.getAttribute('valueType') \
                         or self.valueType
        

    def read(self):
        """
        Reads the Config Var out of config.xml. If it's var Node in
        config.xml DOM not exists, it adds it.

        @rtype:  ConfigVar
        @return: Stored ConfigVar.
        """
        # For the first time Reading: search the varNode
        if not self.nodeFound:
            for varNode in self.category.categoryNode.getElementsByTagName('var'):
                if varNode.getAttribute('name') == self.name:
                    self.nodeFound = varNode
                    # ListVars' nodes are read from another place (directly from the get-methods)
                    if self.valueType.find('list') < 0:
                        self._readNode()
                    break
            # not found: write it!
            if not self.nodeFound:
                self.write(True)
        else:
            # ListVars' nodes are read from another place (directly from the get-methods)
            if self.valueType.find('list') < 0:
                self._readNode()

        return self


    def _writeNode(self, new = False):
        """
        """
        varNode = self.nodeFound
        # Value Node
        valNode = varNode.getElementsByTagName('val')[0]
        # Get Node in which value is stored
        if self.nodeType == valNode.ATTRIBUTE_NODE:
            if new:
                valueToSave = self._value or self._default
            else:
                valueToSave = self._value
            valNode.setAttribute('value', valueToSave)
        elif self.nodeType == valNode.TEXT_NODE:
            # Stored as TextNode
            if not new:
                for textNodeKid in valNode.childNodes:
                    if textNodeKid.nodeType == textNodeKid.TEXT_NODE:
                        newTextNodeKid = self.category.configDoc.createTextNode(self._value)
                        valNode.replaceChild(newTextNodeKid, textNodeKid)
            else:
                valNode.appendChild(self.category.configDoc.createTextNode(self._value or self._default))
        valNode.setAttribute('valueType', self.valueType)
        
        """
        # Setting
        if self.setting:
            # Setting Node
            settingNode = varNode.getElementsByTagName('setting')[0]
            self.setting.writeNode(settingNode)
        """
    
    
    def _createVarNode(self):
        """
        """
        varNode = self.category.configDoc.createElement('var')
        varNode.setAttribute('name', self.name)
        valNode = self.category.configDoc.createElement('val')
        varNode.appendChild(valNode)
        self.category.categoryNode.appendChild(varNode)
        self.nodeFound = varNode
    
    
    def write(self, read = False):
        """
        Writes Var in config.xml DOM. If its var Node does not exist, it creates it.
        """
        # ListVar is written with ListVar.write;
        # It is also written to the DOM within its constructor
        if self.valueType.find('list') >= 0:
            return
        # The configVar isn't read yet
        if not read and not self.nodeFound:
            # Search the node
            for varNode in self.category.categoryNode.getElementsByTagName('var'):
                if varNode.getAttribute('name') == self.name:
                    self.nodeFound = varNode
        # ConfigVar doesn't exist as val Node yet
        if not self.nodeFound:
            # Create the varNode
            self._createVarNode()
            # Write to the created varNode
            self._writeNode(True)
        else:
            # Write to the varNode
            self._writeNode()


    def _getDefault(self):
        """
        _getDefault

        Helpermethod for the Default property

        @rtype:  object
        @return: Default value of the ConfigVar.
        """
        if self.valueType == 'list':
            return self._default.read()
                
        retval = self._default
        
        if self.valueType == 'colour':
            retval = self.__string2Colour(retval)
        elif self.valueType == 'int':
            retval = int(retval)
        elif self.valueType == 'float':
            retval = float (retval)
        elif self.valueType == 'boolean':
            if retval == 'True' or retval == 'true':
                retval = True
            else:
                retval = False
        elif self.valueType == 'string':
            try:
                retval = str(retval)
            except UnicodeEncodeError:
                retval = unicode(retval)
                
        return retval
        
        
    Default = property(_getDefault)
            
    
    def _setValue(self, val):
        """
        _setValue.

        Helpermethod for the Value property

        @type  val: string
        @param val: Value of the ConfigVar to set.
        """
        if self.valueType == 'list':
            self._value = ListVar(self, val)
            self._value.write()
            return
        if self.valueType == 'colour':
            self._value = self.__colour2String(val)
        elif self.valueType != 'string':
            self._value = str(val)
        else:
            # the config.xml is opened with the codecs.open func.
            # this func worries about wether its ascii or unicode
            # or whatever bullshit encoded
            self._value = val
        
        self.write()


    def _getValue(self):
        """
        _getValue.

        Helpermethod for the Value property

        @rtype:  object
        @return: Value of the ConfigVar.
        """
        if self.valueType == 'list':
            if self._value == '':
                listVar = self._default
            else:
                listVar = self._value
            return listVar.read()
                
        self.read()
        if self._value == '':
            retval = self._default
        else:
            retval = self._value
        
        if self.valueType == 'colour':
            retval = self.__string2Colour(retval)
        elif self.valueType == 'int':
            retval = int(retval)
        elif self.valueType == 'float':
            retval = float(retval)
        elif self.valueType == 'boolean':
            if retval == 'True' or retval == 'true':
                retval = True
            else:
                retval = False
        elif self.valueType == 'string':
            try:
                retval = str(retval)
            except UnicodeEncodeError, e:
                retval = unicode(retval)
            
        return retval
        

    Value = property(_getValue, _setValue)
    
    
    def setVal(self, val):
        """
        Wrapper for category.setVal()
        """
        varIndex = self.category.vars.index(self)
        self.category.setVal(varIndex, val)


    def getVal(self):
        """
        Wrapper for category.getVal()
        """
        varIndex = self.category.vars.index(self)
        return self.category.getVal(varIndex)
        
        
    def _getSetting(self):
        """
        If there is a setting, reads it out of config.xml 
        (if not already written, it writes the settingNode)
        and returns it.
        
        @rtype: config.Setting
        @return: Setting of ConfigVar
        """
        if self._setting:
            # Read the configVar (to be sure there is a self.nodeFound)
            if not self.nodeFound:
                self.read()
            # Find the settingNode
            settingNodes = self.nodeFound.getElementsByTagName('setting')
            if len(settingNodes) == 0:
                settingNode = self.category.configDoc.createElement('setting')
                self.nodeFound.appendChild(settingNode)
                self._setting.writeNode(settingNode)
                return self._setting
            else:
                self._setting.readNode(settingNodes[0])
                return self._setting
        else:
            return None
            
            
    def _setSetting(self, value):
        """
        """
        self._setting = value
            
    setting = property(_getSetting, _setSetting)
    

    def __colour2String (self, colour):
        """
        Converts a wx.Colour object to a string representation
        in the form of:
            (red, green, blue).
        
        @type  colour: wx.Colour
        @param colour: Colour to convert into string.
        @rytpe:  string
        @return: representation of colour as a string (red, green, blue).
        """
        return '(' + \
                     str(colour.Red()) + ', ' + \
                     str(colour.Green()) + ', ' + \
                     str(colour.Blue()) + \
                  ')'
                  
        
    def __string2Colour (self, colour):
        """
        Converts strings of the form (red, green, blue) to a wx.Colour object.
        
        @type  colour: string
        @param colour: string in the form of (red, green, blue)
        @rytpe:  wx.Colour
        @return: Colour.
        """
        colour = colour.lstrip('(')
        colour = colour.rstrip(')')
        cValues = colour.split(',')
        if len(cValues) == 3:
            return wx.Colour(int(cValues[0]), int(cValues[1]), int(cValues[2]))
        else:
            raise ValueError
            

            
class ConfigEnumVar(ConfigVar):
    """
    ConfigEnumVar.
    
    Like ConfigVar, but with additional instance var enum. Saves as the value the index
    of the value in the own enumeration list enum.
    
    @type enum: list
    @ivar enum: List of predefined possible values to be selected.
    @type _default: int
    @ivar _default: Index of enum.
    @type Default: self.valueType
    @ivar Default: Default Value (value of self.enum[self._default]).
    @type Value: self.valueType
    @ivar Value: Value of self.enum[self.Index]
    @type Index: int
    @ivar Index: Actual index of ConfigEnumVar.
    """
    
    def __init__(self, category, name, default, setting = None, enum = []):
        """
        Standardconstructor.
        
        Like ConfigVar constructor, with additional param enum.
        
        @type enum: list
        @param enum: List of predefined possible values to be selected.
        @type default: int
        @param default: Index in self.enum
        """
        self.enum = enum
        self._enumListVar = None
        defVal = enum[default]

        # workaround for enum of lists; we don't want ListVars in enumVars
        if isinstance(defVal, list):
            valueType = 'enum-list'
            defVal = default
        else:
            valueType = None

        # base constructor    
        ConfigVar.__init__(self, category, name, defVal, setting)

        # restore default/workaround stuff
        self._default = str(default)
        if valueType:
            self.valueType = valueType
        else:
            self.valueType = 'enum-' + self.valueType
        
        
    def _getDefault(self):
        """
        """
        return self.enum[int(self._default)]
    
    Default = property(_getDefault)
    
    
    def _getValue(self):
        """
        """
        return self.enum[self._getIndex()]
            
    def _setValue(self, value):
        """
        """
        if value in self.enum:
            self._value = str(self.enum.index(value))
        else:
            self._value = str(len(self.enum))
            self.enum.append(value)
        self.write()
    
    Value = property(_getValue, _setValue)    
        
        
    def _getIndex(self):
        """
        """
        self.read()
        if self._value == '':
            return int(self._default)
        else:
            return int(self._value)
            
    def _setIndex(self, index):
        """
        """
        if index >= len(self.enum):
            for e in xrange(len(self.enum), index):
                self.enum.append(None)
        self._value = str(index)
        self.write()
        
    Index = property(_getIndex, _setIndex)
    
    
    def _createVarNode(self):
        """
        """
        ConfigVar._createVarNode(self)
        if not self._enumListVar:
            self._enumListVar = ListVar(self, self.enum, parentNode = self.nodeFound, setting = None, varNodeName = 'enum')
           
    
    def _readNode(self):
        """
        """
        ConfigVar._readNode(self)
        if self._enumListVar:
            self.enum = self._enumListVar.read()
        else:
            self._enumListVar = ListVar(self, self.enum, parentNode = self.nodeFound, setting = None, varNodeName = 'enum')
            self.enum = self._enumListVar.read()
        
        
    def _writeNode(self, new = False):
        """
        """
        ConfigVar._writeNode(self, new)
        if self._enumListVar:
            self._enumListVar.write(self.enum)
        else:
            self._enumListVar = ListVar(self, self.enum, parentNode = self.nodeFound, setting = None, varNodeName = 'enum')
            self._enumListVar.write()

            
class Setting(object):
    """
    Setting.
    
    Encapsulates information which serve for the graphical representation of the config.xml.
    
    @type description: string
    @ivar description: Description of corresponding configVar. Used for Tooltip.
    @type displayName: string
    @ivar displayName: Display name of corresponding configVar.
    @type notNone: boolean
    @ivar notNone: Must not be None the value.
    @type group: string
    @ivar group: Corr. ConfigVar belongs should be displayed grouped in a box labeld with this string.
                 ConfigVars with a group setting 'None' are displayed solemnly.
    @type dialog: boolean
    @ivar dialog: Show ConfigVar in the preferences dialog?
    @type ctrlHeight: int
    @ivar ctrlHeight: Number of lines for multiLine string configVar.
    @type updateFunc: string
    @ivar updateFunc: If this is set, the configurator automatically notifies all in
                      model.module.Workspace registered observers.
                      The argument for the observers is the function name.
    @type choose: string
    @ivar choose: Specifies wether the configVar value can be choosen out of a control.
                  Possible values are:
                      'file': -> FileChooser
                      'path': -> DirectoryChooser
                      'None': -> No Choose option
    @type hint: string
    @ivar hint: A link to a hint text fragment.
    @type __update: boolean
    @ivar __update: If true, the values saved in config.xml overwrite the hardcoded values.
    """
    
    def __init__(self, description, displayName):
        """
        Standardconstructor.
        
        @type description: string
        @param description: Description of corresponding configVar. Used for Tooltip.
        @type displayName: string
        @param displayName: Display name of corresponding configVar.
        """
        self.description = description
        self.displayName = displayName
        self.notNone = True
        self.group = None
        self.dialog = True
        self._var = None
        self.ctrlHeight = None
        self.updateFunc = None
        self.__update = False
        self.hint = None
        self.choose = None
        self._domChanged = False
        
    
    def writeNode(self, settingNode):
        """
        Write settingNode to corresponding configVar node in config.xml
        
        @type settingNode: xml.dom.minidom.Node
        @pram settingNode: Node in which the setting params are stored.
        """
        """ OLD CODE
        settingNode.setAttribute('description', self.description)
        settingNode.setAttribute('displayName', self.displayName)
        settingNode.setAttribute('notNull', str(self.notNone))
        settingNode.setAttribute('group', self.group)
        settingNode.setAttribute('dialogEntry', str(self.dialog))
        settingNode.setAttribute('directory', str(self.directory))
        if self.ctrlHeight:
            settingNode.setAttribute('height', str(self.ctrlHeight))
        if self.updateFunc:
            settingNode.setAttribute('updateFunc', self.updateFunc)
        if self.hint:
            hintNode = self._var.category.configDoc.createElement('hint')
            hintTextNode = self._var.category.configDoc.createTextNode(self.hint)
            hintNode.appendChild(hintTextNode)
            if len(settingNode.getElementsByTagName('hint')) > 0:
                settingNode.replaceChild(hintNode, settingNode.getElementsByTagName('hint')[0])
            else:
                settingNode.appendChild(hintNode)
        """
        # Write overwrite attribute if not yet written.
        updateAttribVal = settingNode.getAttribute('update')
        if not updateAttribVal:
            settingNode.setAttribute('update', str(self.__update))
            self._domChanged |= True
            
        self.__setAttribute(settingNode, 'description', self.description)
        self.__setAttribute(settingNode, 'displayName', self.displayName)
        self.__setAttribute(settingNode, 'notNull', self.notNone)
        self.__setAttribute(settingNode, 'group', self.group)
        self.__setAttribute(settingNode, 'dialogEntry', self.dialog)
        self.__setAttribute(settingNode, 'chooser', self.choose, False)
        self.__setAttribute(settingNode, 'height', self.ctrlHeight, False)
        self.__setAttribute(settingNode, 'updateFunc', self.updateFunc, False)
        self.__setAttribute(settingNode, 'hint', self.hint, False)
        
        # Save changed DOM
        if self._domChanged:
            self._var.category._save()
            self._domChanged = False
        
        
    def __setAttribute(self, settingNode, attrib, value, writeNone=True, overwrite=None):
        """
        Write Setting Attribute to config.xml if self is not an overwrite setting.
        
        @type settingNode: xml.dom.minidom.Node
        @param settingNode: Node on which setting attribute is to save.
        @type attrib: string
        @param attrib: Name of attribute.
        @type value: object
        @param value: Value of attribute.
        @type writeNone: boolean.
        @param writeNone: Write also None value of attribute? Default: True.
        @type overwrite: boolean
        @param overwrite: Determines wether the saved config.xml values should be overwritten.
                          Default: not self.__update
        """
        if overwrite == None:
            overwrite = not self.__update
        if overwrite:
            if not writeNone:
                if value == None:
                    # remove None attribute
                    try:
                        settingNode.removeAttribute(attrib)
                        self._domChanged |= True
                        return
                    except xml.dom.NotFoundErr:
                        return
            # write attribute
            if settingNode.getAttribute(attrib) != str(value):
                settingNode.setAttribute(attrib, str(value))
                self._domChanged |= True
            
    
    def readNode(self, settingNode):
        """
        Read settingNode of corresponding configVar node in config.xml
        
        @type settingNode: xml.dom.minidom.Node
        @pram settingNode: Node in which the setting params are stored.
        """
        """ OLD CODE
        self.description = settingNode.getAttribute('description')
        self.displayName = settingNode.getAttribute('displayName')
        self.notNone = self._getBooleanFromAttribute(settingNode.getAttribute('notNull'))
        self.group = settingNode.getAttribute('group')
        self.dialog = self._getBooleanFromAttribute(settingNode.getAttribute('dialogEntry'))
        self.directory = self._getBooleanFromAttribute(settingNode.getAttribute('directory'))
        hei = settingNode.getAttribute('height')
        if hei.isalnum():
            self.ctrlHeight = int(hei)
        else:
            self.ctrlHeight = 0
        self.updateFunc = settingNode.getAttribute('updateFunc')
        """
        # Read update Attribute to determine wether
        # to overwrite the default setting values or not
        updateAttributeVal = settingNode.getAttribute('update')
        if not updateAttributeVal:
            settingNode.setAttribute('update', str(self.__update))
            self._domChanged |= True
        else:
            self.__update = self._getBooleanFromAttribute(updateAttributeVal)
        
        self.description = (self.__getSettingValue(self.description, settingNode, 'description') == '#DONT!#' and \
                             [self.description] or \
                             [self.__getSettingValue(self.description, settingNode, 'description')])[0]
        
        self.displayName = (self.__getSettingValue(self.displayName, settingNode, 'displayName') == '#DONT!#' and \
                             [self.displayName] or \
                             [self.__getSettingValue(self.displayName, settingNode, 'displayName')])[0]
        
        self.notNone = (self.__getSettingValue(self.notNone, settingNode, 'notNull', 'bool') == '#DONT!#' and \
                             [self.notNone] or \
                             [self.__getSettingValue(self.notNone, settingNode, 'notNull', 'bool')])[0]
        
        self.group = (self.__getSettingValue(self.group, settingNode, 'group') == '#DONT!#' and \
                             [self.group] or \
                             [self.__getSettingValue(self.group, settingNode, 'group')])[0]
        
        self.dialog = (self.__getSettingValue(self.dialog, settingNode, 'dialogEntry', 'bool') == '#DONT!#' and \
                             [self.dialog] or \
                             [self.__getSettingValue(self.dialog, settingNode, 'dialogEntry', 'bool')])[0]
        
        self.choose = (self.__getSettingValue(self.choose, settingNode, 'chooser', writeNone=False) == '#DONT!#' and \
                             [self.choose] or \
                             [self.__getSettingValue(self.choose, settingNode, 'chooser', writeNone=False)])[0]
        
        self.ctrlHeight = (self.__getSettingValue(self.ctrlHeight, settingNode, 'height', 'int', False) == '#DONT!#' and \
                             [self.ctrlHeight] or \
                             [self.__getSettingValue(self.ctrlHeight, settingNode, 'height', 'int', False)])[0]
        
        self.updateFunc = (self.__getSettingValue(self.updateFunc, settingNode, 'updateFunc', writeNone=False) == '#DONT!#' and \
                             [self.updateFunc] or \
                             [self.__getSettingValue(self.updateFunc, settingNode, 'updateFunc', writeNone=False)])[0]
        
        self.hint = (self.__getSettingValue(self.hint, settingNode, 'hint', writeNone=False) == '#DONT!#' and \
                             [self.hint] or \
                             [self.__getSettingValue(self.hint, settingNode, 'hint', writeNone=False)])[0]
                
        # Save changed DOM
        if self._domChanged:
            self._var.category._save()
            self._domChanged = False
    
    
    def __getSettingValue(self, ivar, settingNode, attrib, _type='str', writeNone=True):
        """
        Read the given attrib from settingNode and return its value
        if self is an 'update' setting.
        If the givven attrib is not yet saved in config.xml, save it's default value and return
        the 'don't update string' #DONT!#
        
        @type ivar: var
        @param ivar: Setting instance Var.
        @type settingNode: xml.dom.minidom.Node
        @param settingNode: Node on which setting attribute is to save.
        @type attrib: string
        @param attrib: Name of attribute.
        @type _type: string
        @param _type: Determines of which type ivar is. Default: 'str'
        @type writeNone: boolean.
        @param writeNone: Write also None value of attribute? Default: True.
        @rtype: str/int/float/boolean
        @return: The saved value if it should be updated, else '#DONT!#'.
        """
        value = settingNode.getAttribute(attrib)
        
        # The xml attrib for this setting value is not yet written
        if value == None or not value:
            # write the in iVar saved default value
            self.__setAttribute(settingNode, attrib, ivar, writeNone, True)
            return '#DONT!#'
        
        # The xml attrib for this setting was yet written, now read it    
        if self.__update:
            if value == 'None' or value == 'none':
                return None
            if value:
                try:
                    if _type == 'int':
                        value = int(value)
                    elif _type == 'float':
                        value = float(value)
                    elif _type == 'bool' or type == 'boolean':
                        value = self._getBooleanFromAttribute(value)
                    elif _type != 'str':
                        raise ValueError("Can't convert setting attribute " + \
                                          str(attrib) + "to type " + str(type) + ".")
                except ValueError, msg:
                    print msg
            return value
        # If still not returned the ivar shouldn't be updated
        return '#DONT!#'
                
    
    def updateView(self, workSpace):
        """
        Calls the update methods of all observers in model.workspace.
        
        @type workSpace: view.workspace.CabelFrame
        @param workSpace: The Cabel view workspace.
        """
        if self.updateFunc:
            workSpace._controller._model.setChanged()
            workSpace._controller._model.notifyObservers(['funCall', self.updateFunc])
    
    
    def _getCtrlLength(self):
        """
        Calculates the length of a 'easy-type' configVars which are
        entered through a TextCtrl (int, float, string).
        
        @rtype: int
        @return: len(ConfigVar.Value)
        """
        if self._var.valueType == 'int' or \
           self._var.valueType == 'float' or \
           self._var.valueType == 'string':
            try:
                length = len(str(self._var.Value))
            except UnicodeEncodeError:
                length = len(unicode(self._var.Value))
            return (100 < length < 350 and [length] or [350])[0]
        else:
            return 0
                
    ctrlLength = property(_getCtrlLength)
    
        
    def _getBooleanFromAttribute(self, attribVal):
        """
        Parse all possible 'string-boolean' xml-attribute values to boolean.
        
        @type attribVal: string
        @param attribVal: In config.xml saved boolean attrib value.
        @rtype: boolean
        @return: boolean value.
        """
        if attribVal == 'true' or attribVal == 'True' or attribVal == '1':
            return True
        else:
            return False
