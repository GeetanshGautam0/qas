"""

FTSRA Version 2
Complete Re-write (3)

Developed By Geetansh Gautam, Coding Made Fun
(C) Coding Made Fun

Intended for Quizzing Application Suite Version 2.bb.aa

"""

# Custom modules
import qa_time as QATime
import qa_logging as QaLog
import qa_appinfo as QAInfo
import qa_diagnostics as QADiagnostics
import qa_theme as QATheme
import qa_globalFlags as QAJSONHandler

# Python default modules
import sys, os, threading, shutil, traceback, math
import tkinter as tk
from tkinter import messagebox as tkmsb
from tkinter import filedialog as tkfile

# Global Variables
boot_time_start = QATime.now()
apptitle = "QA FTS+RA Utility"

# Class Declarations

class UI(threading.Thread):
    def __init__(self, **flags):
        # Thread
        self.thread = threading.Thread
        self.thread.__init__(self)

        # Flags defaults
        def_title = 'FTS + RA Utility'
        icon = QAInfo.icons_ico['ftsra']

        # Flags
        self.flags = {
            'frame_title': [def_title, (def_title, str)],
            'title_lbl_txt': [def_title, (def_title, str)],
            'padX': [20, (20, int)],
            'padY': [20, (20, int)],
            'icon': [icon, (icon, str)]
        }

        self.flags = flags_handler(ref=self.flags, flags=flags, __rePlain=True)

        # Basic UI
        self.root = tk.Tk() # Main UI Frame

        # Size
        self.ss = (self.root.winfo_screenwidth(), self.root.winfo_screenheight()) # Screen Size
        self.ds = (700, 650) # Default Size
        self.ws = (self.ss[0] if self.ds[0] >= self.ss[0] else self.ds[0],
                   self.ss[1] if self.ds[1] >= self.ss[1] else self.ds[1]) # Window Size
        self.wp = (int(self.ss[0]/2 - self.ws[0]/2),
                   int(self.ss[1]/2 - self.ws[1]/2)) # Window Position

        # Class (Instance-Based) Vars
        self.script_key = 'ftsra'

        self.Theme: dict = QATheme.load_theme() # Theme dictionary
        debug(f"Loaded the following theme: {self.Theme}")

        # UI
        self.title = tk.Label(self.root) # Title (Label)
        self.sbttl = tk.Label(self.root) # Subtitle (Label) [not used?]

        self.btn_grp = tk.LabelFrame(self.root) # Button Container (Label Frame)
        self.btns_owr = tk.Button(self.btn_grp) # Button (Overwrite)
        self.btns_cpy = tk.Button(self.btn_grp) # Button (Copy Files)
        self.btns_owr_conf = tk.Button(self.btn_grp) # Button (OWR Configuration)

        self.misc_btns_grp = tk.LabelFrame(self.root)
        self.btns_help = tk.Button(self.misc_btns_grp)
        self.btns_checkFiles = tk.Button(self.misc_btns_grp)

        self.btns = [] # BTNs will be added automatically later
        self.lbls = [] # LBLs will be added automatically later

        # Instances
        self.io_instance = IO() # IO Instance
        self.ch_instance = CrashHandler() # Crash Handler Instance
        self.eh_instance = ErrorHandler() # Error Handler Instance

        # Last things
        self.start() # Starts thread and calls self.run

        global boot_time_start # Boot start time
        boot_time_calc(start=boot_time_start, end=QATime.now()) # Calculate boot time

        self.root.mainloop() # Run UI (Last statement in UI.__init__)

    def enable_all_btns(self) -> None:
        for i in self.btns:
            debug(f"Set button state 'ENABLED' (NORMAL) for button {i.cget('text')}")
            i.config(state=tk.NORMAL)

    def disable_all_btns(self) -> None:
        for i in self.btns:
            debug(f"Set button state 'DISABLED' for button {i.cget('text')}")
            i.config(state=tk.DISABLED)

    def update_ui(self) -> None:
        debug(f"Updating theme for label types {self.lbls} an button types {self.btns} and {self.root}")

        self.root.iconbitmap(QAInfo.icons_ico.get('ftsra'))
        
        # Buttons   
        def set_btn_theme(btn_handler, Theme):
            btn_handler.config(
                bg=Theme['bg'],  # BG Color
                fg=Theme['fg'],  # FG Color
                activebackground=Theme['ac'],  # Active BG color (Accent color set)
                activeforeground=Theme['hg'],  # Active FG color (Highlight color set)
                highlightbackground=Theme['border_color'], # Border color
                bd=Theme['border'],  # Border Width
                font=(Theme['font'], Theme['btn_fsize']),  # Font
            )  # Set theme

        # Labels
        def set_lbl_theme(lbl_handler, Theme):
            fsize = lbl_handler.cget('font').split(" ")[-1]

            lbl_handler.config(
                bg=Theme['bg'], # Background Color
                fg=Theme['fg'], # Foreground Color'))
            )

            # Font
            try:
                int(fsize)
                debug(
                    f"Using font {(Theme['font'], fsize)} for {lbl_handler} ({lbl_handler.cget('text')})")
                lbl_handler.config(font=(Theme['font'], fsize))

            except:
                debug(f"Using font {(Theme['font'], Theme['min_fsize'])} for {lbl_handler} ({lbl_handler.cget('text')})")
                lbl_handler.config(font=(Theme['font'], Theme['min_fsize']))

        th_inst = QATheme.Get()
        th_inst.refresh_theme()

        self.Theme = th_inst.get('theme')

        # Buttons
        for i in self.btns: set_btn_theme(i, self.Theme)

        # Labels + LabelFrames
        for i in self.lbls: set_lbl_theme(i, self.Theme)

        # Root
        self.root.config(bg=self.Theme['bg'])

    def run(self) -> None:
        # UI configuration
        title = self.flags['frame_title']
        geometry = f"{self.ws[0]}x{self.ws[1]}+{self.wp[0]}+{self.wp[1]}"
        icon = self.flags['icon']

        self.root.title(title)
        self.root.geometry(geometry)
        self.root.iconbitmap(icon)
        self.root.config(background=self.Theme['bg'])
        self.root.protocol("WM_DELETE_WINDOW", Exit)

        debug(f"Set frame title to '{title}'")
        debug(f"Set frame geometry to {geometry}")
        debug(f"Using icon {icon} for frame.")
        debug(f"Set frame background to {self.Theme['bg']}")

        # Element Configuration
        def set_btn_data(btn_handler, text, command, Theme):
            if not btn_handler in self.btns: self.btns.append(btn_handler)

            btn_handler.config(text=text, command=command)  # Set text + command
            btn_handler.config(
                bg=Theme['bg'],  # BG Color
                fg=Theme['fg'],  # FG Color
                activebackground=Theme['ac'],  # Active BG color (Accent color set)
                activeforeground=Theme['hg'],  # Active FG color (Highlight color set)
                bd=Theme['border'],  # Border Width
                font=(Theme['font'], Theme['btn_fsize']) # Font
            )  # Set theme

        def set_lbl_data(instance, Theme, fsize):
            if instance not in self.lbls: self.lbls.append(instance)

            instance.config(
                bg=Theme['bg'],  # BG Color
                fg=Theme['fg'], # FG Color
                font=(Theme['font'], fsize) # Font
            )  # Set theme

        # Title label
        self.title.config(text=self.flags['title_lbl_txt']) # Set text
        ttl_fsize = int(
            self.ws[0] / len(self.title.cget('text'))
        ) # Calculate title font size
        set_lbl_data(self.title, self.Theme, ttl_fsize) # Set theme and add to self.lbls

        # Subtitle (not used)

        # Btns Lbl Frame
        self.btn_grp.config(text='IO Control') # Set text
        set_lbl_data(self.btn_grp, self.Theme, self.Theme.get('min_fsize')) # Set theme and add to self.lbls

        # Misc. btns lbl frame
        self.misc_btns_grp.config(text='Miscellaneous') # Set text
        set_lbl_data(self.misc_btns_grp, self.Theme, self.Theme.get('min_fsize')) # Set theme and add to self.lbls

        # Buttons

        # OWR (Overwrite) button
        set_btn_data(self.btns_owr, "Reset All Files", self.owr_handler, self.Theme)

        # OWR (Overwrite) config button
        set_btn_data(self.btns_owr_conf, "Reset Configuration File", self.owr_config_handler, self.Theme)

        # Copy files button
        set_btn_data(self.btns_cpy, "Copy Missing Files", self.cpy_handler, self.Theme)

        # Information Button
        set_btn_data(self.btns_help, "Help Me", self.aid, self.Theme)

        # Check Files Button
        set_btn_data(self.btns_checkFiles, "Check File Integrity", self.check_files, self.Theme)

        # Element Placement
        px = self.flags['padX']; py = self.flags['padY']; pxh = int(px/2); pyh = int(py/2)

        # Top -> Bottom (IGNR L->R)
        self.title.pack(fill=tk.BOTH, expand=True)
        self.btn_grp.pack(fill=tk.BOTH, expand=True, padx=px, pady=(py, pyh))
        self.misc_btns_grp.pack(fill=tk.BOTH, expand=True, padx=px, pady=(pyh, py))

        def place_btn(btn_name, padx, pady):
            btn_name.pack(fill=tk.BOTH, expand=True, padx=padx, pady=pady, side=tk.LEFT)

        place_btn(self.btns_owr, (px, pxh), py)
        place_btn(self.btns_owr_conf, pxh, py)
        place_btn(self.btns_cpy, (pxh, px), py)

        self.btns_help.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(px, pxh), pady=py)
        self.btns_checkFiles.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=(pxh, px), pady=py)

    # Button Handlers
    def owr_handler(self) -> None:
        global apptitle

        self.disable_all_btns() # Disable all inputs

        debug(f"Running UI.owr_handler")
        # Confirm overwrite
        confirm = tkmsb.askyesno(apptitle,
                                 f"This process will overwrite all data relevant to the application and cannot be undone; this data contains all scores, themes, configuration, questions, question backups, etc.\n\nAre you sure you want to continue?")

        if not confirm:
            debug(f"User wishes to NOT continue; aborting")
            self.enable_all_btns()  # Enable all inputs
            return

        debug(f"User wishes to continue with overwrite")

        self.io_instance.owr_files(preConf=True) # Call IO.owr (Last thing)

        self.update_ui()

        self.enable_all_btns() # Enable all inputs

    def owr_config_handler(self) -> None:
        global apptitle

        self.disable_all_btns()

        debug(f"Running UI.owr_config_handler")

        # Confirm overwrite
        confirm = tkmsb.askyesno(apptitle,
                                 f"This process will overwrite all configuration data relevant to the application and cannot be undone.\nAre you sure you want to continue?")

        if not confirm:
            debug(f"User wishes to NOT continue; aborting")
            self.enable_all_btns()
            return

        debug(f"User wishes to continue with overwrite")

        self.io_instance.owr_config(preConf=True)  # Call IO.owr (Last thing)
        self.enable_all_btns()

    def cpy_handler(self) -> None:
        self.disable_all_btns()
        debug(f"Running UI.cpy_handler")
        self.io_instance.copy_files()
        self.update_ui()
        self.enable_all_btns()

    def aid(self) -> None:
        debug(f"Running UI.aid")
        os.system(f"{QAInfo.help_files[self.script_key]}")

    def check_files(self) -> None:

        diagnostics_inst = QADiagnostics.Diagnostics()
        diagnostics_data = QADiagnostics.Data()
        result = diagnostics_inst.run_diagnostics(diagnostics_data.FTSRA_appdata_checks)

        if result:
            tkmsb.showinfo(apptitle, f"All files inspected are valid.")

        else:
            corrections = QADiagnostics.Corrections()
            corrections.run_correction(diagnostics_data.FTSRA_appdata_checks)

            tkmsb.showinfo(apptitle, f"Failed internal tests; the errors were patched logged.")

        pass

    def __del__(self):
        pass

