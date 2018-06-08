from time import sleep


class Battleship:
    def __init__(self, height, width, ships, display, connection, is_host):
        self.height = height
        self.width = width
        self.ships = ships
        self.display = display
        self.is_host = is_host
        self.ai = None
        self.connection = connection
        if is_host:
            self.waiting = False
        else:
            self.waiting = True

        self.waiting_for_rematch = False
        self.enemy_board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.ally_board = [[0 for _ in range(self.width)] for _ in range(self.height)]

    @staticmethod
    def get_color(color):
        """
        0: black,
        1: green,
        2: red,
        3: blue,
        other: black
        :param color: Int representing a color
        :return: (r, g, b)
        """
        if color == 0:
            return 0, 0, 0
        elif color == 1:
            return 0, 255, 0
        elif color == 2 or color == 4:
            return 255, 0, 0
        elif color == 3:
            return 0, 0, 255
        else:
            return 0, 0, 0

    def draw_board(self, board):
        """
        Draw board on self.display
        """
        for y in range(len(board)):
            for x in range(len(board[y])):
                r, g, b = self.get_color(board[y][x])
                self.display.set_pixel(x, y, r, g, b)

    def draw_ally_board(self):
        self.draw_board(self.ally_board)

    def draw_enemy_board(self):
        self.draw_board(self.enemy_board)

    def draw_victory_board(self):
        self.draw_board([[1 for _ in range(self.width)] for _ in range(self.height)])

    def draw_loser_board(self):
        self.draw_board([[2 for _ in range(self.width)] for _ in range(self.height)])

    def reset(self):
        self.enemy_board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.ally_board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.waiting_for_rematch = False

    def blink_and_set(self, board, x, y, value):
        for i in range(1, 9):
            board[y][x] = value if i % 2 else 0
            self.draw_board(board)
            self.display.show()
            sleep(0.2)
        board[y][x] = value

    def send_missile(self, cursor_x, cursor_y):
        self.connection.send_data([cursor_y, cursor_x])
        response = self.connection.receive_data()
        self.blink_and_set(self.enemy_board, cursor_x, cursor_y, response)
        if response == 4:
            self.draw_victory_board()
            self.display.show()
            sleep(4)
            if self.is_host:
                sleep(1)
            self.waiting_for_rematch = True
            self.enemy_board[cursor_y][cursor_x] = response
        self.waiting = True

    def await_incoming(self):
        y, x = self.connection.receive_data()
        lost = False
        if self.ally_board[y][x] == 1:
            res = 2
            self.ally_board[y][x] = 2
            lost = self.has_lost()
        else:
            res = 3

        if lost:
            self.connection.send_data(4)
            self.blink_and_set(self.ally_board, x, y, res)
            self.draw_loser_board()
            self.display.show()
            sleep(4)
            if self.is_host:
                sleep(2)
            self.waiting_for_rematch = True
        else:
            self.connection.send_data(res)
            self.blink_and_set(self.ally_board, x, y, res)
        self.waiting = False

    def has_lost(self):
        for y in range(len(self.ally_board)):
            for x in range(len(self.ally_board[y])):
                if self.ally_board[y][x] == 1:
                    return False
        return True
