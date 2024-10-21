import socket
import json
import threading

class ClientCommunication:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self._recv_buffer = b""
        self.running = True

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"Connected to server at {self.host}:{self.port}")

        threading.Thread(target=self.receive_messages, daemon=True).start()

        self.send_messages()

    def send_messages(self):
        while self.running:
            input_message = input("Enter '-chat <message>' to chat: ")

            if input_message.startswith("-chat"):
                chat_message = input_message.split(' ', 1)[1] if len(input_message.split()) > 1 else ""
                request = {"option": "-chat", "message": chat_message}

                message = json.dumps(request).encode('utf-8')
                self.sock.sendall(message)
            else:
                print("Unknown command. Use '-chat <message>' to send a chat message.")

    def receive_messages(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(4096)
                if data:
                    buffer += data.decode('utf-8')
                    messages = buffer.split('\n')
                
                    
                    for message in messages[:-1]:
                        if message.strip():
                            try:
                                json_message = json.loads(message)
                                print(f"\nResponse from server: {json_message['message']}\n> ", end='')
                            except json.JSONDecodeError as e:
                                print(f"Error decoding server's JSON response: {e}")
                
                    buffer = messages[-1]
            except Exception as e:
                print(f"Error: {e}")
                self.running = False
                break


    def close(self):
        self.sock.close()
