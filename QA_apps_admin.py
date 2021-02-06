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
import qa_errors as QAErrors
import qa_splash as QASplash

import qa_onlineVersCheck as QA_OVC

# Misc. Imports
import threading, sys, os, shutil, traceback, json, time, random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkmsb
from tkinter import filedialog as tkfldl

apptitle = f"Administrator Tools v{QAInfo.versionData[QAInfo.VFKeys['v']]}"

boot_steps = {
    1: 'Loading Variables',
    2: 'Loading Functions',
    3: 'Loading Configuration',
    4: 'Running Boot Checks',
    5: 'Fetching Version Information Online'
}; boot_steps_amnt = len(boot_steps)  

# The splash screen

splRoot = tk.Toplevel()
splObj = QASplash.Splash(splRoot)

splObj.setImg(QAInfo.icons_png.get('admt'))
splObj.setTitle("Administrator Tools")

def set_boot_progress(ind, resolution=1000):
    global boot_steps; global boot_steps_amnt; global splObj
    
    splObj.setInfo(boot_steps[ind])
    
    ind -= 1 # 0 >> Max
    Max = boot_steps_amnt-1
    prev = ind - 1 if ind > 0 else ind
    
    for i in range(prev*resolution, ind*resolution):
        for j in range(20): pass # < 0.01 sec delay
        
        splObj.changePbar(
            (i/boot_steps_amnt)/(resolution/100)
        )

def show_splash_completion(resolution=1000):
    global boot_steps_amnt; global splObj
    
    ind = boot_steps_amnt - 1
    
    splObj.completeColor()
    splObj.setInfo(f"Completed Boot Process")
    
    for i in range(ind*resolution, boot_steps_amnt*resolution):
        for j in range(20): pass # < 0.01 sec delay
        
        splObj.changePbar(
            (i/boot_steps_amnt)/(resolution/100)
        )
    
    time.sleep(0.5)
    
# Adjust Splash
set_boot_progress(1)

# Globals
QAS_encoding = 'utf-32'
self_icon = QAInfo.icons_ico.get('admt')
configruationFilename = '{}\\{}'.format(QAInfo.appdataLoc.strip('\\').strip(), QAInfo.confFilename)
configuration_saved: dict = {}

# Adjust Splash
set_boot_progress(2)

# Classes

class JSON:
    def __init__(self):
        self.jsonHandlerInst = QAJSONHandler.QAFlags(); self.jsonHandler = self.jsonHandlerInst
        
        self.crashID = self.jsonHandlerInst.ADMTs_crash_id
        self.timedEventID = self.jsonHandler.ADMTs_timed_crash_id
        
        self.unrID = self.jsonHandlerInst.log_unr_id
        self.funcID = self.jsonHandlerInst.log_function_id
        self.timeID = self.jsonHandlerInst.log_time_id
        self.infoID = self.jsonHandlerInst.log_info_id
        
        self.noFuncID = self.jsonHandlerInst.no_func_id
    
    def logCrash(self, info:str, functionCall=None):
        id = self.crashID
        time = f"{QATime.now()}"

        self.setFlag(
            filename=QAInfo.global_nv_flags_fn,
            data_key=id,
            data_val={
                self.unrID: True,
                self.infoID: info,
                self.timeID: time,
                self.funcID: functionCall if functionCall is not None else self.noFuncID
            }
        )
    
    def removeFlag(self, filename: str, data_key: str):
        flag_io = QAJSONHandler.QAFlags()
        key = flag_io.REMOVE
        
        flag_io.io(
            key,
            filename=filename,
            key=data_key
        )
        
        return
    
    def setFlag(self, filename: str, data_key: str, data_val: any, **kwargs):
        Flags = {
        'append': [True, (True, bool)],
        'reload_nv_flags': [True, (True, bool)]
        }

        Flags = flags_handler(Flags, kwargs, __rePlain=True)

        flag_io = QAJSONHandler.QAFlags()
        key = flag_io.SET

        flag_io.io(key,
                filename=filename,
                data={
                    data_key: data_val
                },
                appendData=Flags['append'],
                reloadJSON=Flags['reload_nv_flags'])

        return
    
    def getFlag(self, filename: str, data_key: str, **kwargs):
        Flags = {
        'return_boolean': [True, (True, bool)],
        'reload_nv_flags': [True, (True, bool)]
        }

        Flags = flags_handler(Flags, kwargs)

        temp: dict = {}
        for i in Flags: temp[i] = Flags[i][0]

        Flags = temp

        debug(f"Querying for flag {data_key} in file '{filename}'")

        flagsIO = QAJSONHandler.QAFlags()
        key = flagsIO.GET

        result = flagsIO.io(Key=key,
                            key=data_key,
                            filename=filename,
                            re_bool=Flags['return_boolean'],
                            reloadJSON=Flags['reload_nv_flags'])

        debug(f"Result of query: '{result}'")

        return result
    
    def log_crash_fix(self, urd: bool, tp: bool, apd: str, apftf: str, crinfo: str, crtime: str, crfunc: str):
        time = f"{QATime.now()}"
        id = self.timedEventID.strip() + " " + time

        self.setFlag(
            filename=QAInfo.global_nv_flags_fn,
            data_key=id,
            data_val={
                "time": time,
                "crash_detected": {
                    self.infoID: crinfo,
                    self.timeID: crtime,
                    self.funcID: crfunc
                },
                "ran_diagnostics": urd,
                "test_passed": tp,
                "diagnostics_function": apd,
                "correction_function": apftf
            }
        )    
    
    def boot_check(self):
        # Step 1: Does the key exist?
        if self.getFlag(QAInfo.global_nv_flags_fn, self.crashID):
            
            # Step 2: Is the error un-resolved?
            check = self.getFlag(QAInfo.global_nv_flags_fn, self.crashID, return_boolean=False)
            
            if check.get(self.unrID): # Un-reolved
                
                # Step 1: Vars
                _dData = QADiagnostics.Data()
                _test = _dData.diagnostics_function_mapping.get(
                    check.get(self.funcID)
                )
                _corr = _dData.correction_function_mapping.get(
                        check.get(self.funcID)
                )
                
                # Run the test
                _result = _test()
                
                if not _result:
                    # Run the diagnostics
                    _corr()

                # log_crash_fix(self, urd: bool, tp: bool, apd: str, apftf: str, crinfo: str, crtime: str, crfunc: str):
                self.log_crash_fix(
                    True,
                    _result,
                    f"{_test}",
                    f"{_corr}",
                    check.get(self.infoID),
                    check.get(self.timeID),
                    check.get(self.funcID)
                )
                
                self.removeFlag(
                    QAInfo.global_nv_flags_fn,
                    self.crashID
                )
                
                tkmsb.showinfo(apptitle, f"The application had detected a boot-error flag and thus ran the appropriate diagnostics.")
            
        # True = Test passed
        return True

