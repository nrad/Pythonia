import StringIO
import os
import xml.dom
from xml.dom import minidom
import view.module
import model.module

class XmlGenerator(object):
    """
    XmlGenerator.
    
    Generates Cabel Xml.
    
    @type doc: xml.dom.Document
    @ivar doc: Root Document.
    @type name: string
    @ivar name: Name of the File (without extension '.cw').
    @type filePath: string
    @ivar filePath: Path of the file to save.
    """
    
    
    def __init__(self, fileLocation):
        """
        Standardconstructor.
        
        @type fileLocation: string
        @param fileLocation: Complete path to the save file.
        """
        self.name = fileLocation[fileLocation.rindex(os.path.sep) + 1:fileLocation.rindex('.cw')]
        self.filePath = fileLocation[0:fileLocation.rindex(os.path.sep)]
        self.doc = xml.dom.getDOMImplementation().createDocument(None, 'workspace', None)
        
        
    def getXmlModuleReference(self, mod):
        """
        Returns a xml module reference node.
        
        @type mod: model.module.Module
        @param mod: Model module to create the reference node.
        @rtype: xml.dom.Element
        @return: Xml module reference node.
        """
        # Module root element (<module>)
        moduleNode = self.doc.createElement('moduleReference')
        moduleNode.setAttribute('name', mod.fullName)
        moduleNode.setAttribute('description', mod.description)
        
        # Input Vars (<input>)
        if len(mod.inVars) > 0:
            inputNode = self.doc.createElement('input')
            for i in xrange(0, len(mod.inVars)):
                inVarNode = self.doc.createElement('vardef')
                inVarNode.setAttribute('description', mod.inVars[i].description)
                if mod.inVars[i].max != 32767:
                    inVarNode.setAttribute('max', str(mod.inVars[i].max))
                if mod.inVars[i].min != -32768:
                    inVarNode.setAttribute('min', str(mod.inVars[i].min))
                if mod.inVars[i].digits != 3:
                    inVarNode.setAttribute('digits', str(mod.inVars[i].digits))
                inVarNode.setAttribute('csType', mod.inVars[i].type)
                inVarNode.setAttribute('name', mod.inVars[i].name)
                inputNode.appendChild(inVarNode)
            moduleNode.appendChild(inputNode)
                
        # OutPut Vars (<output>)
        if len(mod.outVars) > 0:
            outputNode = self.doc.createElement('output')
            for o in xrange(0, len(mod.outVars)):
                outVarNode = self.doc.createElement('vardef')
                outVarNode.setAttribute('description', mod.outVars[o].description)
                outVarNode.setAttribute('csType', mod.outVars[o].type)
                outVarNode.setAttribute('name', mod.outVars[o].name)
                outputNode.appendChild(outVarNode)
            moduleNode.appendChild(outputNode)
                
        # Globals (<globa>)
        if len(mod.globals) > 0:
            globalsNode = self.doc.createElement('global')
            for g in xrange(0, len(mod.globals)):
                globalNode = self.doc.createElement('def')
                globalNode.setAttribute('description', mod.globals[g][0])
                globalNode.appendChild(self.doc.createTextNode(mod.globals[g][1]))
                globalsNode.appendChild(globalNode)
            moduleNode.appendChild(globalsNode)
            
        # Opcode (<opcode>)
        opcodeNode = self.doc.createElement('opcode')
        opcodeNode.appendChild(self.doc.createTextNode(mod.opcode))
        moduleNode.appendChild(opcodeNode)
        
        return moduleNode
                
            
    def getXmlModuleInstance(self, mod):
        """
        Returns a Xml module instance node
                
        @type mod: view.module.Module
        @param mod: View module to create the instance node.
        @rtype: xml.dom.Element
        @return: Xml module instance node.
        """
        # Basic Info for the instance node
        moduleNode = self.doc.createElement('moduleInstance')
        moduleNode.setAttribute('name', mod.module.fullName)
        moduleNode.setAttribute('id', str(mod.module.id))
        moduleNode.setAttribute('xPos', str(mod.x))
        moduleNode.setAttribute('yPos', str(mod.y))
        
        # Values of the inputs
        valuesNode = self.doc.createElement('inputs')
        for i in xrange(0, len(mod.module.inVars)):
            valueNode = self.doc.createElement('val')
            valueNode.setAttribute('id', str(i))
            valueNode.setAttribute('value', str(mod.module.inVars[i].Value))
            valueNode.setAttribute('description', str(mod.module.inVars[i].description))
            valuesNode.appendChild(valueNode)
        moduleNode.appendChild(valuesNode)
        
        return moduleNode
        
        
    def getXmlConnections(self, cons):
        """
        Returns Xml connection nodes
        
        @type cons: list
        @param cons: List of view connections.
        @rtype: xml.dom.Element
        @return: Xml connections node.
        """
        connectionsNode = self.doc.createElement('connections')
        for c in xrange(0, len(cons)):
            conNode = self.doc.createElement('connection')
            conNode.setAttribute('outModule', str(cons[c].outModule.module.id))
            conNode.setAttribute('inModule', str(cons[c].inModule.module.id))
            conNode.setAttribute('outputNum', str(cons[c].outputNum))
            conNode.setAttribute('inputNum', str(cons[c].inputNum))
            connectionsNode.appendChild(conNode)
        
        return connectionsNode
        
        
    def getXmlAdditionalInfo(self, workspace):
        """
        Returns node with addiotional Information to be saved.
        
        @type workspace: view.workspace.CabelFrame
        @param modules: The view workspace.
        @rtype: xml.dom.Element
        @return: Xml node.
        """
        additionalNode = self.doc.createElement('additionalInfo')
        
        # actual selected Module
        actModuleNode = self.doc.createElement('param')
        actModuleNode.setAttribute('name', 'actualModule')
        if workspace._controller._actModule:
            actModuleId = str(workspace._controller._actModule.module.id)
        else:
            actModuleId = ''
        actModuleNode.setAttribute('value', actModuleId)
        additionalNode.appendChild(actModuleNode)
        
        # last module id
        lastIdNode = self.doc.createElement('param')
        lastIdNode.setAttribute('name', 'lastModuleId')
        lastIdNode.setAttribute('value', str(workspace._controller._model._id))
        additionalNode.appendChild(lastIdNode)
        
        return additionalNode
        
        
    def getXml(self, workspace):
        """
        Returns a Xml node with reference-, instance- and connections-nodes. 
        
        @type workspace: view.workspace.CabelFrame
        @param modules: The view workspace.
        @rtype: xml.dom.Element
        @return: Xml node.
        """
        modules = workspace._modules
        connections = workspace._connections
        usedModelModules = []
        
        # Workspace
        workspaceNode = self.doc.documentElement
        
        referenceNode = self.doc.createElement('referencesModules')
        instanceNode = self.doc.createElement('instancesModules')
        
        for viewMod in modules:
            modelMod = viewMod.module
            
            # If not yet done create xml module reference
            if not modelMod.fullName in usedModelModules:
                usedModelModules.append(modelMod.fullName)
                referenceNode.appendChild(self.getXmlModuleReference(modelMod))
                
            # And the instances
            instanceNode.appendChild(self.getXmlModuleInstance(viewMod))
            
        connectionsNode = self.getXmlConnections(connections)
        additionalNode = self.getXmlAdditionalInfo(workspace)
        
        workspaceNode.appendChild(referenceNode)
        workspaceNode.appendChild(instanceNode)
        workspaceNode.appendChild(connectionsNode)
        workspaceNode.appendChild(additionalNode)
        
        return workspaceNode
        
        
    def writeWorkspace(self, workspace):
        """
        Writes the workspace to a xml File.
        
        @type workspace: view.workspace.CabelFrame
        @param workspace: The workspace to be saved.
        @rtype: [boolean,string]
        @return: [True, ''] if saved, [False, 'Message'] if error.
        """
        fileLocation = os.path.join(self.filePath, self.name + '.cw')
        try:
            savedworkspaceFile = file(fileLocation, 'w')
        except IOError, eMsg:
            return [False, eMsg]
        
        rootElement = self.getXml(workspace)
        rootElement.setAttribute('name', self.name)
        
        # linesep workaround
        stringBuf = StringIO.StringIO()
        self.doc.writexml(stringBuf, encoding='utf-8', newl='\n', addindent='\t')
        lines = []
        for line in stringBuf.getvalue().split('\n'):
            if not line.isspace():
                lines.append(line + '\n')
        savedworkspaceFile.writelines(lines)
        
        savedworkspaceFile.close()
        
        workspace._saved = True
        workspace.fileName = self.name
        workspace.filePath = self.filePath
        workspace._controller._pushToRecentFiles(fileLocation)
        workspace.workspace.Refresh()
        return [True, '']
        