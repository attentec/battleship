#!/usr/bin/env python3
from time import sleep
import unicornhat as unicorn
import sys
import curses
from comunication import Connection
from ship import Ship

unicorn.set_layout(unicorn.PHAT)
unicorn.rotation(180)
unicorn.brightness(0.5)

enemy_board = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0]
]

ally_board = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0]
]

cursorX = 0
cursorY = 0

enemy_ip = ""
enemy_turn = False
is_host = False
waiting = True
connection = None
ship = Ship(3)

vic_board = [
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0]
    ]

los_board = [
        [0, 0, 2, 0, 0, 2, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 2, 2, 2, 2, 0, 0],
        [0, 2, 0, 0, 0, 0, 2, 0]
    ]


def reset():
    global enemy_board, ally_board, cursorX, cursorY, enemy_turn, waiting, setup, ship
    enemy_board = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    ally_board = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ]

    cursorX = 0
    cursorY = 0

    enemy_turn = False
    waiting = True
    setup = True
    ship = Ship(3)


def rematch():
    play_rematch = input("Rematch? [y/n] ")
    if play_rematch.upper() == "Y":
        connection.send_data(True)
        response = connection.receive_data()
        if response:
            reset()
        else:
            print("Opponent quit")
            exit(0)
    else:
        connection.send_data(False)
        connection.close_connection()
        exit(0)


def blink_and_set(board, x, y, value):
    for i in range(1, 9):
        board[y][x] = value if i % 2 else 0
        draw_board(board)
        unicorn.show()
        sleep(0.2)
    board[y][x] = value


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
    elif color == 2:
        return 255, 0, 0
    elif color == 3:
        return 0, 0, 255
    else:
        return 0, 0, 0


def draw_board(board):
    """
    Draw board on unicorn
    """
    for y in range(len(board)):
        for x in range(len(board[y])):
            r, g, b = get_color(board[y][x])
            unicorn.set_pixel(x, y, r, g, b)


def send_missile():
    global cursorX, cursorY, connection, waiting
    connection.send_data([cursorY, cursorX])
    response = connection.receive_data()
    if response == 4:
        draw_board(vic_board)
        unicorn.show()
        sleep(4)
        if is_host:
            sleep(1)
        rematch()
    enemy_board[cursorY][cursorX] = response
    waiting = True
    blink_and_set(enemy_board, cursorX, cursorY, response)


def await_incoming():
    global connection, waiting
    y, x = connection.receive_data()
    lost = False
    if ally_board[y][x] == 1:
        res = 2
        ally_board[y][x] = 2
        lost = has_lost()
    else:
        res = 3

    if lost:
        connection.send_data(4)
        blink_and_set(ally_board, x, y, res)
        draw_board(los_board)
        unicorn.show()
        sleep(4)
        if is_host:
            sleep(2)
        rematch()
    else:
        connection.send_data(res)
        blink_and_set(ally_board, x, y, res)
    waiting = False


def has_lost():
    for y in range(len(ally_board)):
        for x in range(len(ally_board[y])):
            if ally_board[y][x] == 1:
                return False
    return True

def place_ships(win):
    while (ship.length):
        sleep(0.1)
        key = win.getch()
        unicorn.clear()
        if key == curses.KEY_DOWN:
            ship.move_down()
        elif key == curses.KEY_UP:
            ship.move_up()
        elif key == curses.KEY_RIGHT:
            ship.move_right()
        elif key == curses.KEY_LEFT:
            ship.move_left()
        elif key == 114:  # R
            ship.rotate()
        elif key == 32:  # Space
            ship.place(ally_board)
        draw_board(ally_board)
        ship.draw(unicorn, ally_board)
        unicorn.show()
        

def main(win):
    global cursorX, cursorY, enemy_board, ally_board, enemy_ip, enemy_turn, is_host, waiting, ship

    win.nodelay(True)

    place_ships(win)
    
    while True:
        sleep(0.1)    
        key = win.getch()
        unicorn.clear()
        if key == curses.KEY_DOWN and cursorY < 3:
            cursorY += 1
        elif key == curses.KEY_UP and cursorY > 0:
            cursorY -= 1
        elif key == curses.KEY_RIGHT and cursorX < 7:
            cursorX += 1
        elif key == curses.KEY_LEFT and cursorX > 0:
            cursorX -= 1
        elif key == 32 and not waiting and enemy_board[cursorY][cursorX] == 0:  # Space
            send_missile()
        draw_board(enemy_board)
        unicorn.set_pixel(cursorX,cursorY,255,255,255)

        if waiting:
            draw_board(ally_board)
            unicorn.show()
            await_incoming()
            curses.flushinp()
        unicorn.show()


def init_game():
    global is_host, enemy_ip, waiting, connection
    if len(sys.argv) == 1:
        is_host_input = input("Host? [y/n] ")
        if is_host_input.upper() == "Y":
            is_host = True
        if not is_host:
            enemy_ip = input("Enemy ip: ")
    elif len(sys.argv) == 2 and sys.argv[1].lower() == "host":
        is_host = True
    elif len(sys.argv) == 2 and sys.argv[1].lower() == "client":
        print("You must provide an ip-address to the host")
        exit(1)
    elif len(sys.argv) == 3 and sys.argv[1].lower() == "client":
        enemy_ip = sys.argv[2]
    else:
        print("Unknown argument provided")
        exit(1)

    if is_host:
        waiting = False
        connection = Connection("0.0.0.0", False)
    else:
        try:
            connection = Connection(enemy_ip, True)
        except ConnectionRefusedError:
            print("No host found at: {}".format(enemy_ip))
            exit(2)
        except OSError:
            print("Invalid ip-address.")
            exit(2)
    try:
        curses.wrapper(main)
    except EOFError:
        print("Opponent disconnected")
        connection.close_connection()
        exit(0)


if __name__ == '__main__':
    try:
        init_game()
    except KeyboardInterrupt:
        print("\n\nBye")
        exit(0)
