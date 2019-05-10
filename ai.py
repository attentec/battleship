"""File containing the AI."""
import random


class Ai:
    """Basic example of a battleship AI."""

    def __init__(self, width, height, display):
        """
        Initialize the AI providing the width, height and what display is used.

        :param width: Width of the game plan
        :param height: Height of the game plan
        :param display: -1 = no display, 0 = terminal, other = RPI
        """
        self.moves = []
        for y in range(height):
            for x in range(width):
                self.moves.append([y, x])
        self.width = width
        self.height = height
        self.enable_logging = False
        if display == -1:
            self.enable_logging = True

        random.shuffle(self.moves)

    def get_move(self, enemy_board):
        """
        Get next coordinates to fire at the opponent at.

        :param enemy_board: The known data about the enemy board.
        :return: The coordinates to fire at as a list [y, x]
        """
        if self.enable_logging:
            print(enemy_board)
        return self.moves.pop()

    def place_ships(self, ships, valid_pos, place_ship):
        """
        Place the ships.

        :param ships: List of ship length to place
        :param valid_pos: Function to validate that the position is valid.
        :param place_ship: Function to place the ship.
        :return:
        """
        index = 0
        while index < len(ships):
            rot = random.choice([0, 90])

            if rot == 0:
                x = random.randint(0, self.width - ships[index])
                y = random.randint(0, self.height - 1)
            else:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - ships[index])

            ship = [[x + i, y] if rot == 0 else [x, y + i] for i in range(ships[index])]

            if valid_pos(ship):
                place_ship(ship)
                index = index + 1
