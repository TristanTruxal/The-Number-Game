import selectors
import socket
import json
from games import Game

class ServerCommunication:
    def __init__(self):
        self.sel = selectors.DefaultSelector()
        self.clients = {}
        self.queue = []
        self.sessions = {}

    def accept(self, sock):
        conn, addr = sock.accept()
        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        self.clients[conn] = addr


        self.queue.append(conn)
        self.sel.register(conn, selectors.EVENT_READ, self.read)

        self.notify_queue_status(conn)

        if len(self.queue) >= 2:
            self.pair_clients()

    def notify_queue_status(self, conn):
        message = {"status": "waiting", "message": "You are in the queue, waiting for another client to join..."}
        self.send_message(conn, message)

    def pair_clients(self):
        if len(self.queue) >= 2:
            player1 = self.queue.pop(0)
            player2 = self.queue.pop(0)

            game = Game(player1, player2, self.send_message, self.broadcast_to_all)
            self.sessions[player1] = game
            self.sessions[player2] = game


    def broadcast_to_all(self, message):
        for conn in self.clients:
            self.send_message(conn, {"message": message})

    def read(self, conn):
        """Read data from a client, deserialize it using JSON protocol."""
        try:
            data = conn.recv(4096)
            if data:
                message = data.decode('utf-8')

                try:
                    request = json.loads(message)
                    print(f"Received message from {self.clients[conn]}: {request}")

                    if conn in self.sessions:
                        game = self.sessions[conn]
                        game.handle_request(conn, request)
                    else:
                        self.send_message(conn, {"message": "You are not in a chat session yet."})
                except json.JSONDecodeError:
                    print("Error decoding JSON")
            else:
                self.handle_disconnection(conn)
        except Exception as e:
            print(f"Error: {e}")
            self.handle_disconnection(conn)

    def handle_disconnection(self, conn):

        if conn in self.sessions:
            game = self.sessions[conn]
            remaining_player = game.handle_disconnection(conn)


            if remaining_player:
                del self.sessions[conn]
                del self.sessions[remaining_player]


                self.queue.append(remaining_player)
                self.notify_queue_status(remaining_player)

                if len(self.queue) >= 2:
                    self.pair_clients()


        elif conn in self.queue:
            self.queue.remove(conn)


        self.sel.unregister(conn)
        conn.close()
        del self.clients[conn]

    def send_message(self, conn, message):
        try:
            serialized_message = json.dumps(message).encode('utf-8') + b'\n'
            conn.sendall(serialized_message)
        except BrokenPipeError:
            print(f"Could not send to {self.clients[conn]} (client disconnected)")


    def start_server(self, host, port):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((host, port))
        server_sock.listen()
        server_sock.setblocking(False)
        self.sel.register(server_sock, selectors.EVENT_READ, self.accept)

        print(f"Server listening on {host}:{port}")

        while True:
            events = self.sel.select(timeout=None)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)