class CrashHandler(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)

        self.jsonHandler_instance = QAJSONHandler.QAFlags()

        self.start()

    def log_crash(self, time, info: str, function: str):
        debug(f"Logging crash from time {time}")

        # Variables
        global apptitle
        time = f"{time}" # "Convert" to string
        ID = self.jsonHandler_instance.ftsra_crash_id

        # Log
        json_setFlag(ID, {
            self.jsonHandler_instance.log_time_id: time,
            self.jsonHandler_instance.log_function_id: function,
            self.jsonHandler_instance.log_info_id: info,
            self.jsonHandler_instance.log_unr_id: True
        })

    def log_event(self, ID: str, info: any):
        if ID is None: ID = self.jsonHandler_instance.no_func_id

        debug(f"Logging event with ID {ID} ")
        json_setFlag(ID, info)

    def boot_check(self) -> bool:
        result = True # True = passed, False = failed, ran scripts
        global apptitle

        if json_getFlag(self.jsonHandler_instance.ftsra_crash_id): # If the thing exists
            debug(f"An error log exists in the global_nv_flags file")

            check2 = json_getFlag(self.jsonHandler_instance.ftsra_crash_id, mode=any)

            if check2[self.jsonHandler_instance.log_unr_id]: # If unresolved
                tkmsb.showerror(apptitle, f"Found unresolved boot error flags; running diagnostics.\n\nPress OK to continue.")

                debug(f"The error was marked as unresolved; running diagnostics.")
                result = False

                logged_info = {
                    'function': check2[self.jsonHandler_instance.log_function_id],
                    'time': check2[self.jsonHandler_instance.log_time_id],
                    'info': check2[self.jsonHandler_instance.log_info_id]
                }

                debug(f"Time of error: {logged_info['time']}; info: {logged_info['info']}")
                debug(f"Running diagnostics script with key {logged_info['function']}")

                # Run Diagnostics
                diagnostics = QADiagnostics.Diagnostics()
                diagnostics_results = diagnostics.run_diagnostics(key=logged_info['function'])

                if not diagnostics_results:
                    debug(f"Diagnostics failed; running correction scripts")
                    tkmsb.showerror(apptitle, f"Failed requested tests; running correction scripts.\n\nPress OK to continue.")

                    # Corrections
                    corrections = QADiagnostics.Corrections()
                    corrections.run_correction(logged_info['function'])

                else:
                    debug(f"Diagnostics passed; still returning False")
                    tkmsb.showinfo(apptitle, f"Passed requested tests")

                # Log event in the same file
                ID = self.jsonHandler_instance.FTSRA_timed_log.strip() + f"{QATime.now()}"
                debug(f"Logging boot error/corrections with key {ID}")

                debug(f"Marking error as 'RESOLVED'")
                toSave = check2
                toSave[self.jsonHandler_instance.log_unr_id] = False
                json_setFlag(self.jsonHandler_instance.ftsra_crash_id, toSave)
                tkmsb.showinfo(apptitle, f"Cleared boot-error flag.")

                self.log_event(ID, {
                    'crash_time': logged_info['time'],
                    'crash_info': logged_info['info'],
                    'crash_function_key': logged_info['function'],
                    'crash_diagnostics_passed': diagnostics_results
                })

            else:
                debug(f"Error was marked as resolved before correction or diagnostics scripts were ran; starting app normally.")

        return result

    def __del__(self):
        pass

