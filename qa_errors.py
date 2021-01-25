stem = "QuizzingApplicationError:"

class FileIO_NoBackup(Exception):
    def __init__(self, Filename: str = "Unknown File", ErrInfo: str = "Unknown Error"):
        self.ErrInfo = ErrInfo
        self.filename = Filename

    def __str__(self):
        global stem
        return f'{stem} Unable to create backup for file {self.filename}; unsafe to continue. Original error: {self.ErrInfo}'

class UnsupportedType(Exception):
    def __init__(self, got: type, *expected):
        self.got = got
        self.expected = expected

    def __str__(self):
        global stem
        return f"{stem} Unsupported Data Type: Expected: {self.expected}; Got: {self.got}"

class RestorationFailed(Exception):
    def __init__(self, FileIOObject: object):
        self.filename = FileIOObject.filename
        self.id = FileIOObject.id

    def __str__(self):
        global stem
        return f"{stem} Failed to restore to (automatic) backup after a failed operation; filename = {self.filename}, objectID = {self.id}"
