class VarValueOutOfRangeError(Exception):
    """
    VarValueOutOfRangeError.

    Exception if new value for InVar is out of rage.
    """
    pass


class Var(object):
    """
    Module variable.

    Var contains its corresponding module, variable name and variable
    type. This class serves as interface for special variables.

    @type module: Module
    @ivar module: Module to which this variable belongs.
    @type name: string
    @ivar name: Name of variable.
    @type type: string
    @ivar type: Type of variable.
    """

    def __init__(self, module, name, _type, description=''):
        """
        Standard constructor.

        @type  module: model.module.Module
        @param module: Module to which this variable belongs.
        @type  name: string
        @param name: Name of variable.
        @type  _type: string
        @param _type: Type of variable.
        @type description: string
        @var  description: describes the meaning of variable.
        
        """
        self.module = module
        self.name = name
        self.type = _type
        self.description = description


#---------------------------------------------------------------------------

class InVar(Var):
    """
    Module input variable.

    Special Var for input variables, which can set its actual value in
    the range min to max if not connected.

    @type min: float
    @ivar min: Minimal allowed value for value.
    @type max: float
    @ivar max: Maximal allowed value for value.
    @type value: float
    @ivar value: Initial value of variable.
    @type digits: int
    @ivar digits: Number of digits (or presicion) for the value.
    @type connection: model.connection.Connection
    @ivar connection: Link to connection to this var.
    """

    def __init__(self, module, name, _type, description='', _min=-32768, _max=32767, value=0, digits = 3):
        """
        Standard constructor.

        @type  module: model.module.Module
        @param module: Module to which this variable belongs.
        @type  name: string
        @param name: Name of variable.
        @type  _type: string
        @param _type: Type of variable.
        @type  _min: float
        @param _min: Minimal allowed value for value.
        @type  _max: float
        @param _max: Maximal allowed value for value.
        @type  digits: int
        @param digits: Number of digits (or presicion) for the value.
        @type  value: float
        @param value: Initial value of variable.
        """
        Var.__init__(self, module, name, _type, description)
        self.min = _min
        self.max = _max
        self.value = value
        self.digits = digits
        self.connection = None
        
        
    def __setValue(self, value):
        """
        Set function for the Value property.
        
        @type: int
        @param: Value of the InVar.
        @raise VarValueOutOfRangeError: If new value is out of range.
        """
        if value < self.min or value > self.max:
            format = "(%." + str(self.digits) + "f - %." + str(self.digits) + "f)"
            rangeText = " " + str(format % (self.min, self.max))
            raise VarValueOutOfRangeError, \
                  "New value for " + self.module.name + str(self.module.id) \
                  + "." + self.type + self.name + " is out of allowed range" \
                  + rangeText
        self.value = value
        
        
    def __getValue(self):
        """
        Get accessor for the value attrib of InVar.
        
        @rtype: int
        @return: The Value of the InVar.
        """
        return self.value
        
        
    Value = property(__getValue, __setValue)

#---------------------------------------------------------------------------

class OutVar(Var):
    """
    Module output variable.

    At the moment this is just a wrapper for Var with special name.
    
    @type description: string
    @ivar description: describes the meaning of the input-var
    """

    def __init__(self, module, name, _type, description=''):
        """
        Standard constructor.

        @type  module: model.module.Module
        @param module: Module to which this variable belongs.
        @type  name: string
        @param name: Name of variable.
        @type  _type: string
        @param _type: Type of variable.
        """
        Var.__init__(self, module, name, _type, description)
