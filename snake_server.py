import numpy as np
import socket
from _thread import *
from snake import SnakeGame
import threading
import uuid
import time
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

# server = "10.11.250.207"
server = "localhost"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

counter = 0
rows = 20

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

game = SnakeGame(rows)
game_state = ""
interval = 0.2
moves_queue = set()


# Add a lock for synchronization
lock = threading.Lock()
connections = []

def broadcast(message):
    global connections
    for connection in connections:
        try:
            connection.sendall(message.encode())
        except Exception as e:
            print("Error broadcasting message to a client:", e)

def game_thread():
    global game, moves_queue, game_state
    while True:
        with lock:
            game.move(moves_queue)
            moves_queue = set()
            game_state = game.get_state()
        time.sleep(interval)

def send_client_data(conn):
    global game_state
    conn.sendall(game_state.encode())

def player_thread(conn, unique_id):
    global game, moves_queue, connections

    color = rgb_colors_list[np.random.randint(0, len(rgb_colors_list))]
    game.add_player(unique_id, color=color)

    try:
        while True:
            data = conn.recv(500).decode()
            send_client_data(conn)

            move = None
            if not data:
                print("no data received from client")
                break
            elif data == "get":
                print("received get")
                pass
            elif data == "quit":
                print("received quit")
                game.remove_player(unique_id)
                # Broadcast a message to inform other clients about the player quitting
                broadcast(f"Player {unique_id} has quit.")
                break
            elif data == "reset":
                game.reset_player(unique_id)
            elif data in ["up", "down", "left", "right"]:
                move = data
                moves_queue.add((unique_id, move))
            elif data in ["z", "x", "c"]:
                if data == "z":
                    chat_message = "chat:Congratulations!"
                elif data == "x":
                    chat_message = "chat:It works!"
                elif data == "c":
                    chat_message = "chat:Ready?"
                broadcast(chat_message)
            else:
                print("Invalid data received from client:", data)

    finally:
        # Remove the connection from the list when the player thread exits
        connections.remove(conn)
        conn.close()

def main():
    global s, game, counter, rows, interval, moves_queue, game_state, rgb_colors_list, connections

    # Initialize your SnakeGame here or replace it with your actual game initialization
    game = SnakeGame(rows)

    start_new_thread(game_thread, ())

    while True:
        try:
            conn, addr = s.accept()
            print("Connected to:", addr)

            unique_id = str(uuid.uuid4())
            connections.append(conn)  # Add the new connection to the list
            start_new_thread(player_thread, (conn, unique_id))
        except Exception as e:
            print("Error accepting connection:", e)

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", 5555))
    s.listen(5)

    interval = 0.2
    moves_queue = set()
    game_state = ""
    rgb_colors_list = [(255, 0, 0), (0, 255, 0)]

    main()
