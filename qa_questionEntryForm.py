import tkinter as tk
import threading

import qa_appinfo as QAInfo
import qa_theme as QATheme
import qa_fileIOHandler as QAFileIO

class IO:
    def __init__(self, filename, **kwargs):
        self.filename = filename
        print(kwargs.get('test'))
    
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
    
class UI(threading.Thread):
    def __init__(self):
        pass
    
    def __del__(self):
        pass

class KWARGS:
    def change(object):
        print('a')
    
    def function_kwargsHandlder(object, kwargs: dict):
        print('b')
