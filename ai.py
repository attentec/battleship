import random


class Ai:
    def __init__(self, width, height):
        self.moves = [[[y, x] for x in range(width)] for y in range(height)]

        random.shuffle(self.moves)

    def get_move(self, enemy_board):
        return self.moves.pop()

    @staticmethod
    def valid_pos(ship, ally_board):
        for pos in ship:
            if ally_board[pos[1]][pos[0]]:
                return False
        return True

    @staticmethod
    def place_ship(ship, ally_board):
        for pos in ship:
            ally_board[pos[1]][pos[0]] = 1

    def place_ships(self, length, ally_board):
        while length > 0:
            rot = random.choice([0, 90])

            if rot == 0:
                x = random.randint(0, 8-length)
                y = random.randint(0, 3)
            else:
                x = random.randint(0, 7)
                y = random.randint(0, 4-length)

            ship = [[x+i, y] if rot == 0 else [x, y+i] for i in range(length)]
        
            if self.valid_pos(ship, ally_board):
                self.place_ship(ship, ally_board)
                length = length - 1
