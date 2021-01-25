import appdirs, os, sys, shutil, json, traceback
import tkinter.messagebox as msb
import qa_globalFlags as qaFlags
from qa_logging import *
import qa_theme as Theme

if __name__ == "__main__": sys.exit("Cannot run as main file")

# General
global scriptName; k = b'FJf5hmYl7OiaUkOpiU-7xrrGtRaN_11mSRjiG6xf_ps='; global themegetter
scriptName = __file__.replace("/","\\").split("\\")[-1].strip()
themegetter = Theme.Get()

# Logging
global logFilename; global logRef; global variablesRef
logRef = Log()
variablesRef = Variables()
def createLogFile(__from__): logFilename = logRef.logFile_create(__from__)


def close(exCode): sys.exit(exCode)

# Error Handling Method
def errorHandler(errCode="Error Code Unknown", exit=False, exit_code="Exit Code Unknown",showGUIMessage=False):
    if not variablesRef.genDebugFile(): createLogFile(scriptName)
    log_information = f'An error occurred whilst running {scriptName}; more information:\n    Require termination: {exit}\n   Show GUI: {showGUIMessage}\n    Error Code: {errCode}\n    Exit Code:{exit_code}'
    logRef.log(log_information, scriptName)
    if exit: ex_req = "; the application may not continue with said error and therefore will be terminated."
    else: ex_req = "; however, the error is not critical enough to require the termination of the application."
    if showGUIMessage: msb.showerror("Quizzing Application Error", f"An error occurred{ex_req}.\n\nDiagnostic Information:\n\n{errCode}")
    if exit: close(exit_code)

# Version File Variables + Loading + Checking
versionFilename = "qa_versionInfo.json"
VFKeys = {
    'au' : 'AuthorName',
    'v' : 'Version',
    'pro' : 'Product',
    'roam' : "Roaming"
}

qa_flags_ref = qaFlags.QAFlags()
try:
    versionData = qa_flags_ref.io(
        qa_flags_ref.GET,
        filename=versionFilename,
        key=None, # Return the entire thing
        reloadJSON=True,
        re_bool=False # Return the stored data
    )
    if not type(versionData) is dict: raise TypeError("Version Data Input was not {}; it was instead {}. INPUT: {}".format(dict, type(versionData), versionData))

except Exception as e:
    errorHandler(traceback.format_exc(), True, e.__class__.__name__, True)

# AppData Variables
appdataLoc = appdirs.user_data_dir(appauthor=versionData[VFKeys['au']],appname=versionData[VFKeys['pro']],version=str(versionData[VFKeys['v']]),roaming=bool(versionData[VFKeys['roam']]))
if not os.path.exists(appdataLoc):
    os.makedirs(appdataLoc)
    logRef.log("Created missing AppData DIRs", scriptName)

def log_isGen(): return [variablesRef.genDebugFile(), variablesRef.logFilename()]

# Filename varaibles
confFilename = "configuration.json"
readOnlyFilename = "disp.qaFile"
qasFilename = "qas.qaFile"
scoresFolderName = "Scores"
themeFilename = "theme.qaFile"

cdfn = 'codes.json'

codes_keys = {
    'incomplete_install': {
        'FTSRA': 'FTSRA_INCOMPLETE_FILES'
    }
}

exten = 'qaFile'

# FTSRA Variables
ftsFolder = "QAFTSRA"
QaFTSRAFiles = ("configuration.json", "qas.qaFile", "disp.qaFile", "theme.qaFile", "Scores")

# Flags File
global_nv_flags_fn = f"{appdataLoc}\\{qa_flags_ref.flags_fn}"

# Theme Variables
THEME: dict = themegetter.get('theme')
SuiteName: str = "Quizzing Application"
AppNames: dict = {
    'ftsra' : "First Time Setup + Recovery Agent\nUtility",
    'quf' : 'Quizzing Form',
    'adts' : 'Administrator Tools',
    'th' : 'Custom Theming Utility'
}
def getAppName(key: str): return AppNames[key] if key in AppNames else None

# Icons
icons_ico = {
    'tu': 'icons\\themer.ico',
    'ftsra': 'icons\\ftsra.ico',
    'admt': 'icons\\admin_tools.ico',
    'qt': 'icons\\quizzing_tool.ico'
}; icons_png  = {
    'tu': 'icons\\themer_64.png',
    'ftsra': 'icons\\ftsra_64.png',
    'admt': 'icons\\admin_tools_64.png',
    'qt': 'icons\\quizzing_tool_64.png'
}

help_files = {
    'ftsra': f"FTSRA_AID\\FTSRA_AID.pdf"
}

theme_presets: dict = {
    'Monochrome Dark': 'TU_MONOCHROME_DARK.qaFile',
    'Monochrome Light': 'TU_MONOCHROME_LIGHT.qaFile',
    'Dark': 'TU_DARK.qaFile',
    'Default': 'TU_DEFAULT.qaFile',
    'High Contrast': 'TU_HIGH_CONTRAST.qaFile'
}; theme_presets_foldername = 'TU_THEME_PRESETS'
