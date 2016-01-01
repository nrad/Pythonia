import os

class Module(object):
    """
    Module.

    A Module contains its user-defined opcode text and lists of its
    In- and OutVars.

    @type id: integer
    @ivar id: Unique id for module.
    @type name: string
    @ivar name: Name of module/user-defined opcode
    @type description: string
    @ivar description: describes module.
    @type inVars: list
    @ivar inVars: List of input variables.
    @type outVars: list
    @ivar outVars: List of output variables.
    @type globals: list
    @ivar globals: List of Strings for global statements.
    @type opcode: string
    @ivar opcode: Text of user defined opcode for name
    @type instrument: model.instrument.Instrument
    @ivar instrument: Instrument containing this module.
    """

    def __init__(self, name, description="", opcode="", _id=0):
        """
        Standard constructor.

        @type  fullName: string
        @param fullName: Name of module including relative path
        @type  name: string
        @param name: Name of module/user-defined opcode
        @type description: string
        @param description: describes module.
        @type  opcode: string
        @param opcode: Text of user defined opcode for name
        @type  _id: integer
        @param _id: Unique id for module.
        """
        self.fullName = name
        # workaround for platform problem: Saved on windows/linux-mac
        # and opend with linux-mac/windows.
        # os.sep doesn't work for this
        if name.rfind('\\') > 0:
            self.name = name[name.rfind('\\') + 1:]
        elif name.rfind('/') > 0:
            self.name = name[name.rfind('/') + 1:]
        else:
            self.name = name
        self.id = _id
        self.description = description
        self.inVars = []
        self.outVars = []
        self.globals = []
        self.opcode = opcode
        self.instrument = None


    def addInVar(self, inVar):
        """
        add inVar to the list of the module's input-vars.

        @type inVar: model.var.inVar
        @param inVar: new input to the module
        """
        self.inVars.append(inVar)
        
        
    def setInVarValues(self, values):
        """
        Set inVar values.
        
        @type values: list
        @param values: List of tuples each describing a var by its id and value.
        """
        for val in values:
            self.inVars[val[0]].Value = val[1]


    def addOutVar(self, outVar):
        """
        add outVar to the list of the module's output-vars.

        @type outVar: model.var.outVar
        @param outVar: new output of the module
        """
        self.outVars.append(outVar)


    def addGlobal(self, globus, description):
        """
        add globus (global is a fukin' keyword) to the list of the
        module's global-vars.

        nice to save tables in, so that the csoundGenerator can
        extract them and doesn't have to generate one for every
        instance of the module.

        @type globus: str
        @param globus: new global-var for the module as crude csound-code
        @type description: str
        @param description: description for the global-var
        """
        self.globals.append((description, globus))


    def getGlobalAsCsoundCode(self, index):
        """
        Returns the GlobalVar definition as a crude csound-code string.
        If there is a description stored it is appended as a comment.
        
        @type index: int
        @param index: The index of the global.
        @rtype: str
        @return: The global var definition as crude csound-code string
                 with or without comment.
        """
        if self.globals[index][0]:
            return '/* ' + self.globals[index][0] + ' */\n' + self.globals[index][1]
        else:
            return self.globals[index][1]
        
    
    def printInputs(self):
        """
        Print input names, indices, their values and value ranges to
        standard output.
        """
        num = 0
        for v in self.inVars:
            if v.connection:
                print str(num) + ": " + v.type + v.name + " = " \
                      + v.connection.fromVar.module.name \
                      + str(v.connection.fromVar.module.id) \
                      + "." + v.connection.fromVar.type + v.connection.fromVar.name \
                      + "   (" + str(v.min) + " - " + str(v.max) + ")"                
            else:
                print str(num) + ": " + v.type + v.name + " = " + str(v.value) \
                      + "   (" + str(v.min) + " - " + str(v.max) + ")"
            num += 1


    def printOutputs(self):
        """
        Print output names and indices to standard output.
        """
        num = 0
        for v in self.outVars:
            print str(num) + ": " + v.type + v.name
            num += 1

