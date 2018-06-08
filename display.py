import curses

PHAT = 0
window = None

def set_layout(layout):
    pass

def rotation(degree):
    pass

def brightness(percent):
    pass

def clear():
    global window
    window.clear()

def set_pixel(x, y, r, g, b):
    global window
    color = 1
    if r == 255 and g == 255 and b == 255:
        color = 2
    elif r == 255:
        color = 3
    elif g == 255:
        color = 4
    elif b == 255:
        color = 5
    window.addstr(y * 3 + 1, x * 5 + 1, "█", curses.color_pair(color))
    window.addstr(y * 3 + 1, x * 5 + 2, "█", curses.color_pair(color))
    window.addstr(y * 3 + 1, x * 5 + 3, "█", curses.color_pair(color))
    window.addstr(y * 3 + 1, x * 5 + 4, "█", curses.color_pair(color))
    window.addstr(y * 3 + 2, x * 5 + 1, "█", curses.color_pair(color))
    window.addstr(y * 3 + 2, x * 5 + 2, "█", curses.color_pair(color))
    window.addstr(y * 3 + 2, x * 5 + 3, "█", curses.color_pair(color))
    window.addstr(y * 3 + 2, x * 5 + 4, "█", curses.color_pair(color))

def show():
    global window
    add_border()
    window.refresh()

def add_border():
    global window
    window.addstr(0, 0, "┌", curses.color_pair(6))
    window.addstr(12, 0, "└", curses.color_pair(6))
    window.addstr(0, 40, "┐", curses.color_pair(6))
    window.addstr(12, 40, "┘", curses.color_pair(6))
    for x in range(0,9):
        if x != 0 and x != 8:
            window.addstr(0, x * 5, "┬", curses.color_pair(6))
            window.addstr(12, x * 5, "┴", curses.color_pair(6))
        for y in range(1,12):
            if x == 0 and y % 3 == 0:
                window.addstr(y, x * 5, "├", curses.color_pair(6))
            elif x == 8 and y % 3 == 0:
                window.addstr(y, x * 5, "┤", curses.color_pair(6))
            elif y % 3 == 0:
                window.addstr(y, x * 5, "┼", curses.color_pair(6))
            else:
                window.addstr(y, x * 5, "│", curses.color_pair(6))
    for y in range(0, 5):
        for x in range(0, 8):
            for l in range(1, 5):
                window.addstr(y * 3, x * 5 + l, "─", curses.color_pair(6))

def set_window(win):
    global window
    window = win
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_RED)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_GREEN)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLUE)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