class ErrorHandler(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)

        self.ch_instance = CrashHandler()

        self.start()

    def error_handler(self, err_info: str = "No diagnostic information", **flags) -> None:
        """
        **QA_APPS_FTSRA.ErrorHandler.error_handler**

        :param err_info: Error Information (str)
        :param flags: Flags (dict; see Supported Flags for more information)
        :return: None

        ===================

        **Supported Flags**

        1) *exit*
            * Type: bool
            * Default: False
            * Other supported inputs: --
            * Information: Should the function terminate the application when done with the error handling?

        2) *exit_code*
            * Type: str, int
            * Other supported inputs: --
            * Default: 1 (int)
            * Information: The exit code to exit with (only applies if *exit* is set to *True*)

        3) *log_error*
            * Type: bool
            * Other Supported Inputs: --
            * Default: True
            * Information: Should the application log the error message to the debug file?

        4) *show_ui*
            * Type: bool
            * Other Supported Inputs: --
            * Default: True
            * Information: Should the error be shown on a tkinter.messagebox.showerror dialogue?

        5) *customUIMsg*
            * Type: str
            * Other Supported Inputs: *None* (NoneType)
            * Default: None
            * Information:
                * If set to *type str*, the application will display the given string in the error dialogue (applicable only for *show_ui* = *True*)
                * If set to *None*, the application will display a concatenated string of the base string + err_info in the error dialogue (applicable only for *show_ui* = *True*)

        6) *log_crash*
            * Type: bool
            * Other Supported Inputs: --
            * Default: False
            * Information: Automatically call *QA_apps_ftsra.CrashHandler.log_crash()* with the given information?

        7) *crash_function*
            * Type: str
            * Other Supported Inputs: --
            * Default: qa_diagnostics.Data.no_func_key
            * Information: Function key for the appropriate diagnostic + correction function; note that the key must be a valid variable in *qa_diagnostics*

        8) *crash_info*
            * Type: str
            * Other Supported Inputs: --
            * Default: "No Diagnostic Information"
            * Information: CrashHandler.crash_info; only required if *log_crash* is set to *True*


        ===================

        """

        # Globals
        global apptitle

        # Defaults
        no_func_id = QADiagnostics.Data()
        no_func_id = no_func_id.no_func_key

        def_cinfo = "No diagnostic information"

        Flags = {
            #
            'exit': [False, (False, bool)],
            'exit_code': [1, (1, str, int)],
            'log_error': [True, (True, bool)],
            'show_ui': [True, (True, bool)],
            'customUIMsg': [None, (None, type(None), str)],

            # Crash Handler
            'log_crash': [False, (False, bool)],
            'crash_function': [no_func_id, (no_func_id, str)],
            'crash_info': [def_cinfo, (def_cinfo, str)]
        }

        Flags = flags_handler(Flags, flags, __rePlain=True)

        # Step 1: Figure out the string (if needed)
        err_string = err_info
        base_str = "An error occurred whilst running an application script"
        severity_str = {
            'low': '.\n\nMore Diagnostic Information:\n',
            'high': ' and the application needs to be terminated due to the severity of the error.\n\nMore Diagnostic Information:\n'
        }

        if Flags['show_ui'] or Flags['log_error']: # If needed; else don't waste time
            if Flags['customUIMsg'] is None: # Use base.join(err_info)
                err_string = base_str.join([
                    severity_str['low'] if not Flags['exit'] else severity_str['high'],
                    err_info
                    ])

            else: err_string = Flags['customUIMsg'] # Use custom str

        debug(f"Loaded the following error string: {err_string}")

        # Step 2: Show UI (if needed)
        temp = tkmsb.showerror(apptitle, err_string) if Flags['show_ui'] else None

        # Step 3: Log (If needed)
        debug(f"The following error occurred: {err_string}") # time is shown in debug logs automatically.

        # Stp 4: CrashHandler (If needed)
        if Flags['log_crash']:
            self.ch_instance.log_crash(
                time=QATime.now(),
                info=Flags['crash_info'],
                function=Flags['crash_function']
            )

        # Step 5: Exit (if needed)
        temp = Exit(Flags['exit_code']) if Flags['exit'] else None

        debug(f"Finished error handling")

    def __del__(self):
        pass


