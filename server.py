import sys
import socket
import selectors
import types
import logging


sel = selectors.DefaultSelector()

client_states = {}
lobbies = {}
next_lobby_id = 1
lobby_queue = []


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_lobby_id(sock):
    for lobby_id, states in lobbies.items():
        if sock in states:
            return lobby_id
    return None



def check_guesses(client_states, lobby_id):
    if len(client_states) == 2 and all(client["guess"] is not None for client in client_states.values()):
        clients = list(client_states.keys())
        guesser, opponent = (clients[0], clients[1]) if client_states[clients[0]]["turn"] else (clients[1], clients[0])

        guess = client_states[guesser]["guess"]
        opponent_guess = client_states[opponent]["guess"]

        if guess == opponent_guess:
            win_response = f"Congratulations! You guessed correctly. The number was {opponent_guess}. You win!\n"
            lose_response = f"Sorry, your opponent guessed your number {opponent_guess}. You lose!\n"
            guesser.send(win_response.encode())
            opponent.send(lose_response.encode())

            guesser.close()
            opponent.close()
            sel.unregister(guesser)
            sel.unregister(opponent)
            del lobbies[lobby_id]
            logging.info(f"Lobby {lobby_id} closed after game end.")
        else:
            no_match_response = f"No match! You guessed {guess}. Now it's your opponent's turn.\n"
            guesser.send(no_match_response.encode())
            client_states[guesser]["guess"] = None
            client_states[guesser]["turn"] = False
            client_states[opponent]["turn"] = True




def accept_wrapper(sock):
    conn, addr = sock.accept()
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"", guess=None)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

    global next_lobby_id
    lobby_queue.append(conn)
    if len(lobby_queue) == 2:
        lobby_id = next_lobby_id
        next_lobby_id += 1
        player1, player2 = lobby_queue[0], lobby_queue[1]
        lobbies[lobby_id] = {
            player1: {"addr": player1.getpeername(), "guess": None, "turn": True, "player_id": "Player 1"},
            player2: {"addr": player2.getpeername(), "guess": None, "turn": False, "player_id": "Player 2"}
        }
        lobby_queue.clear()
        logging.info(f"New lobby {lobby_id} created with Player 1: {player1.getpeername()}, Player 2: {player2.getpeername()}")
        
        welcome_message1 = "You are Player 1. Please wait for your turn."
        welcome_message2 = "You are Player 2. It will soon be your turn to guess."
        player1.send(welcome_message1.encode())
        player2.send(welcome_message2.encode())







def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    lobby_id = find_lobby_id(sock)
    if lobby_id is None:
        return

    client_states = lobbies[lobby_id]
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            try:
                received_number = int(recv_data.decode())
                client_states[sock]["guess"] = received_number
                logging.info(f"Received guess {received_number} from {data.addr}")
                check_guesses(client_states, lobby_id)
            except ValueError:
                data.outb += b"Invalid number! Please try again.\n"
        else:
            logging.info(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
            del client_states[sock]





host = '127.0.0.1'
port = 12358


logging.info("Server is starting...")
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
logging.info(f"Listening on {(host, port)}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)


try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
except KeyboardInterrupt:
    logging.info("Caught keyboard interrupt, exiting")
finally:
    sel.close()
    logging.info("Server shutdown")