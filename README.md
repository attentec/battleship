# Battleship
This is a game of Battleship played over a network.

Start the game by running main.py.

## Instructions for writing a AI

Start by making a copy of the `ai.py` file.
Improve the ai by implementing smarter functions to make it perform better in the game of battleship.

### Test your implementation
Open 2 terminals and in the first run:

Change the `<first ai>` to the name of the `ai` python file you want to try.

`python3 main.py --host --ships 5 4 4 3 3 3  --width 15 --height 10 --speed 10 --ai <first ai>`

In the second terminal run:

Change the `<ip>` to that displayed in the first terminal.
Change the `<second ai>` to the name of the `ai` python file you want to run your first ai against, it could be the same ai.

`python3 main.py --display --client <ip> --speed 10 --ai <second ai>`

Hold Esc to quit a ongoing AI match


## Instructions of use
The game can be executed on a Raspberry pi with a 4 x 8 Unicorn pHAT or in a terminal.
To run this game on a Raspberry Pi with a Unicorn pHAT the script must be run as root and the [unicorn-hat](https://github.com/pimoroni/unicorn-hat) package installed .

Execute the `main.py` to start the game.

The script can take the `--host` flag to run as the host or `--client=<ip>` to connect to the host.

The script can also take `--ai` to run the AI implementation as the player.

To run the game on the Raspberry Pi with a unicorn pHAT no other flags should be provided.

To run the game in terminal run with `--display` or in an environment without unicornhat.

To run a game without a display, useful when playing against the AI, run with `--no-display`.

The default port is 5000 but can be changed by providing a number to `--port=<port nr>`

## Controls
**Arrow keys** — Move cursor/ship.

**Space** — Send missile/place ship.

**R** — Rotate ship during placement.

**Esc** — Quit the game. Only possible during your turn. Hold to quit an AI game

## Runing on windows
Install Python 3 for Windows

Install curses with the following command: `python -m pip install windows-curses`
