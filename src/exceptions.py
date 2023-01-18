class FilesException(Exception):
    def __init__(self, code: str, detail: str, message: str):
        self.code = code
        self.detail = detail
        self.message = message