# Functions

def Exit(_code: any=0):
    sys.exit(_code)

def debug(debug_data) -> None:
    Log = QaLog.Log(); LogVar = QaLog.Variables()
    sc_name = sys.argv[0].replace("/","\\").split("\\")[-1].strip().split('.')[0].strip() # Script name

    if not LogVar.genDebugFile(): Log.logFile_create(sc_name)
    Log.log(data=debug_data, from_=sc_name)

    return

def boot_time_calc(start, end) -> None:
    btime = QATime.calcDelta(start=start, end=end)
    debug(f'FTSRA booted in "{btime}"')

def json_setFlag(flagID: str, data: any, **flags) -> None:
    """
    **QA_APPS_FTSRA.json_setFlag**

    :param flagID: Flag ID (dict key; str)
    :param data: Flag Data (dict data; any)
    :param flags: Flags (See Supported Flags)
    :return: None

    =================

    **Supported Flags**

    1) *filename*
        * Type: str
        * Other Supported Inputs: --
        * Default: qa_appinfo.appdataLoc + qa_globalFlags.flags_fn
        * Information: Location of the JSON file in question.

    2) *append*
        * Type: bool
        * Other Supported Inputs: --
        * Default: True [HIGHLY RECOMMENDED]
        * Information: Append new data to JSON file instead of a complete overwrite.

    3) *reloadJSON*
        * Type: bool
        * Other Supported Inputs: --
        * Default: True [HIGHLY RECOMMENDED]
        * Information: Reload JSON dictionary to memory before setting data, and after.

    =================

    """

    # Vars
    JSONHandlerInstance = QAJSONHandler.QAFlags()
    ref = JSONHandlerInstance.SET

    # Defaults
    fn = f"{QAInfo.appdataLoc}\\{JSONHandlerInstance.flags_fn}"

    # Flags
    Flags = {
        'filename': [fn, (fn, str)],
        'append': [True, (True, bool)],
        'reloadJSON': [True, (True, bool)]
    }

    Flags = flags_handler(Flags, flags, __rePlain=True)

    # Logic
    debug(f"Setting JSON flag in file {Flags['filename']} for {flagID} to {data}")

    JSONHandlerInstance.io(
        Key=ref,
        data={
            flagID: data
        },
        appendData=Flags['append'],
        reloadJSON=Flags['reloadJSON'],
        filename=Flags['filename']
    )

