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

        self.config_allowCustomConfig_container = tk.LabelFrame(self.config_mainContainer)

        self.config_qs_pa_container = tk.LabelFrame(self.config_mainContainer)
        self.config_qs_divF_container = tk.LabelFrame(self.config_qs_pa_container)

        self.config_deduc_ed_container = tk.LabelFrame(self.config_mainContainer)
        self.config_deduc_points_container = tk.LabelFrame(self.config_deduc_ed_container)

        # Screen 1 (Configuration) Elements
        self.config_acc_enbButton = tk.Button(self.config_allowCustomConfig_container)
        self.config_acc_dsbButton = tk.Button(self.config_allowCustomConfig_container)
        
        self.config_qspa_partButton = tk.Button(self.config_qs_pa_container)
        self.config_qspa_allButton = tk.Button(self.config_qs_pa_container)
        self.config_divf_entry = tk.Entry(self.config_qs_divF_container)
        
        self.config_qed_enb = tk.Button(self.config_deduc_ed_container)
        self.config_qed_dsb = tk.Button(self.config_deduc_ed_container)
        self.config_qed_amnt_entry = tk.Entry(self.config_deduc_points_container)
        
        self.save_configuration_button = tk.Button(self.config_mainContainer)
        
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
        self.update_entries: list = []
        
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
        self.update_bg.extend([
            self.configurationScreen,
            self.IOScreen,
            self.runScreen,
            self.scoresScreen
        ])
        
        # Elements
        def addFontInst(inst: object, element: object, font: tuple):
            inst.update_fonts[element] = font
        
        # Configuration
        CONFBTNs = [
            self.config_acc_enbButton,
            self.config_acc_dsbButton,
            self.config_qspa_partButton,
            self.config_qspa_allButton,
            # self.config_divf_entry
            self.config_qed_enb,
            self.config_qed_dsb,
            # self.config_qed_amnt_entry
            self.save_configuration_button
        ]; CONFLBLFs = [
            self.config_allowCustomConfig_container,
            self.config_qs_pa_container,
            self.config_qs_divF_container,
            self.config_deduc_ed_container,
            self.config_deduc_points_container
        ]; CONFENTs = [
            self.config_qed_amnt_entry,
            self.config_divf_entry
        ]
        
        self.update_btn.extend(CONFBTNs)
        
        for i in CONFBTNs:
            addFontInst(self, i, (self.theme.get('font'), self.theme.get('btn_fsize')))
        
        self.update_lbl.extend(CONFLBLFs); self.update_lbl.append(self.config_mainContainer)
        
        for i in CONFLBLFs:
            addFontInst(self, i, (self.theme.get('font'), 10))
            
        addFontInst(self, self.config_mainContainer, (self.theme.get('lblFrame_font')))
        
        self.update_entries.extend(CONFENTs)
        
        for i in CONFENTs:
            addFontInst(self, i, self.theme.get('fsize_para'))
        
        self.update_accent_fg.extend([
            self.config_mainContainer,
            self.config_allowCustomConfig_container,
            self.config_qs_pa_container,
            self.config_qs_divF_container,
            self.config_deduc_ed_container,
            self.config_deduc_points_container
        ])
        
        # Event binding
        self.configurationScreen.bind(f"<<NotebookTabChanged>>", self.tab_changed)
        self.runScreen.bind(f"<<NotebookTabChanged>>", self.tab_changed)
        self.IOScreen.bind(f"<<NotebookTabChanged>>", self.tab_changed)
        self.scoresScreen.bind(f"<<NotebookTabChanged>>", self.tab_changed)
        
        # last thing
        self.update_ui() # Sets the elements
        self.update_theme() # Sets the theme

    def tab_changed(self, envent):
        # Framing (oof)
        curr_name = self.getFrameName() # Capture frame
        print(curr_name)
        
    def getFrameName(self):
        self.scName = self.sc_index_mapping[self.screen_parent.index(self.screen_parent.select())]
        return self.scName
    
    def update_theme(self, *args):
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
                activebackground=self.theme.get('ac'),
                bd=self.theme.get('border')
            )
        
        # Font
        for i in self.update_fonts: i.config(font=self.update_fonts[i])
        
        # BG Only
        for i in self.update_bg: i.config(bg=self.theme.get('bg'))
        
        # Accent FG
        for i in self.update_accent_fg: i.config(fg=self.theme['ac'])

        # Entries
        for i in self.update_entries:
            i.config(
                fg=self.theme['fg'],
                bg=self.theme['bg'],
                selectforeground=self.theme['hg'],
                selectbackground=self.theme['ac'],
                insertbackground=self.theme['ac']
            )
        
    def update_ui(self, *args): # *args so that the event handler does not raise an error due to excessive arguments        
        # Screen specific
        self.getFrameName() # Set the screen name
        
        if self.scName == self.CONFIG_SCREEN: self.setup_config_screen()
            
        elif self.scName == self.IO_SCREEN: self.setup_io_screen()
            
        elif self.scName == self.RUN_SCREEN: self.setup_run_screen()
            
        elif self.scName == self.SCORES_SCREEN: self.setup_scores_screen()
    
    def all_screen_widgets(self):
        _config = self.configurationScreen.winfo_children()
        _run = self.runScreen.winfo_children()
        _io = self.IOScreen.winfo_children()
        _scores = self.scoresScreen.winfo_children()
        
        for item in _config:
            if item.winfo_children(): _config.extend(item.winfo_children())
        
        for item in _run:
            if item.winfo_children(): _run.extend(item.winfo_children())
        
        for item in _io:
            if item.winfo_children(): _io.extend(item.winfo_children())
        
        for item in _scores:
            if item.winfo_children(): _scores.extend(item.winfo_children())
        
        __all = [*_config, *_run, *_io, *_scores]
        
        return (__all, _config, _scores, _io, _run)        
    
    def clearUI(self):
        widgets = self.all_screen_widgets()[0]
        
        for i in widgets:
            try: i.pack_forget()
            except: continue
    
    def setup_config_screen(self):
        self.clearUI()
        
        # The actual setup
        # Theming has been taken care of already
        # Simply commit to the structure

        # CONFIGURATION
        # All containers arranged from top to bottom, with the exception of two that are to be placed inside 
        
        # self.config_mainContainer <= Parent Container
        self.config_mainContainer.pack(fill=tk.BOTH, expand=True, padx=int(self.padX/2), pady=int(self.padY/2))
        self.config_mainContainer.config(text="Edit Configuration")
        
        pady = int(self.padY/4); padx = int(self.padX/2)
        
        # self.config_allowCustomConfig_container
        self.config_allowCustomConfig_container.pack(fill=tk.BOTH, expand=True, padx=padx, pady=(int(self.padY/2), pady))
        self.config_allowCustomConfig_container.config(text="Custom Cofiguration")
                
        # self.config_qs_pa_container
        #   self.config_qs_divF_container <= Child of config_qs_pa_container
        self.config_qs_pa_container.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady)
        self.config_qs_pa_container.config(text="Questions: Part Or All")
        
        self.config_qs_divF_container.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady, side=tk.RIGHT)
        self.config_qs_divF_container.config(text="Divisor")
        
        # self.config_deduc_ed_container
        #   self.config_deduc_points_container
        self.config_deduc_ed_container.pack(fill=tk.BOTH, expand=True, padx=padx, pady=(pady, int(self.padY/2)))
        self.config_deduc_ed_container.config(text="Deductions")
        
        self.config_deduc_points_container.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady, side=tk.RIGHT)
        self.config_deduc_points_container.config(text="Deduction Amount")
        
        # Button Configuration + Info LBL conf.
        wl = int(self.ss[0]-self.ss[0]*0.55)
        
        # self.config_acc_enbButton = tk.Button(self.config_allowCustomConfig_container)
        # self.config_acc_dsbButton = tk.Button(self.config_allowCustomConfig_container)        
        
        self.config_acc_enbButton.config(text="Enable", command=self.acc_enb)
        self.config_acc_dsbButton.config(text="Disable", command=self.acc_dsb)
        
        config_acc_infoLbl = tk.Label(self.config_allowCustomConfig_container)
        config_acc_infoLbl.config(
            text="Allow Custom Quiz Configuration (Info): If set to 'Enable', the quiz taker will be given the option to setup the other quiz configuration themselves; 'Disable' removes the control from them.",
            justify=tk.CENTER,
            wraplength=wl
        )
        self.update_lbl.append(config_acc_infoLbl)
        self.update_fonts[config_acc_infoLbl] = (self.theme.get('font'), self.theme.get('fsize_para'))
        
        config_acc_infoLbl.pack(fill=tk.X, expand=True, padx=padx,pady=(pady, int(pady/2)), side=tk.TOP)
        
        self.config_acc_enbButton.pack(fill=tk.BOTH, expand=True, padx=(padx, int(padx/2)), pady=(int(pady/2), pady), side=tk.LEFT)
        self.config_acc_dsbButton.pack(fill=tk.BOTH, expand=True, padx=(int(padx/2), padx), pady=(int(pady/2), pady), side=tk.RIGHT)
        
        # self.config_qspa_partButton = tk.Button(self.config_qs_pa_container)
        # self.config_qspa_allButton = tk.Button(self.config_qs_pa_container)
        # self.config_divf_entry = tk.Entry(self.config_qs_divF_container)
        
        self.config_qspa_partButton.config(text="Part", command=self.qspa_part)
        self.config_qspa_allButton.config(text="All", command=self.qspa_all)
        
        config_qspa_infoLbl = tk.Label(self.config_qs_pa_container)
        config_qspa_infoLbl.config(
            text="Part or All Questions: If 'Part' is selected, only a certain percent (given by you) of the questions are used to prompt the user; 'All' simply prompts the user wil all the questions.",
            justify=tk.CENTER,
            wraplength=int(wl/2)
        )
        self.update_lbl.append(config_qspa_infoLbl)
        self.update_fonts[config_qspa_infoLbl] = (self.theme.get('font'), self.theme.get('fsize_para'))
        
        config_qspa_infoLbl.pack(fill=tk.X, expand=True, padx=padx,pady=(pady, int(pady/2)), side=tk.TOP)
        
        self.config_qspa_partButton.pack(fill=tk.BOTH, expand=True, padx=(padx, int(padx/2)), pady=(int(pady/2), pady), side=tk.LEFT)
        self.config_qspa_allButton.pack(fill=tk.BOTH, expand=True, padx=(int(padx/2), padx), pady=(int(pady/2), pady), side=tk.RIGHT)
        
        config_qspa_divF_lbl = tk.Label(self.config_qs_divF_container)
        config_qspa_divF_lbl.config(
            text="The divisor of questions (See 'Help Me' for info)",
            wraplength=int(wl/3),
            justify=tk.CENTER
        )
        self.update_lbl.append(config_qspa_divF_lbl)
        self.update_fonts[config_qspa_divF_lbl] = (self.theme.get('font'), self.theme.get('fsize_para'))
        
        config_qspa_divF_lbl.pack(fill=tk.X, expand=True, padx=padx,pady=(pady, int(pady/2)), side=tk.TOP)
        
        self.config_divf_entry.config() # TODO: Set the value
        self.config_divf_entry.pack(fill=tk.BOTH, expand=True, padx=padx,pady=(int(pady/2), pady), side=tk.TOP)
        
        # self.config_qed_enb = tk.Button(self.config_deduc_ed_container)
        # self.config_qed_dsb = tk.Button(self.config_deduc_ed_container)
        # self.config_qed_amnt_entry = tk.Entry(self.config_deduc_points_container)
        
        self.config_qed_enb.config(text="Enable", command=self.qed_enb)
        self.config_qed_dsb.config(text="Disable", command=self.qed_dsb)
        
        config_qed_infoLbl = tk.Label(self.config_deduc_ed_container)
        config_qed_infoLbl.config(
            text="Whether to deduct points for getting a questions wrong; 'Enable' to deduct an amount (user provided) of points after an incorrect response, and 'Disable' to not penalize incorrect answers.",
            wraplength=int(wl/2),
            justify=tk.CENTER
        )
        self.update_lbl.append(config_qed_infoLbl)
        self.update_fonts[config_qed_infoLbl] = (self.theme.get('font'), self.theme.get('fsize_para'))
        
        config_qed_infoLbl.pack(fill=tk.X, expand=True, padx=padx,pady=(pady, int(pady/2)), side=tk.TOP)
        
        self.config_qed_enb.pack(fill=tk.BOTH, expand=True, padx=(padx, int(padx/2)), pady=(int(pady/2), pady), side=tk.LEFT)
        self.config_qed_dsb.pack(fill=tk.BOTH, expand=True, padx=(int(padx/2), padx), pady=(int(pady/2), pady), side=tk.RIGHT)
        
        config_qed_sub_infoLbl = tk.Label(self.config_deduc_points_container)
        config_qed_sub_infoLbl.config(
            text="The amount of points to deduct (See 'Help Me' for more info)",
            wraplength=int(wl/3),
            justify=tk.CENTER
        )
        self.update_lbl.append(config_qed_sub_infoLbl)
        self.update_fonts[config_qed_sub_infoLbl] = (self.theme.get('font'), self.theme.get('fsize_para'))     
        
        config_qed_sub_infoLbl.pack(fill=tk.X, expand=True, padx=padx,pady=(pady, int(pady/2)), side=tk.TOP)
        
        self.config_qed_amnt_entry.config() # TODO: Set the value
        self.config_qed_amnt_entry.pack(fill=tk.BOTH, expand=True, padx=padx,pady=(int(pady/2), pady), side=tk.TOP)
        
        # Save Button
                
        self.save_configuration_button.config(
            text="Save Configuration",
            command=self.saveConfiguration
        )
        
        self.save_configuration_button.pack(fill=tk.BOTH, expand=True, padx=padx,pady=pady)
        
    def setup_run_screen(self):
        self.clearUI()
        
        # The actual setup
        # Theming has been taken care of already
        # Simply commit to the structure
    
    def setup_io_screen(self):
        self.clearUI()
        
        # The actual setup
        # Theming has been taken care of already
        # Simply commit to the structure
    
    def setup_scores_screen(self):
        self.clearUI()
        
        # The actual setup
        # Theming has been taken care of already
        # Simply commit to the structure
    
    def __del__(self):
        self.thread.join(self, 0)

    # Button Functions
    def acc_enb(self):
        pass
    
    def acc_dsb(self):
        pass
    
    def qspa_all(self):
        pass
    
    def qspa_part(self):
        pass
    
    def qed_enb(self):
        pass
    
    def qed_dsb(self):
        pass
    
    def saveConfiguration(self):
        pass
    
    # Logic Functions 
    
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