class UI(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)

        # UI Vars
        # Configuration (Internal)
        # Do not use an internal dictionary and attempt to synchronize with the global dict like 1.5x;
        # Instead, use the button states to simulate the dictionary.
        
        # Global
        self.root = tk.Tk()  # Main frame
        self.root.withdraw()
        
        self.screen_parent = ttk.Notebook(self.root)
        
        # Screens
        self.runScreen = tk.Frame(self.screen_parent)
        self.configurationScreen = tk.Frame(self.screen_parent)
        self.scoresScreen = tk.Frame(self.screen_parent)
        self.IOScreen = tk.Frame(self.screen_parent)
        self.questionsScreen = tk.Frame(self.screen_parent)

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
        
        # Screen 2 (IO) Elements
        self.io_ie_frame = tk.LabelFrame(self.IOScreen)
        self.io_ie_importButton = tk.Button(self.io_ie_frame)
        self.io_ie_exportButton = tk.Button(self.io_ie_frame)
        self.io_ie_exportScoresButton = tk.Button(self.io_ie_frame)
        
        self.io_ie_checkContainer = tk.LabelFrame(self.IOScreen)
        self.io_ie_cc_invisCont_left = tk.LabelFrame(self.io_ie_checkContainer)
        self.io_ie_cc_invisCont_right = tk.LabelFrame(self.io_ie_checkContainer)
        
        self.io_ie_ICToggle = tk.Button(self.io_ie_cc_invisCont_left)
        self.io_ie_IQToggle = tk.Button(self.io_ie_cc_invisCont_left)
        self.io_ie_ISToggle = tk.Button(self.io_ie_cc_invisCont_left)
        
        self.io_ie_import_selectedFileLbl = tk.Label(self.io_ie_cc_invisCont_right)
        self.io_ie_importCommitButton = tk.Button(self.io_ie_cc_invisCont_right)
        
        self.io_imConf = False
        self.io_imQs = False
        self.io_imSks = False
        
        self.io_valFile_c = False
        self.io_valFile_s = False
        self.io_valFile_q = False
        
        self.io_import_fn = None
        
        # Misc. Screen
        self.misc_runBugReport = tk.Button(self.runScreen)
        
        # Global
        self.CONFIG_SCREEN = "<<%%QAS_QAAT_SCREEN-01%Configuration01>>"
        self.SCORES_SCREEN = "<<%%QAS_QAAT_SCREEN-02%Scores02>>"
        self.IO_SCREEN = "<<%%QAS_QAAT_SCREEN-03%IO03>>"
        self.RUN_SCREEN = "<<%%QAS_QAAT_SCREEN-04%Run04>>"
        self.QUESTIONS_SCREEN = "<<%%QAS_QAAT_SCREEN-05%Questions05>>"

        self.sc_name_mapping = {
            self.CONFIG_SCREEN: "Configuration",
            self.SCORES_SCREEN: "Scores",
            self.IO_SCREEN: "IO",
            self.RUN_SCREEN: "Miscellaneous",
            self.QUESTIONS_SCREEN: "Questions"
        }
        
        self.sc_inst_map = {
            self.CONFIG_SCREEN: self.configurationScreen,
            self.IO_SCREEN: self.IOScreen,
            self.RUN_SCREEN: self.runScreen,
            self.SCORES_SCREEN: self.scoresScreen,
            self.QUESTIONS_SCREEN: self.questionsScreen
        }

        self.sc_index_mapping: dict = {
            0: self.CONFIG_SCREEN,
            1: self.IO_SCREEN,
            2: self.RUN_SCREEN,
            3: self.SCORES_SCREEN,
            4: self.QUESTIONS_SCREEN
        }
        
        self.scName: str = self.CONFIG_SCREEN  # Sets the first screen

        self.IO_QSIMPORT_KEY = "<%%QAS--QUESTIONS--IMPORT--%%>"
        self.IO_CONFIMPORT_KEY = "<%%QAS-CONFIGURATION--IMPORT--%%>"
        self.IO_SCIMPORT_KEY = "<%%QAS-SCORES--IMPORT--%%>"

        self.IO_DIVEND_KEY = "<%%QAS-IMPORT-END_DIV%%>"

        # Theme
        self.theme = QATheme.Get().get('theme')
        
        # Add extra elements
        self.theme['lblFrame_font'] = (self.theme.get('font'), 11)
        
        self.dsbAll_fg = '#595959'
        
        # Window sizing
        # Set window transform information
        self.txy = {'x': 0, 'y': 1}  # Coordinate template
        self.ss = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())  # Screen size
        self.ds_ratio = (
            1000/1920, # Width
            900/1080 # Height
        )
        self.ds = (int(self.ds_ratio[0]*self.ss[0]),
                   int(self.ds_ratio[1]*self.ss[1]))  # Default size
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
        # self.root.title(
        #     f"{apptitle} - {self.sc_name_mapping.get(self.scName)}")
        self.root.protocol("WM_DELETE_WINDOW", self.safe_close)
        
        # Notebook
        self.screen_parent.pack(fill=tk.BOTH, expand=True)
        for i in self.sc_inst_map:
            # txt = self.sc_name_mapping[self.sc_index_mapping[i]]
            ref = self.sc_inst_map[i]
            txt = self.sc_name_mapping[i]
            self.screen_parent.add(ref, text=txt) # Keeps the order
            self.update_bg.append(self.sc_inst_map[i]) # Frames
        
        # Elements
        def addFontInst(inst: object, element: object, font: tuple):
            inst.update_fonts[element] = font
        
        # Configuration Screen
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
        
        # IO Screen
        
        IOBTNs = [
            self.io_ie_importButton,
            self.io_ie_exportButton,
            self.io_ie_ICToggle,
            self.io_ie_IQToggle,
            self.io_ie_ISToggle,
            self.io_ie_importCommitButton,
            self.io_ie_exportScoresButton
        ]; IOLBLFs = [
            self.io_ie_frame,
            self.io_ie_checkContainer,
            self.io_ie_import_selectedFileLbl
        ]
        
        self.update_btn.extend(IOBTNs)
        
        for i in IOBTNs:
            addFontInst(self, i, (self.theme.get('font'), self.theme.get('btn_fsize')))     
        
        self.update_lbl.extend(IOLBLFs)
        
        for i in IOLBLFs:
            addFontInst(self, i, (self.theme.get('font'), 10))
        
        self.update_accent_fg.extend([
            self.io_ie_frame,
            self.io_ie_checkContainer
        ])

        # MISC
        MISC_BUTTONS = [
            self.misc_runBugReport            
        ]
        
        self.update_btn.extend(MISC_BUTTONS)
        
        for i in MISC_BUTTONS:
            addFontInst(self, i, (self.theme.get('font'), self.theme.get('btn_fsize')))
        
        addFontInst(self, self.io_ie_import_selectedFileLbl, (self.theme.get('font'), self.theme.get('fsize_para')))

        # Event binding
        self.screen_parent.bind(f"<<NotebookTabChanged>>", self.tab_changed)
        
        # last things
        self.update_ui() # Sets the elements
        self.update_theme() # Sets the theme
        self.setConfigStates() # Set the states (Conf)
        self.conf_io_btns() # Set the states (IO)
        self.update_frame_title()
        
        self.root.deiconify()
    
    def safe_close(self):
        global apptitle
        
        debug(f"\nB: {configuration_begining}\nComparing /\\ to \\/\nS: {configuration_saved}")
        
        if not conf_saved():
            __conf = tkmsb.askyesno(apptitle, 'Would you like to save changes to the configuration?')
            if __conf: self.saveConfiguration()
            
        application_exit(0)
    
    def tab_changed(self, event):
        # Framing (oof)
        curr_name = self.getFrameName() # Capture frame
        self.update_frame_title()
    
    def update_frame_title(self):
        self.root.title(
            f"{apptitle} - {self.sc_name_mapping.get(self.scName)}")
    
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
        
        # if self.scName == self.CONFIG_SCREEN: self.setup_config_screen()
            
        # elif self.scName == self.IO_SCREEN: self.setup_io_screen()
            
        # elif self.scName == self.RUN_SCREEN: self.setup_run_screen()
            
        # elif self.scName == self.SCORES_SCREEN: self.setup_scores_screen()

        self.setup_config_screen()
        self.setup_io_screen()
        self.setup_run_screen()
        self.setup_scores_screen()
        self.setup_questions_screen()
        
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
    
    def setup_questions_screen(self):
        pass
    
    def setup_config_screen(self):
        
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
        
    def setup_run_screen(self): # TODO: Make the screen code
        
        # The actual setup
        # Theming has been taken care of already
        # Simply commit to the structure
        
        self.misc_runBugReport.config(
            text="Report a Bug",
            command=self.launch_bug_report            
        )
        
        self.misc_runBugReport.pack(
            fill=tk.BOTH,
            expand=True,
            padx=int(self.padX/2),
            pady=int(self.padY/2)
        )
        
        return
    
    def setup_io_screen(self):
        # sself.clearUI()
        
        # The actual setup
        # Theming has been taken care of already
        # Simply commit to the structure
        
        self.io_ie_frame.config(text="Select File")
        self.io_ie_frame.pack(fill=tk.BOTH, expand=True, padx=int(self.padX/2), pady=(self.padY/2, self.padY/4))
        
        self.io_ie_importButton.config(text="Import File", command=self.io_ie_import)
        self.io_ie_importButton.pack(
            fill=tk.BOTH, 
            expand=True, 
            side=tk.LEFT, 
            padx=(int(self.padX/2), int(self.padX/4)),
            pady=int(self.padY/2)
        )
        
        self.io_ie_exportButton.config(text="Export File", command=self.io_ie_export)
        self.io_ie_exportButton.pack(
            fill=tk.BOTH, 
            expand=True, 
            side=tk.RIGHT, 
            padx=(int(self.padX/2), int(self.padX/4)),
            pady=int(self.padY/2),
        )

        self.io_ie_exportScoresButton.config(text="Export Scores", command=self.io_ie_exportScores)
        self.io_ie_exportScoresButton.pack(
            fill=tk.BOTH,
            expand=True,
            side=tk.RIGHT,
            padx=(int(self.padX / 2), int(self.padX / 4)),
            pady=int(self.padY / 2),
        )
        
        self.io_ie_checkContainer.config(text="Import Options")
        self.io_ie_checkContainer.pack(fill=tk.BOTH, expand=True, padx=int(self.padX/2), pady=(self.padY/4, self.padY/2))
        
        self.io_ie_cc_invisCont_left.config(
            bg=self.theme.get('bg'),
            fg=self.theme.get('fg'),
            bd=0
        )
        self.io_ie_cc_invisCont_left.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        self.io_ie_cc_invisCont_right.config(
            bg=self.theme.get('bg'),
            fg=self.theme.get('fg'),
            bd=0
        )
        self.io_ie_cc_invisCont_right.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        
        self.io_ie_ICToggle.config(
            text="Import Configuration",
            command=self.ioConf
        )
        self.io_ie_ICToggle.pack(fill=tk.BOTH, expand=True, padx=(int(self.padX/2), int(self.padX/4)), pady=int(self.padY/2))
        
        self.io_ie_IQToggle.config(
            text="Import Questions",
            command=self.ioQs
        )
        self.io_ie_IQToggle.pack(fill=tk.BOTH, expand=True, padx=(int(self.padX/2), int(self.padX/4)), pady=int(self.padY/2))
        
        self.io_ie_ISToggle.config(
            text="Import Scores",
            command=self.ioSks
        )
        self.io_ie_ISToggle.pack(fill=tk.BOTH, expand=True, padx=(int(self.padX/2), int(self.padX/4)), pady=int(self.padY/2))
        
        self.io_ie_import_selectedFileLbl.config(
            text="No File Selected",
            wraplength=450
        )
        self.update_accent_fg.append(self.io_ie_import_selectedFileLbl)
        self.io_ie_import_selectedFileLbl.pack(fill=tk.BOTH, expand=True, padx=(int(self.padX/4), int(self.padX/2)), pady=int(self.padY/2))
        
        self.io_ie_importCommitButton.config(
            text="Import Selected Data",
            command=self.io_commitImport
        )
        self.io_ie_importCommitButton.pack(fill=tk.BOTH, expand=True, padx=(int(self.padX/4), int(self.padX/2)), pady=int(self.padY/2))
    
    def setup_scores_screen(self): # TODO: Make the screen code
        pass
        
        # The actual setup
        # Theming has been taken care of already
        # Simply commit to the structure
    
    def __del__(self):
        self.thread.join(self, 0)

    # Button Functions (Event Handlers)
    def launch_bug_report(self):
        # os.system(f"{QAInfo.bugReportLink}")

        os.system(f"start \"\" {QAInfo.bugReportLink}")
        
    def acc_enb(self):
        global configuration_begining
        
        # ACC = Allow Custom Configuration; enb = Enable
        
        # Step 1: Disable the button and set the color (fg)
        self.config_acc_enbButton.config(state=tk.DISABLED,
                                         disabledforeground=self.theme.get('ac')
        )

        # Step 2: Enable the other button
        self.config_acc_dsbButton.config(state=tk.NORMAL)
        
        # Step 3: Enable all other things
        self.qspa_enbAll() # All / Part Container + Buttons + Sub-Container + Entry (divF)
        self.qed_enbAll() # QED and all of it's child objects
        
        # Step 4: Write the changes to the dict
        configuration_begining[
            QAConfig.keys_quizTaker_customConfig
        ] = True
        
        return
        
    def acc_dsb(self):
        # ACC = Allow Custom Configuration; dsb = Disable
        
        # Step 1: Disable the button and set the color (fg)
        self.config_acc_dsbButton.config(state=tk.DISABLED,
                                         disabledforeground=self.theme.get('ac')
        )

        # Step 2: Enable the other button
        self.config_acc_enbButton.config(state=tk.NORMAL)

        # Step 3: Disable all other things
        self.qspa_dsbAll() # All / Part Container + Buttons + Sub-Container + Entry (divF)
        self.qed_dsbAll() # QED and all of it's child objects
        
        # Step 4: Write the changes to the dict
        configuration_begining[
            QAConfig.keys_quizTaker_customConfig
        ] = False
        
        return
    
    def qspa_divF_dsb(self):
        self.config_qs_divF_container.config(
            fg=self.dsbAll_fg,
            text=self.config_qs_divF_container.cget('text').replace(' (Disabled)', '') + ' (Disabled)'
        )
        
        self.config_divf_entry.config(
            state=tk.DISABLED,
            disabledforeground=self.dsbAll_fg,
            disabledbackground=self.theme.get('bg')
        )
    
    def qspa_divF_enb(self):
        self.config_qs_divF_container.config(
            fg=self.theme.get('ac'),
            text=self.config_qs_divF_container.cget('text').replace(' (Disabled)', '')
        )
            
        self.config_divf_entry.config(state=tk.NORMAL)
    
    def qspa_enbAll(self):
        global configuration_begining
        conf = configuration_begining
        
        if conf.get(QAConfig.keys_questions_partOrAll) == QAConfig.values_qspa_part: self.qspa_part()
        else: self.qspa_all()

        self.config_qs_pa_container.config(
            text=self.config_qs_pa_container.cget('text').replace(' (Disabled)', ''),
            fg=self.theme.get('ac')
        )
        
        self.qspa_divF_enb() # Div F Entry + Container
        
    def qspa_dsbAll(self):
        debug(f"Disabling input for 'QSPA'")
        
        global configuration_begining
        conf = configuration_begining
        
        self.config_qs_pa_container.config(
            text=self.config_qs_pa_container.cget('text').replace(' (Disabled)', '') + ' (Disabled)',
            fg=self.dsbAll_fg
        )
            
        self.config_qspa_allButton.config(
            state=tk.DISABLED,
            disabledforeground=self.dsbAll_fg
        )

        self.config_qspa_partButton.config(
            state=tk.DISABLED,
            disabledforeground=self.dsbAll_fg
        )
    
        self.qspa_divF_dsb() # Div F Entry + Container
    
    def qspa_all(self):
        # QS = Question amount Selection, PA = Part or All
        
        # Step 1: Disable the button and set the color (fg)
        self.config_qspa_allButton.config(
            state=tk.DISABLED,
            disabledforeground=self.theme.get('ac')
        )

        # Step 2: Enable the other button
        self.config_qspa_partButton.config(
            state=tk.NORMAL
        )
        
        # Step 4: Write the changes to the dict
        configuration_begining[
            QAConfig.keys_questions_partOrAll
        ] = QAConfig.values_qspa_all
        
        return
        
    def qspa_part(self):
        # QS = Question amount Selection, PA = Part or All
        
        # Step 1: Disable the button and set the color (fg)
        self.config_qspa_partButton.config(
            state=tk.DISABLED,
            disabledforeground=self.theme.get('ac')
        )

        # Step 2: Enable the other button
        self.config_qspa_allButton.config(
            state=tk.NORMAL
        )

        # Step 4: Write the changes to the dict
        configuration_begining[
            QAConfig.keys_questions_partOrAll
        ] = QAConfig.values_qspa_part
        
        return
    
    def qed_enbAll(self):
        global configuration_begining
        conf = configuration_begining

        if conf.get(QAConfig.keys_deductions_mode): self.qed_enb()
        else: self.qed_dsb()
        
        self.config_deduc_ed_container.config(
            text=self.config_deduc_ed_container.cget('text').replace('(Disabled)', '').strip(),
            fg=self.theme.get('ac')
        )
        
        self.qed_entry_enbAll()
        
    def qed_dsbAll(self):
        global configuration_begining
        conf = configuration_begining

        self.config_qed_enb.config(
            state=tk.DISABLED,
            disabledforeground=self.dsbAll_fg
        )
        
        self.config_qed_dsb.config(
            state=tk.DISABLED,
            disabledforeground=self.dsbAll_fg
        )
        
        self.config_deduc_ed_container.config(
            text=self.config_deduc_ed_container.cget('text').replace('(Disabled)', '').strip() + " (Disabled)",
            fg=self.dsbAll_fg
        )
        
        self.qed_entry_dsbAll()
        
    def qed_entry_dsbAll(self):
        self.config_deduc_points_container.config(
            text=self.config_deduc_points_container.cget('text').replace('(Disabled)', '').strip() + " (Disabled)",
            fg=self.dsbAll_fg
        )
        
        self.config_qed_amnt_entry.config(
            state=tk.DISABLED,
            disabledforeground=self.dsbAll_fg,
            disabledbackground=self.theme.get('bg')
        )
    
    def qed_entry_enbAll(self):
        self.config_deduc_points_container.config(
            text=self.config_deduc_points_container.cget('text').replace('(Disabled)', '').strip(),
            fg=self.theme.get('ac')
        )
        
        self.config_qed_amnt_entry.config(
            state=tk.NORMAL,
            disabledforeground=self.theme.get('ac')
        )
    
    def qed_enb(self):
        # Q = Question, ED = Enable Deductions, ENB = Enable
        
        # Step 1: Disable the button and set the color (fg)
        self.config_qed_enb.config(
            state=tk.DISABLED,
            disabledforeground=self.theme.get('ac')
        )
        
        # Step 2: Enable the other button
        self.config_qed_dsb.config(
            state=tk.NORMAL
        )
        
        # Step 4: Write the changes to the dict
        configuration_begining[
            QAConfig.keys_deductions_mode
        ] = True
        
        return
    
    def qed_dsb(self):
        # Q = Question, ED = Enable Deductions, DSB = Disable
                
        # Step 1: Disable the button and set the color (fg)
        self.config_qed_dsb.config(
            state=tk.DISABLED,
            disabledforeground=self.theme.get('ac')
        )
        
        # Step 2: Enable the other button
        self.config_qed_enb.config(
            state=tk.NORMAL
        )
        
        # Step 4: Write the changes to the dict
        configuration_begining[
            QAConfig.keys_deductions_mode
        ] = False
        
        return
    
    def saveConfiguration(self):
        # All information except the two entries has been stored already;
        # load the information from the two entries and save to dict
        # Then OWR the file with the new data
        
        global configuration_begining; global configruationFilename; global apptitle; global configuration_saved
        # Do not load configuration_begining to secondary variable or data won't be saved to the main dict
        
        # QSPA - DivF
        __df = self.config_divf_entry.get()
        
        # QED - Deducs
        __deducs = self.config_qed_amnt_entry.get()
        
        configuration_begining[
            QAConfig.keys_questions_divistionFactor
        ] = __df
        
        configuration_begining[
            QAConfig.keys_deduction_perPoint
        ] = __deducs
        
        # Convert dict to JSON
        __save = json.dumps(configuration_begining, indent=4)
        
        # Save the data
        __IOInst = IO(configruationFilename, append=False)
        __IOInst.saveData(
            __save
        )
        
        configuration_saved = configuration_begining
        
        tkmsb.showinfo(
            apptitle,
            'Saved Configuration Information Successfully'
        )
        
        return

    def io_ie_exportScores(self):
        pass

    def io_ie_import(self):
        self.conf_io_btns(True)
        self.io_import_fn = None

        fn = tkfldl.askopenfilename(
            defaultextension=f".{QAInfo.export_file_extension}",
            filetypes=((f"QA Export (*.{QAInfo.export_file_extension})", f"*.{QAInfo.export_file_extension}"), )
        )

        if not type(fn) is str: fn = None
        elif fn.strip() == '': fn = None
        elif not len(fn.split('.')) == 2:
            tkmsb.showerror(apptitle, f"Unable to deduce file extension.")
            fn = None
        elif not fn.split('.')[-1] == QAInfo.export_file_extension:
            tkmsb.showerror(apptitle, f"Invalid File type '.{fn.split('.')[-1]}'")
            fn = None
        elif not os.path.exists(fn):
            tkmsb.showerror(apptitle, f"(Unusual) Error - Import::IO::1k91:: File Not Found")
            fn = None

        debug(f"IO::1070 >> Import filename = {fn}")

        if fn is None:
            self.io_ie_import_selectedFileLbl.config(text="No File Selected")
            return

        self.io_ie_import_selectedFileLbl.config(text=f"Selected File: {fn}")

        __ioInst = IO(fn)
        raw = __ioInst.autoLoad()
        debug(f"Raw import: {raw}")

        vers = QAInfo.fileIO_version_info_header in raw; versionfound = "<No Version Data>"

        if vers:
            for i in raw.split('\n'):
                if QAInfo.fileIO_version_info_header in i:
                    versData = i.replace(QAInfo.fileIO_version_info_header, '').strip().lower()

                    if len(versData) <= 0:
                        vers = False
                        break

                    versData = QATypeConv.convert(
                        str(
                            QATypeConv.convert(versData, float, returnDataOnly=True)
                        ).split('.')[0].strip().lower(),
                        int,
                        returnDataOnly=True
                    )

                    debug(f"IO_IMPORT::1127 - Version Data = {versData}")

                    valV = QATypeConv.convert(
                        str(QAInfo.versionData[QAInfo.VFKeys['v']]).split('.')[0].strip().lower(),
                        int,
                        returnDataOnly=True
                    )

                    versionfound = f'{versData}.x'

                    if versData == valV: vers = True
                    else: vers = False

                    break

        if not vers:
            debug(f"Invalid version; raising error")
            self.io_ie_import_selectedFileLbl.config(text=f"Selected File: {fn} (Invalid Version Information)")
            tkmsb.showerror(apptitle, f"Invalid File Version Information; Cannot Load File (File compatible with version(s) {versionfound})")
            return

        __num = 0
        __lst = []

        for i in raw.split('\n'):
            if i.strip() == self.IO_DIVEND_KEY: __lst.append('div_end')
            elif i.strip() == self.IO_SCIMPORT_KEY: __lst.append('s')
            elif i.strip() == self.IO_QSIMPORT_KEY: __lst.append('q')
            elif i.strip() == self.IO_CONFIMPORT_KEY: __lst.append('c')

        if len(__lst) % 2 == 0:
            __num = int(len(__lst)/2)
            debug(f"IO::IMPORT::1138:: Clean Div -- __num = {__num}")

        else: # Bruh
            debug(f"IO::IMPORT::1141:: Cleaning Loaded Data")

            clean = []

            On = False; observing = ''

            for i in __lst: # Simplified, smarter
                if i == 'div_end' and not On: continue
                elif i == 'c' or i == 'q' or i == 's':
                    On = True
                    observing = i
                elif i == 'div_end' and On: clean.extend([observing, 'div_end'])

            __lst = clean

            #     On = False; ind = 0
            #
            #     if i == 'div_end' and not On:
            #         if not __lst.index(i)-1 in pops: pops.append(__lst.index(i)-1)
            #
            #     elif i == 's' or i == 'c' or i == 'q':
            #         if not On:
            #             On = True
            #             ind = __lst.index(i)-1
            #
            #         else:
            #             if not ind in pops: pops.append(ind)
            #             ind = __lst.index(i)-1
            #
            #     elif i == 'div_end' and On:
            #         On = False

            # pops = pops[::-1]
            #
            # debug(f"IO::IMPORT::1163:: Popping Indexes {pops} from list {__lst}")
            # for i in pops: debug(f"To pop: {__lst[i]}")
            #
            # for i in pops:
            #     __lst.pop(i)

            debug(f"IO::IMPORT::1168:: Post-pop:: {__lst}")

            __num = int(len(__lst)/2)

        if __num > 0:

            self.conf_io_btns(True)

            if 'c' in __lst:
                self.io_valFile_c = True

            if 's' in __lst:
                self.io_valFile_s = True

            if 'q' in __lst:
                self.io_valFile_q = True

            self.conf_io_btns(False)
            self.io_import_fn = fn

            tkmsb.showinfo(apptitle, f'Found {__num} valid datasets in the file; the appropriate selectors are now enabled')

        else:
            code = "(No Data Found)"
            self.io_ie_import_selectedFileLbl.config(
                text=self.io_ie_import_selectedFileLbl.cget('text').replace(code, '').strip() + f" {code}"
            )

            tkmsb.showerror(apptitle, f"File type is valid; but no (un-corrupted) data could be decoded from the file.")

        return
    
    def io_ie_export(self): # TODO: setup
        pass
    
    def ioConf(self, inv: bool = True):
        if inv: self.io_imConf = not self.io_imConf
        self.io_ie_ICToggle.config(
            state=tk.NORMAL,
            fg=self.theme.get('hg') if self.io_imConf else self.theme.get('fg'),
            bg=self.theme.get('ac') if self.io_imConf else self.theme.get('bg'),
            text=(self.io_ie_ICToggle.cget('text').replace('\u2713', '').strip() + (' \u2713' if self.io_imConf else '')).strip()
        )
    
    def ioQs(self, inv: bool = True):
        if inv: self.io_imQs = not self.io_imQs
        self.io_ie_IQToggle.config(
            state=tk.NORMAL,
            fg=self.theme.get('hg') if self.io_imQs else self.theme.get('fg'),
            bg=self.theme.get('ac') if self.io_imQs else self.theme.get('bg'),
            text=(self.io_ie_IQToggle.cget('text').replace('\u2713', '').strip() + (' \u2713' if self.io_imQs else '')).strip()
        )
    
    def ioSks(self, inv: bool = True):
        if inv: self.io_imSks = not self.io_imSks
        self.io_ie_ISToggle.config(
            state=tk.NORMAL,
            fg=self.theme.get('hg') if self.io_imSks else self.theme.get('fg'),
            bg=self.theme.get('ac') if self.io_imSks else self.theme.get('bg'),
            text=(self.io_ie_ISToggle.cget('text').replace('\u2713', '').strip() + (' \u2713' if self.io_imSks else '')).strip()
        )
    
    def io_commitImport(self):
        global configuration_begining
        global configuration_saved

        if self.io_import_fn is None or type(self.io_import_fn) is not str:
            tkmsb.showerror(apptitle, f"No valid file selected")
            return

        C = self.io_imConf and self.io_valFile_c and type(self.io_import_fn) is str
        S = self.io_imSks and self.io_valFile_s and type(self.io_import_fn) is str
        Q = self.io_imQs and self.io_valFile_q and type(self.io_import_fn) is str

        if not C and not S and not Q:
            tkmsb.showerror(apptitle, f"No import options selected (or an invalid file was selcted)")
            return

        __raw = IO(self.io_import_fn).autoLoad().split("\n")

        if C:
            # Finding the Conf
            conf_ind = [None, None] # Indexes (start > end)
            on = False
            for i in __raw:
                if self.IO_CONFIMPORT_KEY in i:
                    on = True
                    conf_ind[0] = __raw.index(i)

                if on and self.IO_DIVEND_KEY in i:
                    on = False
                    conf_ind[1] = __raw.index(i)
                    break

            __str = __raw[conf_ind[0]:conf_ind[1]]

            # Basic Conf Loading
            conf_raw = {}
            for i in __str:
                if self.IO_CONFIMPORT_KEY not in i and self.IO_DIVEND_KEY not in i:
                    i = i.strip()
                    k = i.split(' ')[0].strip(); v = i.replace(k, '').strip()

                    if len(k.strip()) > 0 and len(v.strip()) > 0:
                        conf_raw[k.strip()] = v.strip()

            # Validating the Conf
            val = True
            conf_conv = {}

            for i in QAConfig.default_configuration.keys():
                if i not in conf_raw:
                    val = False
                    break

            if val:
                pops = []

                for i in conf_raw:
                    if i not in QAConfig.default_configuration.keys():
                        pops.append(i) # Remove un necessary information.

                    else:
                        try:
                            tmp = QATypeConv.convert(
                                conf_raw[i].strip(),
                                type(QAConfig.default_configuration[i]),
                                returnDataOnly=True
                            )
                            debug(f"Converted '{conf_raw[i].strip()}' to '{tmp}' ({type(conf_raw[i])} to {type(QAConfig.default_configuration[i])})")
                            conf_conv[i] = tmp

                        except Exception as E1:
                            if type(QAConfig.default_configuration[i]) is bool:
                                try:
                                    tmp = conf_raw[i].strip().lower() == '0' or conf_raw[i].strip().lower() == 'true'

                                    debug(
                                        f"Converted '{conf_raw[i].strip()}' to '{tmp}' ({type(conf_raw[i])} to {type(QAConfig.default_configuration[i])})")

                                    conf_conv[i] = tmp

                                except Exception as E:
                                    debug(f"Failed to convert entry for '{i}' (error = {E1} (og) {E} (new))")

                                    val = False
                                    break

                if val:
                    for i in pops:
                        conf_raw.pop(i)
                        conf_conv.pop(i)

            if not val:
                self.conf_io_btns(True)
                self.io_ie_import_selectedFileLbl.config(
                    text=f"{self.io_import_fn} (Import Terminated)"
                )
                tkmsb.showerror(apptitle, f"Invalid Configuration Found; for security reasons, the remaining importing process will be terminated.")

                return

            # Set
            configuration_begining = configuration_saved = conf_conv
            __save = json.dumps(conf_conv, indent=4)

            # Write
            __Inst = IO("{}\\{}".format(
                QAInfo.appdataLoc.strip('\\').strip(),
                QAInfo.confFilename.strip('\\').strip()
            ), append=False)

            __Inst.saveData(__save)

        if S:
            tkmsb.showinfo(apptitle, f"Unsupported feature; please wait until this feature has been addded.")

        if Q:
            # Finding the Questions
            qs_ind = [None, None]  # Indexes (start > end)
            on = False
            for i in __raw:
                if self.IO_QSIMPORT_KEY in i:
                    on = True
                    qs_ind[0] = __raw.index(i)

                if on and self.IO_DIVEND_KEY in i:
                    on = False
                    qs_ind[1] = __raw.index(i)
                    break

            __str = __raw[qs_ind[0]:qs_ind[1]]

            # Basic Conf Loading
            qs_raw = {}
            for i in __str:
                if self.IO_QSIMPORT_KEY not in i and self.IO_DIVEND_KEY not in i:
                    i = i.strip()
                    k = i.split(QAInfo.QuestionSeperators['QA'])[0].strip()
                    v = i.replace(k, '').replace(QAInfo.QuestionSeperators['QA'], '').strip()

                    if len(k.strip()) > 0 and len(v.strip()) > 0:
                        qs_raw[k.strip()] = v.strip()

            val1 = len(qs_raw) > 0; debug(f"IMPORT::1413 :: Questions read (raw) :: {qs_raw} :: Minimum condition met? {val1}")

            if not val1:
                tkmsb.showerror(apptitle, f"Unable to read any questions from the file")

            if val1:
                # Continue the 'Q' routine

                qs_cleaned = qs_raw; pops = []
                for i in qs_raw:
                    if len(i.strip()) <= 0: pops.append(i)

                for i in pops: qs_cleaned.pop(i)

                append = tkmsb.askyesno(apptitle, f'Do you want to append the new questions?\n\nYes = Append\nNo = Overwrite')

                if append:
                    og: list = IO(
                        "{}\\{}".format(
                            QAInfo.appdataLoc.strip("\\").strip(),
                            QAInfo.qasFilename.strip("\\").strip()
                        ),
                        encrypt=QAInfo.questions_file_info.get('enc'),
                        encoding=QAInfo.questions_file_info.get('encoding')
                    ).autoLoad().split(
                       "\n"
                    )

                    # QAInfo.QuestionSeperators.get('N') is for IN question newlines, questions are still separated by \n

                    debug(og)

                    og_dict = {}

                    for i in og:
                        k = i.split(QAInfo.QuestionSeperators.get('QA'))[0].strip()
                        v = i.replace(k, '').replace(QAInfo.QuestionSeperators.get('QA'), '').strip()

                        if len(k) > 0 and len(v) > 0:
                            og_dict[k] = v

                    __save_plain_str = ''
                    questions = og_dict; questions.update(qs_cleaned)

                    debug(f"Saving the following dictionary (questions): {questions}")

                    _sps = "" # Save - Plain String

                    for i in questions:
                        q = i.strip()
                        a = questions[i].strip()

                        _sps += f"{q}{QAInfo.QuestionSeperators.get('QA')}{a}\n" # Template

                    debug(f"Formulated (plain text) questions str: {_sps}")

                    IO(
                        "{}\\{}".format(
                            QAInfo.appdataLoc.strip("\\").strip(),
                            QAInfo.qasFilename.strip("\\").strip()
                        ),
                        encrypt=QAInfo.questions_file_info.get('enc'),
                        encoding=QAInfo.questions_file_info.get('encoding')
                    ).saveData(_sps)

                else:
                    __save_plain_str = ''
                    questions = qs_cleaned

                    debug(f"Saving the following dictionary (questions): {questions}")

                    _sps = ""  # Save - Plain String

                    for i in questions:
                        q = i.strip()
                        a = questions[i].strip()

                        _sps += f"{q}{QAInfo.QuestionSeperators.get('QA')}{a}\n"  # Template

                    debug(f"Formulated (plain text) questions str: {_sps}")

                    IO(
                        "{}\\{}".format(
                            QAInfo.appdataLoc.strip("\\").strip(),
                            QAInfo.qasFilename.strip("\\").strip()
                        ),
                        encrypt=QAInfo.questions_file_info.get('enc'),
                        encoding=QAInfo.questions_file_info.get('encoding')
                    ).saveData(_sps)

        tkmsb.showinfo(
            apptitle,
            "Successfully inserted (valid) requested information."
        )

        return

    # Logic Functions 

    def conf_io_btns(self, reset=False):
        # Reset
        if reset:
            self.io_imSks = False; self.io_imQs = False; self.io_imConf = False
            self.io_valFile_q = False
            self.io_valFile_s = False
            self.io_valFile_c = False

        # Configuration Import Button
        if self.io_valFile_c:
            self.ioConf(False)
        else:
            self.ioConf(False)
            self.io_ie_ICToggle.config(
                state=tk.DISABLED,
                disabledforeground=self.dsbAll_fg
            )

        # Questions Import Button
        if self.io_valFile_q:
            self.ioQs(False)
        else:
            self.ioQs(False)
            self.io_ie_IQToggle.config(
                state=tk.DISABLED,
                disabledforeground=self.dsbAll_fg
            )

        # Scores Import Button
        if self.io_valFile_s:
            self.ioSks(False)
        else:
            self.ioSks(False)
            self.io_ie_ISToggle.config(
                state=tk.DISABLED,
                disabledforeground=self.dsbAll_fg
            )

        # Import Data
        if not self.io_valFile_s and not self.io_valFile_c and not self.io_valFile_q:
            self.io_ie_importCommitButton.config(
                state=tk.DISABLED,
                disabledforeground=self.dsbAll_fg
            )
        else:
            self.io_ie_importCommitButton.config(
                state=tk.NORMAL
            )

    def setConfigStates(self):
        global configuration_begining
        conf = configuration_begining
        
        # QSPA
        self.qspa_enbAll() # Does the logic check
        
        # QED
        if conf.get(QAConfig.keys_deductions_mode): self.qed_enb()
        else: self.qed_dsb()
        
        # QS Div Factor
        qsdf = str(conf.get(QAConfig.keys_questions_divistionFactor))
        self.config_divf_entry.delete(0, tk.END)
        self.config_divf_entry.insert(0, qsdf)
        
        # QED Entry
        qed_amnt = str(conf.get(QAConfig.keys_deduction_perPoint))
        self.config_qed_amnt_entry.delete(0, tk.END)
        self.config_qed_amnt_entry.insert(0, qed_amnt)
        
        # ACC (Call at end)
        if conf.get(QAConfig.keys_quizTaker_customConfig): self.acc_enb()
        else: self.acc_dsb()
        
        return
    
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

