#!/usr/bin/env python3
import argparse
import sys
import curses
from time import sleep
from comunication import Connection
from ship import Ship
from ai import Ai
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--host', action="store_true")
parser.add_argument('--client', type=str, help='is client', dest='ip', default=None)
parser.add_argument('--display', action="store_true")
parser.add_argument('--ai', action="store_true")
parser.add_argument('--no-display', dest='no_display', action="store_true")

args = parser.parse_args()
try:
    if args.no_display:
        import empty_display as unicorn
    elif not args.display:
        import unicornhat as unicorn
    else:
        import display as unicorn
except ImportError:
    import display as unicorn

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
is_ai = False
waiting = True
waiting_for_rematch = False
connection = None
ship = Ship(3)
ai = Ai()

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


def reset(win):
    global enemy_board, ally_board, cursorX, cursorY, enemy_turn, waiting, setup, ship, waiting_for_rematch
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

    waiting_for_rematch = False
    ship = Ship(3)
    ai = Ai()
    place_ships(win)


def rematch(win):
    print("Rematch? [y/n] ")
    while True:
        sleep(0.1)
        key = win.getch()
        if key == 121:
            print("Waiting for opponent response...")
            connection.send_data(True)
            response = connection.receive_data()
            if response:
                reset(win)
                return
            else:
                print("Opponent quit")
                connection.close_connection()
                sleep(2)
                exit(0)
        elif key == 110:
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
    elif color == 2 or color == 4:
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
    global cursorX, cursorY, connection, waiting, waiting_for_rematch
    connection.send_data([cursorY, cursorX])
    response = connection.receive_data()
    blink_and_set(enemy_board, cursorX, cursorY, response)
    if response == 4:
        draw_board(vic_board)
        unicorn.show()
        sleep(4)
        if is_host:
            sleep(1)
        waiting_for_rematch = True
    enemy_board[cursorY][cursorX] = response
    waiting = True


def await_incoming():
    global connection, waiting, waiting_for_rematch
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
        waiting_for_rematch = True
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
    if is_ai:
        ai.place_random_ships(ship.length, ally_board)
        draw_board(ally_board)
        unicorn.show()
        return

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
    global cursorX, cursorY, enemy_board, ally_board, enemy_ip, enemy_turn, is_host, waiting, ship, waiting_for_rematch
    try:
        unicorn.set_window(win)
    except AttributeError:
        pass
    win.nodelay(True)

    place_ships(win)

    while True:
        if not is_ai:
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
        elif is_ai and not waiting:
            sleep(0.5)
            move = ai.get_move()
            cursorX = move[1]
            cursorY = move[0]
            send_missile()

        if waiting and not waiting_for_rematch:
            draw_board(ally_board)
            unicorn.show()
            await_incoming()
            curses.flushinp()

        if waiting_for_rematch:
            rematch(win)
        unicorn.show()


def init_game():
    global is_host, enemy_ip, waiting, connection, is_ai
    if args.ai:
        is_ai = True

    if not args.host and not args.ip:
        is_host_input = input("Host? [y/n] ")
        if is_host_input.upper() == "Y":
            is_host = True
        if not is_host:
            enemy_ip = input("Enemy ip: ")
    elif args.host:
        is_host = True
    elif args.ip:
        enemy_ip = args.ip
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
