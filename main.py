#!/usr/bin/env python3
import argparse
import curses
import sys
from time import sleep
from comunication import Connection
from ship import Ship
from battelship import Battleship

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--host', action="store_true")
parser.add_argument('--client', type=str, help='host ip', dest='ip', default=None)
parser.add_argument('--display', action="store_true")
parser.add_argument('--ai', dest='ai', type=str, nargs='?', default='not_set')
parser.add_argument('--no-display', dest='no_display', action="store_true")
parser.add_argument('--port', dest='port', type=int, default=5000)
parser.add_argument('--width', dest='width', type=int, default=8)
parser.add_argument('--height', dest='height', type=int, default=4)
parser.add_argument('-s', '--ships', dest='ships', nargs='*', type=int)

KEY_Y = 121
KEY_N = 110
KEY_R = 114
KEY_SPACE = 32
KEY_ESC = 27

args = parser.parse_args()
is_unicorn = False
try:
    if args.no_display:
        import empty_display as display
    elif not args.display:
        import unicornhat as display
        is_unicorn = True
        if args.width > 8 or args.height > 4:
            print("Unsupported size")
            exit(2)
    else:
        import display as display
except ImportError:
    import display as display

display.set_layout(display.PHAT)
display.rotation(180)
display.brightness(0.5)
height = 0
width = 0
ships = []

cursorX = 0
cursorY = 0

enemy_ip = ""
is_host = False
is_ai = False
ai = None
connection = None
game = None


def place_ships(win):
    ship = Ship(game.ships, game.width, game.height)
    if is_ai:
        ai.place_ships(ships, game.valid_pos, game.place_ship)
        game.draw_ally_board()
        display.show()
        return

    while ship.index < len(ships):
        sleep(0.1)
        key = win.getch()
        display.clear()
        if key == curses.KEY_DOWN:
            ship.move_down()
        elif key == curses.KEY_UP:
            ship.move_up()
        elif key == curses.KEY_RIGHT:
            ship.move_right()
        elif key == curses.KEY_LEFT:
            ship.move_left()
        elif key == KEY_R:
            ship.rotate()
        elif key == KEY_SPACE:
            ship.place(game.ally_board)
        game.draw_ally_board()
        ship.draw(display, game.ally_board)
        display.show()


def main(win):
    global ai, game, cursorX, cursorY, is_host

    if is_ai:
        ai_module = __import__(args.ai.replace('.py', '') if args.ai is not None else 'ai')
        ai = ai_module.Ai(width, height)

    game = Battleship(height, width, ships, display, connection, is_host)

    try:
        display.set_window(win, width, height)
    except AttributeError:
        pass
    win.nodelay(True)

    place_ships(win)

    while True:
        if not is_ai:
            sleep(0.1)
            key = win.getch()
            display.clear()
            if key == curses.KEY_DOWN and cursorY < height - 1:
                cursorY += 1
            elif key == curses.KEY_UP and cursorY > 0:
                cursorY -= 1
            elif key == curses.KEY_RIGHT and cursorX < width - 1:
                cursorX += 1
            elif key == curses.KEY_LEFT and cursorX > 0:
                cursorX -= 1
            elif key == KEY_SPACE and not game.waiting and game.enemy_board[cursorY][cursorX] == 0:
                game.send_missile(cursorX, cursorY)
            elif key == KEY_ESC:
                connection.close_connection()
                exit(0)
            game.draw_board(game.enemy_board)
            display.set_pixel(cursorX, cursorY, 255, 255, 255)
        elif not game.waiting:
            sleep(0.5)
            move = ai.get_move(game.enemy_board)
            game.send_missile(move[1], move[0])

        if game.waiting and not game.waiting_for_rematch:
            game.draw_ally_board()
            display.show()
            game.await_incoming()
            curses.flushinp()

        if game.waiting_for_rematch:
            print("Rematch? [y/n] ")
            while True:
                sleep(0.1)
                key = win.getch()
                if key == KEY_Y:
                    print("Waiting for opponent response...")
                    connection.send_data(True)
                    response = connection.receive_data()
                    if response:
                        game.reset()
                        break
                    else:
                        print("Opponent quit")
                        connection.close_connection()
                        sleep(2)
                        exit(0)
                elif key == KEY_N:
                    connection.send_data(False)
                    connection.close_connection()
                    exit(0)
            cursorX = 0
            cursorY = 0
            if is_ai:
                ai_module = __import__(args.ai.replace('.py', '') if args.ai is not None else 'ai')
                ai = ai_module.Ai(width, height)
            place_ships(win)
        display.show()


def init_game():
    global is_host, enemy_ip, connection, is_ai, width, height, ships
    if args.ai != 'not_set':
        is_ai = True

    if not args.host and not args.ip:
        is_host_input = input("Host? [y/n] ")
        if is_host_input.upper() == "Y":
            is_host = True
        if not is_host:
            enemy_ip = input("Enemy ip: ")
    elif args.host:
        is_host = True
        sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=args.height * 3 + 2, cols=args.width * 5 + 2))
        height = args.height
        width = args.width
        if args.ships:
            try:
                ships = [int(ship) for ship in args.ships]
            except ValueError:
                print("Unknown ship provided")
                exit(1)
        else:
            ships = [3, 2, 1]
    elif args.ip:
        enemy_ip = args.ip
    else:
        print("Unknown argument provided")
        exit(1)

    if is_host:
        connection = Connection("0.0.0.0", False, args.port)
        connection.send_data([width, height, ships])
        if not connection.receive_data():
            print("Unsupported size at client")
            exit(2)
    else:
        try:
            connection = Connection(enemy_ip, True, args.port)
            res = connection.receive_data()

            if is_unicorn and (res[0] > 8 or res[1] > 4):
                connection.send_data(False)
                print("Unsupported size")
                exit(2)
            else:
                connection.send_data(True)
                width = res[0]
                height = res[1]
                ships = res[2]
                sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=height * 3 + 2, cols=width * 5 + 2))
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
