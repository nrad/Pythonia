from model.instrument import Instrument
from model.connection import Connection
from model.xmlReader import XmlModuleReader
from model.xmlReader import XmlWorkspaceReader
from model.observer import Observable
from model.csound import CsoundGenerator
import tools.config


class ConnectionError(Exception):
    """
    ConnectionError.

    Exception if connection fails.
    """
    pass


class Workspace(Observable):
    """
    Workspace.

    Manages list of instruments and connections between modules and
    module-IDs.

    @type _id: integer
    @cvar _id: Last free unique id for modules.
    @type config: tools.config.Config
    @cvar config: Interface to config categories.
    @type _modulesDict: dict
    @cvar _modulesDict: Maps ids to corresponding modules.
    @type instruments: list
    @ivar instruments: List of intruments.
    @type _csoundGenerator: model.csound.CsoundGenerator
    @ivar _csoundGenerator: Csound Generator.
    """

    _id = 0
    config = tools.config.Config()

    def __init__(self):
        """
        Standard constructor.
        """
        Observable.__init__(self)
        self.instruments = []
        self._modulesDict = {}
        self._csoundGenerator = CsoundGenerator(self)
        self.ioTextCtrl = None


    def createWorkspace(self, workspaceReader = None):
        """
        Create a Workspace from a workspaceReader object or a new, empty one.
        Informes observers.
        
        @type workspaceReader: model.xmlReader.XmlWorkspaceReader
        @param workspaceReader: Reads a complete cabel workspace from .cw files.
        """
        # Delete old Workspace
        self.instruments = []
        Workspace._id = 0
        self._modulesDict = {}
        
        if workspaceReader:
            # Suspend Observers
            self.suspendObservation()        
            
            # Read relevant Nodes from the Workspace
            modulesDict = workspaceReader.modelModules
            connections = workspaceReader.connections
            
            # Add Modules
            for module in modulesDict.values():
                self.addModule(module)
    
            # And connect them according to saved connections
            for c in connections:
                self.connect2(c['fromModuleId'], c['fromVarId'], c['toModuleId'], c['toVarId'])
                
            # Set last module id
            Workspace._id = int(workspaceReader.additionalInfo['lastModuleId'])
            
            # Resume Observators
            self.resumeObservation()
        
        # Notify Observers
        self.setChanged()
        arg = ['loadWorkspace', workspaceReader]
        self.notifyObservers(arg)
        
        return self
        

    def _getNextId(self):
        """
        Return next free ID for modules.
        """
        Workspace._id += 1
        return Workspace._id


    def addModule(self, module):
        """
        Add module to workspace and create a
        new instrument which includes this module. Adds entry in
        self._modulesDict dictionary.

        @type  module: model.module.Module
        @param module: Module to be added.
        """
        instr = Instrument()
        self.instruments.append(instr)
        module.instrument = instr
        instr.modules.append(module)
        self._modulesDict[module.id] = module

        self.setChanged()
        arg = ['add', module]
        self.notifyObservers(arg)

    
    def addXmlModule(self, moduleName):
        """
        Reads an xml-module with an unique id and adds it to the workspace...
        
        @type  moduleName: str
        @param moduleName: the name of the module which should be
                           defined in a moduleName.xml File in the
                           searchPath of the moduleReader ('modules/'
                           by default)
        @raise ModuleNotFoundError: if the given moduleName-module
                                    couldn't be found in the searchpath
        @raise ModuleDefinitionError: if the given moduleName-xml-module
                                      wasn't valid
        @rtype : model.module.Module
        @return: Returns added module.
        """
        mr = XmlModuleReader()
        module = mr.getModule(moduleName)
        module.id = self._getNextId()
        self.addModule(module)
        return module


    def removeModule(self, module):
        """
        Remove module and all its ingoing and outgoing connections
        from workspace. Removes entry in self._modulesDict dictionary.

        @type  module: model.module.Module
        @param module: Module which should be removed.
        """
        # Get all in- and outgoing connections of module
        connections = []
        for c in module.instrument.connections:
            if c.fromVar.module == module:
                connections.append(c)
            if c.toVar.module == module:
                connections.append(c)

        # Disconnect all connections
        for c in connections:
            self.disconnect(c)

        # Remove module and its instrument
        instr = module.instrument
        instr.modules.remove(module)
        self.instruments.remove(instr)
        self._modulesDict[module.id] = None

        self.setChanged()
        arg = ['remove', module, connections]
        self.notifyObservers(arg)


    def connect2(self, fromModuleId, fromVarId, toModuleId, toVarId):
        """
        Same implementation, different call than connect(fromVar, toVar).
        @type fromModuleId: int
        @param fromModuleId: Module id in the workspace.
        @type fromVarId: int
        @param fromVarId: Output number of the fromModule.
        @type toModuleId: int
        @param toModuleId: Module id in the workspace.
        @type toVarId: int
        @param toVarId: Input number of the fromModule.
        """
        fromVar = self.getModuleById(fromModuleId).outVars[fromVarId]
        toVar = self.getModuleById(toModuleId).inVars[toVarId]
        self.connect(fromVar, toVar)

    
    def connect(self, fromVar, toVar):
        """
        Connect fromVar to toVar, add all modules of
        toVar-module-instrument to instrument of fromVar-module and
        sort modules list in the correct order for csound code
        generation.

        @type  fromVar: model.var.OutVar
        @param fromVar: Startpoint of connection.
        @type  toVar: model.var.InVar
        @param toVar: Endpoint of connection.
        @raise ConnectionError: If connection from module to itself.
        @rtype : model.Connection.connection
        @return: New connection.
        """
        if fromVar.module == toVar.module:
            raise ConnectionError, "Can\'t connect module with itself"

        if fromVar.type == "a" and toVar.type == "i":
            raise ConnectionError, \
                  "Can\'t connect audio rate output to initialisation rate input"

        if fromVar.type == "i" and toVar.type == "a":
            raise ConnectionError, \
                  "Can\'t connect initialisation rate output to audio rate input"

        if toVar.connection:
            raise ConnectionError, "There's already a connection to this input "

        newConnection = Connection(fromVar, toVar)

        targetInstr = fromVar.module.instrument
        leftInstr = toVar.module.instrument
        targetInstr.connections.append(newConnection)
        toVar.connection = newConnection

        # Append all modules and connections of leftInstr to
        # targetInstr and remove leftInstr from workspace
        if targetInstr != leftInstr:
            for m in leftInstr.modules:
                m.instrument = targetInstr
                targetInstr.modules.append(m)
            for c in leftInstr.connections:
                targetInstr.connections.append(c)
            self.instruments.remove(leftInstr)
        else:
            if targetInstr.modules.index(fromVar.module) \
               > targetInstr.modules.index(toVar.module):
                # Place toVar module behind fromVar module and close
                # the gap
                fromIdx = targetInstr.modules.index(fromVar.module)
                toIdx = targetInstr.modules.index(toVar.module)
                targetInstr.modules \
                                    = targetInstr.modules[:toIdx] \
                                    + targetInstr.modules[(toIdx+1):fromIdx] \
                                    + [targetInstr.modules[fromIdx], \
                                       targetInstr.modules[toIdx]] \
                                    + targetInstr.modules[(fromIdx+1):]
        self.setChanged()
        arg = ['connect', newConnection]
        self.notifyObservers(arg)
        
        return newConnection


    def disconnect(self, connection):
        """
        Delete connection. Test if we need to create a new instrument
        for the disconnected modules.

        @type  connection: model.connection.Connection
        @param connection: Connection which should be deleted.
        """
        fromVar = connection.fromVar
        toVar = connection.toVar
        toVar.module.instrument.connections.remove(connection)
        toVar.connection = None

        # Start breadth first search from toVar.module
        connectedModules = self._getConnectedModules(toVar.module)
        
        # If fromVar.module is in queue we're done, else insert all
        # modules from connectedModules queue into new instrument
        if not fromVar.module in connectedModules:
            oldInstr = toVar.module.instrument
            newInstr = Instrument()
            self.instruments.append(newInstr)

            oldInstrModules = list(oldInstr.modules)
            
            for m in oldInstrModules:
                if m in connectedModules:
                    m.instrument = newInstr
                    newInstr.modules.append(m)
                    oldInstr.modules.remove(m)

            for c in list(oldInstr.connections):
                if c.fromVar.module in connectedModules:
                    newInstr.connections.append(c)
                    oldInstr.connections.remove(c)

        self.setChanged()
        arg = ['disconnect', connection]
        self.notifyObservers(arg)


    def setIoTextCtrl(self, control):
        """
        """
        self.ioTextCtrl = control


    def printInstruments(self):
        """
        Print instruments with their contained modules and indices to
        standard output.
        """
        num = 0
        for i in self.instruments:
            print str(num) + ":"
            for m in i.modules:
                print "   " + m.name + str(m.id)
            num += 1


    def _getConnectedModules(self, startModule):
        """
        Nondirectional breadth first search for connected modules
        starting with startMod.

        @type  startModule: model.module.Module
        @param startModule: Start module for search.
        @rtype : list
        @return: List of connected modules.
        """
        visitedModules = [startModule]
        workQueue = [startModule]

        while workQueue:

            actMod = workQueue.pop()
            
            # Get all in- and outgoing connections of actMod
            connections = []
            for c in actMod.instrument.connections:
                if c.fromVar.module == actMod:
                    connections.append(c)
                if c.toVar.module == actMod:
                    connections.append(c)

            # Test all adjacent modules if we already visited them
            for c in connections:
                adjacentMod = c.fromVar.module
                if adjacentMod == actMod:
                    adjacentMod = c.toVar.module
                
                if not adjacentMod in visitedModules:
                    workQueue.append(adjacentMod)
                    visitedModules.append(adjacentMod)

        return visitedModules


    def getModuleById(self, id):
        """
        Returns module with this id.

        @type  id: int
        @param id: Id of wanted module.
        @rtype : model.module.Module
        @return: Module with this id or None if not found.
        """
        if self._modulesDict.has_key(id):
            return self._modulesDict[id]
        return None


    def setValue(self, var, value):
        """
        Set var to value.

        @type  var: model.var.InVar
        @param var: Variable which we want to change.
        @type  value: float
        @param value: New value for variable.
        @raise VarValueOutOfRangeError: If new value is out of range.
        """
        # Set only if value has changed
        if var.Value != value:
            var.Value = value

            self.setChanged()
            arg = ['set', var, value]
            self.notifyObservers(arg)


    def getValue(self, var):
        """
        Return actual value of var.

        @type  var: model.var.InVar
        @param var: Variable whose value we want.
        @rtype : float
        @return: Value of var.
        """
        return var.value


    def getModuleDescription(self, module):
        """
        Return description string of module.

        @type  module: model.module.Module
        @param module: Module whose description we want.
        @rtype : str
        @return: Description of module.
        """
        return module.description


    def getVarDescription(self, var):
        """
        Return description string of variable.

        @type  var: model.module.Module
        @param var: Module whose description we want.
        @rtype : str
        @return: Description of module.
        """
        return var.description


    def play(self):
        """
        Starts csound in separate process.
        """        
        # Start Csound process in csoundGenerator
        if self._csoundGenerator.play():
            # Notify observers of workspace of the change taken effect
            self.setChanged()
            arg = ['play', None]
            self.notifyObservers(arg)
        
        
    def stop(self):
        """
        Stops csound process.
        """
        # Stop Csound process if there is one running
        if self._csoundGenerator.stop():
            # Notify observers of workspace of the change taken effect
            self.setChanged()
            arg = ['stop', None]
            self.notifyObservers(arg)
            
            
    def isPlaying(self):
        """
        Return wether cabel is in playing state or not.
        """
        return self._csoundGenerator._playing