def __logError(errorCode: str, **kwargs):
    crash_msg: str  = f"The application has encountered an error; internal diagnostics will be run during the next boot sequence of this application.\n\nDiagnostic Code: {errorCode}"
        
    flags = {
        
        'logError': [True, (bool, )],
        
        'exit': [False, (bool, )],
        'exitCode': [-1, (str, int)],
        
        'showUI': [True, (bool, )],
        'UI_Message': [crash_msg, (str, )],
        
        'runDiagnostics': [False, (bool, )],
        'diagnosticsInfo': [crash_msg, (str, )],
        'diagnosticsFunctionName': [QAJSONHandler.QAFlags().no_func_id, (str, )]
        
    }; flags = flags_handler(flags, kwargs, __rePlain=True)
    
    if flags['logError']:
        debug(f"The application encountered an error; exit: {flags['exit']}; exitCode: {flags['exitCode']}, runDiagnostics: {flags['runDiagnostics']}, diagnostics_code: {flags['diagnosticsInfo']}, error code: {errorCode}")

    if flags['showUI']:
        tkmsb.showerror(apptitle, flags['UI_Message'])
        
    if flags['runDiagnostics']: # TODO: fix this
        __inst = JSON()
        
        dinfo = ""
        dfunction = flags['diagnosticsFunctionName']
        
        __inst.logCrash(info=dinfo, functionCall=dfunction)
        
    if flags['exit']:
        application_exit(flags['exitCode'])
    
