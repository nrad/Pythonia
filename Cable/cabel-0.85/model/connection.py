class Connection(object):
    """
    Connection between two modules.

    A Connection is defined by its start Var and its end Var.

    @type fromVar: model.var.OutVar
    @ivar fromVar: Start Var of this connection.
    @type toVar: model.var.InVar
    @ivar toVar: End Var of this connection.
    """

    def __init__(self, fromVar, toVar):
        """
        Standard constructor.

        @type  fromVar: model.var.OutVar
        @param fromVar: Start Var of this connection.
        @type  toVar: model.var.InVar
        @param toVar: End Var of this connection.
        """
        self.fromVar = fromVar
        self.toVar = toVar
