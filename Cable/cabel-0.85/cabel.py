from model.workspace import Workspace
from view.workspace import CabelFrame
import wx

# Create model
w = Workspace()

# Create view
class CabelApp(wx.App):
    def OnInit(self):
        self.frame = CabelFrame(w)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

app = CabelApp()

# Show view
app.MainLoop()
