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
from tkinter import ttk
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
        self.root = tk.Tk()  # Main frame
        self.screen_parent = ttk.Notebook(self.root)
        
        # Screens
        self.runScreen = tk.Frame(self.screen_parent)
        self.configurationScreen = tk.Frame(self.screen_parent)
        self.scoresScreen = tk.Frame(self.screen_parent)
        self.IOScreen = tk.Frame(self.screen_parent)

        # Screen 1 (Config)
        self.config_mainContainer = tk.LabelFrame(self.configurationScreen)

        self.config_allowCustomConfig_container = tk.LabelFrame(
            self.config_mainContainer)

        self.config_qs_pa_container = tk.LabelFrame(self.config_mainContainer)
        self.config_qs_divF_container = tk.LabelFrame(
            self.config_qs_pa_container)

        self.config_deduc_ed_container = tk.LabelFrame(
            self.config_mainContainer)
        self.config_deduc_points_container = tk.LabelFrame(
            self.config_deduc_ed_container)

        # Global
        self.CONFIG_SCREEN = "<<%%QAS_QAAT_SCREEN-01%Configuration01>>"
        self.SCORES_SCREEN = "<<%%QAS_QAAT_SCREEN-02%Scores02>>"
        self.IO_SCREEN = "<<%%QAS_QAAT_SCREEN-03%IO03>>"
        self.RUN_SCREEN = "<<%%QAS_QAAT_SCREEN-04%Run04>>"

        self.sc_name_mapping = {
            self.CONFIG_SCREEN: "Configuration",
            self.SCORES_SCREEN: "Scores",
            self.IO_SCREEN: "IO",
            self.RUN_SCREEN: "Run App"
        }
        
        self.sc_inst_map = {
            self.CONFIG_SCREEN: self.configurationScreen,
            self.IO_SCREEN: self.IOScreen,
            self.RUN_SCREEN: self.runScreen,
            self.SCORES_SCREEN: self.scoresScreen
        }

        self.sc_index_mapping: dict = {
            0: self.CONFIG_SCREEN,
            1: self.SCORES_SCREEN,
            2: self.IO_SCREEN,
            3: self.RUN_SCREEN
        }
        
        self.scName: str = self.CONFIG_SCREEN  # Sets the first screen
        
        # Theme
        self.theme = QATheme.Get().get('theme')
        
        # Add extra elements
        self.theme['lblFrame_font'] = (self.theme.get('font'), 11)
        
        # Window sizing
        # Set window transform information
        self.txy = {'x': 0, 'y': 1}  # Coordinate template
        self.ss = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())  # Screen size
        self.ds = (1000, 900)  # Default size
        self.ds_ratio = (
            self.ds[0]/1920, # Width
            self.ds[1]/1080 # Height
        )
        self.ws = [
            self.ds[self.txy['x']] if self.ds[self.txy['x']] < self.ss[self.txy['x']] else int(self.ss[self.txy['x']]*self.ds_ratio[0]),
            self.ds[self.txy['y']] if self.ds[self.txy['y']] < self.ss[self.txy['y']] else int(self.ss[self.txy['y']]*self.ds_ratio[1])
        ]  # Window size (adjustable)
        self.sp = (int(self.ss[self.txy['x']] / 2 - self.ws[self.txy['x']] / 2),
                   int(self.ss[self.txy['y']] / 2 - self.ws[self.txy['y']] / 2))  # Position on screen

        # Padding x and y
        self.padX = 20; self.padY = 20
        
        # Update vars
        self.update_lbl: list = []
        self.update_btn: list = []
        self.update_bg: list = []
        self.update_fonts: dict = {} # Put in font tuples (Font Face, Font size)
        self.update_accent_fg: list = []
        
        # Last things
        self.start()  # Start the thread

        self.root.mainloop()  # Final thing; initiate the UI mainloop

    def run(self):
        # Root
        self.root.title(
            f"Quizzing Application Administrator Tools - {self.sc_name_mapping.get(self.scName)}")
        self.root.protocol("WM_DELETE_WINDOW", application_exit)
        
        # Notebook
        self.screen_parent.pack(fill=tk.BOTH, expand=True)
        for i in self.sc_inst_map:
            # txt = self.sc_name_mapping[self.sc_index_mapping[i]]
            ref = self.sc_inst_map[i]
            txt = self.sc_name_mapping[i]
            self.screen_parent.add(ref, text=txt) # Keeps the order
        
        # Frames
        # All done already
        
        # Elements
        self.update_lbl.extend([
            self.config_mainContainer,
            self.config_allowCustomConfig_container,
            self.config_qs_pa_container,
            self.config_qs_divF_container,
            self.config_deduc_ed_container,
            self.config_deduc_points_container
        ])
        
        self.update_bg.extend([
            self.configurationScreen,
            self.IOScreen,
            self.runScreen,
            self.scoresScreen
        ])
        
        self.update_accent_fg.extend([
            self.config_mainContainer,
            self.config_allowCustomConfig_container,
            self.config_qs_pa_container,
            self.config_qs_divF_container,
            self.config_deduc_ed_container,
            self.config_deduc_points_container
        ])
        
        self.config_mainContainer.pack(fill=tk.BOTH, expand=True, padx=self.padX, pady=self.padY)
        self.config_mainContainer.config(text="Edit Configuration", font=self.theme.get('lblFrame_font'))
        
        # Event binding
        self.configurationScreen.bind(f"<<NotebookTabChanged>>", self.tab_changed)
        self.runScreen.bind(f"<<NotebookTabChanged>>", self.tab_changed)
        self.IOScreen.bind(f"<<NotebookTabChanged>>", self.tab_changed)
        self.scoresScreen.bind(f"<<NotebookTabChanged>>", self.tab_changed)
        
        # last thing
        self.update_ui()

    def tab_changed(self, envent):
        # Framing (oof)
        curr_name = self.getFrameName() # Capture frame
        print(curr_name)
        
    def getFrameName(self):
        self.scName = self.sc_index_mapping[self.screen_parent.index(self.screen_parent.select())]
        return self.scName
    
    def update_ui(self, *args): # *args so that the event handler does not raise an error due to excessive arguments        
        # Root
        self.root.config(bg=self.theme.get('bg')) # BG
        self.root.iconbitmap(self_icon) # Icon
        self.root.geometry(f"{self.ws[0]}x{self.ws[1]}+{self.sp[0]}+{self.sp[1]}") # Size, Position
        
        # Label-likes
        for i in self.update_lbl:
            i.config(
                bg=self.theme.get('bg'),
                fg=self.theme.get('fg')
            )            
            
        # Button-likes
        for i in self.update_btn:
            i.config(
                bg=self.theme.get('bg'),
                fg=self.theme.get('fg'),
                activeforeground=self.theme.get('hg'),
                activebackground=self.theme.get('ac')
            )
        
        # Font
        for i in self.update_fonts: i.config(font=self.update_fonts[i])
        
        # BG Only
        for i in self.update_bg: i.config(bg=self.theme.get('bg'))
        
        # Accent FG
        for i in self.update_accent_fg: i.config(fg=self.theme['ac'])
        
        # Screen specific
        self.getFrameName() # Set the screen name
        
        if self.scName == self.CONFIG_SCREEN: pass
            
        elif self.scName == self.IO_SCREEN: pass
            
        elif self.scName == self.RUN_SCREEN: pass
            
        elif self.scName == self.SCORES_SCREEN: pass
        
    def __del__(self):
        self.thread.join(self, 0)


class IO:  # Object Oriented like FileIOHandler
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
