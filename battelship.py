"""File containing the game mechanics of the battleship game."""
from time import sleep


class Battleship:
    def __init__(self, height, width, ships, display, connection, is_host, is_unicorn):
        """
        Initialize a game of battleship.

        :param height: Height of the game plan.
        :param width: Width of the game plan.
        :param ships: List of length of ships to use.
        :param display: Display to use
        :param connection: Connection to opponent.
        :param is_host: Is host?
        """
        self.height = height
        self.width = width
        self.ships = ships
        self.display = display
        self.is_host = is_host
        self.is_unicorn = is_unicorn
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
        Get the RGB representation of a color.

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

    def draw_board(self, board, offest = 0):
        """Draw board on the display."""
        for y in range(len(board)):
            for x in range(len(board[y])):
                r, g, b = self.get_color(board[y][x])
                self.display.set_pixel(x, y + offest, r, g, b)

    def draw_ally_board(self):
        """Draw the players board."""
        self.draw_board(self.ally_board)

    def draw_enemy_board(self):
        """Draw whats known about the enemy board."""
        self.draw_board(self.enemy_board)

    def draw_both_boards(self):
        """Draw both boards."""
        self.draw_board(self.enemy_board)
        self.draw_board(self.ally_board, self.height + 1)

    def draw_victory_board(self):
        """Draw a all green board to symbolise a game won."""
        self.draw_board([[1 for _ in range(self.width)] for _ in range(self.height)])

    def draw_loser_board(self):
        """Draw a all red board to symbolise a game lost."""
        self.draw_board([[2 for _ in range(self.width)] for _ in range(self.height)])

    def reset(self):
        """Reset the game boards."""
        self.enemy_board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.ally_board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.waiting_for_rematch = False

    def blink_and_set(self, board1, x, y, value, board2, offset1 = 0, offset2 = 0):
        """Blink and set the pixel at x, y on the provided board with the given value."""
        for i in range(1, 6):
            if not self.is_unicorn:
                self.draw_board(board2, offset1)
            board1[y][x] = value if i % 2 else 0
            self.draw_board(board1, offset2)
            self.display.show()
            sleep(0.2)
        board1[y][x] = value

    def send_missile(self, x, y):
        """Send missile at the opponent at x, y."""
        self.connection.send_data([y, x])
        response = self.connection.receive_data()
        if self.is_unicorn:
            self.blink_and_set(self.enemy_board, x, y, response)
        else:
            self.draw_ally_board()
            self.blink_and_set(self.enemy_board, x, y, response, self.ally_board, self.height + 1)
        if response == 4:
            self.draw_victory_board()
            self.print_message('You won!')
            self.display.show()
            sleep(3)
            if self.is_host:
                sleep(1)
            self.waiting_for_rematch = True
            self.enemy_board[y][x] = response
        self.waiting = True

    def await_incoming(self):
        """Await incoming missile from the opponent."""
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
            if self.is_unicorn:
                self.blink_and_set(self.ally_board, x, y, res)
            else:
                self.draw_enemy_board()
                self.blink_and_set(self.ally_board, x, y, res, self.enemy_board, 0, self.height + 1)

            self.draw_loser_board()            
            self.print_message('You lost!')
            self.display.show()
            sleep(3)
            if self.is_host:
                sleep(2)
            self.waiting_for_rematch = True
        else:
            self.connection.send_data(res)
            if self.is_unicorn:
                self.blink_and_set(self.ally_board, x, y, res)
            else:
                self.draw_enemy_board()
                self.blink_and_set(self.ally_board, x, y, res, self.enemy_board, 0, self.height + 1)

        self.waiting = False

    def has_lost(self):
        """Check if the player has lost."""
        for y in range(len(self.ally_board)):
            for x in range(len(self.ally_board[y])):
                if self.ally_board[y][x] == 1:
                    return False
        return True

    def valid_pos(self, ship):
        """Check if the ship position is a valid position."""
        for pos in ship:
            if self.ally_board[pos[1]][pos[0]]:
                return False
        return True

    def place_ship(self, ship):
        """Place ship on ally board."""
        for pos in ship:
            self.ally_board[pos[1]][pos[0]] = 1

    def print_message(self, message):
        if self.is_unicorn:
            print(message)
        else:
            self.display.draw_text(message)
