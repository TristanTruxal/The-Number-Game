import json

class Game:
    def __init__(self, player1, player2, send_message_func, broadcast_func):
        self.player1 = player1
        self.player2 = player2
        self.send_message = send_message_func
        self.broadcast_to_all = broadcast_func

        self.broadcast_to_all("A new game has started between Player 1 and Player 2.")

    def handle_request(self, player, request):
        option = request.get("option")

        if option == "-chat":
            chat_message = request.get("message", "")
            self.handle_chat(player, chat_message)
        else:
            self.send_message(player, {"message": "Unknown option. Please use '-chat <message>' to send a message."})

    def handle_chat(self, player, chat_message):
        """Handle chat messages between players."""
        if player == self.player1:
            self.send_message(self.player2, {"message": f"Player 1 says: {chat_message}"})
        elif player == self.player2:
            self.send_message(self.player1, {"message": f"Player 2 says: {chat_message}"})
        else:
            self.send_message(player, {"message": "Unknown player. Chat cannot be processed."})



    def handle_disconnection(self, player):
        if player == self.player1:
            self.send_message(self.player2, {"message": "Your chat partner has disconnected. You will be re-entered into the queue."})
            self.broadcast_to_all("Player 1 has disconnected from the game.")
            return self.player2
        elif player == self.player2:
            self.send_message(self.player1, {"message": "Your chat partner has disconnected. You will be re-entered into the queue."})
            self.broadcast_to_all("Player 2 has disconnected from the game.")
            return self.player1
        return None
