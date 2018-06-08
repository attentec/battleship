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
    color = curses.COLOR_BLACK
    if r == 255 and g == 255 and b == 255:
        color = curses.COLOR_WHITE
    elif r == 255:
        color = curses.COLOR_RED
    elif g == 255:
        color = curses.COLOR_GREEN
    elif b == 255:
        color = curses.COLOR_BLUE
    window.addstr(y, x, "█", curses.color_pair(color))

def show():
    global window
    window.refresh()

def set_window(win):
    global window
    window = win
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)
    curses.init_pair(curses.COLOR_BLACK, curses.COLOR_BLACK, -1)
    curses.init_pair(curses.COLOR_RED, curses.COLOR_RED, -1)
    curses.init_pair(curses.COLOR_WHITE, curses.COLOR_WHITE, -1)
    curses.init_pair(curses.COLOR_GREEN, curses.COLOR_GREEN, -1)
    curses.init_pair(curses.COLOR_BLUE, curses.COLOR_BLUE, -1)
