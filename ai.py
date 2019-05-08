import random


class Ai:
    def __init__(self, width, height):
        self.moves = []
        for y in range(height):
            for x in range(width):
                self.moves.append([y, x])
        self.width = width
        self.height = height

        random.shuffle(self.moves)

    def get_move(self, enemy_board):
        return self.moves.pop()

    def place_ships(self, ships, valid_pos, place_ship):
        index = 0
        while index < len(ships):
            rot = random.choice([0, 90])

            if rot == 0:
                x = random.randint(0, self.width-ships[index])
                y = random.randint(0, self.height - 1)
            else:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - ships[index])

            ship = [[x+i, y] if rot == 0 else [x, y+i] for i in range(ships[index])]
        
            if valid_pos(ship):
                place_ship(ship)
                index = index + 1
