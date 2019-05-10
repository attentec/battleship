"""Implementation of the display interface that draws in the terminal window."""
import curses

PHAT = 0
window = None
width = 0
height = 0


def set_layout(layout):
    """Do nothing, just here to implement the display interface."""
    pass


def rotation(degree):
    """Do nothing, just here to implement the display interface."""
    pass


def brightness(percent):
    """Do nothing, just here to implement the display interface."""
    pass


def clear():
    """Clear the window."""
    global window
    window.clear()


def set_pixel(x, y, r, g, b):
    """
    Set color of pixel.

    :param x: X coordinate
    :param y: Y coordinate
    :param r: Red
    :param g: Green
    :param b: Blue
    :return: None
    """
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
    """Show pixels on display."""
    global window
    add_border()
    window.refresh()


def add_border():
    """Add border to display."""
    global window
    window.addstr(0, 0, "┌", curses.color_pair(6))
    window.addstr(height * 3, 0, "└", curses.color_pair(6))
    window.addstr(0, width * 5, "┐", curses.color_pair(6))
    window.addstr(height * 3, width * 5, "┘", curses.color_pair(6))
    for x in range(0, width + 1):
        if x != 0 and x != width:
            window.addstr(0, x * 5, "┬", curses.color_pair(6))
            window.addstr(height * 3, x * 5, "┴", curses.color_pair(6))
        for y in range(1, height * 3):
            if x == 0 and y % 3 == 0:
                window.addstr(y, x * 5, "├", curses.color_pair(6))
            elif x == width and y % 3 == 0:
                window.addstr(y, x * 5, "┤", curses.color_pair(6))
            elif y % 3 == 0:
                window.addstr(y, x * 5, "┼", curses.color_pair(6))
            else:
                window.addstr(y, x * 5, "│", curses.color_pair(6))
    for y in range(0, height + 1):
        for x in range(0, width):
            for l in range(1, 5):
                window.addstr(y * 3, x * 5 + l, "─", curses.color_pair(6))
    window.addstr(height * 3 + 1, 0, " ", curses.color_pair(0))


def set_window(win, w, h):
    """Set initial values to be used in displaying."""
    global window, width, height
    width = w
    height = h
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
