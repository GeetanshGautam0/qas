import os, sys, shutil, time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkmsb
import qa_appinfo as QAInfo
import qa_errors as QAErrors
import qa_time as QATime
import installer_options as IOptions

# Globals
apptitle = f"Quizzing Application {QAInfo.versionData[QAInfo.VFKeys['v']]} - Setup"
icon = QAInfo.icons_ico.get('installer')
logFn = file = f"{QAInfo.appdataLoc}\\setup.log"
theme = {}
def_theme_file_loc = IOptions.themeFile
def_theme_file = open(def_theme_file_loc, 'r').read()

class UI(tk.Toplevel):

    def __init__(self, master=None):
        self.root = master
        self.mainFrame = tk.Frame(self.root)

        self.h = 400; self.w = 800; self.gem = "{}x{}+{}+{}".format(
            self.w,
            self.h,
            int(self.root.winfo_screenwidth()/2 - self.w/2),
            int(self.root.winfo_screenheight()/2 - self.h/2)
        )

        self.progStyle = ttk.Style()
        self.progStyle.theme_use('alt') # alt

        self.start_button = tk.Button(self.root)
        self.titleLbl = tk.Label(self.mainFrame)
        self.subtitleLbl = tk.Label(self.mainFrame)
        self.info_lbl = tk.Label(self.mainFrame)
        self.progBar = ttk.Progressbar(self.mainFrame)
        self.procProgbar = ttk.Progressbar(self.mainFrame)

        self.imgInd = 0
        self.pr1 = 0
        self.complete = False
        self.inprogress = False
        self.run()
        self.root.mainloop()

    def close(self):
        if not self.complete:
            if self.inprogress:
                tkmsb.showerror(apptitle, f"Setup in progress; please wait.")
                return

            else:
                conf = tkmsb.askyesno(apptitle, f"Setup not completed; are you sure you want to exit?")
                if not conf: return

        self.root.after(0, self.root.quit)

    def run(self):
        global theme; global apptitle; global icon

        self.root.title(apptitle)
        self.root.geometry(self.gem)
        self.root.iconbitmap(icon)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.start_button.pack(fill=tk.BOTH, expand=False, side=tk.LEFT, ipadx=12)
        self.mainFrame.config(bg=theme.get('bg'))
        self.mainFrame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        self.titleLbl.config(
            text="Quizzing Application Suite",
            bg=theme.get('bg'),
            fg=theme.get('ac'),
            font=(theme.get('font'), 32),
            anchor=tk.W
        )

        self.titleLbl.pack(
            fill=tk.X,
            expand=False,
            padx=20,
            pady=(10, 5)
        )

        self.subtitleLbl.config(
            text="Setup",
            bg=theme.get('bg'),
            fg=theme.get('fg'),
            anchor=tk.W,
            font=(theme.get('font'), 16)
        )

        self.subtitleLbl.pack(
            fill=tk.X,
            expand=False,
            padx=20
        )

        self.progStyle.configure(
            "Horizontal.TProgressbar",
            foreground=theme.get('ac'),
            background=theme.get('ac'),
            troughcolor=theme.get('bg'),
            thickness=20
        )

        cred = tk.Label(self.mainFrame, text="Coding Made Fun, {}".format(
            QATime.form("%Y")
        ), bg=theme.get('bg'), fg=theme.get('fg'), font=(theme.get('font'), 8), anchor=tk.SE).pack(
            fill=tk.X,
            expand=False,
            padx=20,
            side=tk.BOTTOM
        )

        self.procProgbar.pack(
            fill=tk.X,
            expand=False,
            side=tk.BOTTOM,
            padx=20,
            pady=(2, 5)
        )

        self.progBar.pack(
            fill=tk.X,
            expand=False,
            side=tk.BOTTOM,
            padx=20
        )

        self.info_lbl.config(
            text="Please click 'Start Installation' to continue.",
            bg=theme.get('bg'),
            fg=theme.get('fg'),
            anchor=tk.W,
            font=(theme.get('font'), 10)
        )

        self.info_lbl.pack(
            side=tk.BOTTOM,
            fill=tk.X,
            expand=False,
            padx=20,
            pady=2
        )

        self.start_button.config(
            text="Start\nInstallation",
            font=(theme.get('font'), 13),
            bg=theme.get('ac'),
            fg=theme.get('hg'),
            activebackground=theme.get('bg'),
            activeforeground=theme.get('fg'),
            disabledforeground=theme.get('fg'),
            bd=0,
            command=self.finish_installation
        )

    def finish_installation(self):
        self.inprogress = True

        img=tk.PhotoImage(file=IOptions.installer_picture.format(self.imgInd))

        self.start_button.config(
            image=img,
            width=100,
            command=self.scrollImg
        )

        self.overwrite_and_copy()
        self.complete = True

        sys.exit(1)

    def scrollImg(self):
        # self.imgInd += 1
        # try:
        #     img = tk.PhotoImage(file=IOptions.installer_picture.format(self.imgInd))
        #
        # except:
        #     self.imgInd = 0
        #     img = tk.PhotoImage(file=IOptions.installer_picture.format(self.imgInd))
        #
        # print(IOptions.installer_picture.format(self.imgInd))
        # self.start_button.config(
        #     image=img,
        #     width=100
        # ); self.start_button.update_ui()

        # self.start_button.pack_forget()

        pass

    def overwrite_and_copy(self):
        ldr = os.listdir(QAInfo.appdataLoc)

        for i in ldr:
            time.sleep(0.1)

            self.smooth_prog(
                (ldr.index(i) / (len(ldr)-1)) * 100,
                0, 3,
                f"Deleting {i}"
            )

            self.root.update_ui()

            if os.path.exists(f"{QAInfo.appdataLoc}\\{i}"):  # Only if it already exists

                if os.path.isdir(f"{QAInfo.appdataLoc}\\{i}"):  # If it is a directory
                    dump_debug(f"Deleting directory {QAInfo.appdataLoc}\\{i}")
                    try: os.rmdir(f"{QAInfo.appdataLoc}\\{i}")
                    except Exception as e:
                        try:
                            shutil.rmtree(f"{QAInfo.appdataLoc}\\{i}")
                        except Exception as E:
                            error(
                                apptitle,
                                f"Failed to remove pre-existing files; files may have been corrupted;\n\nUse Quizzing Application FTS+RA Utility to fix.\n\n{e}\n\n{E}",
                                False
                            )

                elif os.path.isfile(f"{QAInfo.appdataLoc}\\{i}"):  # If it's a file
                    dump_debug(f"Deleting file {QAInfo.appdataLoc}\\{i}")
                    os.remove(f"{QAInfo.appdataLoc}\\{i}")

                else:  # No conditions met (error)
                    dump_debug(
                        f"No delete condition met, raising {IOError}: No delete condition met for entry {QAInfo.appdataLoc}\\{i}; setting boot error flag.")
                    error(apptitle, f"No delete condition met for entry {QAInfo.appdataLoc}\\{i}", True)

        # Copy
        fdr = QAInfo.QaFTSRAFiles

        for i in fdr:
            time.sleep(0.1)
            fpath = f"{QAInfo.ftsFolder}\\{i}"
            apath = f"{QAInfo.appdataLoc}\\{i}"

            self.smooth_prog(
                (fdr.index(i) / (len(fdr)-1)) * 100,
                33, 3,
                f"Copying {i}"
            )

            self.root.update_ui()

            if not os.path.exists(fpath):
                dump_debug(f"FTSRA file '{fpath}' does not exist; raising error.")
                tkmsb.showerror(apptitle,
                                f"Critical error: file '{fpath}' required for this routine does not exist; a complete reinstall may be required if the error persists.")
                error(
                    apptitle,
                    f"Critical error: file '{fpath}' required for this routine does not exist; a complete reinstall may be required if the error persists.",
                    True
                )

            if os.path.isdir(fpath):  # If the file is a directory
                dump_debug(f"Copying directory {fpath} to {apath}")
                shutil.copytree(fpath, apath)

            elif os.path.isfile(fpath):  # If the file is a file
                dump_debug(f"Copying file {fpath} to {apath}")
                shutil.copy(fpath, apath)

            else:  # No conditions met (error)
                dump_debug(f"{IOError(f'No copy condition met for file {fpath} -> {apath}')}; setting boot error flag")
                error(
                    apptitle,
                    f"No copy condition met for file {fpath} -> {apath}",
                    True
                )

        # Icons
        self.progBar['value'] = 0
        self.smooth_prog(0, 67, 3, "Configuring Icons")

        os.system("%s" % QAInfo.icons_regFile)

        self.smooth_prog(100, 67, 3, "Finished configuring icons.")

        self.progBar['value'] = 100
        self.procProgbar['value'] = 100

        self.info_lbl.config(text=f"Setup Completed \u2713")

        tkmsb.showinfo(
            apptitle,
            "You will now be signed out to finish configuring the icons, and therefore the setup."
        )

        os.system("shutdown -l")

    def smooth_prog(self, prog1, prog2Add, prog2Div, info="", res=1):

        print(prog1, prog2Add, prog2Div, info, res)

        for i in range(self.pr1*res, int(prog1)*res):
            self.progBar['value'] = i/res
            self.procProgbar['value'] = prog2Add + ((i / res) / prog2Div)
            self.root.update_ui()
            try:
                self.info_lbl.config(
                    text=f"{info} ({int((i/res / int((int(prog1)))) * 100) + 1}%; Current task: {int(i/res)}% done; Total: {int(prog2Add + ((i / res) / prog2Div)) + 1}% done)"
                )

            except ZeroDivisionError:
                try:
                    self.info_lbl.config(
                        text=f"{info} (0%; {int(prog2Add + ((i / res) / prog2Div)) + 1}% total)"
                    )

                except ZeroDivisionError:
                    self.info_lbl.config(
                        text=f"{info} (0%; 0% total)"
                    )

        self.pr1 = int(prog1)

