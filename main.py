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
setup = True
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
            sleep(2)
        connection.close_connection()
        exit(0)
    enemy_board[cursorY][cursorX] = response
    waiting = True
    for i in range(0, 4):
        enemy_board[cursorY][cursorX] = response
        draw_board(enemy_board)
        unicorn.show()
        sleep(0.2)
        enemy_board[cursorY][cursorX] = 0
        draw_board(enemy_board)
        unicorn.show()
        sleep(0.2)
    enemy_board[cursorY][cursorX] = response


def await_incomming():
    global connection, waiting
    coordinates = connection.receive_data()
    lost = False
    if ally_board[coordinates[0]][coordinates[1]] == 1:
        res = 2
        ally_board[coordinates[0]][coordinates[1]] = 2
        lost = has_lost()
    else:
        res = 3
    if lost:
        connection.send_data(4)
        draw_board(los_board)
        unicorn.show()
        sleep(4)
        if is_host:
            sleep(2)
        connection.close_connection()
        exit(0)
    else:
        connection.send_data(res)
    waiting = False
    for i in range(0, 4):
        ally_board[coordinates[0]][coordinates[1]] = res
        draw_board(ally_board)
        unicorn.show()
        sleep(0.2)
        ally_board[coordinates[0]][coordinates[1]] = 0
        draw_board(ally_board)
        unicorn.show()
        sleep(0.2)
    ally_board[coordinates[0]][coordinates[1]] = res


def has_lost():
    for y in range(len(ally_board)):
        for x in range(len(ally_board[y])):
            if ally_board[y][x] == 1:
                return False
    return True


def main(win):
    global cursorX, cursorY, enemy_board, ally_board, enemy_ip, enemy_turn, is_host, waiting, ship, setup
    
    win.nodelay(True)

    while True:
        sleep(0.1)    
        key = win.getch()
        unicorn.clear()
        if setup:
            if key == curses.KEY_DOWN:
                ship.move_down()
            elif key == curses.KEY_UP:
                ship.move_up()
            elif key == curses.KEY_RIGHT:
                ship.move_right()
            elif key == curses.KEY_LEFT:
                ship.move_left()
            elif key == 114:  # r
                ship.rotate()
            elif key == 32:  # Space
                if ship.place(ally_board):
                    ship.length -= 1
                    if ship.length == 0:
                        setup = False
            draw_board(ally_board)
            ship.draw(unicorn, ally_board)
        else:
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
                await_incomming()
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
    except:
        connection.close_connection()


if __name__ == '__main__':
    try:
        init_game()
    except KeyboardInterrupt:
        print("\n\nBye")
        exit(0)
