import tkinter as tk
import threading

import qa_appinfo as QAInfo
import qa_theme as QATheme
import qa_fileIOHandler as QAFileIO
import qa_errors as QAExceptions

class IO:    
    def __init__(self, fn: str, **kwargs):
        self.filename = fn
        self.object = QAFileIO.create_fileIO_object(self.filename)
        
        self.flagsHandlerDict = {
            'append': [False, (bool, )],
            'append_sep': ["\n", (str, bytes)],
            'suppressError': [False, (bool,)],
            'encoding': ['utf-8', (str, )],
            'encrypt': [False, (bool, )]
        }
        
        print(kwargs)
        
        self.flags = {}; KWARGS(self, 'f', flags=kwargs)
        
        print(self.flags)
        
    def rawLoad(self) -> bytes:
        return QAFileIO.load(self.object)

    def save(self, Data):  # Secure Save
        QAFileIO.save(
            self.object,
            Data,
            append=self.flags['append'],
            appendSeperator=self.flags['append_sep'],
            encryptData=self.flags['encrypt'],
            encoding=self.flags['encoding']
        )

    def clear(self) -> None:
        open(self.object.filename, 'w').close()

    def autoLoad(self) -> str:
        return QAFileIO.read(self.object)

    def encrypt(self) -> None:
        QAFileIO.encrypt(self.object)

    def decrypt(self) -> None:
        QAFileIO.decrypt(self.object)
    
class UI(threading.Thread):
    def __init__(self):
        pass
    
    def __del__(self):
        pass

def KWARGS(Object: object, call: str, flags: dict = {}, **kwargs) -> any: # Object-Oriented
    chKey = "c"; fHKey = "f"
    call = call.lower().strip()
    def flagsHandler(Object: object, kwargs: dict, __raiseErr: bool = True, __ignoreLen: bool = True):
        if len(kwargs) <= 0 and not __ignoreLen: return # Do not waste time
        # Actual - Filters
        ac_ks = [i.strip() for i in Object.flagsHandlerDict.keys()] # str
        ac_vs = [i for i in Object.flagsHandlerDict.values()] # list
        ac_fs = {ac_ks[i]: ac_vs[i] for i in range(0, len(ac_ks))} # Flags
        
        # Given - Filters
        g_ks = [i.strip() for i in kwargs.keys()] # str
        g_vs = [i for i in kwargs.values()] # list
        g_fs = {g_ks[i]: g_vs[i] for i in range(0, len(g_ks))} # Flags
        
        # Output
        out = ac_fs # Set all other flags automatically
        
        # Logic
        for i in g_fs:
            if not i in ac_fs and __raiseErr: raise QAExceptions.QA_InvalidFlag(f"Invalid flag name '{i}'")
            else:
                if not type(g_fs.get(i)) in ac_fs.get(i)[-1]:
                    raise QAExceptions.QA_InvalidFlag(f"Invalid data type {type(g_fs.get(i))} for flag '{i}'; expected one of: {ac_fs.get(i)[-1]}")
                
                else:
                    out[i] = [g_fs.get(i), ac_fs[i][-1]] # Reconstruct the specific flag with the new data
                    
        # Set
        # Flags for this function:
        Object.flagsHandlerDict = out
        
        # Plain + Set
        plain = {
            i: out[i][0] for i in out
        }; Object.flags = plain
        
        print((out, plain))
        
        return (out, plain) # Tuple; cannot change
                    
    if call == chKey:
        # change(Object, kwargs)
        return flagsHandler(Object, kwargs)
        
    elif call == fHKey:
        return flagsHandler(Object, flags)
        
    else:
        return {
            "change": chKey,
            "flagsHandler": fHKey
        }
    