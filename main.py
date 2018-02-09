#!/usr/bin/env python3
from time import sleep
import unicornhat as unicorn
import random
import curses

unicorn.set_layout(unicorn.PHAT)
unicorn.rotation(180)
unicorn.brightness(0.5)

enemy_board = [
    [1,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0],
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

def draw_enemy_board():
    for y in range(len(enemy_board)):
        for x in range(len(enemy_board[y])):
            if enemy_board[y][x]:
                unicorn.set_pixel(x,y,255,0,0)
            else:
                unicorn.set_pixel(x,y,0,0,0)

def draw_ally_board():
    for y in range(len(ally_board)):
        for x in range(len(ally_board[y])):
            if ally_board[y][x]:
                unicorn.set_pixel(x,y,255,0,0)
            else:
                unicorn.set_pixel(x,y,0,0,0)


def main(win):
    global cursorX, cursorY, enemy_board, ally_board, enemy_ip, enemy_turn, is_host
    
    win.nodelay(True)

    while True:
        sleep(0.1)    
        key = win.getch()
        unicorn.clear()

        draw_enemy_board()

        if key == curses.KEY_DOWN:
            cursorY += 1
        elif key == curses.KEY_UP:
            cursorY -= 1
        elif key == curses.KEY_RIGHT:
            cursorX += 1
        elif key == curses.KEY_LEFT:
            cursorX -= 1

        unicorn.set_pixel(cursorX,cursorY,0,0,255)
        
        unicorn.show()

is_host_input = input("Host? [y/n] ")
if is_host_input.upper() == "Y":
    is_host = True

if not is_host:
    enemy_ip = input("Enemy ip: ")

curses.wrapper(main)