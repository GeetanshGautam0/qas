from pynput.keyboard import Key, Listener
import keyboard, qa_win10toast, os, threading, sys
import qa_appinfo as QAInfo

class KeyLogger(threading.Thread):
    def __init__(self, filepathname, icon=None, actIm=False):
        
        # Thread handler
        self.thread = threading.Thread
        self.thread.__init__(self)
        self.start()
        
        # Vars
        self.file = filepathname
        self.activated = actIm
        self.listener = Listener(on_press=self.key_press)
        self.prev = ''
        
        self.icon = icon if icon is not None else QAInfo.icons_ico.get('qt')
        self.icon = self.icon if os.path.exists(self.icon) else QAInfo.icons_ico.get('qt')
        
        # Basic IO
        open(self.file, 'w').close()
        
        if self.activated: self.toggle(True)
        
    def toggle(self, onOff: bool):
        self.activated = onOff
        
        if self.activated:
            
            tDur = 5
            
            qa_win10toast.Toast(
                "Quizzing Application",
                f"Your keystrokes will be under observation in {tDur} seconds",
                self.icon,
                Duration=tDur
            )
            
            self.listener.start()
            self.listener.join()
            
        else:
            qa_win10toast.Toast(
                "Quizzing Application",
                "Your keystrokes will no longer be under observation in 5 seconds.",
                self.icon,
                Duration=0
            )

    def key_mapper(self, key) -> str:
        maps = {
            "backspace": " <<Backspace>> ",
            "delete": " <<Delete>> ",
            
            "ctrl_l": " <<Control>> ",
            "ctrl_r": " <<Control>> ",
            
            "esc": "\n\n<<Escape>>\n\n",
            
            "tab": " <<Tab>> ",
            
            "enter": "\n",
            
            "space": ' ',
            
            "shift": '',
            
            "left": '<<Left Arrow>> ',
            "right": "<<Left Arrow>> ",
            "down": "<<Left Arrow>> ",
            "up": "<<Left Arrow>> ",
            
            "cmd": "\n<<Windows Key>>",
            
            "alt_l": "  <<Alt>> ",
            "alt_r": "  <<Alt>> ",
            
            "num_lock": " <<Num Lock>> ",
            "caps_lock": "<<Caps Lock>> ",
            
            # Key Codes
            "<96>": "0",
            "<97>": "1",
            "<98>": "2",
            "<99>": "3",
            "<100>": "4",
            "<101>": "5",
            "<102>": "6",
            "<103>": "7",
            "<104>": "8",
            "<105>": "9",
            
            "<110>": ".",
            
            "\x01": "\n   <<Control + A (Select All)>>   \n",
            "\x02": "\n   <<Control + B>>   \n",
            "\x03": "\n   <<Control + C (Copy)>>   \n",
            "\x04": "\n   <<\\x04 Description>>   \n",
            "\x05": "\n   <<\\x05 Description>>   \n",
            "\x06": "\n   <<\\x06 Description>>   \n",
            "\x07": "\n   <<\\x07 Description>>   \n",
            "\x08": "\n   <<\\x08 Description>>   \n",
            "\x09": "\n   <<\\x09 Description>>   \n",
            "\x10": "\n   <<\\x10 Description>>   \n",
            "\x11": "\n   <<\\x11 Description>>   \n",
            "\x12": "\n   <<\\x12 Description>>   \n",            
            "\x13": "\n   <<Control + S (Save)>>   \n"
        }
        
        try: 
            out = key.char.strip()
            if out in maps: out = maps.get(out)
            
            out = f"{out}"
            
        except:
            try:
                K = key.name.strip().lower()            
                m = maps.get(K) if K in maps else K
                
                print(f"{K}::{m}")
                
                out = m
            
            except:
                out = maps.get(str(key).strip()) if str(key).strip() in maps else f"\n{str(key).strip()}\n"
                print(f"Final Resort:: {out}")
                
        ok = "<<Control>> f12" not in self.prev + out
        
        self.prev = out if ok else ''
        
        return (out, ok)
        
    def key_press(self, key) -> None:
        
        if self.activated:
            print(f"Pressed: {key}")
            
            d = open(self.file, 'r').read().strip()
            
            print(d)
            
            k = self.key_mapper(key)
            
            print(k)
            
            if k[-1]:
                with open(self.file, 'a') as file: 
                    file.write(
                         str(k[0])
                    )
                    file.close()
            
            if not k[-1]:
                
                qa_win10toast.Toast(
                    "Quizzing Application",
                    "Your keyboard strokes will no longer be under observation in 5 seconds.",
                    self.icon,
                    Duration=5
                )
                
                return False # Stop the listner

        else:
            qa_win10toast.Toast(
                "Quizzing Application",
                "Your keyboard strokes will no longer be under observation in 5 seconds.",
                self.icon,
                Duration=5
            )
            
            return False # Stop the listner
        
    def __del__(self):
        self.thread.join(self, 0)

if __name__ == "__main__": sys.exit("Cannot run module standalone")

# s = KeyLogger(f"loggerTest.log")
# s.toggle(True)
