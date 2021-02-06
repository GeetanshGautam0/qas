import threading, sys, os
from PIL import Image as PILImage, ImageTk as PILImageTk
from tkinter import *
import tkinter.ttk as ttk
import qa_theme as QATheme
import qa_appinfo as QAInfo

theme = QATheme.Get().get('theme')

class Splash(Toplevel):
    def __init__(self, master=None):
        global theme; self.theme = theme
        
        # UI Vars
        self.pbarStyle = ttk.Style()
        self.pbarStyle.theme_use('default')
        self.pbarStyle.configure(
            "Horizontal.TProgressbar",
            foreground=self.theme.get('ac'),
            background=self.theme.get('ac'),
            borderwidth=0
        )
        
        self.root = master
        self.frame = Frame(self.root)
        
        self.geo = "700x350+{}+{}".format(
            int(self.root.winfo_screenwidth()/2 - 350),
            int(self.root.winfo_screenheight()/2 - 250)
        )
        
        self.root.geometry(self.geo)
        
        self.titleLbl = Label(self.frame)
        self.imgLbl = Button(self.frame, anchor=NW)
        self.pbar = ttk.Progressbar(self.frame,length=100, mode='determinate', orient=HORIZONTAL)
        self.infoLbl = Label(self.frame)
        
        self.title = "Quizzing Application"
        self.information = "Loading..."
        self.img = os.path.abspath(f"{QAInfo.icons_png['qt']}").replace('/', '\\')
        
        # UI Config
        self.run()

        # UI Update
        self.root.update()
    
    def run(self):
        self.root.overrideredirect(True)
        self.root.protocol("WM_DELETE_WINDOW", lambda: destroy(self))
        self.root.wm_attributes('-topmost', 1)
        
        self.frame.pack(fill=BOTH, expand=True)
        self.frame.config(bg=self.theme.get('bg'))
        
        image = PILImageTk.PhotoImage(PILImage.open(self.img).resize((32, 32)), master=self.root)
        self.imgLbl.configure(
            image=image, 
            bg=self.theme.get('bg'), 
            command=sys.exit,
            bd=0,
            activebackground=self.theme.get('bg')
        )
        self.imgLbl.image = image
        
        self.titleLbl.config(text=self.title, bg=self.theme.get('bg'), fg=self.theme.get('ac'), font=(self.theme.get('font'), 30), anchor=N)
        self.infoLbl.config(text=self.information, bg=self.theme.get('bg'), fg=self.theme.get('fg'), font=(self.theme.get('font'), self.theme.get('fsize_para')), anchor=NW)
        
        self.imgLbl.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.titleLbl.pack(fill=BOTH, expand=True)
        self.pbar.pack(fill=BOTH, expand=1, padx=5)
        self.infoLbl.pack(fill=X, expand=True, padx=5)
        
    def setImg(self, img) -> None:
        self.img = img
        image = PILImageTk.PhotoImage(PILImage.open(self.img).resize((32, 32)), master=self.root)
        self.imgLbl.configure(
            image=image
        )
        self.imgLbl.image = image
        self.root.update()
    
    def changePbar(self, per: float) -> None:
        self.pbar['value'] = per
        self.pbar.configure(style="Horizontal.TProgressbar")
        self.root.update()
        
    def setInfo(self, text) -> None:
        self.information = text
        self.infoLbl.config(text=self.information)
        self.root.update()
    
    def setTitle(self, text: str) -> None:
        # self.title = text.replace(' ', '\n')
        self.title = text.strip()
        self.titleLbl.config(text=self.title)
        self.root.update()
    
    def update(self) -> None:
        self.root.update()

def Pass(): pass

def destroy(__inst: object):
    __inst.root.after(0, __inst.root.destroy)
    return

def update(__inst: object):
    __inst.root.update()

if __name__ == "__main__":
    s = Splash(Toplevel())
    
    for i in range(10000):
        s.changePbar(i/10)
