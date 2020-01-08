#!/usr/bin/env python3
"""Main entry point for the Battleship game."""
import curses
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from time import sleep

from CustomErrors import CheatingDetected

from battelship import Battleship

from comunication import Connection

from ship import Ship

parser = ArgumentParser(
    description='The game of Battleship\n\n'
                'Rules:\n'
                'Before play begins, each player secretly arranges their ships on their primary\n'
                'grid.\n'
                'Each ship occupies a number of consecutive squares on the grid, arranged\n'
                'either horizontally or vertically.\n'
                'The number of squares for each ship is determined by the type of the ship.\n'
                'The ships cannot overlap, only one ship can occupy a given square in the grid.\n'
                'The types and numbers of ships allowed are the same for each player.\n'
                'After the ships have been positioned, the game proceeds in a series of rounds.\n'
                'In each round, each player takes a turn to announce a target square in the\n'
                'opponent\'s grid which is to be shot at.\n'
                'The opponent announces whether or not the square is occupied by a ship.\n'
                'If all of a player\'s ships have been sunk, their opponent wins.\n'
                '', formatter_class=RawTextHelpFormatter)

parser.add_argument('--host', help="Start as host", action="store_true")
parser.add_argument('--client', type=str, help='Start as client and connect to host ip', dest='ip', default=None)
parser.add_argument('--display', help="Run with terminal as display.", action="store_true")
parser.add_argument('--ai',
                    help="AI instead of human player.\n"
                         "Provide a file name to including the ai or leave blank\n"
                         "to use the default implementation.",
                    dest='ai', type=str, nargs='?', default='not_set')
parser.add_argument('--no-display', help="Run game without an display, useful for debugging.",
                    dest='no_display', action="store_true")
parser.add_argument('--port', help="Port to connect to on the remote host.", dest='port', type=int, default=5000)
parser.add_argument('--width', help="Width of game plan.", dest='width', type=int, default=8)
parser.add_argument('--height', help="Height of game plan.", dest='height', type=int, default=4)
parser.add_argument('--ships', help="Specify the ships wanted.\n"
                                    "Default: --ships 3 2 1", dest='ships', nargs='*', type=int)
parser.add_argument('--speed',
                    help="Speed up the animation between each turn by this factor.", dest='speed', type=int, default=1)

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
        import display
except ImportError:
    import display

display.set_layout(display.PHAT)
display.rotation(180)
display.brightness(0.5)
height = 0
width = 0
ships = []

cursor_x = 0
cursor_y = 0

enemy_ip = ""
is_host = False
is_ai = False
ai = None
connection = None
game = None


def place_ships(win):
    """
    Place ships.

    :param win: Window
    :return: None
    """
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
            ship.place(game.place_ship)
        game.draw_ally_board()
        ship.draw(display, game.ally_board)
        display.show()


def main(win):
    """
    Game loop function.

    :param win: Window
    :return: None
    """
    global ai, game, cursor_x, cursor_y, is_host, is_unicorn

    if is_ai:
        ai_module = __import__(args.ai.replace('.py', '').replace('.\\', '') if args.ai is not None else 'ai')
        ai = ai_module.Ai(width, height, display.PHAT)

    game = Battleship(height, width, ships, display, connection, is_host, is_unicorn, args.speed)

    try:
        display.set_window(win, width, height)
    except AttributeError:
        pass
    win.nodelay(True)

    place_ships(win)

    if not game.ships_are_placed():
        raise CheatingDetected('Ships not placed.')

    while True:
        if not is_ai:
            sleep(0.1)
            key = win.getch()
            display.clear()
            if key == curses.KEY_DOWN and cursor_y < height - 1:
                cursor_y += 1
            elif key == curses.KEY_UP and cursor_y > 0:
                cursor_y -= 1
            elif key == curses.KEY_RIGHT and cursor_x < width - 1:
                cursor_x += 1
            elif key == curses.KEY_LEFT and cursor_x > 0:
                cursor_x -= 1
            elif key == KEY_SPACE and not game.waiting and game.enemy_board[cursor_y][cursor_x] == 0:
                game.send_missile(cursor_x, cursor_y)
            elif key == KEY_ESC:
                connection.close_connection()
                exit(0)

            if is_unicorn:
                game.draw_enemy_board()
            else:
                game.draw_both_boards()
            display.set_pixel(cursor_x, cursor_y, 255, 255, 255)
        elif not game.waiting:
            sleep(0.5 / args.speed)
            key = win.getch()
            if key == KEY_ESC:
                connection.close_connection()
                exit(0)
            move = ai.get_move(game.enemy_board)
            game.send_missile(move[1], move[0])

        if game.waiting and not game.waiting_for_rematch:
            if is_unicorn:
                game.draw_ally_board()
            else:
                game.draw_both_boards()
            display.show()
            game.await_incoming()
            curses.flushinp()
            game.print_message("AI: {}".format(args.ai))

        if game.waiting_for_rematch:
            if is_ai:
              game.print_message("AI: {} {}\nRematch? [y/n] ".format(args.ai, 'won' if game.won else 'lost'))
            else:
              game.print_message("{}\nRematch? [y/n] ".format('You won' if game.won else 'You lost'))
            while True:
                sleep(0.1)
                key = win.getch()
                if key == KEY_Y:
                    game.print_message("Waiting for opponent response...")
                    connection.send_data(True)
                    response = connection.receive_data()
                    if response:
                        game.reset()
                        break
                    else:
                        game.print_message("Opponent quit")
                        connection.close_connection()
                        sleep(2)
                        exit(0)
                elif key == KEY_N:
                    connection.send_data(False)
                    connection.close_connection()
                    exit(0)
            cursor_x = 0
            cursor_y = 0
            if is_ai:
                ai_module = __import__(args.ai.replace('.py', '').replace('.\\', '') if args.ai is not None else 'ai')
                ai = ai_module.Ai(width, height, display.PHAT)
            place_ships(win)
        display.show()


def init_game():
    """Initialize connections and start the game."""
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
        sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=args.height * 6 + 5, cols=args.width * 5 + 2))
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
                sys.stdout.write("\x1b[8;{rows};{cols}t".format(rows=height * 6 + 5, cols=width * 5 + 2))
        except ConnectionRefusedError:
            print("No host found at: {ip}".format(ip=enemy_ip))
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
