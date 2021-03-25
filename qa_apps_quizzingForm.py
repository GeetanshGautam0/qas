import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as tkfld
from tkinter import messagebox as tkmsb
import os, sys, threading, shutil, time, json, sqlite3

import qa_appinfo as QAInfo
import qa_diagnostics as QADiagnostics
import qa_splash as QASplash
import qa_typeConvertor as QAConvertor
import qa_logging as QALogging
import qa_fileIOHandler as QAFileIO
import qa_onlineVersCheck as QA_OVC
import qa_win10toast as Win10Toast
import qa_time as QATime
import qa_globalFlags as QAJSONHandler
import qa_errors as QAErrors
import qa_questions as QAQuestionStandard
import qa_theme as QATheme

boot_steps = {
    1: 'Loading Variables',
    2: 'Loading Classes',
    3: 'Loading Functions',
    4: 'Running Boot Checks',
    5: 'Fetching Version Information (Online)'
}; boot_steps_amnt = len(boot_steps)

if not QAInfo.doNotUseSplash:
    splRoot = tk.Toplevel()
    splObj = QASplash.Splash(splRoot)

    splObj.setImg(QAInfo.icons_png.get('qt'))
    splObj.setTitle("Quizzing Form")


def set_boot_progress(ind, resolution=100):
    if QAInfo.doNotUseSplash: return

    global boot_steps;
    global boot_steps_amnt;
    global splObj

    splObj.setInfo(boot_steps[ind])

    ind -= 1  # 0 >> Max
    prev = ind - 1 if ind > 0 else ind

    for i in range(prev * resolution, ind * resolution):
        for j in range(20): pass  # < 0.01 sec delay

        splObj.changePbar(
            (i / boot_steps_amnt) / (resolution / 100)
        )


def show_splash_completion(resolution=100):
    if QAInfo.doNotUseSplash: return

    global boot_steps_amnt;
    global splObj

    ind = boot_steps_amnt - 1

    splObj.completeColor()
    splObj.setInfo(f"Completed Boot Process")

    for i in range(ind * resolution, boot_steps_amnt * resolution):
        for j in range(20): pass  # < 0.01 sec delay

        splObj.changePbar(
            (i / boot_steps_amnt) / (resolution / 100)
        )

    time.sleep(0.5)


# Adjust Splash
set_boot_progress(1)

# Globals
apptitle = f"Quizzing Form v{QAInfo.versionData[QAInfo.VFKeys['v']]}"
QAS_encoding = 'utf-8'
self_icon = QAInfo.icons_ico.get('qt')
defs_configruationFilename = '{}\\{}'.format(QAInfo.appdataLoc.strip('\\').strip(), QAInfo.confFilename)

# Adjust Splash
set_boot_progress(2)

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

def dc_lst(Dict: dict, index) -> dict:
    out: dict = {}
    for i in Dict:
        out[i] = (Dict[i][index])

    return out