def json_getFlag(flagID: str, **flags) -> any:
    """
    **QA_APPS_FTSRA.json_getFlag**

    :param flagID: Flag ID (Dict Key; str)
    :param flags: Flags (See Supported Flags)
    :return: any

    ===========

    **Return Info**

    * The function will return whatever you've selected; this can be a boolean or any;
    * If set to *bool* mode, the *bool* output represents whether if there is any valid data for the requested key in the given file.
    * If set to *any* mode, the output is the data for the given flag ID; if the ID is invalid, the output will be *None*

    ==========

    **Supported Flags**

    1) *filename*
        * Type: str
        * Other Supported Inputs: --
        * Default: qa_appinfo.appdataLoc + qa_globalFlags.flags_fn
        * Information: Path to the JSON file

    2) *mode*
        * Type: type; supported: *any*, *bool*
        * Other Supported Inputs: --
        * Default: *bool*
        * Information: Read *Return Info*; note that if set to anything but *any* or *bool*, the variable will be reset to *bool mode*

    3) *reloadJSON*
        * Type: bool
        * Other Supported Inputs: --
        * Default: True (Highly Recommended)
        * Information: Update JSON to memory before querying flag ID.

    ==========

    """

    # Defaults
    JSONHandlerInstance = QAJSONHandler.QAFlags()
    def_fn = f"{QAInfo.appdataLoc}\\{JSONHandlerInstance.flags_fn}"

    # Flags
    Flags = {
        'filename': [def_fn, (def_fn, str)], # JSON File
        'mode': [bool, (bool, type)], # any = return the data; bool = return existence boolean
        'reloadJSON': [True, (True, bool)] # reload JSON before getting flag data
    }; Flags = flags_handler(Flags, flags, __rePlain=True)

    # Vars
    Key = JSONHandlerInstance.GET

    debug(f"Querying ID {flagID} in {Flags['filename']}")
    try:
        output = JSONHandlerInstance.io(Key=Key,
                                        key=flagID,
                                        reloadJSON=Flags['reloadJSON'],
                                        filename=Flags['filename'],
                                        re_bool = False if Flags['mode'] is any else True)
    except Exception as e:
        debug(f"An error was raised whilst querying for the flag; more information: {e.__class__.__name__}; {e}; {traceback.format_exc()}")
        output = None if Flags['mode'] is any else False

    debug(f"Query result for ID {flagID} in {Flags['filename']}: {output}")

    return output

