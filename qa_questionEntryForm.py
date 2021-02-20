import tkinter as tk
from tkinter import ttk
import threading, os, sys

import qa_theme as QATheme
import qa_appinfo as QAInfo
import qa_fileIOHandler as QAFileIO

class UI(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)
        
        self.theme = QATheme.Get().get('theme')
        
        self.root = tk.Toplevel()
        
        self.vsb_style = ttk.Style()
        self.vsb_style.theme_use('default')
        
        self.sep_style = ttk.Style()
        self.sep_style.theme_use('default')
        
        self.canv = tk.Canvas(self.root)
        self.frame = tk.Frame(self.root)     
        self.vsb = ttk.Scrollbar(self.root)
        
        self.question_entry = tk.Text(self.frame); self.questionLbl = tk.Label(self.frame, text="Enter Question")
        self.answer_entry = tk.Text(self.frame); self.answerLbl = tk.Label(self.frame, text="Enter Correct Answer")
        
        self.mcSel = tk.Button(self.frame, text="Multiple Choice", command=self.mc_click)
        self.submitButton = tk.Button(self.frame, text="Add Question", command=self.add)
        
        self.clearButton = tk.Button(self.frame, text="Delete All Questions", command=self.delAll)
        self.helpButton = tk.Button(self.frame, text="Instructions", command=self.help)
        
        self.sep = ttk.Separator(self.frame)
        
        self.ss = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.ws = [680, 800]
        self.wp = [
            int(self.ss[0]/2 - self.ws[0]/2),
            int(self.ss[1]/2 - self.ws[1]/2)
        ]
        
        # Theme data sets
        self.theme_label: list = []
        self.theme_label_font: dict = {}
        self.theme_button: list = []
        self.theme_accent: list = []
        
        self.start()
        self.root.mainloop()
        
    def run(self):
        # Root configuration
        self.root.geometry(f"{self.ws[0]}x{self.ws[1]}+{self.wp[0]}+{self.wp[1]}")
        self.root.resizable(False, True)
        self.root.minsize(self.ws[0], int(self.ws[1]/2))
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.title("Add Question")
        self.root.iconbitmap(QAInfo.icons_ico.get('admt'))
        
        # Widget configuration + placement
        # The basic back
        self.canv.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        self.vsb.pack(fill=tk.Y, expand=False, side=tk.RIGHT)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # The actual control
        
        ttl = tk.Label(self.frame, text="Add Questions")
        ttl.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        self.theme_label.append(ttl)
        self.theme_accent.append(ttl)
        self.theme_label_font[ttl] = (
            self.theme.get('font'),
            32
        )
        
        self.helpButton.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        self.theme_button.append(self.helpButton)
        self.theme_label_font[self.helpButton] = (
            self.theme.get('font'),
            16
        )
        
        self.sep.pack(fill=tk.X, expand=True, padx=5) 
        
        self.questionLbl.config(anchor=tk.SW)
        self.theme_label.append(self.questionLbl)
        self.theme_accent.append(('bg', self.theme.get('bg'), self.questionLbl))
        
        self.questionLbl.pack(fill=tk.X, expand=True, padx=10, pady=(5, 0))
        self.question_entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        
        self.answerLbl.config(anchor=tk.SW)
        self.theme_label.append(self.answerLbl)
        self.theme_accent.append(('bg', self.theme.get('bg'), self.answerLbl))
        
        self.answerLbl.pack(fill=tk.X, expand=True, padx=10)
        self.answer_entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        self.mcSel.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        self.theme_button.append(self.mcSel)        
        self.theme_label_font[self.mcSel] = (
            self.theme.get('font'),
            14
        )
        
        self.submitButton.pack(
            fill=tk.BOTH,
            expand=True,
            padx=(10, 5),
            pady=(0, 5),
            side=tk.LEFT
        )
        self.theme_button.append(self.submitButton)        
        self.theme_label_font[self.submitButton] = (
            self.theme.get('font'),
            14
        )
        
        self.clearButton.pack(
            fill=tk.BOTH,
            expand=True,
            padx=(10, 5),
            pady=(0, 5),
            side=tk.RIGHT
        )
        self.theme_label_font[self.clearButton] = (
            self.theme.get('font'),
            14
        )
        
        # ttk :: SB conf. (After widget placement)
        self.vsb.configure(command=self.canv.yview)
        
        self.canv.configure(
            yscrollcommand=self.vsb.set
        )
        
        self.canv.create_window(
            (0,0),
            window=self.frame,
            anchor="nw",
            tags="self.frame"
        )
        
        # Final Things
        self.update()
        
        # Event Handlers
        self.frame.bind("<Configure>", self.onFrameConfig)
        self.frame.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """
        Straight out of stackoverflow
        Article: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
        Change
        : added "int" around the first arg
        """
        # self.canv.yview_scroll(int(-1 * (event.delta / 120)), "units")
        pass
    
    def onFrameConfig(self, event): # for scbar
        self.canv.configure(
            scrollregion=self.canv.bbox("all")
        )
        
    def close(self):
        if __name__ == "__main__":
            sys.exit("WM_DELETE_WINDOW")
        else:
            self.root.after(0, self.root.destroy)
            return
    
    def update_theme(self):
        # Pre
        QATheme.Get().refresh_theme()
        self.theme = QATheme.Get().get('theme')
        
        # TTK
        self.vsb_style.configure(
            "TScrollbar",
            background=self.theme.get('bg'),
            arrowcolor=self.theme.get('fg'),
            bordercolor=self.theme.get('bg'),
            troughcolor=self.theme.get('bg')
        )

        self.vsb_style.map(
            "TScrollbar",
            background=[
                ("active", self.theme.get('ac')), ('disabled', self.theme.get('bg'))
            ]
        )

        self.sep_style.configure(
            "TSeparator",
            background=self.theme.get('fg')
        )
        
        # TK
        self.root.config(
            bg=self.theme.get('bg')
        )
        
        self.canv.config(
            bg=self.theme.get('bg')
        )
        
        self.frame.config(
            bg=self.theme.get('bg')
        )
        
        self.question_entry.config(
            bg=self.theme.get('bg'),
            fg=self.theme.get('fg')
        )
        
        self.answer_entry.config(
            bg=self.theme.get('bg'),
            fg=self.theme.get('fg')
        )
        
        # self.theme_label: list = []
        # self.theme_label_font: dict = {}
        # self.theme_button: list = []
        # theme_accent: list = []
        
        for i in self.theme_label:
            try:
                i.config(
                    bg=self.theme.get('bg'),
                    fg=self.theme.get('fg')
                )
            
            except: pass
            
        for i in self.theme_label_font:
            try:
                i.config(
                    font=self.theme_label_font.get(i)
                )

            except:
                pass
            
        for i in self.theme_button:
            i.config(
                bg=self.theme.get('bg'),
                fg=self.theme.get('fg'),
                activebackground=self.theme.get('ac'),
                activeforeground=self.theme.get('hg'),
                bd=0
            )
        
        for i in self.theme_accent:
            try:
                if type(i) is tuple or type(i) is list:
                    
                    if i[0] is 'bg':
                        i[-1].config(
                            bg=self.theme.get('ac'),
                            fg=i[1]
                        )

                else:
                    i.config(
                        fg=self.theme.get('ac')
                    )

            except: pass
        
        # Exceptions
        self.clearButton.config(
            bg="red",
            fg="white",
            activebackground="white",
            activeforeground="red",
            bd=0
        )    

    def update(self):
        self.update_theme()
    
    # Event Handlers
    
    # Button Handlers
    
    def help(self):
        pdf = QAInfo.QA_ENTRY_HELP
        os.system(f"{pdf}")
    
    def submit(self):
        pass
    
    def mc_click(self): 
        pass
    
    def delAll(self): 
        pass
    
    def add(self):
        pass
    
    def __del__(self):
        self.thread.join(0, self)
    
class IO:
    def __init__(self):
        pass
    
    def save(self, data):
        pass
    
    def autoLoad(self):
        pass
    
    def rawLoad(self):
        pass
    
    def encrypt(self):
        pass
    
    def decrypt(self):
        pass
    
    def __del__(self):
        pass


if __name__ == "__main__":
    UI()