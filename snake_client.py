import pygame
import socket
import sys

pygame.init()

# Initialize the display
win_size = 500
win = pygame.display.set_mode((win_size, win_size))
pygame.display.set_caption("Snake Game")

# Set up the socket connection
server = "localhost"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server, port))

# Colors
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)

def drawWindow(surface, players_pos, snacks_pos):
    surface.fill(black)
    for pos_str in players_pos.split("**"):
        pos_list = [pos[1:-1].split(",") for pos in pos_str.split("*")]
        for p in pos_list:
            try:
                pygame.draw.rect(surface, red, (int(p[0]) * 25, int(p[1]) * 25, 25, 25))
            except ValueError as e:
                pass

    for pos in snacks_pos.split("**"):
        pos_list = pos[1:-1].split(",")
        try:
            pygame.draw.rect(surface, green, (int(pos_list[0]) * 25, int(pos_list[1]) * 25, 25, 25))
        except ValueError as e:
            pass

    pygame.display.update()

def main():
    clock = pygame.time.Clock()

    hotkey_pressed = False  # Flag to track if a hotkey is already pressed

    try:
        while True:
            clock.tick(10)  # Limit the frame rate

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # Handle keydown events for hotkeys
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        s.sendall(b"left")
                    elif event.key == pygame.K_RIGHT:
                        s.sendall(b"right")
                    elif event.key == pygame.K_UP:
                        s.sendall(b"up")
                    elif event.key == pygame.K_DOWN:
                        s.sendall(b"down")

                    elif event.key == pygame.K_r:
                        s.sendall(b"reset")
                    elif event.key == pygame.K_q:
                        s.sendall(b"quit")

                    # Handle hotkeys (send messages to the server)
                    elif event.key == pygame.K_z and not hotkey_pressed:
                        s.sendall(b"z")
                        hotkey_pressed = True
                    elif event.key == pygame.K_x and not hotkey_pressed:
                        s.sendall(b"x")
                        hotkey_pressed = True
                    elif event.key == pygame.K_c and not hotkey_pressed:
                        s.sendall(b"c")
                        hotkey_pressed = True

                # Handle keyup events to reset the hotkey_pressed flag
                elif event.type == pygame.KEYUP:
                    hotkey_pressed = False

            s.sendall(b"get")
            data = s.recv(2048).decode()

            # Split the data into a list of player/snack positions
            positions_list = data.split("|")

            # Ensure there are at least two elements in the list
            if len(positions_list) >= 2:
                players_pos, snacks_pos = positions_list[:2]
                drawWindow(win, players_pos, snacks_pos)
            else:
                print(data)

    finally:
        s.sendall(b"quit")
        s.close()

if __name__ == "__main__":
    main()


