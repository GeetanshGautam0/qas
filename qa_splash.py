import tkinter as tk, threading, sys
import qa_theme as QATheme

theme = QATheme.Get().get('theme')

class Splash(tk.Toplevel):
    def __init__(self, master=None):
        
        tk.Toplevel.__init__(self, master)
        
        # UI Vars
        self.root = master

        # UI Config
        self.run()

        # UI Update
        self.root.update()
    
    def run(self):
        self.root.overrideredirect(True)
        self.root.protocol("WM_DELETE_WINDOW", lambda: destroy(self))
    
    def change_text(self, text: str) -> None:
        pass
    
    def update(self) -> None:
        self.root.update()
    
    def set_bar(self, percentage: float) -> None:
        pass
            
    def __del__(self):
        self.thread.join(self, 0)

Z = True

def destroy(__inst: object):
    Z = False
    __inst.root.after(0, __inst.root.quit)

def update(__inst: object):
    __inst.root.update()

s = Splash(tk.Tk())

print('a')

destroy(s)

print('b')
