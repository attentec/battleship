#!/usr/bin/env python3
from time import sleep
import unicornhat as unicorn
import random
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


def draw_enemy_board():
    for y in range(len(enemy_board)):
        for x in range(len(enemy_board[y])):
            if enemy_board[y][x] == 2:
                unicorn.set_pixel(x,y,255,0,0)
            elif enemy_board[y][x] == 3:
                unicorn.set_pixel(x,y,255,255,255)
            else:
                unicorn.set_pixel(x,y,0,0,0)


def draw_ally_board():
    for y in range(len(ally_board)):
        for x in range(len(ally_board[y])):
            if ally_board[y][x] == 1:
                unicorn.set_pixel(x,y,0,255,0)
            elif ally_board[y][x] == 2:
                unicorn.set_pixel(x, y, 255, 0, 0)
            elif ally_board[y][x] == 3:
                unicorn.set_pixel(x, y, 255, 255, 255)
            else:
                unicorn.set_pixel(x,y,0,0,0)

def draw_sunken_board():
    los_board = [
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0]
    ]
    for y in range(len(los_board)):
        for x in range(len(los_board[y])):
            if los_board[y][x]:
                unicorn.set_pixel(x,y,255,0,0)
            else:
                unicorn.set_pixel(x,y,0,0,0)


def draw_victory_board():
    vic_board = [
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 0, 0, 0, 0, 1, 0]
    ]
    for y in range(len(vic_board)):
        for x in range(len(vic_board[y])):
            if vic_board[y][x]:
                unicorn.set_pixel(x,y,0,255,0)
            else:
                unicorn.set_pixel(x,y,0,0,0)


def send_missile():
    global cursorX, cursorY, connection, waiting
    connection.send_data([cursorY, cursorX])
    response = connection.receive_data()
    if response == 4:
        draw_victory_board()
        unicorn.show()
        sleep(3)
        connection.close_connection()
        exit(0)
    enemy_board[cursorY][cursorX] = response
    draw_enemy_board()
    unicorn.show()
    waiting = True
    sleep(1)


def await_incomming():
    global connection, waiting
    coordinates = connection.receive_data()
    lost = False
    if ally_board[coordinates[0]][coordinates[1]] == 1:
        res = 2
        ally_board[coordinates[0]][coordinates[1]] = 2
    else:
        res = 3
        ally_board[coordinates[0]][coordinates[1]] = 3
        lost = has_lost()
    if lost:
        connection.send_data(4)
        draw_sunken_board()
        unicorn.show()
        sleep(3)
        connection.close_connection()
        exit(0)
    else:
        connection.send_data(res)
    draw_ally_board()
    unicorn.show()
    waiting = False
    sleep(1)


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
            draw_ally_board()
            ship.draw(unicorn, ally_board)
        else:
            if key == curses.KEY_DOWN:
                cursorY += 1
            elif key == curses.KEY_UP:
                cursorY -= 1
            elif key == curses.KEY_RIGHT:
                cursorX += 1
            elif key == curses.KEY_LEFT:
                cursorX -= 1
            elif key == 32 and not waiting:  # Space
                send_missile()
            draw_enemy_board()
            unicorn.set_pixel(cursorX,cursorY,0,0,255)

            if waiting:
                draw_ally_board()
                await_incomming()
                curses.flushinp()
        unicorn.show()


is_host_input = input("Host? [y/n] ")
if is_host_input.upper() == "Y":
    is_host = True
    waiting = False
    connection = Connection("0.0.0.0", False)

if not is_host:
    enemy_ip = input("Enemy ip: ")
    connection = Connection(enemy_ip, True)

try:
    curses.wrapper(main)
except:
    connection.close_connection()