class LoginUI(threading.Thread):

    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)

        self.root = tk.Toplevel()
        self.root.withdraw()

        # Theme
        self.theme = QATheme.Get().get('theme')

        # Other variables (theme)
        self.lblFrame_font = (self.theme.get('font'), 11)
        self.dsb_fg = '#595959'

        # Geometry
        self.txy = {'x': 0, 'y': 1}  # Coordinate template
        self.ss = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())  # Screen size
        self.ds_ratio = (
            1000 / 1920,  # Width
            900 / 1080  # Height
        )
        self.ds = (int(self.ds_ratio[0] * self.ss[0]),
                   int(self.ds_ratio[1] * self.ss[1]))  # Default size
        self.ws = [
            self.ds[self.txy['x']] if self.ds[self.txy['x']] < self.ss[self.txy['x']] else int(
                self.ss[self.txy['x']] * self.ds_ratio[0]),
            self.ds[self.txy['y']] if self.ds[self.txy['y']] < self.ss[self.txy['y']] else int(
                self.ss[self.txy['y']] * self.ds_ratio[1])
        ]  # Window size (adjustable)
        self.sp = (int(self.ss[self.txy['x']] / 2 - self.ws[self.txy['x']] / 2),
                   int(self.ss[self.txy['y']] / 2 - self.ws[self.txy['y']] / 2))  # Position on screen

        self.gem = "{}x{}+{}+{}".format(self.ws[0], self.ws[1], self.sp[0], self.sp[1])

        # Padding x and y
        self.padX = 10
        self.padY = 5

        # Frames
        self.dbSelctFrame = tk.Frame(self.root)
        self.credFrame = tk.Frame(self.root)
        self.configFrame = tk.Frame(self.root)
        self.finalFrame = tk.Frame(self.root)

        # Screen Indexing System
        self.screen_index = 0
        self.scI_mapping = {
            0: ["Database Selection", self.dbSelctFrame, self.screen_1],
            1: ["Credentials", self.credFrame, self.screen_2],
            2: ["Configuration", self.configFrame, self.screen_3],
            3: ["Preparing Quiz", self.finalFrame, self.screen_4]
        }

        self.sc_navButton_next_states = {
            0: True,
            1: True,
            2: True,
            3: True
        }; self.screen_data = {
            0: {
                'defaults': {
                    'i': 'Internal Database',
                    'e': 'External Database'
                },
                'flags': {
                    'selected': False
                },
                'strs': {
                    'errors': {
                        'selectDB': 'ERROR: Please select a database',
                        'notValid': 'ERROR: Invalid DB file selected',
                        'unknown': 'ERROR: Unknown error (logged)',
                        'invalidDB': 'ERROR: Invalid Database (logged; ID=0)',
                        'invalidDB_noQs': 'ERROR: Invalid Database - no questions found (logged; ID=1)'
                    }
                }
            },
            1: {
                'strs': {
                    'errors': {
                        'addInformation': 'ERROR: Please enter the requested information'
                    }
                }
            },
            2: {
                'poa_btn_state': {
                    ''
                },
                'defaults': {
                    'strs': {
                        'POA_part': "Selected: Part of all Questions",
                        'POA_all': "Selected: All Questions",
                        "QDF_enb": "Enabled Point Deductions",
                        "QDF_dsb": "No Deductions",
                        "acqc_disabled": "The administrator has disabled custom quiz configuration."
                    },
                    'information_strs': {
                        'POA': "Description:\nShould all questions be included in the quiz, or only a part of the questions; click on the button below to toggle the option. If you choose to only answer a part of the questions, enter the divisor amount (1/n questions will be used, where n is the number you provide)",
                        'QDF': "Description:\nShould the application deduct points when an incorrect response is given; click on the button below to toggle to option - enter the amount of points that you wish to be deducted for every incorrect option in the field below."
                    }
                }
            },
            3: {
                'start_requested': {

                }
            },
            'nav': {
                'next': {
                    'defaults': {
                        'str_next': "Next \u2b9e",
                        'str_start': "Start Quiz \u2713"
                    }
                },
                'prev': {
                    'defaults': {
                        'str_prev': '\u2b9c Back'
                    }
                }
            }
        }

        # Frame Elements
        # Root Elements *excluding frames
        self.previous_button = tk.Button(self.root)
        self.next_button = tk.Button(self.root)

        self.creditLbl = tk.Label(self.root)

        #   - Frame 1: Database selection
        self.dbSel_ttl = tk.Label(self.dbSelctFrame)
        self.dbSel_info = tk.Label(self.dbSelctFrame)
        self.dbSel_btnContainer = tk.LabelFrame(self.dbSelctFrame)
        self.dbSel_btns_external = tk.Button(self.dbSel_btnContainer)
        self.dbSel_btns_internal = tk.Button(self.dbSel_btnContainer)
        self.dbSel_error_lbl = tk.Label(self.dbSelctFrame)

        #   - Frame 2: Credentials
        self.cred_ttl = tk.Label(self.credFrame)
        self.cred_info = tk.Label(self.credFrame)
        self.cred_container = tk.LabelFrame(self.credFrame)
        self.cred_name_cont = tk.LabelFrame(self.cred_container)
        self.cred_first_invis_cont = tk.LabelFrame(self.cred_name_cont)
        self.cred_first = tk.Entry(self.cred_first_invis_cont)
        self.cred_first_lbl = tk.Label(self.cred_first_invis_cont)
        self.cred_last_invis_cont = tk.LabelFrame(self.cred_name_cont)
        self.cred_last = tk.Entry(self.cred_last_invis_cont)
        self.cred_last_lbl = tk.Label(self.cred_last_invis_cont)
        self.cred_studentID_invis_cont = tk.LabelFrame(self.cred_container)
        self.cred_studentID_lbl = tk.Label(self.cred_studentID_invis_cont)
        self.cred_studentID_field = tk.Entry(self.cred_studentID_invis_cont)
        self.cred_error_lbl = tk.Label(self.credFrame)

        #    - Frame 3: Configuration
        self.config_ttl = tk.Label(self.configFrame)
        self.config_info = tk.Label(self.configFrame)
        self.config_disallowed_LBL = tk.Label(self.configFrame)
        self.config_container1 = tk.LabelFrame(self.configFrame)
        self.config_container2 = tk.LabelFrame(self.configFrame)
        self.config_poa_button = tk.Button(self.config_container1)
        self.config_poa_descLbl = tk.Label(self.config_container1)
        self.config_poa_df_field = tk.Entry(self.config_container1)
        self.config_qdf_button = tk.Button(self.config_container2)
        self.config_qdf_descLbl = tk.Label(self.config_container2)
        self.config_qdf_field = tk.Entry(self.config_container2)
        self.config_error_label = tk.Label(self.configFrame)
        self.config_poaField_descLbl = tk.Label(self.config_container1)
        self.config_qdfField_descLbl = tk.Label(self.config_container2)

        # UI Update System
        self.update_element = {
            'lbl': [],
            'btn': [],
            'acc_fg': [],
            'acc_bg': [],
            'font': [],
            'frame': [],
            'error_lbls': [],
            'enteries': []
        }

        self.configuration = {}
        self.questions = {}
        self.canClose = True

        # Final calls
        self.start()
        self.root.mainloop()

    def close(self):
        if not self.canClose:
            tkmsb.showerror(apptitle, "The quiz is now in progress; you cannot exit\n\nPress ok to return to quiz.")
            return

        conf = tkmsb.askyesno(apptitle, "Are you sure you want to exit?")
        if conf: sys.exit(0)

    def run(self):
        global apptitle, self_icon

        self.root.title(apptitle)
        self.root.geometry(self.gem)
        self.root.iconbitmap(self_icon)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.update_element['lbl'].extend([
            self.dbSel_ttl,
            self.dbSel_btnContainer,
            self.dbSel_info,
            self.dbSel_error_lbl,

            self.cred_ttl,
            self.cred_info,
            self.cred_container,
            self.cred_name_cont,
            self.cred_first_lbl,
            self.cred_last_lbl,
            self.cred_studentID_lbl,
            self.cred_error_lbl,

            self.config_ttl,
            self.config_info,
            self.config_disallowed_LBL,
            self.config_container1,
            self.config_container2,
            self.config_qdf_descLbl,
            self.config_poa_descLbl,
            self.config_qdfField_descLbl,
            self.config_poaField_descLbl
        ])

        self.update_element['btn'].extend([
            self.dbSel_btns_external,
            self.dbSel_btns_internal,

            self.config_poa_button,
            self.config_qdf_button
        ])

        self.update_element['acc_fg'].extend([
            self.dbSel_btnContainer,
            self.dbSel_ttl,

            self.cred_ttl,
            self.cred_container,
            self.cred_name_cont,

            self.config_ttl,
            self.config_disallowed_LBL,
            self.config_container1,
            self.config_container2,
            self.config_qdf_button,
            self.config_poa_button,
            self.config_error_label
        ])

        self.update_element['acc_bg'].extend([
            self.root
        ])

        self.update_element['font'].extend([
            [self.next_button, (self.theme.get('font'), 12)],
            [self.previous_button, (self.theme.get('font'), 12)],
            [self.creditLbl, (self.theme.get('font'), 8)],

            [self.dbSel_ttl, (self.theme.get('font'), 32)],
            [self.dbSel_info, (self.theme.get('font'), 12)],
            [self.dbSel_btnContainer, (self.theme.get('font'), 10)],
            [self.dbSel_btns_external, (self.theme.get('font'), 14)],
            [self.dbSel_btns_internal, (self.theme.get('font'), 14)],
            [self.dbSel_error_lbl, (self.theme.get('font'), 11)],

            [self.cred_ttl, (self.theme.get('font'), 32)],
            [self.cred_info, (self.theme.get('font'), 12)],
            [self.cred_container, (self.theme.get('font'), 10)],
            [self.cred_name_cont, (self.theme.get('font'), 10)],
            [self.cred_first, (self.theme.get('font'), 13)],
            [self.cred_last, (self.theme.get('font'), 13)],
            [self.cred_first_lbl, (self.theme.get('font'), 13)],
            [self.cred_last_lbl, (self.theme.get('font'), 13)],
            [self.cred_studentID_field, (self.theme.get('font'), 13)],
            [self.cred_studentID_lbl, (self.theme.get('font'), 13)],
            [self.cred_error_lbl, (self.theme.get('font'), 11)],

            [self.config_ttl, (self.theme.get('font'), 32)],
            [self.config_info, (self.theme.get('font'), 12)],
            [self.config_disallowed_LBL, (self.theme.get('font'), 14)],
            [self.config_container1, (self.theme.get('font'), 10)],
            [self.config_container2, (self.theme.get('font'), 10)],
            [self.config_poa_button, (self.theme.get('font'), 14)],
            [self.config_poa_descLbl, (self.theme.get('font'), 13)],
            [self.config_poa_df_field, (self.theme.get('font'), 13)],
            [self.config_qdf_button, (self.theme.get('font'), 14)],
            [self.config_qdf_descLbl, (self.theme.get('font'), 13)],
            [self.config_qdf_field, (self.theme.get('font'), 13)],
            [self.config_error_label, (self.theme.get('font'), 11)],
            [self.config_qdfField_descLbl, (self.theme.get('font'), 13)],
            [self.config_poaField_descLbl, (self.theme.get('font'), 13)]
        ])

        self.update_element['frame'].extend([
            self.configFrame,
            self.dbSelctFrame,
            self.credFrame,
            self.finalFrame
        ])

        self.update_element['error_lbls'].extend([
            self.dbSel_error_lbl,
            self.cred_error_lbl,

            self.config_error_label
        ])

        self.update_element['enteries'].extend([
            self.cred_first,
            self.cred_last,
            self.cred_studentID_field,

            self.config_qdf_field,
            self.config_poa_df_field
        ])

        self.next_button.config(
            text=self.screen_data['nav']['next']['defaults']['str_next'],
            command=self.next_page,
            anchor=tk.E
        )

        self.previous_button.config(
            text=self.screen_data['nav']['prev']['defaults']['str_prev'],
            command=self.prev_page,
            anchor=tk.W
        )

        self.creditLbl.config(
            text="Coding Made Fun, {}".format(QATime.form('%Y')),
            anchor=tk.E,
            justify=tk.RIGHT
        )

        self.update_ui(0, True)
        self.root.deiconify()

    def update_ui(self, screenI_counter=0, force_refresh=False):
        # Config.
        self.screen_index += screenI_counter
        if self.screen_index < 0: self.screen_index = 0
        elif self.screen_index >= len(self.scI_mapping): self.screen_index = len(self.scI_mapping) - 1

        self.title()

        debug("Screen re-draw params: i. scic = ", screenI_counter, "; ii. f_r = ", force_refresh)

        if screenI_counter != 0 or force_refresh:
            self.clear_screen()

            self.scI_mapping.get(self.screen_index)[-1]() # Call the screen setup function

            # if self.screen_index > 0: self.previous_button.pack(fill=tk.X, expand=True, side=tk.LEFT)
            # if self.screen_index < len(self.scI_mapping) - 1: self.next_button.pack(fill=tk.X, expand=True, side=tk.RIGHT)

            self.creditLbl.pack(fill=tk.X, expand=False, side=tk.BOTTOM)

            self.previous_button.pack(fill=tk.X, expand=True, side=tk.LEFT)
            self.next_button.pack(fill=tk.X, expand=True, side=tk.RIGHT)
            self.config_nav_buttons()

        # Theme
        self.root.config(bg=self.theme.get('bg'))

        for i in self.scI_mapping:
            self.scI_mapping[i][1].config(bg=self.theme.get('bg'))

        for i in self.update_element['lbl']:
            try:
                i.config(
                    bg=self.theme.get('bg'),
                    fg=self.theme.get('fg')
                )
            except Exception as e:
                debug(f"An exception occurred whilst theming lbl {i}: {e}")

        for i in self.update_element['btn']:
            try:
                i.config(
                    bg=self.theme.get('bg'),
                    fg=self.theme.get('fg'),
                    activebackground=self.theme.get('ac'),
                    activeforeground=self.theme.get('hg'),
                    bd='0'
                )
            except Exception as e:
                debug(f"An exception occurred whilst theming btn {i}: {e}")

        for i in self.update_element['acc_fg']:
            try:
                i.config(
                    fg=self.theme.get('ac')
                )
            except Exception as e:
                debug(f"An exception occurred whilst applying the accent color as fg to {i}: {e}")

        for i in self.update_element['acc_bg']:
            try:
                i.config(
                    bg=self.theme.get('ac')
                )
            except Exception as e:
                debug(f"An exception occurred whilst applying the accent color as bg to {i}: {e}")

        for i in self.update_element['font']:
            try:
                i[0].config(
                    font=i[1]
                )
            except Exception as e:
                debug(f"An exception occurred whilst applying font {i[1]} to {i[0]}: {e}")

        for i in self.update_element['frame']:
            try:
                i.config(
                    bg=self.theme.get('bg')
                )
            except Exception as e:
                debug(f"An exception occurred whilst theming frame {i}: {e}")

        for i in self.update_element['error_lbls']:
            i.config(
                fg=self.theme.get('ac'),
                bg=self.theme.get('bg'),
                text=""
            )

        for i in self.update_element['enteries']:
            i.config(
                fg=self.theme['fg'],
                bg=self.theme['bg'],
                selectforeground=self.theme['hg'],
                selectbackground=self.theme['ac'],
                insertbackground=self.theme['ac']
            )

        # Exceptions

        for i in [self.next_button, self.previous_button]:
            i.config(
                bg=self.theme.get('ac'),
                fg=self.theme.get('hg'),
                activebackground=self.theme.get('hg'),
                activeforeground=self.theme.get('ac'),
                bd='0'
            )

        self.creditLbl.config(
            bg=self.theme.get('ac'),
            fg=self.theme.get('hg')
        )

        for i in [self.dbSel_btns_external, self.dbSel_btns_internal]:
            i.config(
                disabledforeground=self.theme.get('hg')
            )

        for i in [self.cred_last_invis_cont, self.cred_first_invis_cont, self.cred_studentID_invis_cont]:
            i.config(bd='0', bg=self.theme.get('bg'))

        if screenI_counter != 0 or force_refresh:
            self.update_ui_elements()

        # --- end ---

    def update_ui_elements(self):
        if self.screen_data[0]['flags']['selected']:

            debug("screen_data[0].get('database_selection'): ", self.screen_data[0].get('database_selection'))

            if self.screen_data[0].get('database_selection') == 'i':
                self.dbSel_btns_external.config(state=tk.NORMAL, bg=self.theme.get('bg'))
                self.dbSel_btns_internal.config(
                    state=tk.DISABLED, bg=self.theme.get('ac'),
                    text=self.screen_data[0]['defaults']['i'] + ' \u2713'
                )

            elif self.screen_data[0].get('database_selection') == 'e':
                self.dbSel_btns_internal.config(state=tk.NORMAL, bg=self.theme.get('bg'))
                self.dbSel_btns_external.config(
                    state=tk.DISABLED, bg=self.theme.get('ac'),
                    text=self.screen_data[0]['defaults']['e'] + ' \u2713\n' +
                         self.screen_data[0]['external_database']['filename'].split('\\')[-1]
                )

    def all_screen_widgets(self) -> list:
        _db = self.dbSelctFrame.winfo_children()
        _cred = self.credFrame.winfo_children()
        _conf = self.configFrame.winfo_children()
        _fin = self.finalFrame.winfo_children()
        __all = self.root.winfo_children()

        for item in _db:
            if item.winfo_children(): _db.extend(item.winfo_children())

        for item in _cred:
            if item.winfo_children(): _cred.extend(item.winfo_children())

        for item in _conf:
            if item.winfo_children(): _conf.extend(item.winfo_children())

        for item in _fin:
            if item.winfo_children(): _fin.extend(item.winfo_children())

        for item in __all:
            if item.winfo_children(): __all.extend(item.winfo_children())

        return [__all, _db, _cred, _conf, _fin]

    def clear_screen(self):
        widgets = self.all_screen_widgets()[0]

        for i in widgets:
            try: i.pack_forget()
            except Exception as e: debug(f'exception whilst clearing screen: {e}')

    def title(self):
        global apptitle
        self.root.title(f"{apptitle} - {self.scI_mapping.get(self.screen_index)[0]}")

    def screen_1(self): # DB Selection
        debug(f"Setting up DB Select Page (ind = {self.screen_index})")

        self.dbSelctFrame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.dbSel_ttl.config(text="Quizzing Form", anchor=tk.W)
        self.dbSel_ttl.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY, self.padY/4))

        self.dbSel_info.config(
            text="Step 1/{}: Question Database Selection;\nSelect a database from an external file, or the internal database by selecting the appropriate buttons below.".format(
                len(self.scI_mapping)
            ),
            anchor=tk.W,
            justify=tk.LEFT,
            wraplength=int(self.ws[0] - self.padX*2)
        )
        self.dbSel_info.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY/4, self.padY))

        self.dbSel_btnContainer.config(text="Options")
        self.dbSel_btnContainer.pack(
            fill=tk.BOTH,
            expand=True,
            padx=self.padX,
            pady=self.padY*3
        )

        self.dbSel_btns_internal.config(text=self.screen_data[0]['defaults']['i'], command=self.btns_dbSel_int)
        self.dbSel_btns_internal.pack(fill=tk.BOTH, expand=True, padx=(self.padX / 2, self.padX), pady=self.padY,
                                      side=tk.LEFT)

        self.dbSel_btns_external.config(text=self.screen_data[0]['defaults']['e'], command=self.btns_dbSel_ext)
        self.dbSel_btns_external.pack(fill=tk.BOTH, expand=True, padx=(self.padX, self.padX/2), pady=self.padY, side=tk.LEFT)

        self.dbSel_error_lbl.config(
            wraplength=(self.ws[0] - self.padX * 2)
        )
        self.dbSel_error_lbl.pack(
            fill=tk.X,
            expand=False,
            side=tk.BOTTOM
        )

    def screen_2(self): # Credentials
        debug(f"Setting up Credentials Page (ind = {self.screen_index})")

        self.credFrame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.cred_ttl.config(text="Quizzing Form", anchor=tk.W, justify=tk.LEFT)
        self.cred_ttl.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY, self.padY/4))

        self.cred_info.config(
            text="Step 2/{}: Credentials;\nEnter the information requested in the form below.".format(
                len(self.scI_mapping)
            ),
            anchor=tk.W,
            justify=tk.LEFT,
            wraplength=int(self.ws[0] - self.padX * 2)
        )
        self.cred_info.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY / 4, self.padY))

        self.cred_container.config(text="Information Required")
        self.cred_container.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY)

        self.cred_name_cont.config(text="Full Name")
        self.cred_name_cont.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=(self.padY, self.padY / 2))

        self.cred_first_invis_cont.pack(fill=tk.BOTH, expand=False, pady=(self.padY, self.padY / 2))
        self.cred_last_invis_cont.pack(fill=tk.BOTH, expand=False, pady=(self.padY / 2, self.padY))

        self.cred_first_lbl.config(text="First Name")
        self.cred_first_lbl.pack(fill=tk.X, expand=False, side=tk.LEFT, padx=(self.padX, 0))

        self.cred_first.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, self.padX))

        self.cred_last_lbl.config(text="Last Name")
        self.cred_last_lbl.pack(fill=tk.X, expand=False, side=tk.LEFT, padx=(self.padX, 0))

        self.cred_last.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, self.padX))

        self.cred_studentID_invis_cont.pack(fill=tk.BOTH, expand=False, pady=(self.padY / 2, self.padY))

        self.cred_studentID_lbl.config(text="Student ID")
        self.cred_studentID_lbl.pack(fill=tk.X, expand=False, side=tk.LEFT, padx=(self.padX, 0))

        self.cred_studentID_field.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, self.padX))

        self.cred_error_lbl.config(
            wraplength=(self.ws[0] - self.padX * 2)
        )
        self.cred_error_lbl.pack(
            fill=tk.X,
            expand=False,
            side=tk.BOTTOM
        )
        
    def screen_3(self): # Configuration
        debug(f"Setting up Configuration Page (ind = {self.screen_index})")

        self.configFrame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.config_ttl.config(text="Quizzing Form", anchor=tk.W, justify=tk.LEFT)
        self.config_ttl.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY, self.padY / 4))

        self.config_info.config(
            text="Step 3/{}: Configuration;\nConfigure the quiz you're about to take (if allowed by the administrator)".format(
                len(self.scI_mapping)
            ),
            anchor=tk.W,
            justify=tk.LEFT,
            wraplength=int(self.ws[0] - self.padX * 2)
        )
        self.config_info.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY / 4, self.padY))

        if not self.configuration['customQuizConfig']:
            self.config_disallowed_LBL.config(
                text=self.screen_data[2]['defaults']['strs']['acqc_disabled'],
                wraplength=int(self.ws[0]-self.padX*2)
            )
            self.config_disallowed_LBL.pack(fill=tk.BOTH, expand=True, padx=self.padX, pady=self.padY)

        else:

            self.config_container1.config(
                text="Question Selection"
            )
            self.config_container1.pack(
                fill=tk.BOTH, expand=False, padx=self.padX, pady=(self.padY, self.padY/4)
            )

            self.config_poa_descLbl.config(
                text=self.screen_data[2]['defaults']['information_strs']['POA'],
                wraplength=int(self.ws[0] - self.padX * 2),
                justify=tk.LEFT,
                anchor=tk.W
            )
            self.config_poa_descLbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY)

            self.config_poa_button.config(
                text=self.screen_data[2]['defaults']['strs']['POA_part' if self.configuration.get('partOrAll') == 'part' else 'POA_all'],
                command=self.config_poa
            )

            self.config_poa_button.pack(
                fill=tk.BOTH,
                expand=False,
                padx=self.padX,
                pady=self.padY,
                ipadx=self.padX / 4,
                ipady=self.padY / 4,
                side=tk.LEFT
            )

            if self.configuration.get('partOrAll') == 'part':

                self.config_poa_df_field.delete(0, tk.END)
                self.config_poa_df_field.insert(0, str(self.configuration['poa_divF']))

                self.config_poa_df_field.pack(
                    fill=tk.X, expand=True,
                    padx=(self.padX, self.padX / 4), pady=self.padY,
                    side=tk.RIGHT
                )

                self.config_poaField_descLbl.config(
                    text="Divisor: ",
                    wraplength=int(self.ws[0] - self.padX * 2),
                    justify=tk.RIGHT,
                    anchor=tk.E
                )

                self.config_poaField_descLbl.pack(
                    fill=tk.X, expand=False,
                    padx=(self.padX, self.padX/4), pady=self.padY,
                    side=tk.RIGHT
                )

            self.config_container2.config(
                text="Incorrect Response Penalty"
            )
            self.config_container2.pack(
                fill=tk.BOTH, expand=False, padx=self.padX, pady=(self.padY, self.padY / 4)
            )

            self.config_qdf_descLbl.config(
                text=self.screen_data[2]['defaults']['information_strs']['QDF'],
                wraplength=int(self.ws[0] - self.padX * 2),
                justify=tk.LEFT,
                anchor=tk.W
            )

            self.config_qdf_descLbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY)

            self.config_qdf_button.config(
                text=self.screen_data[2]['defaults']['strs']['QDF_enb' if bool(self.configuration.get('a_deduc')) else 'QDF_dsb'],
                command=self.config_qdf
            )

            self.config_qdf_button.pack(
                fill=tk.BOTH,
                expand=False,
                padx=self.padX,
                pady=self.padY,
                ipadx=self.padX / 4,
                ipady=self.padY / 4,
                side=tk.LEFT
            )

            if bool(self.configuration.get('a_deduc')):
                self.config_qdf_field.delete(0, tk.END)
                self.config_qdf_field.insert(0, str(self.configuration['deduc_amnt']))

                self.config_qdf_field.pack(
                    fill=tk.X, expand=True,
                    padx=(self.padX, self.padX / 4), pady=self.padY,
                    side=tk.RIGHT
                )

                self.config_qdfField_descLbl.config(
                    text="Penalty: ",
                    wraplength=int(self.ws[0] - self.padX * 2),
                    justify=tk.RIGHT,
                    anchor=tk.E
                )

                self.config_qdfField_descLbl.pack(
                    fill=tk.X, expand=False,
                    padx=(self.padX, self.padX / 4), pady=self.padY,
                    side=tk.RIGHT
                )

        self.config_error_label.config(wraplength=int(self.ws[0] - self.padX * 2))
        self.config_error_label.pack(
            fill=tk.X, expand=False,
            padx=self.padX, pady=self.padY,
            side=tk.BOTTOM
        )

    def screen_4(self): # Final (Wait)
        debug(f"Setting up final page (ind = {self.screen_index})")

        self.finalFrame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

    def config_nav_buttons(self, index=None, setTo=None):
        if self.screen_index == 0: self.previous_button.config(state=tk.DISABLED)
        else: self.previous_button.config(state=tk.NORMAL)

        if self.screen_index == len(self.scI_mapping) - 1:
            self.next_button.config(text=self.screen_data['nav']['next']['defaults']['str_start'])
        else:
            self.next_button.config(text=self.screen_data['nav']['next']['defaults']['str_next'])

        if type(index) is int and type(setTo) is bool:
            self.sc_navButton_next_states[index] = setTo

        if self.sc_navButton_next_states[self.screen_index]:
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)

    # Button Handlers
    def config_qdf(self):
        if bool(self.configuration.get('a_deduc')):
            self.configuration['a_deduc'] = 0
        else:
            self.configuration['a_deduc'] = 1

        self.update_ui(force_refresh=True)

    def config_poa(self):
        if self.configuration['partOrAll'] == 'part':
            self.configuration['partOrAll'] = 'all'
        else:
            self.configuration['partOrAll'] = 'part'

        self.update_ui(force_refresh=True)

    def btns_dbSel_int(self):
        # Reset
        self.dbSel_btns_external.config(
            state=tk.NORMAL, bg=self.theme.get('bg'),
            text=self.screen_data[0]['defaults']['e']
        )

        self.screen_data[0]['flags']['selected'] = False

        # Check
        try:
            eCode = "<!ERROR:QAS_173462374&*^^783845783845*&^*&67df7**&63569^^87>%"
            ra = loadData_intern(eCode)

            debug(f"External DB: raw load (debID: 141) : ", ra)

            if ra == eCode:
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB']
                )
                return

            elif ra[0] == eCode:
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB']
                )
                return

            elif ra[1] == eCode:
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB']
                )
                return

            elif len(ra[1]) <= 0:
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB_noQs']
                )
                return

            self.configuration = ra[0]
            self.questions = ra[1]

        except Exception as E:
            debug("Error whilst loading extern_db: ", E)
            self.dbSel_error_lbl.config(
                text=self.screen_data[0]['strs']['errors']['unknown']
            )

            return

        # Set

        self.dbSel_btns_internal.config(
            state=tk.DISABLED, bg=self.theme.get('ac'),
            text=self.screen_data[0]['defaults']['i'] + ' \u2713'
        )

        self.dbSel_error_lbl.config(
            text=""
        )

        self.screen_data[0]['database_selection'] = 'i'
        self.screen_data[0]['flags']['selected'] = True
        self.config_nav_buttons(0, True)

    def btns_dbSel_ext(self):
        # Checks
        self.dbSel_btns_internal.config(
            state=tk.NORMAL, bg=self.theme.get('bg'),
            text=self.screen_data[0]['defaults']['i']
        )

        self.screen_data[0]['flags']['selected'] = False

        file = tkfld.askopenfilename(
            defaultextension=f".{QAInfo.export_quizFile}",
            filetypes=((f"QA Quiz Database (*.{QAInfo.export_quizFile})", f"*.{QAInfo.export_quizFile}"), )
        )

        ret = type(file) is not str
        if not ret:
            file = file.replace('/', '\\')
            ret = ret or not((file.strip() != "") and os.path.exists(file))

        try:
            eCode = "<!ERROR:QAS_173462374&*^^783845783845*&^*&67df7**&63569^^87>%"
            ra = loadData_extern(file, eCode)

            debug(f"External DB: raw load (debID: 142) : ", ra)

            if ra == eCode:
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB']
                )
                return

            elif ra[0] == eCode:
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB']
                )
                return

            elif ra[1] == eCode:
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB']
                )
                return

            elif len(ra[1]) <= 0:
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB_noQs']
                )
                return

            self.configuration = ra[0];
            self.questions = ra[1]

        except Exception as E:
            debug("Error whilst loading extern_db: ", E)
            self.dbSel_error_lbl.config(
                text=self.screen_data[0]['strs']['errors']['unknown']
            )

            return

        # All good
        debug("External database selected: ", file, "; exit = ", ret)

        if ret:
            self.screen_data[0]['flags']['selected'] = False
            self.dbSel_error_lbl.config(
                text=self.screen_data[0]['strs']['errors']['notValid']
            )
            return

        self.screen_data[0]['flags']['selected'] = True
        self.dbSel_error_lbl.config(
            text=""
        )

        self.dbSel_btns_external.config(
            state=tk.DISABLED, bg=self.theme.get('ac'),
            text=self.screen_data[0]['defaults']['e'] + ' \u2713\n' + file.split('\\')[-1]
        )

        self.screen_data[0]['database_selection'] = 'e'
        self.screen_data[0]['external_database'] = {}; self.screen_data[0]['external_database']['filename'] = file
        self.config_nav_buttons(0, True)

    def next_page(self):

        # Checks
        if self.screen_index == 0: # DB Select
            if not self.screen_data[0]['flags']['selected']:
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['selectDB']
                )
                return

            if self.screen_data[0]['database_selection'] == 'e':
                try:
                    eCode = "<!ERROR:QAS_173462374&*^^783845783845*&^*&67df7**&63569^^87>%"
                    ra = loadData_extern(self.screen_data[0]['external_database']['filename'], eCode)

                    if ra[0] == eCode:
                        self.dbSel_error_lbl.config(
                            text=self.screen_data[0]['strs']['errors']['invalidDB']
                        )
                        return

                    elif ra[1] == eCode:
                        self.dbSel_error_lbl.config(
                            text=self.screen_data[0]['strs']['errors']['invalidDB']
                        )
                        return

                    elif len(ra[1]) <= 0:
                        self.dbSel_error_lbl.config(
                            text=self.screen_data[0]['strs']['errors']['invalidDB_noQs']
                        )
                        return

                except Exception as E:
                    debug("Error whilst loading extern_db: ", E)
                    self.dbSel_error_lbl.config(
                        text=self.screen_data[0]['strs']['errors']['unknown']
                    )

                    return

        elif self.screen_index == 1: # Credentials
            if len(self.cred_first.get()) <= 0 or len(self.cred_last.get()) <= 0 or len(self.cred_studentID_field.get()) <= 0:
                self.cred_error_lbl.config(
                    text=self.screen_data[1]['strs']['errors']['addInformation']
                )
                return

        elif self.screen_index == 2: # Configuration
            pass

        elif self.screen_index == 3: # Final
            self.canClose = False
            self.previous_button.config(
                state=tk.DISABLED
            )
            self.next_button.config(
                state=tk.DISABLED
            )
            return

        self.update_ui(1)

    def prev_page(self):
        self.update_ui(-1)

    def __del__(self):
        self.thread.join(self, 0)

