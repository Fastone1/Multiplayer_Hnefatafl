import os
from dotenv import load_dotenv
load_dotenv()
print("Loaded environment variables from .env file")

SQUARE_SIZE = 16
DISPLAY_WIDTH = 9 * SQUARE_SIZE
DISPLAY_HEIGHT = 9 * SQUARE_SIZE
RENDER_SCALE = 4
WIDTH = DISPLAY_WIDTH * RENDER_SCALE
HEIGHT = DISPLAY_HEIGHT * RENDER_SCALE
SIDE_PANEL = 256

FPS = 30

WHITE = 0
BLACK = 1

ROOK = 2
KING = 3

DARK_TILE = (157, 90, 61)
LIGHT_TILE = (244, 229, 166)

PORT = int(os.getenv("SERVER_PORT", 8080))  # Default port set to 8080
SERVER = os.getenv("SERVER_IP", "localhost")
ENCODER = "utf-8"
END_CONNECTION = "!END!"
MESSAGE_LENGTH = 4

print(PORT, SERVER)