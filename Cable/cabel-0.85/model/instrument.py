class Instrument(object):
    """
    Instrument.

    An Instrument contains a list of included modules and their
    connections.

    @type modules: list
    @ivar modules: Modules contained in intrument.
    @type connections: list
    @ivar connections: Connections between intrument modules.
    """

    def __init__(self):
        """
        Standard constructor.
        """
        self.modules = []
        self.connections = []


    def printModules(self):
        """
        Print contained modules and their indices to standard output.
        """
        num = 0
        for m in self.modules:
            print str(num) + ": " + m.name + str(m.id)
            num += 1


    def printConnections(self):
        """
        Print connections and their indices to standard output.
        """
        num = 0
        for c in self.connections:
            print str(num) + ": " \
                  + c.fromVar.module.name + str(c.fromVar.module.id) \
                  + "[" + str(self.modules.index(c.fromVar.module)) + "]"\
                  + "." + c.fromVar.type + c.fromVar.name \
                  + " -> " \
                  + c.toVar.module.name + str(c.toVar.module.id) \
                  + "[" + str(self.modules.index(c.toVar.module)) + "]"\
                  + "." + c.toVar.type + c.toVar.name
            num += 1