class FormUI(threading.Thread):

    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)

        self.start()

    def __del__(self):
        self.thread.join(self, 0)


class JSON:
    def __init__(self):
        self.jsonHandlerInst = QAJSONHandler.QAFlags()
        self.jsonHandler = self.jsonHandlerInst

        self.crashID = self.jsonHandlerInst.QT_crash_id
        self.timedEventID = self.jsonHandler.QT_timed_crash_id

        self.unrID = self.jsonHandlerInst.log_unr_id
        self.funcID = self.jsonHandlerInst.log_function_id
        self.timeID = self.jsonHandlerInst.log_time_id
        self.infoID = self.jsonHandlerInst.log_info_id

        self.noFuncID = self.jsonHandlerInst.no_func_id

    def logCrash(self, info: str, functionCall=None):
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
        global splObj
        # Step 1: Does the key exist?
        if self.getFlag(QAInfo.global_nv_flags_fn, self.crashID):

            # Step 2: Is the error un-resolved?
            check = self.getFlag(QAInfo.global_nv_flags_fn, self.crashID, return_boolean=False)

            if check.get(self.unrID):  # Un-resolved

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

                QASplash.hide(splObj)
                tkmsb.showinfo(apptitle,
                               f"The application had detected a boot-error flag and thus ran the appropriate diagnostics.")
                QASplash.show(splObj)

        # True = Test passed
        return True