def json_removeFlag(flagID: str, **flags) -> None:
    # Defaults
    JSONHandlerInstance = QAJSONHandler.QAFlags()
    def_fn = f"{QAInfo.appdataLoc}\\{JSONHandlerInstance.flags_fn}"

    # Flags
    Flags = {
        'filename': [def_fn, (def_fn, str)],
        'reloadJSON': [True, (True, bool)]
    }; Flags = flags_handler(Flags, flags, __rePlain=True)

    # Vars
    Key = JSONHandlerInstance.REMOVE

    # Pop
    debug(f"Removing data for ID {flagID} in file {Flags['filename']}")

    JSONHandlerInstance.io(Key=Key,
                           key=flagID,
                           reloadJSON=Flags['reloadJSON'],
                           filename=Flags['filename'])

def openFile(path): os.startfile(os.path.realpath(path))

def flags_handler(ref: dict, flags: dict, __raiseErr: bool = True, __rePlain: bool = False) -> dict:
    """
    **BASIC INFORMATION ONLY**

    :param ref: Reference dictionary
    :param flags: Flags given
    :param __raiseErr: Raise error (def True)
    :param __rePlain: Return plain data (only index 0 from Expected Syntax) (def False)
    :return: Adjusted dictionary

    Expected syntax:
    {
        'flag name' : List[<set>, Tuple(<default value>, *<types>)]
    }
    """
    output = ref

    for i in flags:

        if i in ref: # If flag is valid

            if type(flags[i] in ref[i][1][1::]): # If type is valid
                output[i] = [flags[i], ref[i][1]] # Reset
                debug(f"Set flag '{i}' to {output[i]}")

            elif __raiseErr: # Raise Error
                debug(f"Invalid type for flag '{i}' (expected {ref[i][1][1::]}, got {type(flags[i])}); raising error for __raiseErr is set to True")
                raise TypeError(f"Invalid type for flag '{i}' (expected {ref[i][1][1::]}, got {type(flags[i])})")

            else: # Pass
                debug(
                    f"Invalid type for flag '{i}' (expected {ref[i][1][1::]}, got {type(flags[i])}); suppressing error for __raiseErr is set to False")
                pass

        elif __raiseErr: # Raise Error
            debug(
                f"Invalid flag '{i}'; raising error for __raiseErr is set to True")
            raise TypeError(f"Invalid flag '{i}'")

        else: # Pass
            debug(
                f"Invalid flag '{i}'; suppressing error for __raiseErr is set to False")
            pass

    if __rePlain:
        debug(f"Clearing excessive information from output dictionary.")
        for i in output: output[i] = output[i][0]

    debug(f"Outputting the following flags dictionary: {output}")
    return output

