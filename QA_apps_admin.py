# QA Python Files
import qa_time as QATime
import qa_theme as QATheme
import qa_appinfo as QAInfo
import qa_logging as QALog
import qa_globalFlags as QAJSONHandler
import qa_diagnostics as QADiagnostics
import qa_fileIOHandler as QAFileIO
import qa_pdfGen as QAPDFGen
import qa_win10toast as QAWinToast
import qa_quizConfig as QAConfig
import qa_typeConvertor as QATypeConv

# Misc. Imports
import threading
import sys
import os
import shutil
import traceback
import tkinter as tk
from tkinter import messagebox as tkmsb

# Globals
QAS_encoding = 'utf-32'
self_icon = QAInfo.icons_ico.get('admt')

# Classes


class Error(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)
        
        self.start()

    def __del__(self):
        self.thread.join(self, 0)

class JSON(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)
        
        self.start()
        
    def __del__(self):
        self.thread.join(self, 0)


class UI(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)
        
        # UI Vars
        # Global
        self.root = tk.Tk() # Main frame
        
        # Screens
        self.runScreen = tk.Frame(self.root)
        self.configurationScreen = tk.Frame(self.root)
        self.scoresScreen = tk.Frame(self.root)
        self.IOScreen = tk.Frame(self.root)
        
        # Screen 1 (Config)
        self.config_mainContainer = tk.LabelFrame(self.configurationScreen)
        
        self.config_allowCustomConfig_container = tk.LabelFrame(self.config_mainContainer)
        
        self.config_qs_pa_container = tk.LabelFrame(self.config_mainContainer)
        self.config_qs_divF_container = tk.LabelFrame(self.config_qs_pa_container)
        
        self.config_deduc_ed_container = tk.LabelFrame(self.config_mainContainer)
        self.config_deduc_points_container = tk.LabelFrame(self.config_deduc_ed_container)
                
        # Global
        self.CONFIG_SCREEN = "<<%%QAS_QAAT_SCREEN-01%Configuration01>>"
        self.SCORES_SCREEN = "<<%%QAS_QAAT_SCREEN-02%Scores02>>"
        self.IO_SCREEN = "<<%%QAS_QAAT_SCREEN-03%IO03>>"
        self.RUN_SCREEN = "<<%%QAS_QAAT_SCREEN-04%Run04>>"
        
        self.screenName_mapper = {
            self.CONFIG_SCREEN: "Configuration",
            self.SCORES_SCREEN: "Scores",
            self.IO_SCREEN: "IO",
            self.RUN_SCREEN: "Run App"
        }
        
        self.scName: str = self.CONFIG_SCREEN # Sets the first screen
        
        # Last things        
        self.start() # Start the thread
        
        self.root.mainloop() # Final thing; initiate the UI mainloop

    def run(self):
        self.root.title(f"Quizzing Application Administrator Tools - {self.screenName_mapper.get(self.scName)}")
        self.root.protocol("WM_DELETE_WINDOW", application_exit)
        
        # last thing
        self.update_ui()
    
    def update_ui(self):
        self.root.iconbitmap(self_icon)
    
    def __del__(self):
        self.thread.join(self, 0)

class IO: # Object Oriented like FileIOHandler
    def __init__(self, fn: str, **kwargs):
        self.filename = fn
        self.object = QAFileIO.create_fileIO_object(self.filename)
        self.flags = {
            'append': [False, (bool, )],
            'append_sep': ["\n", (str, bytes)],
            'suppressError': [False, (bool,)],
            'encoding': ['utf-8', (str, )],
            'encrypt': [False, (bool, )]
        }
        self.kwargs = kwargs
        
        self.reload_kwargs()

    def rawLoad(self, *args, **kwargs) -> bytes:
        return QAFileIO.load(self.object)

    def saveData(self, Data, **kwargs):  # Secure Save
        self.flags = flags_handler(self.flags, kwargs)  # Same flags
        flags = dc_lst(self.flags, 0)
        debug(f"1")
        QAFileIO.save(
            self.object,
            Data,
            append=flags['append'],
            appendSeperator=flags['append_sep'],
            encryptData=flags['encrypt'],
            encoding=flags['encoding']
        )

    def clear(self, *args, **kwargs) -> None:
        open(self.object.filename, 'w').close()
    
    def autoLoad(self, *args, **kwargs) -> str:
        return QAFileIO.read(self.object)

    def encrypt(self, *args, **kwargs) -> None:
        QAFileIO.encrypt(self.object)
        
    def decrypt(self, *args, **kwargs) -> None:
        QAFileIO.decrypt(self.object)
        
    def reload_kwargs(self) -> None:
        self.flags = flags_handler(self.flags, self.kwargs)

# Functions
# Low level

def application_exit(code: str = "0") -> None:
    sys.exit(code)

def editKWARGS(Object: object, **kwargs):
    Object.kwargs = kwargs
    Object.reload_kwargs()

def dc_lst(Dict: dict, index) -> dict:
    out: dict = {}
    for i in Dict:
        out[i] = (Dict[i][index])
    
    return out

def debug(debugData: str):
    # Script Name
    try:
        scname = __file__.replace(
            '/', '\\').split('\\')[-1].split('.')[0].strip()
    except:
        scname = sys.argv[0].replace(
            '/', '\\').split('\\')[-1].split('.')[0].strip()

    # Instance
    Log = QALog.Log()

    # Generation
    if not QALog.Variables().genDebugFile():
        Log.logFile_create(from_=scname)

    # Log
    Log.log(data=debugData, from_=scname)


def flags_handler(reference: dict, kwargs: dict, __raiseERR=True, __rePlain=False) -> dict:
    debug(f"Refference ::: {reference}")
    
    out: dict = reference

    for i in kwargs:
        if i in out:  # Valid name
            kdt = type(kwargs[i])
            valt = reference[i][-1]  # Type tuple

            if kdt in valt:
                if not kwargs[i] == reference[i][0]:
                    out[i] = [kwargs[i], reference[i][-1]]
                    debug(f"Changed flag '{i}' to '{out[i]}'")

            elif __raiseERR:
                debug(
                    f"Invalid type {kdt} for flag '{i}' expected: {valt}; raising error")
                raise TypeError(
                    f"Invalid type {kdt} for flag '{i}' expected: {valt}")

            else:
                debug(
                    f"Invalid type {kdt} for flag '{i}' expected: {valt}; __raiseERR != True; suppressing error")

        elif __raiseERR:
            debug(f"Invalid type flag name '{i}'; raising error")
            raise KeyError(f"Invalid type flag name '{i}'")

        else:
            debug(
                f"Invalid type flag name '{i}'; __raiseERR != True; suppressing error")

    if __rePlain:
        for i in out.keys():
            out[i] = out[i][0]

    debug(f"Returning edited kwargs {out}")
    return out


UI()
