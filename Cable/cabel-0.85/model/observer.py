class Observer(object):
    """
    Observer.

    A class can inherit from Observer interface when it wants to be
    informed of changes in observable objects.
    """

    def __init__(self):
        """
        Standard constructor.
        """
        pass


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
        pass


#---------------------------------------------------------------------------

class Observable(object):
    """
    Observable.

    This class represents an observable object, or "data"
    in the model-view paradigm. It can be subclassed to represent an
    object that the application wants to have observed.  An observable
    object can have one or more observers. After an observable
    instance changes, an application calling the Observable's
    notifyObservers method causes all of its observers to be notified
    of the change by a call to their update method.

    @type _changed: bool
    @ivar _changed: Flag if state of Observable has changed.
    @type _observers: Observer
    @ivar _observers: List of observers to update if Observable has changed.
    """

    def __init__(self):
        """
        Standard constructor.
        """
        self._changed = False
        self._suspended = False
        self._observers = []


    def addObserver(self, observer):
        """
        Adds a new observer to the list of observers.

        @type  observer: Observer
        @param observer: New observer to add.
        """
        if not observer in self._observers:
            self._observers.append(observer)


    def removeObserver(self, observer):
        """
        Remove observer from list of observers.

        @type  observer: Observer
        @param observer: Observer to remove.
        """
        if observer in self._observers:
            self._observers.remove(observer)


    def notifyObservers(self, arg=None):
        """
        If this object has changed, as indicated by the hasChanged
        method, then notify all of its observers and then call the
        clearChanged method to indicate that this object has no longer
        changed. Each observer has its update method called with two
        arguments: this observable object and the arg argument.

        @type  arg: object
        @param arg: Data representing the change in Observable.
        """
        if not self.hasChanged():
            return
        for o in self._observers:
            o.update(self, arg)
        self.clearChanged()


    def deleteObservers(self):
        """
        Clears the observer list so that this object no longer has any
        observers.
        """
        self._observers = []


    def setChanged(self):
        """
        Indicated that this object has changed.
        """
        if not self._suspended:
            self._changed = True


    def clearChanged(self):
        """
        Indicates that this object has no longer changed, or that it
        has already notified all of its observers of its most recent
        change.  This method is called automatically by the
        notifyObservers methods.
        """
        self._changed = False


    def hasChanged(self):
        """
        Tests if this object has changed.

        @rtype : bool
        @return: If this object has changed.
        """
        return self._changed


    def suspendObservation(self):
        """
        """
        self._suspended = True
        
        
    def resumeObservation(self):
        """
        """
        self._suspended = False
        

    def countObservers(self):
        """
        Returns the number of observers of this object.

        @rtype : int
        @return: Number of observers.
        """
        return len(self._observers)
