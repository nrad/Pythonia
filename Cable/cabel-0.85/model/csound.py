try:
    import csnd
except ImportError:
    import CsoundVST
from model.observer import Observer
import model.workspace
import tools.config
import os
import sys

class CsoundGenerator(Observer):
    """
    CsoundGenerator.

    Generates csound code from actual state of workspace.

    @type workspace: model.workspace.Workspace
    @ivar workspace: Link to workspace object.
    @type csoundVars: tools.config.Csound
    @ivar csoundVars: Defines and encapsulates user specified csound
                      relevant variables. (see config.xml)
    @type _playing: bool
    @ivar _playing: Flag if csound is currently playing.
    @type _prcss: subprocess.Popen
    @ivar _prcss: Popen object of csound process (if subprocess module exists).
    @type  _pid: int
    @ivar _pid: Process id to kill.
    @type _handle: win32process.PyHANDLE
    @ivar _handle: The process handle (on MSW).
    @type config: tools.config.Config
    @ivar config: Defines and encapsulates user specified csound
                           relevant variables. (see config.xml)
    
    """

    def __init__(self, workspace):
        """
        Standard constructor.

        @type  workspace: model.workspace.Workspace
        @param workspace: Workspace on which the CsoundGenerator works.
        """
        Observer.__init__(self)
        self.workspace = workspace
        self.config = model.workspace.Workspace.config.csound
        self._playing = False
        self.workspace.addObserver(self)
        self._prcss = None


    def generate(self):
        """
        Generates the Csound Code out of the in the workspace bundled
        objects.

        @rtype:  string
        @return: CSound code.
        """
        globalsCode = ""       # Csound code for global statements
        opcodesCode = ""       # Csound code for user-defined opcodes
        instrumentsCode = ""   # Csound code for instrument definitions
        usedModules = []       # Remember already inserted Modules for
                               # opcodes and globals

        for instrIdx in xrange(0, len(self.workspace.instruments)):

            instr = self.workspace.instruments[instrIdx]

            # Get code for globals and user-defined opcodes
            for m in instr.modules:
                if not m.fullName in usedModules:
                    usedModules.append(m.fullName)
                    for g in xrange(0, len(m.globals)):
                        globalsCode += m.getGlobalAsCsoundCode(g) + "\n"
                    opcodesCode += m.opcode + "\n"


            # Get code for each instrument
            instrumentsCode += "instr " + str(instrIdx + 1) + "\n"

            # Test for loops (connection from rear to front in modules
            # list) and initialize loop variables if loop detected
            for c in instr.connections:
                if instr.modules.index(c.fromVar.module) \
                       >= instr.modules.index(c.toVar.module):
                    instrumentsCode += "   " + c.fromVar.type + c.fromVar.name \
                                       + str(c.fromVar.module.id) \
                                       + "  init  " + str(c.toVar.value) + "\n"

            # Connect modules
            for m in instr.modules:
                opcodeLine = "   "
                initLine = ""

                # Print list of outVars
                opcodeLine += ", ".join([o.type + o.name + str(m.id) \
                                         for o in m.outVars])

                # Print opcode
                opcodeLine += "  " + m.name + "  "

                # Print list of inVars
                inList = []
                for inVar in m.inVars:
                    if inVar.connection:
                        # Print connection fromVar for inVar
                        fromType = inVar.connection.fromVar.type
                        toType = inVar.type
                        conVar = fromType \
                                 + inVar.connection.fromVar.name \
                                 + str(inVar.connection.fromVar.module.id)

                        # Test if we need to convert var type
                        # a -> k: downsamp line in initLine
                        # a -> i: not allowed
                        # k -> a: a(fromVar)
                        # k -> i: i(fromVar)
                        # i -> a: not allowed
                        # i -> k: fromVar
                        assert(not (fromType == "a" and toType == "i" \
                                    or fromType == "i" and toType == "a"))
                        if (fromType == "k" and toType == "a"):
                            conVar = "a(" + conVar + ")"
                        elif (fromType == "k" and toType == "i"):
                            conVar = "i(" + conVar + ")"
                        elif (fromType == "a" and toType == "k"):
                            aConVar = conVar
                            conVar = "k" + inVar.connection.fromVar.name \
                                     + str(inVar.connection.fromVar.module.id)
                            initLine += "   " + conVar + " downsamp " + aConVar + "\n"

                        inList.append(conVar)

                    else:
                        if (inVar.type == "a"):
                            # If const input arg is for a-rate, init a-rate var first
                            varName = inVar.type + inVar.name + str(inVar.module.id)
                            initLine += "   " + varName + " = " + str(inVar.value) + "\n"
                            inList.append(varName)
                        else:
                            # Print value for inVar for i- and k-rate
                            inList.append(str(inVar.value))

                opcodeLine += ", ".join(inList) + "\n"

                instrumentsCode += initLine + opcodeLine

            instrumentsCode += "endin\n\n"

        return str(globalsCode + opcodesCode + instrumentsCode)


    def _startCsound(self):
        """
        Generates CSD file (csound call options, orchestra and score)
        and starts a csound process to play CSD.
        """
        csPath = self.config.getVal(tools.config.Csound.CSOUNDPATH)
        tmpCsdFile = "tmp.csd"
        self.exportToCsd(tmpCsdFile)
        # Windows csound process treatment
        if sys.platform in ("win32"):
            if self._startCsoundOnMSW(str(csPath + ' ' + tmpCsdFile)):
                self._playing = True
            else:
                self._playing = False
                self._handle.Close()
                print("Error: Csound compilation failed!")
                print("  Look at the compilation output in your console window")
                print("  from which you started Cabel for more information.")
                print("  Probably something is not correct with your csound parameters.")
                print("  You can change them in the options menu.")
        # Not windows treatment
        else:
            try:
                import subprocess
                if self._prcss:
                    # Wait for old csound process before starting a new one
                    self._prcss.wait()
                self._prcss = subprocess.Popen([csPath, tmpCsdFile])
                self._pid = self._prcss.pid
    
                # Wait for timeout seconds and test if process already returned an exit code
                timeOut = float(self.config.getVal(tools.config.Csound.FEEDBACK_TIMEOUT)) / 1000.0
                import time
                time.sleep(timeOut)
                if isinstance(self._prcss.poll(), int):
                    self._playing = False
                    print("Error: Csound compilation failed!")
                    print("  Look at the compilation output in your console window")
                    print("  from which you started Cabel for more information.")
                    print("  Probably something is not correct with your csound parameters.")
                    print("  You can change them in the options menu.")
                else:
                    self._playing = True
            except ImportError:
                self._pid = os.spawnv(os.P_NOWAIT, csPath, [csPath, tmpCsdFile])
                self._playing = True # With os.spawnv we can't check if compilation failed
        return self._playing


    def exportToCsd(self, filePath):
        """
        Export options, orchestra and score into CSD file.

        @type  filePath: str
        @param filePath: Path to CSD file (relative or absolute).
        """
        try:
            csound = csnd.CppSound()
        except NameError:
            csound = CsoundVST.CppSound()
        csPath = self.config.getVal(tools.config.Csound.CSOUNDPATH)
        
        orcString =   "sr     = " + self.config.getVal(tools.config.Csound.SAMPLERATE) + "\n" \
                    + "kr     = " + self.config.getVal(tools.config.Csound.KONTROLRATE) + "\n" \
                    + "ksmps  = " + self.config.getVal(tools.config.Csound.KSMPS) + "\n" \
                    + "nchnls = " + self.config.getVal(tools.config.Csound.NCHNLS) + "\n\n" \
                    + "\n" + self.generate()
        
        csound.setOrchestra(str(orcString))
        csound.setScore(self.config.getVal(tools.config.Csound.SCORE))
        
        csound.setCommand(str(csPath + " " + self.config.getVal(tools.config.Csound.PARAMS) \
                              + " " + filePath))
        csound.exportForPerformance()


    def play(self):
        """
        Starts CSD generation and csound in a seperate process. If
        csound's already playing stops it first.
        
        @rtype: boolean
        @return: True if the csound process started successfully.
        """
        if self._playing:
            self.stop()
        return self._startCsound()
    

    def stop(self):
        """
        Stops running Csound process.
        
        @rtype: boolean
        @return: True if there was a running csound process to be stopped, else False.
        """
        if self._playing == True:
            self._kill()
            self._playing = False
            return True
        else:
            return False


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
            if arg[0] == 'set' \
               and self.config.getVal(tools.config.Csound.AUTOPLAY) and self._playing:
                self.play()
            elif arg[0] == 'loadWorkspace' and self._playing:
                self.workspace.stop()


    def _kill(self):
        """
        Wrapper for os.kill to emulate kill if not on unix.
        """
        if sys.platform in ("win32"):
            import win32process
            if self._handle.handle > 0 and win32process.GetExitCodeProcess(self._handle) > 1:
                import win32api
                win32api.TerminateProcess(self._handle, 0)
            self._handle.Close()
            self._pid = None
        else:
            import signal
            os.kill(self._pid, signal.SIGTERM)
            self._pid = None

            
    def _startCsoundOnMSW(self, cmd):
        """
        Wrapper for _startCsound on Windows plattforms
        
        @type cmd: string
        @param cmd: Commando for the csound process.
        """
        import win32process
        
        si = win32process.GetStartupInfo()
        si.dwFlags = 0
        si.hStdInput = None
        si.hStdOutput = None
        si.hStdError = None
        
        procArgs = (None,  # appName
                    cmd,  # commandLine
                    None,  # processAttributes
                    None,  # threadAttributes
                    1,  # bInheritHandles
                    0, # dwCreationFlags
                    None,  # newEnvironment
                    None,  # currentDirectory
                    si)  # startupinfo
        processHandle, threadHandle, pid, tid  = win32process.CreateProcess(*procArgs)
        threadHandle.Close()

        self._handle = processHandle
        self._pid = pid
        
        # Timeout for feedback on the succes of the csound process
        timeOut = float(self.config.getVal(tools.config.Csound.FEEDBACK_TIMEOUT)) / 1000.0
        import time
        time.sleep(timeOut)
        
        return win32process.GetExitCodeProcess(self._handle) == 259