def conv_to_types(theme: dict) -> dict:

    types = {
        'font': str,

        'fsize_para': int,
        'sttl_base_fsize': int,
        'min_fsize': int,

        'bg': str,
        'fg': str,
        'ac': str,
        'hg': str,

        'border': int
    }

    output = theme
    err = False

    for i in types:
        try:
            output[i] = types[i](theme[i])

        except Exception as e:
            err = True

    if err: tkmsb.showerror(apptitle, f'Theme file was corrupted; some anomalies in the theme may be visible.')

    return output

def load_theme(raw):  # File theme.qaFile will not be encrypted
    OUT = {}

    try:
        # Variables
        raw_l: list = raw.split("\n")  # Raw (list)
        sep = " "  # Seperator
        loaded = {}

        # Handle
        for i in raw_l:
            if len(i.strip()) > 0:
                if not i.strip()[0] == "#":
                    # If it is not a comment
                    key = i.split(sep)[0].strip()
                    val = i.replace(key, "", 1).strip()
                    loaded[key] = val

    except Exception as E:
        try:
            raise QAErrors.QA_SetupException(f"Failed to load theme;\n\n{E}")
        except Exception as e:
            error(
                apptitle,
                f"A low-level error occurred whilst loading the theme; using default theme temporarily. Please use the Theming Utility to reset the file.\n\nMore information: {e}",
                True
            )

    OUT = conv_to_types(loaded)
    dump_debug(f"Loaded theme '{OUT}'")
    return OUT