# Adjust Splash
set_boot_progress(3)

# Functions go here

def debug(debugData: str, *args):
    debugData = debugData + " ".join(str(i) for i in args)

    # Script Name
    try:
        scname = __file__.replace(
            '/', '\\').split('\\')[-1].split('.')[0].strip()
    except:
        scname = sys.argv[0].replace(
            '/', '\\').split('\\')[-1].split('.')[0].strip()

    # Instance
    Log = QALogging.Log()

    # Generation
    if not QALogging.Variables().genDebugFile():
        Log.logFile_create(from_=scname)

    # Log
    Log.log(data=debugData, from_=scname)


def loadConfiguration(configruationFilename: str) -> dict:

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

def get_error_code(key) -> tuple:
    key = key.strip()

    out = []

    __raw = JSON().getFlag("codes.json", key, return_boolean=False)
    __info = JSON().getFlag("codes.json", "info", return_boolean=False)

    if key in __info: __info.get(key)
    else: __info = "No Information Found"

    return (__raw, __info)

def loadQuestions(path) -> dict:
    __raw = IO(path).autoLoad()

    __out = QAQuestionStandard.convRawToDict(__raw)
    return __out

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


def __logError(errorCode: str, **kwargs):
    crash_msg: str = f"The application has encountered an error; internal diagnostics will be run during the next boot sequence of this application.\n\nDiagnostic Code: {errorCode}"

    flags = {

        'logError': [True, (bool,)],

        'exit': [False, (bool,)],
        'exitCode': [-1, (str, int)],

        'showUI': [True, (bool,)],
        'UI_Message': [crash_msg, (str,)],

        'runDiagnostics': [False, (bool,)],
        'diagnosticsInfo': [crash_msg, (str,)],
        'diagnosticsFunctionName': [QAJSONHandler.QAFlags().no_func_id, (str,)]

    };
    flags = flags_handler(flags, kwargs, __rePlain=True)

    if flags['logError']:
        debug(
            f"The application encountered an error; exit: {flags['exit']}; exitCode: {flags['exitCode']}, runDiagnostics: {flags['runDiagnostics']}, diagnostics_code: {flags['diagnosticsInfo']}, error code: {errorCode}")

    if flags['showUI']:
        tkmsb.showerror(apptitle, flags['UI_Message'])

    if flags['runDiagnostics']:  # TODO: fix this
        __inst = JSON()

        dinfo = ""
        dfunction = flags['diagnosticsFunctionName']

        __inst.logCrash(info=dinfo, functionCall=dfunction)

    if flags['exit']:
        application_exit(flags['exitCode'])

