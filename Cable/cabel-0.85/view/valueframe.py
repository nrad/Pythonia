import wx
from model.var import VarValueOutOfRangeError
from model.observer import Observer


class CabelValueFrame(wx.Frame, Observer):
    """
    CabelValueFrame.

    Frame to show input values of a model module and sliders to change
    those values.

    @type _module: model.module.Module
    @ivar _module: This frame can change module's inVars.
    @type _sliders: dict
    @ivar _sliders: Dictinary to sliders for inVars.
    @type _model: model.workspace.Workspace
    @ivar _model: Corresponding model for this frame.
    @type _controller: model.controller.CabelController
    @ivar _controller: Controller of _model.
    """

    def __init__(self, module, parent, model, controller, position=(0,0)):
        """
        Standard constructor.

        @type  module: model.module.Module
        @param module: This frame can change module's inVars.
        @type  parent: wx.Window
        @param parent: Parent of CabelValueFrame (always on top of parent).
        @type  model: model.workspace.Workspace
        @param model: Corresponding model for this frame.
        @type controller: model.controller.CabelController
        @ivar controller: Controller of model.
        @type  position: tuple
        @param position: Initial position of frame.
        """
        self._model = model
        self._controller = controller
        self._module = module

        Observer.__init__(self)
        self._model.addObserver(self)
        
        id = -1
        title = module.name + " " + str(module.id)
        wx.Frame.__init__(self, parent, id, title,
                          pos=position, size=(250, 40 * len(self._module.inVars)),
                          style=wx.FRAME_NO_TASKBAR|wx.FRAME_FLOAT_ON_PARENT \
                          |wx.RESIZE_BORDER|wx.CLOSE_BOX|wx.CAPTION\
                          |wx.CLIP_CHILDREN|wx.SYSTEM_MENU)


        panel = wx.Panel(self, -1) # Panel on which sliders are placed
                                   # (for keyboard navigation)

        self._sliders = {}
        sizer = wx.BoxSizer(wx.VERTICAL)
        for i in self._module.inVars:
            self._sliders[i] = CabelSlider(panel, i, self._model)
            sizer.Add(self._sliders[i].getSizer(), 1, wx.BOTTOM|wx.EXPAND, border=7)
        panel.SetSizer(sizer)

        # Try to set focus to first slider
        try:
            self._sliders[self._module.inVars[0]].setSliderFocus()
        except:
            pass

        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_KEY_DOWN, self.onKey)


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
        if arg:
            if arg[0] == "connect":
                newConnection = arg[1]
                if newConnection.toVar in self._sliders.keys():
                    self._sliders[newConnection.toVar].disable()
            elif arg[0] == "disconnect":
                rmConnection = arg[1]
                if rmConnection.toVar in self._sliders.keys():
                    self._sliders[rmConnection.toVar].enable()
            elif arg[0] == "set":
                inVar = arg[1]
                newValue = arg[2]
                if inVar in self._sliders.keys():
                    self._sliders[inVar].setToValue(newValue)
                    

    def onClose(self, event):
        """
        Called when closing value frame.
        """
        self._model.removeObserver(self)
        self._controller.onValueFrameClosed(self)
        event.Skip()


    def onKey(self, event):
        """
        Called when getting a key event input.
        """
        if event.ControlDown() and event.GetKeyCode() == ord('W'):
            self.Close() # Close with CTRL-W
        event.Skip()
        
#---------------------------------------------------------------------------


