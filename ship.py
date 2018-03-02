class Ship:
    def __init__(self, length):
        self.length = length
        self.x = [0,1,2]
        self.y = [0,0,0]
        self.rotation = 0
        self.colliding = False

    def rotate(self):
        if self.length == 1:
            return
        new_x = self.x[:]
        new_y = self.y[:]
        if self.rotation == 0:
            new_x[0] += 1
            new_x[2] -= 1
            new_y[0] -= 1
            new_y[2] += 1
        elif self.rotation == 90:
            new_x[0] += 1
            new_x[2] -= 1
            new_y[0] += 1
            new_y[2] -= 1
        elif self.rotation == 180:
            new_x[0] -= 1
            new_x[2] += 1
            new_y[0] += 1
            new_y[2] -= 1
        elif self.rotation == 270:
            new_x[0] -= 1
            new_x[2] += 1
            new_y[0] -= 1
            new_y[2] += 1

        if self.rotation_invalid(new_x, new_y):
            return

        self.rotation =  (self.rotation + 90) % 360
        self.x = new_x
        self.y = new_y

    def rotation_invalid(self, new_x, new_y):
        return max(new_x[0:self.length]) > 7 or min(new_x[0:self.length]) < 0 or max(new_y[0:self.length]) > 3 or min(new_y[0:self.length]) < 0

    def move_right(self):
        if max(self.x[0:self.length]) == 7:
            return
        self.x[0] += 1
        self.x[1] += 1
        self.x[2] += 1
    
    def move_left(self):
        if min(self.x[0:self.length]) == 0:
            return
        self.x[0] -= 1
        self.x[1] -= 1
        self.x[2] -= 1

    def move_up(self):
        if min(self.y[0:self.length]) == 0:
            return
        self.y[0] -= 1
        self.y[1] -= 1
        self.y[2] -= 1
    
    def move_down(self):
        if max(self.y[0:self.length]) == 3:
            return
        self.y[0] += 1
        self.y[1] += 1
        self.y[2] += 1
    
    def check_collision(self,board):
        for i in range(self.length):
            if board[self.y[i]][self.x[i]]:
                self.colliding = True
                return
        self.colliding = False

    def place(self,board):
        if not self.colliding:
            for i in range(self.length):
                board[self.y[i]][self.x[i]] = 1
            self.length -= 1

    def draw(self, unicorn, board):
        self.check_collision(board)
        if self.colliding:
            for i in range(self.length):
                unicorn.set_pixel(self.x[i],self.y[i],255,0,0)
        else:
            for i in range(self.length):
                unicorn.set_pixel(self.x[i],self.y[i],255,255,255)  
