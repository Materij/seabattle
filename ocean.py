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
        # занятые кораблем точки либо точки куда мы уже стреляли
        self.busy = []
        # пустой список кораблей (позже список начнет пополняться с помощью специального метода)
        self.ships = []

    # вывод корабля на доску
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"
        # параметр, который показывет, нужно ли скрывать корабли на доске
        if self.hide:
            res = res.replace("■", "O")
        return res

    # метод, который проверяет находится ли точка за пределами доски
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # контур корабля
    def contour(self, ship, verb = False): # verb - параметр, который показывает нужно ли ставить точки вокруг кораблей
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy: # если точка не выходит за границы доски и еще не занята -
                    if verb:
                        self.field[cur.x][cur.y] = "." # тогда ставим на её месте символ точки и
                    self.busy.append(cur)              # добавляем её в список занятых точек (показываем, что
                                                       # точка занята (т.е. мы пока прячем контур корабля до игры))

    # добавление корабля на доску
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy: # проверка выходит ли точка корабля за границы и не занята ли
                raise BoardWrongShipException() # выбрасываем исключение
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d) # точки, в которых находится корабль или которые с ним соседствуют

        self.ships.append(ship)
        self.contour(ship)

    # стрельба на доске
    def shot(self, d): # делаем выстрел
        if self.out(d): # проверяем, выходит ли точка за грницы, если выходит -
            raise BoardOutException() # то выбрасываем исключение

        if d in self.busy: # проверяем, занята ли точка, если занята -
            raise BoardUsedException() # то выбрасываем исключение

        self.busy.append(d) # говорим, что точка у нас занята, если до этого момента не была занята

        for ship in self.ships: # проходимся по циклу и проверяем, принадлежит ли точка какому-то кораблю или нет
            if ship.shooten(d):  # если корабль подстрелен этой точкой,
                ship.lives -= 1 # тогда уменьшаем количество жизней корабля
                self.field[d.x][d.y] = "X" # затем ставим в эту точку "X"
                if ship.lives == 0: # если корабль уничтожен,
                    self.count += 1 # тогда прибавляем к счетчику уничтоженных кораблей единицу
                    self.contour(ship, verb=True) # после контур корабля обозначается точками
                    print("Корабль уничтожен!")
                    return False # показываем, что дальше не нужно делать ход, т.к. корабль уничтожен
                else:
                    print("Корабль ранен!")
                    return True # проходимся дальше по циклу (повторяем ход), если количество жизней не нулевое

        self.field[d.x][d.y] = "." # если ни один корабль не был поражен, тогда ход выполняется и ставится "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = [] # сохраняем точки, куда стрелял игрок

# класс "Игрок"
class Player:
    def __init__(self, board, enemy): # передаем в качестве аргументов две доски:
        self.board = board # свою
        self.enemy = enemy # компьютера

    def ask(self): # мы не вызываем этот метод, а показываем, что он должен быть у потомков этого класа
        raise NotImplementedError()

    def move(self): # стараемся в бесконечном цикле сделать выстрел
        while True:
            try:
                target = self.ask() # просим компьютер или пользователя дать координату выстрела
                repeat = self.enemy.shot(target) # выполняем выстрел и если попали -
                return repeat # повторяем ход
            except BoardException as e: # если мы выстрелили плохо, то мы попадаем под исключение и поторяем ход
                print(e)                # (работу цикла)

# класс игрок-компьютер
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5)) # случайно генерируем две точки от 0 до 5
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d

# класс игрок-пользователь
class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split() # запрос координат

            if len(cords) != 2: # проверяем, чтобы две функции были введены
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not(x.isdigit()) or not (y.isdigit()): # проверяем, то что введены числа
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1) # возвращаем нашу точку не забыв вычесть единицу, т.к. индексация
                                     # начинается с нуля, а пользователю показывается единица

# класс игра (генерируем доски, заполненные кораблями)
class Game:
    def __init__(self, size=6): # задаем размер доски
        self.size = size
        pl = self.random_board() # генерируем случайную доску для игрока
        co = self.random_board() # генерируем случайную доску для компьютера
        co.hide = True # скрываем корабли для компьютера

        self.ai = AI(co, pl) # создаем игрока компьютеру
        self.us = User(pl, co) # создаем игрока пользователю

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1] # указываем длины кораблей
        board = Board(size=self.size) # создаем доску
        attempts = 0
        for l in lens: # для корабля каждой длины стараемся его поставить на доску
            while True:
                attempts += 1
                if attempts > 2000: # количество попыток поставить корабли
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship) # добавляем корабли
                    break
                except BoardWrongShipException: # в случае если попытка неудачная - возвращаемся к циклу заново
                    pass
        board.begin() # подготавливаем готовую доску к игре
        return board # после того, как мы расставили все корабли - возвращаем доску

    # метод, который гарантированно генерирует случайную доску, т.к. попытка создания может быть неуспешной
    def random_board(self):
        board = None # вот, та самая неуспешная попытка
        while board is None: # теперь пытаемся ее создать в бесконечном цикле
            board = self.try_board()
        return board

    def greet(self):
        print("**********************")
        print("   Приветствуем Вас   ")
        print("       в игре         ")
        print("     морской бой      ")
        print("**********************")
        print("  формат ввода: x, y  ")
        print("   x - номер строки   ")
        print("   y - номер столбца  ")

    # запускаем игрвой цикл
    def loop(self):
        num = 0 # заводим ноер хода
        while True:
            print("-" * 20)
            print("Доска пользователя") # выводим доску пользователя
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера") # выводим доску компьютера
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!") # если номер хода четный
                repeat = self.us.move() # метод, отвечающий за ход каждого игрока
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1 # в случае попадания оставляем ход тому же игроку

            # проверка количества пораженных кораблей
            if self.ai.board.count == 7: # равносильна количеству пораженных кораблей на доске
                                         # self.ai.board.count == len(self.ai.board.ships):
                print("-" * 20)
                print("Пользователь выиграл!")
                break
            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    # метод start
    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()
