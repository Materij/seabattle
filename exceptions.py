class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "You try to shoot the board"

class BoardUsedException(BoardException):
    def __str__(self):
        return "You already shot that cage"

class BoardWrongShipException(BoardException):
    pass