def loadData_extern(filepath, errorCode) -> list:
    try:
        connector = sqlite3.connect(filepath)
        cursor = connector.cursor()
    
        with connector:
            cursor.execute(
                "SELECT * FROM config"
            )
            conf_raw = cursor.fetchall()[0]

            cursor.execute(
                "SELECT * FROM qas"
            )
            qas_raw = cursor.fetchall()[0]

        connector.commit()
        connector.close()

        debug("conf_raw = ", conf_raw, "\nqas_raw = ", qas_raw)

        config = {
            'customQuizConfig': conf_raw[0],
            'partOrAll': conf_raw[1],
            'poa_divF': conf_raw[2],
            'a_deduc': conf_raw[3],
            'deduc_amnt': conf_raw[4]
        }

        try:
            qas_raw = qas_raw[0]
            questions = ld_q_fr(qas_raw, errorCode)

        except IndexError:
            questions = {}

        except:
            questions = errorCode

        return [config, questions]

    except Exception as e:
        debug(f"Error whilst reading DB: ", e)
        return errorCode

def loadData_intern(errorCode) -> list:
    try:

        def get_conf(flagID: str):
            return JSON().getFlag(
                os.path.join(QAInfo.appdataLoc, QAInfo.confFilename).replace('/', '\\').strip(),
                flagID,
                return_boolean=False
            )

        config = {
            'customQuizConfig': get_conf('acqc'),
            'partOrAll': get_conf('qpoa'),
            'poa_divF': get_conf('qsdf'),
            'a_deduc': get_conf('dma'),
            'deduc_amnt': get_conf('pdpir')
        }

        questions = ld_q_fr(
            IO(
                os.path.join(QAInfo.appdataLoc, QAInfo.qasFilename).replace('/', '\\').strip()
            ).autoLoad(),
            errorCode
        )

        return [config, questions]

    except Exception as E:
        debug("Error whilst loading data from internal files: ", E)
        return errorCode

def ld_q_fr(raw_questions: str, errorCode) -> dict:
    try:
        return QAQuestionStandard.convRawToDict(raw_questions.strip())

    except Exception as e:
        debug("Error whilst loading questions: ", e)
        return errorCode

def application_exit(code: str = "0") -> None:
    debug(f"Exiting with code '{code}'")
    sys.exit(code)

# ===============
# End of function declarations
# Below are the boot steps
# ===============

# Adjust Splash
set_boot_progress(4)
# Boot checks go here

JSON().boot_check()

# Adjust Splash
set_boot_progress(5)
# OVC

try:
    if not QA_OVC.check():
        QASplash.hide(splObj)
        tkmsb.showwarning(apptitle, f"You are running an older version of the application; the database suggests that version '{QA_OVC.latest()}' is the latest (the current installed version is {QAInfo.versionData.get(QAInfo.VFKeys.get('v'))})")
        QASplash.show(splObj)

except:
    tkmsb.showwarning(apptitle, f"Non fatal: Failed to load version information (online)")

# Final Splash Settings
if not QAInfo.doNotUseSplash:
    show_splash_completion() # Show completion
    QASplash.destroy(splObj) # Close the splash screen

LoginUI()
