# Battleship
This is a game of Battleship played over a network.
The game can be executed on a Raspberry pi with a 4 x 8 Unicorn phat or in a terminal.

## Instructions
Execute the `main.py` to start the game.
The script can take the `--host` flag to run as the host or `--client=<ip>` to connect to the host.
The script can also take `--ai` to run the AI implementation as the player.
To run the game on the Raspberry Pi with a unicorn phat no other flags should be provided.
To run the game in terminal run with `--display` or in an environment without unicornhat.
To run a game without a display, useful when playing against the AI, run with `--no-display`.