def dump_debug(data):
    global logFn
    file = logFn

    data = f"QA_Setup : {QATime.now()} : {data}"

    while not os.path.exists(file): open(file, 'x').close()
    print(file, data)

    open(file, 'a').write(
        data
    )

def boot_check():
    if os.path.exists(
        "{}\\{}".format(
            QAInfo.appdataLoc,
            QAInfo.confFilename
        )
    ):
        error(apptitle, f"Installation detected; cannot proceed with the setup routine.", True)

def error(title, message, exit):
    tkmsb.showerror(title, message)
    tkmsb.showwarning(
        title,
        "To finish the installation manually, browse to the installation directory and run 'Quizzing Application FTS + RA Utility'"
    )

    dump_debug(f"QAErrors.QA_SetupException : {message}; exit={exit}")

    if exit:
        raise QAErrors.QA_SetupException(message)
        sys.exit(1) # Fail safe?

if not IOptions.allow_confFile_existence: boot_check()
elif IOptions.ask_owr and os.path.exists("{}\\{}".format(
            QAInfo.appdataLoc,
            QAInfo.confFilename
        )):
    owr = tkmsb.askyesno(apptitle, "An older installation was found; do you want to overwrite the old files?")
    if not owr: sys.exit(0)

if os.path.exists(logFn):
    open(logFn, 'w').close() # Clear

theme = load_theme(def_theme_file)
root = tk.Toplevel()
a = UI(root)
