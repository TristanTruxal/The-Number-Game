import sys
from libclient import ClientCommunication

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    client = ClientCommunication(host, port)

    try:
        client.connect()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client.close()