def confirm() -> bool:
    return tkmsb.askyesno(apptitle, f"Do you want to continue with the requested routine?")

def setBootError(time, info, function=None) -> None:
    QAJSONHandlerData = QAJSONHandler.QAFlags()
    if function is None: function = QAJSONHandlerData.FTSRA_fileCheck

    CH = CrashHandler()
    CH.log_crash(
        time=time,
        info=info,
        function=function
    )

# IO Functions (Class)

class IO:

    def __init__(self):
        self.files = QAInfo.QaFTSRAFiles
        self.folder = QAInfo.ftsFolder
        self.appdata = QAInfo.appdataLoc

    def owr_files(self, **flags):
        global apptitle

        debug(f"Running IO.owr_files")

        # Flags
        Flags = {
            'preConf': [False, (False, bool)]
        }

        Flags = flags_handler(Flags, flags, __rePlain=True)

        # Confirmation
        if not Flags['preConf']:
            if not confirm():
                debug(f"User cancelled routine")
                return
            debug(f"User wished to continue with routine")

        # Ask if the user wants to copy the old data...
        copy_old = tkmsb.askyesno(apptitle,
                                  f"Would you like to copy your old data to an external location prior to resetting it?")

        logvar = QaLog.Variables()

        if copy_old:
            # Get save as location
            new_location = tkfile.askdirectory()
            g = True
            if new_location is None: g = False
            else:
                new_location.replace("/", "\\")

            try:
                if os.path.exists(new_location) and g:
                    new_location += "\\QA FTSRA Export {}".format(QATime.forLog())

                    os.mkdir(new_location) # Make the folder
                    # Copy everything except logs
                    for i in os.listdir(self.appdata):
                        if not i.lower().strip() == logvar.folderName().split("\\")[-1].lower().strip():
                            i_path = f"{self.appdata}\\{i}"
                            nl_i_path = f"{new_location}\\{i}"

                            if os.path.isdir(i_path): # dir
                                debug(f"Copying {i_path} to {nl_i_path} using DIR method")
                                shutil.copytree(i_path, nl_i_path)

                            elif os.path.isfile(i_path): # file
                                debug(f"Copying {i_path} to {nl_i_path} using FILE method")
                                shutil.copy(i_path, nl_i_path)

                            else: # no conditions met; error
                                debug(
                                    f"No delete condition met, raising {IOError}: No delete condition met for entry {self.appdata}\\{i}; setting boot error flag.")
                                setBootError(QATime.now(), f"No delete condition met for entry {self.appdata}\\{i}")
                                raise IOError(f"No delete condition met for entry {self.appdata}\\{i}") # Will not terminate but will end the file copying routine

                    if tkmsb.askyesno(apptitle, f"Copied old data to {new_location}; open folder?"):
                        openFile(new_location)

            except Exception as e:
                if g:
                    tkmsb.showerror(apptitle, f"Failed to export files; continuing.")
                    debug(f"Failed to export files; info: {e.__class__.__name__}; {e}; {traceback.format_exc()}")
                else: pass


        # Reset
        # Delete
        debug(f"Deleting files")

        for i in os.listdir(self.appdata):

            if os.path.exists(f"{self.appdata}\\{i}"): # Only if it already exists

                if i.lower() == logvar.folderName().lower().split("\\")[-1]: # If it's the logs folder
                    debug(f"Passing logs folder")
                    pass

                elif os.path.isdir(f"{self.appdata}\\{i}"): # If it is a directory
                    debug(f"Deleting directory {self.appdata}\\{i}")
                    os.rmdir(f"{self.appdata}\\{i}")

                elif os.path.isfile(f"{self.appdata}\\{i}"): # If it's a file
                    debug(f"Deleting file {self.appdata}\\{i}")
                    os.remove(f"{self.appdata}\\{i}")

                else: # No conditions met (error)
                    debug(f"No delete condition met, raising {IOError}: No delete condition met for entry {self.appdata}\\{i}; setting boot error flag.")
                    setBootError(QATime.now(), f"No delete condition met for entry {self.appdata}\\{i}")
                    raise IOError(f"No delete condition met for entry {self.appdata}\\{i}")

        # Copy
        for i in self.files:
            fpath = f"{self.folder}\\{i}"; apath = f"{self.appdata}\\{i}"

            if not os.path.exists(fpath):
                debug(f"FTSRA file '{fpath}' does not exist; raising error.")
                tkmsb.showerror(apptitle, f"Critical error: file '{fpath}' required for this routine does not exist; a complete reinstall may be required if the error persists.")
                setBootError(QATime.now(),
                             f"Critical error: file '{fpath}' required for this routine does not exist; a complete reinstall may be required if the error persists.")
                raise IOError(f"Critical error: file '{fpath}' required for this routine does not exist; a complete reinstall may be required if the error persists.")

            if os.path.isdir(fpath): # If the file is a directory
                debug(f"Copying directory {fpath} to {apath}")
                shutil.copytree(fpath, apath)

            elif os.path.isfile(fpath): # If the file is a file
                debug(f"Copying file {fpath} to {apath}")
                shutil.copy(fpath, apath)

            else: # No conditions met (error)
                debug(f"{IOError(f'No copy condition met for file {fpath} -> {apath}')}; setting boot error flag")
                setBootError(QATime.now(), f"No copy condition met for file {fpath} -> {apath}")
                raise IOError(f"No copy condition met for file {fpath} -> {apath}")

        tkmsb.showinfo(apptitle, f'Successfully removed and replaced all files.')

    def copy_files(self, **flags):
        global apptitle

        Flags = {

        }

        Flags = flags_handler(Flags, flags, __rePlain=True)

        counter = 0
        for i in self.files:
            fpath = f"{self.folder}\\{i}"; apath = f"{self.appdata}\\{i}"

            if not os.path.exists(fpath):
                debug(f"FTSRA file '{fpath}' does not exist; raising error.")
                tkmsb.showerror(apptitle,
                    f"Critical error: file '{fpath}' required for this routine does not exist; a complete reinstall may be required if the error persists.")
                setBootError(QATime.now(),
                             f"Critical error: file '{fpath}' required for this routine does not exist; a complete reinstall may be required if the error persists.")
                raise IOError(
                    f"Critical error: file '{fpath}' required for this routine does not exist; a complete reinstall may be required if the error persists.")

            if not os.path.exists(apath): # If it doesn't exist already

                counter += 1

                if os.path.isdir(fpath): # Directory
                    debug(f"Copying directory {fpath} to {apath}")
                    shutil.copytree(fpath, apath)

                elif os.path.isfile(fpath): # File
                    debug(f"Copying file {fpath} to {apath}")
                    shutil.copy(fpath, apath)

                else: # Other (unsupported; error)
                    debug(f"{IOError(f'No copy condition met for file {fpath} -> {apath}')}; setting boot error flag")
                    setBootError(QATime.now(), f"No copy condition met for file {self.appdata}\\{i}")
                    raise IOError(f"No copy condition met for file {fpath} -> {apath}")

            else: debug(f"File {apath} already exists; skipping")

        tkmsb.showinfo(apptitle, f"Successfully found and fixed {counter} missing files.")

    def owr_config(self, **flags):
        global apptitle

        # Flags
        Flags = {
            'preConf': [False, (False, bool)]
        }

        Flags = flags_handler(Flags, flags, __rePlain=True)

        # Confirmation
        if not Flags['preConf']:
            if not confirm():
                debug(f"User wishes to not continue; aborting")
                return
            debug(f"User wishes to continue")

        # Logic
        fname = f"{self.folder}\\{QAInfo.confFilename}"; aname = f"{self.appdata}\\{QAInfo.confFilename}"
        if not os.path.exists(fname): # If the base doesn't exist
            debug(f"FTSRA file '{fname}' does not exist; raising error.")
            tkmsb.showerror(apptitle,
                f"Critical error: file '{fname}' required for this routine does not exist; a complete reinstall may be required if the error persists.")
            setBootError(QATime.now(), f"Critical error: file '{fname}' required for this routine does not exist; a complete reinstall may be required if the error persists.")
            raise IOError(
                f"Critical error: file '{fname}' required for this routine does not exist; a complete reinstall may be required if the error persists.")

        if os.path.exists(aname):
            debug(f"{aname} exists; deleting said file.")
            os.remove(aname)

        debug(f"Copying new file")
        shutil.copy(fname, aname)
        debug(f"Successfully copied file") # Would not get here if an error was raised.

        tkmsb.showinfo(apptitle,
                       f"Successfully reset configuration file; you may now use it.")

# Boot check
ch = CrashHandler()
if not ch.boot_check():
    # Logic
    # Should exit if failed
    tkmsb.showwarning(apptitle, f"The application will close now; please restart the application manually.")
    debug(f"The application will close now; please restart the application manually.")
    Exit('boot_check_fail;;ran_scritps')

# Boot check passed
ui = UI() # Call the UI
