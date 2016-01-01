import os
from xml.dom import minidom

import model.var
from model.var import InVar
from model.var import OutVar
import model.module
import view.module
import model.workspace
import tools.config


class ModuleNotFoundError(Exception):
    """
    ModuleNotFoundError.

    Exception if the searched Module wasn't found.
    """
    pass

    
class ModuleDefinitionError(Exception):
    """
    ModuleDefinitionError.
    
    Exception if there is any syntax error in the module xml-file.
    """
    pass


class XmlModuleReader(object):
    """
    XmlModuleReader.
    
    Reads XML modules.

    @type searchPath: str
    @ivar searchPath: Path to directory with XML modules files.
    """
    
    def __init__(self):
        """
        Standard Constructor.
        """
        
        configDir = model.workspace.Workspace.config.directories
        # Relative or absolut path?
        path = configDir.getVal(tools.config.Directories.MODULES)
        if path.startswith('/') or path.find(':') > 0:
            # absolut path
            self.searchPath = path
        else:
            self.searchPath = os.path.join(os.getcwd(), path)


    def getModule(self, name):
        """
        searches for the the xml-file name.xml in the searchpath directory and
        tries to instanciate a module object from it.
        
        @type  name: str
        @param name: Name of the Module we want to instanciate.
        @raise ModuleNotFoundError: If the Xml-File name.xml doesn't exist.
        @rtype : model.module.Module
        @return: Returns new module object.
        @raise ModuleDefinitionError: If the Xml-File isn't valid
        """
        
        # Tries to open the xmlModule file.
        # If it doesn't exist, throws ModuleNotFoundError
        try:
            rootNode = minidom.parse(os.path.join(self.searchPath, name + ".xml")).documentElement
        except IOError:
            raise ModuleNotFoundError ("""Can't find the desired Module """ + \
                os.path.join(self.searchPath, name + ".xml"))
                
        return self.getModuleFromNode(rootNode, name)



    def getModuleFromNode (self, moduleNode, name = ''):
        """
        """
        # Get the description of the module
        modDescr = moduleNode.getAttribute('description')
        
        # If the param 'name' is empty, read it's name out of the name xml-attribute
        if name == '':
            name = moduleNode.getAttribute('name')
        
        # Try to read the opcode-node and instanciate a Module object
        try:
            opcodeNode = moduleNode.getElementsByTagName('opcode')[0]
        
            # syntax check; doesn't make much sense, but... shows good intentions
            if opcodeNode.nodeType == opcodeNode.ELEMENT_NODE:
                # if the first child of opcode-node is a text-node it will be added 
                # to the opcode; 
                if opcodeNode.childNodes[0].nodeType == opcodeNode.TEXT_NODE:
                    opcode = opcodeNode.childNodes[0].nodeValue
                else:
                    raise ModuleDefinitionError("""Error in the following node:\n""" + \
                        opcodeNode.toxml() + """\n Only text-childnodes allowed!""")
            else:
                raise ModuleDefinitionError("""Error in the following node:\n""" + \
                        opcodeNode.toxml())

            module = model.module.Module(name, modDescr, opcode)
        # the opcode-node is empty. Instanciate an empty Module object
        except IndexError:
            module = model.module.Module(name, modDescr)
                
        # Try to read the input-node and add his vardef children to the
        # instanciated module
        try:
            inputNode = moduleNode.getElementsByTagName('input')[0]

            for indefNode in inputNode.childNodes:
                if indefNode.nodeType == indefNode.ELEMENT_NODE:
                    if indefNode.nodeName == 'vardef':
                        varName = indefNode.getAttribute('name')
                        varType = indefNode.getAttribute('csType')
                        input= InVar(module, varName, varType)
                        
                        varDescr = indefNode.getAttribute('description')
                        if (varDescr):
                            input.description = varDescr
                        varMin = indefNode.getAttribute('min')
                        if (varMin):
                            input.min = float(varMin)
                        varMax = indefNode.getAttribute('max')
                        if (varMax):
                            input.max = float(varMax)
                        varVal = indefNode.getAttribute('value')
                        if (varVal):
                            input.value = float(varVal)
                        varDigis = indefNode.getAttribute('digits')
                        if (varDigis):
                            input.digits = int(varDigis)
                        
                        module.addInVar(input)
        # if there are no invars no pasa nada
        except IndexError:
            pass
            
        # Try to read the ouput-node and add his vardef children to the
        # instanciated module
        try:
            outputNode = moduleNode.getElementsByTagName('output')[0]

            for outdefNode in outputNode.childNodes:
                if outdefNode.nodeType == outdefNode.ELEMENT_NODE:
                    if outdefNode.nodeName == 'vardef':
                        varName = outdefNode.getAttribute('name')
                        varType = outdefNode.getAttribute('csType')
                        output = OutVar(module, varName, varType)
                        
                        varDescr = outdefNode.getAttribute('description')
                        if (varDescr):
                            output.description = varDescr
                        
                        module.addOutVar(output)
        # if there are no outvars no pasa nada
        except IndexError:
            pass
        
        # Try to read the global-node and add his def children to the
        # instanciated module
        try:
            globalNode = moduleNode.getElementsByTagName('global')[0]
        
            for gdefNode in globalNode.childNodes:
                if gdefNode.nodeType == gdefNode.ELEMENT_NODE:
                    if gdefNode.nodeName == 'def':
                        try:
                            if gdefNode.childNodes[0].nodeType == gdefNode.TEXT_NODE:
                                gdescr = gdefNode.getAttribute('description')
                                module.addGlobal(gdefNode.childNodes[0].nodeValue.strip(), gdescr)
                            else:
                                raise ModuleDefinitionError( \
                                    """Error in the following node:\n""" \
                                    + gdefNode.childNodes[0].toxml() \
                                    + """\n It has to be a text-node!""")
                        # If the def-node is empty- joder, pues no pasa nada
                        except IndexError:
                            pass
        # if there are no global defs no pasa nada
        except IndexError:
            pass

        return module        

        
    
    def getModulesObjects(self, tree=True):
        """
        Return list of modules with realtive paths as names.
        
        @type  tree: bool
        @param tree: Build tree of modules (recursive list of tuples).
        """
        return self._getPathModules(self.searchPath, tree, False)

    
    def getModules(self, tree=True):
        """
        Return list of modules with their names.
        
        @type  tree: bool
        @param tree: Build tree of modules (recursive list of tuples).
        """
        return self._getPathModules(self.searchPath, tree, True)


    def _getPathModules(self, searchPath, tree, onlyNames):
        """
        Searches in searchPath and its subdirectories for xml Files.
        Returns a list with tuples. The 1st Value is the Name of the
        found Element to represent.
        The 2nd Value is
        a) if the Element is a xml file:
            1) (onlyNames=True)  the relative Path to the xml Module
            2) (onlyNames=False) a instanciated xml Module     
        b) if the Element is a directory:
            other list of tuples (recursive)

        @type  searchPath: str
        @param searchPath: Path to search for modules.
        @type  tree: bool
        @param tree: Build tree of modules (recursive list of tuples).
        @type  onlyNames: bool
        @param onlyNames: Show only name of module, not realtive path.
        @rtype : list
        @return: Sorted (by alohabet and dirs) List of tuples of modules
                 in searchPath.
        """
        files = []
        dirs = []
        pathContent = os.listdir(searchPath)
        pathContent.sort()
        for c in pathContent:
            # Ignore some directories
            if c in ['CVS']:
                continue
            path = os.path.join(searchPath, c)
            if os.path.isfile(path) and c.rfind('.xml') > 0:
                relPathToXmlModule = os.path.join(path)[len(self.searchPath) \
                                                        + len(os.path.sep):]
                if onlyNames:
                    files.append((c[0:c.rfind('.xml')],
                                  relPathToXmlModule[0:relPathToXmlModule.rfind('.xml')]))
                else:
                    files.append((c[0:c.rfind('.xml')],
                                  self.getModule(relPathToXmlModule[0:relPathToXmlModule.rfind('.xml')])))
            elif os.path.isdir(path):
                tmp = self._getPathModules(path, tree, onlyNames)
                if tmp != None:
                    if tree:
                        dirs.extend([(c, tmp)])
                    else:
                        dirs.extend(tmp)
                else:
                    return None
            else:
                continue
        return dirs + files
        

