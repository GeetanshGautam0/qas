import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkmsb
import os, sys, threading, shutil, time, json

import qa_appinfo as QAInfo
import qa_diagnostics as QADiagnostics
import qa_splash as QASplash
import qa_keylogger as QAKeyLogger
import qa_typeConvertor as QAConvertor
import qa_logging as QALogging
import qa_fileIOHandler as QAFileIO
import qa_onlineVersCheck as QA_OVC
import qa_win10toast as Win10Toast
import qa_time as QATime
import qa_globalFlags as QAJSONHandler
import qa_errors as QAErrors
import qa_questions as QAQuestionStandard

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


def set_boot_progress(ind, resolution=1000):
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


def show_splash_completion(resolution=1000):
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

class IO:

    def __init__(self):
        pass

class LoginUI(threading.Thread):

    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)

        self.root = tk.Toplevel()
        self.root.withdraw()

        self.start()

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
        # Step 1: Does the key exist?
        if self.getFlag(QAInfo.global_nv_flags_fn, self.crashID):

            # Step 2: Is the error un-resolved?
            check = self.getFlag(QAInfo.global_nv_flags_fn, self.crashID, return_boolean=False)

            if check.get(self.unrID):  # Un-reolved

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

                tkmsb.showinfo(apptitle,
                               f"The application had detected a boot-error flag and thus ran the appropriate diagnostics.")

        # True = Test passed
        return True

# Adjust Splash
set_boot_progress(3)

# Functions go here

def debug(debugData: str):
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
