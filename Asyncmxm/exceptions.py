class MXMException(Exception):

    codes = {
        400: "The request had bad syntax or was inherently impossible to be satisfied.",
        401: "Authentication failed, probably because of invalid/missing API key.",
        402: "The usage limit has been reached, either you exceeded per day requests limits or your balance is insufficient.",
        403: "You are not authorized to perform this operation.",
        404: "The requested resource was not found.",
        405: "The requested method was not found.",
        500: "Ops. Something were wrong.",
        503: "Our system is a bit busy at the moment and your request can't be satisfied."
    }


    def __init__(self,status_code, message):
        self.status_code = status_code
        if message:
            self.message = message
        else:
            self.message = self.codes.get(status_code) or "Unknown Error"

    
    def __str__(self):
        return f"Error code: {self.status_code} - message: {self.message}"