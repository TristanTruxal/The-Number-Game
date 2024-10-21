# server.py
from libserver import ServerCommunication

if __name__ == "__main__":
    server = ServerCommunication()
    server.start_server('127.0.0.1', 8080)