def application_exit(code: str = "0") -> None:
    debug(f"Exiting with code '{code}'")
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

def loadConfiguration() -> dict:
    global configruationFilename
    
    if not os.path.exists(configruationFilename):
        code = JSON().getFlag('codes.json', QAInfo.codes_keys.get('configuration_file_error').get('conf_file_missing'))
        
        codeInfo = JSON().getFlag('codes.json', "info", return_boolean=False)
        codeInfo = codeInfo[code]
        
        __logError(
            code,
            runDiagnostics=True,
            diagnosticsInfo=code,
            diagnosticsFunctionName=QAJSONHandler.QAFlags().CONF_corruption_fnc,
            UI_Message=f"An error occured whilst loading the configuration;\n\nError Code: {code}\n\nError Info: {codeInfo}",
            exit=True,
            exitCode=f"QAErrors.ConfigurationError"
        )

        raise QAErrors.ConfigurationError(code)
    
    try:
        __IO = IO(configruationFilename)
        raw = __IO.autoLoad()
        _dict = json.loads(raw)
    
    except:
        code_key = QAInfo.codes_keys['configuration_file_error']['conf_file_corrupted']
        code = JSON().getFlag('codes.json', code_key, return_boolean=False)
        
        codeInfo = JSON().getFlag('codes.json', "info", return_boolean=False)
        codeInfo = codeInfo[code]
        
        __logError(
            code,
            runDiagnostics=True,
            diagnosticsInfo=code,
            diagnosticsFunctionName=QAJSONHandler.QAFlags().CONF_corruption_fnc,
            UI_Message=f"An error occured whilst loading the configuration;\n\nError Code: {code}\n\nError Info: {codeInfo}",
            exit=True,
            exitCode=f"QAErrors.ConfigurationError"
        )
        
        raise QAErrors.ConfigurationError(code)
    
    return _dict

