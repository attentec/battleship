"""File containing the Ship class used for placement of the ships."""


class Ship:
    """Class for handling ships."""

    def __init__(self, ships, w, h):
        """Initialize ships."""
        self.ships = ships[:]
        self.index = 0
        self.length = ships[self.index]
        self.width = w
        self.height = h
        self.x = [x for x in range(self.length)]
        self.y = [0 for _ in range(self.length)]
        self.rotation = 0
        self.colliding = False

    def rotate(self):
        """Rotate ship if possible."""
        if self.length == 1:
            return
        new_x = self.x[:]
        new_y = self.y[:]
        if self.rotation == 0:
            for index, y in enumerate(range(self.y[0], self.y[0] + self.length)):
                new_y[index] = y
                new_x[index] = self.x[0]
        elif self.rotation == 90:
            for index, x in enumerate(range(self.x[0], self.x[0] + self.length)):
                new_y[index] = self.y[0]
                new_x[index] = x
        if self.rotation_invalid(new_x, new_y):
            return

        self.rotation = (self.rotation + 90) % 180
        self.x = new_x
        self.y = new_y

    def rotation_invalid(self, new_x, new_y):
        """Check if rotation is invalid."""
        return max(new_x) > self.width - 1 or min(new_x) < 0 or max(new_y) > self.height - 1 or min(new_y) < 0

    def move_right(self):
        """Move ship right if possible."""
        if max(self.x[0:self.length]) == self.width - 1:
            return
        for x in range(self.length):
            self.x[x] += 1

    def move_left(self):
        """Move ship left if possible."""
        if min(self.x[0:self.length]) == 0:
            return
        for x in range(self.length):
            self.x[x] -= 1

    def move_up(self):
        """Move ship up if possible."""
        if min(self.y[0:self.length]) == 0:
            return
        for y in range(self.length):
            self.y[y] -= 1

    def move_down(self):
        """Move ship down if possible."""
        if max(self.y[0:self.length]) == self.height - 1:
            return
        for y in range(self.length):
            self.y[y] += 1

    def check_collision(self, board):
        """Check for collisions and set collision variable."""
        for i in range(self.length):
            if board[self.y[i]][self.x[i]]:
                self.colliding = True
                return
        self.colliding = False

    def place(self, board):
        """Place ship."""
        if not self.colliding:
            for i in range(self.length):
                board[self.y[i]][self.x[i]] = 1
            self.index += 1
            if self.index < len(self.ships):
                self.length = self.ships[self.index]

    def draw(self, unicorn, board):
        """Draw ship."""
        self.check_collision(board)
        if self.colliding:
            for i in range(self.length):
                unicorn.set_pixel(self.x[i], self.y[i], 255, 0, 0)
        else:
            for i in range(self.length):
                unicorn.set_pixel(self.x[i], self.y[i], 255, 255, 255)
