import socket
import sys

def main(server_ip, server_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    server_address = (server_ip, server_port)
    print(f"Connecting to {server_ip} port {server_port}")
    
    try:
        sock.connect(server_address)
        
        while True:
            try:
                message = input("Enter your guess (a number): ")
                if not message.isdigit():
                    print("Please enter a valid number.")
                    continue
                sock.sendall(message.encode())

                data = sock.recv(1024)
                if not data:
                    print("Connection closed by server.")
                    break
                print(f"Received: {data.decode()}")
                if "win" in data.decode().lower() or "lose" in data.decode().lower():
                    print("Game over.")
                    break

            except socket.error as e:
                print(f"Socket error: {e}")
                break

    finally:
        print("Closing socket")
        sock.close()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_ip> <server_port>")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    main(server_ip, server_port)