def conf_saved() -> bool:
    global configuration_begining
    global configuration_saved
    
    return configuration_saved == configuration_begining

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

# Adjust Splash
set_boot_progress(3)

configuration_begining = loadConfiguration()

if type(configuration_begining) is not dict:
    debug(f"ADMT.792:: Could not load configuration; invalid type {type(configuration_begining)}")
    code_key = QAInfo.codes_keys['configuration_file_error']['conf_file_corrupted']
    code = JSON().getFlag('codes.json', code_key, return_boolean=False)
    
    codeInfo = JSON().getFlag('codes.json', "info", return_boolean=False)
    codeInfo = codeInfo[code]
    
    __logError(
        code,
        runDiagnostics=True,
        diagnosticsInfo=code,
        diagnosticsFunctionName=QAJSONHandler.QAFlags().CONF_corruption_fnc,
        UI_Message=f"An error occured whilst loading the configuration;\n\nError Code: {code}\n\nError Info: {codeInfo}\n\nRef: QAADMT.792",
        exit=True,
        exitCode=f"QAErrors.ConfigurationError"
    )

# Pre-boot logic

debug(f"Configuraion Loaded: {configuration_begining}")
configuration_saved = configuration_begining

if not configuration_begining.get(QAConfig.keys_inDist):
    apptitle += " (Experimental Version)"
    tkmsb.showwarning(apptitle, f"Warning: The following application has been marked as 'Experimental' and thus may act in an unstable manner.\n\nApplication By: Geetansh Gautam, Coding Made Fun")

# Adjust Splash
set_boot_progress(4)

JSON().boot_check() # Boot checks (global_nv_flags_fn file flags run these checks...)

# Adjust Splash
set_boot_progress(5)

if not QA_OVC.check():
    tkmsb.showwarning(apptitle, f"You are running an older version of the application; the database suggests that version '{QA_OVC.latest()}' is the latest (the current installed version is {QAInfo.versionData.get(QAInfo.VFKeys.get('v'))})")

# Close the splash screen
show_splash_completion()

QASplash.destroy(splObj)

# Run Boot Command (UI)
UI()
