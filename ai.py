import random

class Ai:
    def __init__(self):
        self.moves = [
            [0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7],
            [1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6], [1, 7],
            [2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6], [2, 7],
            [3, 0], [3, 1], [3, 2], [3, 3], [3, 4], [3, 5], [3, 6], [3, 7]
        ]

        random.shuffle(self.moves)

    def get_move(self):
        return self.moves.pop()

    def valid_pos(self, ship, ally_board):
        for pos in ship:
            if ally_board[pos[1]][pos[0]]:
                return False
        return True

    def place_ship(self, ship, ally_board):
        for pos in ship:
            ally_board[pos[1]][pos[0]] = 1

    def place_random_ships(self, len, ally_board):
        while len > 0:
            rot = random.choice([0,90])

            if rot == 0:
                x = random.randint(0,8-len)
                y = random.randint(0,3)
            else:
                x = random.randint(0,7)
                y = random.randint(0,4-len)

            ship = [[x+i,y] if rot == 0 else [x,y+i] for i in range(len)]
        
            if self.valid_pos(ship, ally_board):
                self.place_ship(ship, ally_board)
                len = len - 1