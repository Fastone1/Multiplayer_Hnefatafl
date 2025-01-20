import socket
import threading
import re

from struct import pack, unpack, error

from scripts.board import Board
from scripts.constants import PORT, END_CONNECTION, MESSAGE_LENGTH, ENCODER, BLACK, WHITE
SERVER = socket.gethostbyname(socket.gethostname())

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.bind((SERVER, PORT))
except socket.error as e:
    print(str(e))

sock.listen()
print("[STARTING] Server is starting...")

connections = 0
boards_9x9: dict[int, dict[str, Board|socket.socket]] = {0: {"board": Board(9, 9), "player1_conn": None, "player0_conn": None}}    # {board_id: {"board": Board, "player1_conn": socket, "player2_conn": socket}}
boards_11x11: dict[int, dict[str, Board|socket.socket]] = {0: {"board": Board(11, 11), "player1_conn": None, "player0_conn": None}}    # {board_id: {"board": Board, "player1_conn": socket, "player2_conn": socket}}

boards = {9: boards_9x9, 11: boards_11x11}

def send(conn: socket.socket, msg: str) -> None:
    try:
        msg_len = len(msg)
        send_len = pack('!I', msg_len)
        conn.send(send_len)
        conn.send(msg.encode(ENCODER))
    except socket.error as e:
        print(f"Send error [{conn.getpeername()}]: {e}")

def recv(conn: socket.socket) -> str:
    try:
        msg_len = unpack('!I', conn.recv(MESSAGE_LENGTH))[0]
        return conn.recv(msg_len).decode()
    except ConnectionError as e:
        print("Conn closed")
        raise e
    except socket.error as e:
        print(f'Recv error [{conn.getpeername()}]: {e}')
    except error as e:
        print(f'Unpacking error [{conn.getpeername()}]: {e}')

def handle_client(conn: socket.socket, addr: tuple, board_id: int, size: int, player_name: str):
    global connections, boards
    connections += 1
    print(f"[NEW CONNECTION] {addr} connected.")

    board = boards[size][board_id]["board"]
    conns = boards[size][board_id]

    if connections % 2 == 0:
        currentId = WHITE
        conns["player0_conn"] = conn
        board.player2 = player_name
    else:
        currentId = BLACK
        conns["player1_conn"] = conn
        board.player1 = player_name
    
    send(conn, f"color {currentId}")

    if currentId == WHITE:
        board.ready = True
        send(conns["player0_conn"], f"start {board.player1} {board.player2}")
        send(conns["player1_conn"], f"start {board.player1} {board.player2}")

    while True:
        msg = recv(conn)
        print(f"[{addr}] {msg}")

        if msg is None:
            break

        if msg == END_CONNECTION:
            send(conn, END_CONNECTION)
            print(f"[{addr}] Closing connection...")
            if board.ready and board.winner is None:
                board.winner = 1 - currentId    # Set the winner to the other player
                send(conns[f"player{1-currentId}_conn"], "win")   # Send win to the other player
            break
        elif re.match(r"move [\d]{1,2} [\d]{1,2} [\d]{1,2} [\d]{1,2}", msg) is not None:
            start_row, start_col, row, col = map(int, msg.split()[1:])
            if board.move_piece(board.get_piece(start_row, start_col), row, col):
                send(conns["player0_conn"], f"move {start_row} {start_col} {row} {col}")
                send(conns["player1_conn"], f"move {start_row} {start_col} {row} {col}")
                print(board)
                if board.winner is not None:
                    break
            else:
                send(conn, "invalid move")
                print(f"[{addr}] Invalid move")
        elif msg == "size":
            send(conn, f"size {board.width} {board.height}")
        else:
            send(conn, "invalid command")

    connections -= 1
    try:
        del boards[size][board_id]
    except:
        pass
    print(f"[ACTIVE CONNECTIONS] {connections}")
    conn.close()

def start():
    while True:
        if connections < 6:
            print("[WAITING FOR CONNECTIONS] Waiting for connections...")
            conn, addr = sock.accept()

            info = recv(conn)
            if info is None or re.match(r"info [\d]{1,2} [a-zA-Z0-9_]{1,16}", info) is None:
                print("Error: info")
                conn.close()
                continue
            print(f"Size received: {info}")
            size = int(info.split(" ")[1])
            player_name = str(info.split(" ")[2])

            board_id = -1
            for id in boards[size]:
                if boards[size][id]["board"].ready == False:
                    print(f"[{addr}] Found board {id}")
                    board_id = id
                    break
            
            if board_id == -1:
                try:
                    board_id = list(boards[size].keys())[-1] + 1
                    boards[size][board_id] = {"board": Board(9, 9), "player1_conn": None, "player2_conn": None}
                except:
                    board_id = 0
                    boards[size][board_id] = {"board": Board(9, 9), "player1_conn": None, "player2_conn": None}

            thread = threading.Thread(target=handle_client, args=(conn, addr, board_id, size, player_name))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {connections}")

    print("[SHUTTING DOWN] Server is shutting down...")
    sock.close()

start()