class XmlWorkspaceReader(object):
    """
    XmlWorkspaceReader.
    
    Reads Xml Workspace files (*.cw)
    
    @type fileName: string
    @ivar fileName: Name of the saved workspace file without extension .cw
    @type filePath: string
    @ivar filePath: Path to the saved workpace file.
    @type rootNode: xml.dom.Node
    @ivar rootNode: The root node of the saved workspace file.
    @type additonalInfo: dictionary.
    @ivar additionalInfo: A dictionary mapping additionalInfo
                          Parameter names to its values (string)
    @type instances: dictionary.
    @ivar instances: A dictionary mapping tuples (moduleName [string], moduleId [int])
                     to moduleInstance Nodeswith the syntax:
                     <moduleInstance id="2" name="ChorusOscils" xPos="442" yPos="272">
                        <inputs>
                            <val id="0" value="0"/>
                            <val id="1" value="0"/>
                        </inputs>
                    </moduleInstance>
    @type references: dictionary
    @ivar references: A dictionary mapping moduleNames to module Nodes with the same
                      xml syntax as used for the module defintions.
    @type connections: list
    @ivar connections: A list of dictionaries with the keys:
                        'fromModuleId',
                        'fromVarId',
                        'toModuleId' and 
                        'toVarId'
                       for the connections saved in .
                       Its value types are int.
    @type modelModules: dictionary
    @ivar modelModules: Dictionary mapping ids (int) to model modules in the saved workspace.
    @type viewModules: dictionary
    @ivar viewModules: Dictionary mapping model modules to their corresponding view modules.
    """
    
    def __init__(self, fileLocation, controller):
        """
        Standardconstructor.
        
        @type fileLocation: string
        @param fileLocation: Path to a saved workspace file.
        @type controller: view.controller.CabelController
        @param controller: CabelController.
        """
        self.fileName = fileLocation[fileLocation.rindex(os.path.sep) + 1:fileLocation.rindex('.cw')]
        self.filePath = fileLocation[0:fileLocation.rindex(os.path.sep)]
        
        # Tries to open the xmlModule file.
        # If it doesn't exist, throws ModuleNotFoundError
        try:
            self.rootNode = minidom.parse(fileLocation).documentElement
        except IOError:
            raise ModuleNotFoundError ("""Can't find the desired Workspace """ + \
                fileLocation)
                
        self.additionalInfo = self.__getAdditionalInfo()
        
        self.instances = self.__getInstancesModules()
        self.references = self.__getReferencesModules()
        
        self.connections = self.__getConnections()
        self.modelModules = self.__getModelModules()
        self.viewModules = self.__getViewModules(controller)
        

    def __getInstancesModules(self):
        """
        Read the 'moduleInstance' nodes of the saved workspace file.
        
        @rtype: dictionary.
        @return: A dictionary mapping tuples (moduleName [string], moduleId [int])
                 to moduleInstance Nodeswith the syntax:
                     <moduleInstance id="2" name="ChorusOscils" xPos="442" yPos="272">
                        <inputs>
                            <val id="0" value="0"/>
                            <val id="1" value="0"/>
                        </inputs>
                    </moduleInstance> 
        """
        instances = {}
        
        instancesNode = self.rootNode.getElementsByTagName('instancesModules')[0]
        
        for instance in instancesNode.childNodes:
            if instance.nodeType == instance.ELEMENT_NODE:
                if instance.nodeName == 'moduleInstance':
                    instanceName = instance.getAttribute('name')
                    instanceId = int(instance.getAttribute('id'))
                    index = (instanceName, instanceId)
                    instances[index] = instance
        return instances
        
        
    def __getReferencesModules(self):
        """
        Read 'moduleReference' Nodes from saved workspace file.
        
        @rtype: dictionary
        @return: A dictionary mapping moduleNames to module Nodes with the same
                 xml syntax as used for the module defintions.
        """
        references = {}
        
        referencesNode = self.rootNode.getElementsByTagName('referencesModules')[0]
        
        for reference in referencesNode.childNodes:
            if reference.nodeType == reference.ELEMENT_NODE:
                if reference.nodeName == 'moduleReference':
                    references[reference.getAttribute('name')] = reference
                    
        return references
        
        
    def __getModelModules(self):
        """
        Create a dictionary mapping module ids (int) to all the
        model module instances on the saved workspace.
        
        @rtype: dictionary
        @return: Dictionary mapping ids (int) to model modules.
        """
        modelModules = {}
        
        moduleReader = XmlModuleReader()
        
        for instanceItem in self.instances.items():
            # get model.module.Module from reference node
            module = moduleReader.getModuleFromNode(self.references[instanceItem[0][0]])
            # set module id
            module.id = instanceItem[0][1]
            # Set inputVar values of module
            try:
                module.setInVarValues(self.__getInputValues(instanceItem[1]))
            except model.var.VarValueOutOfRangeError, msg:
                # TODO: Error Handling?
                print msg
            # add module object to id -> module dictionary
            modelModules[instanceItem[0][1]] = module
            
        return modelModules
    
    
    def __getViewModules(self, controller):
        """
        Create a dictionary mapping model module instances to their
        view module instances saved.
        
        @type controller: view.controller.CabelController
        @param controller: CabelController.
        @rtype: dictionary
        @return: Dictionary mapping ids to their 
                 corresponding view modules.
        """
        viewModules = {}
        
        for modelModuleItem in self.modelModules.items():
            index = (modelModuleItem[1].fullName, modelModuleItem[0])
            instanceNode = self.instances[index]
            
            x = int(instanceNode.getAttribute('xPos'))
            y = int(instanceNode.getAttribute('yPos'))
            
            viewModules[modelModuleItem[0]] = view.module.Module(x, y, modelModuleItem[1], controller)

        return viewModules
        
        
    def __getConnections(self):
        """
        Read the 'connections' node of saved workspace file.
        
        @rtype: list of dictionaries.
        @return: A list of dictionaries with the keys:
                        'fromModuleId',
                        'fromVarId',
                        'toModuleId' and 
                        'toVarId'
                 for the connections saved in.
                 Its value types are int.
        """
        connectionsNode = self.rootNode.getElementsByTagName('connections')[0]
        
        connections = []
        
        for connection in connectionsNode.childNodes:
            if connection.nodeType == connection.ELEMENT_NODE:
                if connection.nodeName == 'connection':
                    fromModuleId = connection.getAttribute('outModule')
                    fromVarId = connection.getAttribute('outputNum')
                    toModuleId = connection.getAttribute('inModule')
                    toVarId = connection.getAttribute('inputNum')
                    connections.append({'fromModuleId': int(fromModuleId), \
                                        'fromVarId': int(fromVarId), \
                                        'toModuleId': int(toModuleId), \
                                        'toVarId': int(toVarId)})
        
        return connections
        
        
    def __getAdditionalInfo(self):
        """
        Read 'additionalInfo' node of saved workspace file.
        
        @rtype: dictionary
        @return: A dictionary of name, value pairs. Both are of type string.
        """
        additionalNode = self.rootNode.getElementsByTagName('additionalInfo')[0]
        
        additionalInfo = {}
        
        for infoNode in additionalNode.childNodes:
            if infoNode.nodeType == infoNode.ELEMENT_NODE:
                if infoNode.nodeName == 'param':
                    name = infoNode.getAttribute('name')
                    value = infoNode.getAttribute('value')
                    additionalInfo[name] = value
                    
        return additionalInfo
        
        
    def __getInputValues(self, instanceNode):
        """
        Read 'inputs' node of module instance node.
        
        @rtype: list
        @return: List of tuples describing a inputvar by its id and value.
        """
        inputsNode = instanceNode.getElementsByTagName('inputs')[0]
        
        inputs = []
        
        for valNode in inputsNode.childNodes:
           if valNode.nodeType == valNode.ELEMENT_NODE:
               if valNode.nodeName == 'val':
                   id = int(valNode.getAttribute('id'))
                   value = float(valNode.getAttribute('value'))
                   inputs.append((id, value))
                   
        return inputs
