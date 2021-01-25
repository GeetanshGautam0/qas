import os, sys
import qa_logging as Logging
from tkinter import messagebox as tkmsb

def rm():
    os.rmdir(Logging.Variables().folderName())
    os.makedirs(Logging.Variables().folderName())

    tkmsb.showinfo("QA-Logs", f"Removed Logs")

if __name__ == "__main__": rm()