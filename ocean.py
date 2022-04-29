from random import randint

from exceptions import BoardException, BoardUsedException, BoardWrongShipException

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hide = False, size = 6):
        self.hide = hide
        self.size = size

        self.count = 0

        self.field = [["O"]*size for _ in range(size)]
        # points occupied by the ship or points where we have already shot
        self.busy = []
        # empty list of ships (later the list will be filled using a special method)
        self.ships = []

    # bringing the ship to the board
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
        # a parameter that shows whether ships should be hidden on the board
        if self.hide:
            res = res.replace("■", "O")
        return res

    # a method that checks if a point is outside the board
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # ship outline
    def contour(self, ship, verb = False): # verb - a parameter that indicates whether it is necessary to put dots around the ships
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy: # if the point does not go beyond the boundaries of the board and is not yet occupied -
                    if verb:
                        self.field[cur.x][cur.y] = "." # then put a dot in its place and
                    self.busy.append(cur)              # add it to the list of busy points (show that the point
                                                       # is occupied (that is, we are still hiding the contour of the ship before the game))

    # adding a ship to the board
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy: # checking if the ship's point goes beyond the boundaries and is not busy
                raise BoardWrongShipException() # throw an exception
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d) # points where the ship is located or which are adjacent to it

        self.ships.append(ship)
        self.contour(ship)

    # board shooting
    def shot(self, d): # take a shot
        if self.out(d): # check if the point is out of bounds, if it goes out -
            raise BoardOutException() # then throw an exception

        if d in self.busy: # check if the point is occupied, if it is occupied -
            raise BoardUsedException() # then throw an exception

        self.busy.append(d) # we say that the point is occupied if it has not been occupied until this moment

        for ship in self.ships: # go through the loop and check if the point belongs to some ship or not
            if ship.shooten(d):  # if the ship is hit by this point,
                ship.lives -= 1 # then we reduce the number of ship's lives
                self.field[d.x][d.y] = "X" # then put "X" at that point
                if ship.lives == 0: # if the ship is destroyed,
                    self.count += 1 # then add one to the counter of destroyed ships
                    self.contour(ship, verb=True) # after the contour of the ship is indicated by dots
                    print("Ship destroyed!")
                    return False # we show that there is no need to make a move further, because ship destroyed
                else:
                    print("Ship injured!")
                    return True # we go further through the cycle (repeat the move), if the number of lives is non-zero

        self.field[d.x][d.y] = "." # if no ship was hit, then the move is made and "." is placed
        print("Past!")
        return False

    def begin(self):
        self.busy = [] # save the points where the player shot

# class "Player"
class Player:
    def __init__(self, board, enemy): # passing two boards as arguments:
        self.board = board # our's
        self.enemy = enemy # computer's

    def ask(self): # we do not call this method, but show that descendants of this class should have it
        raise NotImplementedError()

    def move(self): # we try to make a shot in an endless loop
        while True:
            try:
                target = self.ask() # ask the computer or user to give the coordinate of the shot
                repeat = self.enemy.shot(target) # we shoot and if we hit -
                return repeat # we repeat the move
            except BoardException as e: # if we shot badly, then we get an exception and repeat the move
                print(e)                # (the cycle work)

# "Player-Computer" class
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5)) # randomly generate two points from 0 to 5
        print(f"Computer's turn: {d.x + 1} {d.y + 1}")
        return d

# User-Player" class
class User(Player):
    def ask(self):
        while True:
            cords = input("Your turn: ").split() # coordinate request

            if len(cords) != 2: # check that two functions have been entered
                print(" Enter 2 coordinates! ")
                continue

            x, y = cords

            if not(x.isdigit()) or not (y.isdigit()): # check that numbers are entered
                print(" Enter numbers! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1) # we return our point without forgetting to subtract one, because
                                     # indexing starts from zero, and the user is shown one

# class "Game" (generate boards filled with ships)
class Game:
    def __init__(self, size=6): # set board size
        self.size = size
        pl = self.random_board() # generate a random board for the player
        co = self.random_board() # generate random board for computer
        co.hide = True # hide ships for computer

        self.ai = AI(co, pl) # create a computer player
        self.us = User(pl, co) # create player for user

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1] # indicate the length of the ships
        board = Board(size=self.size) # create a board
        attempts = 0
        for l in lens: # for a ship of each length, we try to put it on the board
            while True:
                attempts += 1
                if attempts > 2000: # number of attempts to set ships
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship) # add ships
                    break
                except BoardWrongShipException: # if the attempt is unsuccessful - we return to the cycle again
                    pass
        board.begin() # preparing the finished board for the game
        return board # after we have placed all the ships - we return the board

    # method that is guaranteed to generate a random board, because creation attempt may fail
    def random_board(self):
        board = None # here is the failed attempt
        while board is None: # now we are trying to create it in an infinite loop
            board = self.try_board()
        return board

    def greet(self):
        print("**********************")
        print("       Welcome        ")
        print("     to the game      ")
        print("      sea battle      ")
        print("**********************")
        print("  input format: x, y  ")
        print("   x - line number    ")
        print("   y - column number  ")

    # start the game loop
    def loop(self):
        num = 0 # enter move number
        while True:
            print("-" * 20)
            print("User Board") # display the user's board
            print(self.us.board)
            print("-" * 20)
            print("Computer board") # take out the computer board
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("User move!") # if the move number is even
                repeat = self.us.move() # method responsible for each player's move
            else:
                print("Computer move!")
                repeat = self.ai.move()
            if repeat:
                num -= 1 # in case of hit, leave the move to the same player

            # checking the number of ships hit
            if self.ai.board.count == 7: # it is equivalent to the number of ships hit on the board
                                         # self.ai.board.count == len(self.ai.board.ships):
                print("-" * 20)
                print("User won!")
                break
            if self.us.board.count == 7:
                print("-" * 20)
                print("Computer won!")
                break
            num += 1

    # method "start"
    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()