class CabelSlider(object):
    """
    This is a combination of wx.Slider and wx.TextCtrl in one
    horizontal Sizer.

    @type inVar: model.var.InVar
    @ivar inVar: Slider/SpinCtrl controls this inVar.
    @type parent: wx.Window
    @ivar parent: Parent window for CabelSlider.
    """


    def __init__(self, parent, inVar, model):
        """
        Standard constructor.

        @type  inVar: model.var.InVar
        @param inVar: Slider/SpinCtrl controls this inVar.
        """
        self.inVar = inVar
        self.parent = parent
        self._model = model

        self.multiplicator = 10**inVar.digits

        self.multValue = int(self.multiplicator * self.inVar.value)
        self.multMin = int(self.multiplicator * self.inVar.min)
        self.multMax = int(self.multiplicator * self.inVar.max)

        label = wx.StaticText(parent, -1, inVar.name)

        self.slider = wx.Slider(parent, -1, self.multValue, self.multMin,
                                self.multMax, name=inVar.name)
        self.slider.SetToolTip(wx.ToolTip(inVar.description \
                                          + '\nRange: [' \
                                          + str(self.inVar.min) + ', ' \
                                          + str(self.inVar.max) + ']'))

        self.text = wx.TextCtrl(parent, -1, str(inVar.value), style=wx.TE_PROCESS_ENTER)
        self.text.SetToolTip(wx.ToolTip(inVar.description \
                                        + '\nRange: [' \
                                        + str(self.inVar.min) + ', ' \
                                        + str(self.inVar.max) + ']'))

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        sliderSizer = wx.BoxSizer(wx.HORIZONTAL)
        sliderSizer.Add(self.slider, 1, wx.LEFT|wx.EXPAND|wx.ALIGN_CENTER, border=3)
        sliderSizer.Add(self.text, 0, wx.ALL|wx.RIGHT|wx.ALIGN_CENTER, border=3)
        self.sizer.Add(label, 1, wx.ALIGN_CENTER)
        self.sizer.Add(sliderSizer, 1, wx.EXPAND)

        self.slider.Bind(wx.EVT_SCROLL, self.onSliderChange)
        self.text.Bind(wx.EVT_TEXT_ENTER, self.onTextChange)
        self.text.Bind(wx.EVT_KILL_FOCUS, self.onTextChange)

        if self.inVar.connection:
            self.disable()


    def getSizer(self):
        """
        Return sizer for CabelSizer.
        """
        return self.sizer


    def onSliderChange(self, event):
        """
        Called when slider is changed.
        """
        multValue = self.slider.GetValue()
        value = multValue / float(self.multiplicator)
        format = "%." + str(self.inVar.digits) + "f"
        self.text.SetValue(format  % value)
        self._setValue(value)


    def onTextChange(self, event):
        """
        Called when text ctrl is changed.
        """
        try:
            txtValue = self.text.GetValue()
            # Change decimal seperator ',' to '.'
            if txtValue.find(',') >= 0:
                txtValue = txtValue.replace(',', '.')
            # Put initial 0 to values starting with '.' 
            if txtValue.find('.') == 0:
                txtValue = '0' + txtValue
            value = float(txtValue)
        except ValueError:
            value = self.inVar.min
            format = "%." + str(self.inVar.digits) + "f"
            self.text.SetValue(format  % value)

        self._setValue(value)

        multValue = int(value * self.multiplicator)
        self.slider.SetValue(multValue)


    def _setValue(self, value):
        """
        Set inVar to value in text ctrl.

        @type  value: float
        @param value: New value for inVar.
        """
        try:
            self._model.setValue(self.inVar, value)
        except VarValueOutOfRangeError, txt:
            d = wx.MessageDialog(self.parent, str(txt), "Var value out of range error",
                                 wx.OK | wx.ICON_ERROR)
            d.ShowModal()
            d.Destroy()


    def setToValue(self, value):
        """
        Sets slider and text ctrl to value.

        @type  value: float
        @param value: New value for slider and text ctrl.
        """
        multValue = int(value * self.multiplicator)
        self.slider.SetValue(multValue)
        format = "%." + str(self.inVar.digits) + "f"
        self.text.SetValue(format % value)


    def enable(self):
        """
        Enables slider and text ctrl.
        """
        self.slider.Enable()
        self.text.Enable()


    def disable(self):
        """
        Disables slider and text ctrl.
        """
        self.slider.Disable()
        self.text.Disable()


    def setSliderFocus(self):
        """
        Set focus to slider widget.
        """
        self.slider.SetFocus()


    def setTextFocus(self):
        """
        Set focus to text widget.
        """
        self.text.SetFocus()
        
