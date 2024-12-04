import unittest
from server import app, socketio

class TestGameServer(unittest.TestCase):
    def setUp(self):
        self.client1 = socketio.test_client(app)
        self.client2 = socketio.test_client(app)
        self.client3 = socketio.test_client(app)

    def tearDown(self):
        if self.client1.is_connected():
            self.client1.disconnect()
        if self.client2.is_connected():
            self.client2.disconnect()
        if self.client3.is_connected():
            self.client3.disconnect()


    def test_user_connect(self):
        response = self.client1.get_received()
        self.assertTrue(any("request_username" in msg["name"] for msg in response))

    def test_user_disconnect(self):
        self.client1.emit("username", "Player1")
        self.client2.emit("username", "Player2")
        self.client1.emit("join_queue")
        self.client2.emit("join_queue")
        self.client1.disconnect()

        response = self.client2.get_received()
        self.assertTrue(any("game_status" in msg["name"] and "disconnected" in msg["args"][0]["message"] for msg in response))

    def test_message_from_lobby(self):
        self.client1.emit("username", "Player1")
        self.client1.emit("chat_message", {"message": "hello"})

        response = self.client1.get_received()
        print("Response:", response) 

        self.assertTrue(any(
            msg.get("name") == "message" and
            isinstance(msg.get("args"), dict) and
            msg["args"].get("user") == "Player1" and
            msg["args"].get("message") == "hello"
            for msg in response
    ))
        
    def test_message_to_room(self):
        self.client1.emit("username", "Player1")
        self.client2.emit("username", "Player2")
        self.client1.emit("join_queue")
        self.client2.emit("join_queue")

        self.client1.emit("chat_message", {"message": "Hello"})


        response = self.client2.get_received()
        print("Response:", response)

        self.assertTrue(any(
            msg.get("name") == "message" and
            isinstance(msg.get("args"), dict) and
            msg["args"].get("user") == "Player1" and
            msg["args"].get("message") == "Hello"
            for msg in response
    ))

    def test_join_queue(self):
        self.client1.emit("username", "Player1")
        self.client1.emit("join_queue")
        response = self.client1.get_received()
        self.assertTrue(any("queue_status" in msg["name"] and "Waiting for another player" in msg["args"][0]["message"] for msg in response))

    def test_paired_players(self):
        self.client1.emit("username", "Player1")
        self.client2.emit("username", "Player2")
        self.client1.emit("join_queue")
        self.client2.emit("join_queue")

        response1 = self.client1.get_received()
        response2 = self.client2.get_received()

        self.assertTrue(any("paired" in msg["name"] for msg in response1))
        self.assertTrue(any("paired" in msg["name"] for msg in response2))

    def test_set_invalid_number(self):
        self.client1.emit("username", "Player1")
        self.client2.emit("username", "Player2")
        self.client1.emit("join_queue")
        self.client2.emit("join_queue")

        self.client1.emit("set_number", {"number": "invalid"})
        response = self.client1.get_received()
        self.assertTrue(any("Invalid number format" in msg["args"][0]["message"] for msg in response
            if isinstance(msg.get("args"), list) and msg["args"]
            )
        )

    def test_set_number_invalid_format(self):
        self.client1.emit("username", "Player1")
        self.client2.emit("username", "Player2")
        self.client1.emit("join_queue")
        self.client2.emit("join_queue")

        self.client1.emit("set_number", {"number": "invalid_format"})

        response = self.client1.get_received()
        print("Response:", response)

        self.assertTrue(any(
            msg.get("name") == "game_status" and
            isinstance(msg.get("args"), list) and
            msg["args"][0].get("message") == "Invalid number format. Please enter a valid number."
            for msg in response
    ))


    def test_correct_guess(self):
        self.client1.emit("username", "Player1")
        self.client2.emit("username", "Player2")
        self.client1.emit("join_queue")
        self.client2.emit("join_queue")

        self.client1.emit("set_number", {"number": 7})
        self.client2.emit("guess_number", {"guess": 7})

        response = self.client1.get_received() + self.client2.get_received()
        print("Response:", response)

        self.assertTrue(
            any(
                "wins the game" in msg.get("args", [{}])[0].get("message", "")
                for msg in response
                if isinstance(msg.get("args"), list) and msg["args"]
            )
        )


    def test_quit_after_win(self):
        self.client1.emit("username", "Player1")
        self.client2.emit("username", "Player2")
        self.client1.emit("join_queue")
        self.client2.emit("join_queue")

        self.client1.emit("set_number", {"number": 7})
        self.client2.emit("guess_number", {"guess": 7})
        self.client1.emit("play_again", {"response": "quit"})
        self.client2.emit("play_again", {"response": "quit"})
        response = self.client2.get_received()
        self.assertTrue(any("chose to quit" in msg["args"][0]["message"] for msg in response
                if isinstance(msg.get("args"), list) and msg["args"]
            )
        )

    def test_queue_mid_match_guesser(self):
        self.client1.emit("username", "Player1")
        self.client2.emit("username", "Player2")
        self.client1.emit("join_queue")
        self.client2.emit("join_queue")

        self.client1.disconnect()

        response = self.client2.get_received()
        self.assertTrue(any(
            "has disconnected. Returning to the lobby." in msg.get("args", [{}])[0].get("message", "")
            for msg in response
            if isinstance(msg.get("args"), list) and msg["args"]
        ))

    def test_queue_mid_match_setter(self):
        self.client1.emit("username", "Player1")
        self.client2.emit("username", "Player2")
        self.client1.emit("join_queue")
        self.client2.emit("join_queue")

        self.client2.disconnect()

        response = self.client1.get_received()
        self.assertTrue(any(
            "has disconnected. Returning to the lobby." in msg.get("args", [{}])[0].get("message", "")
            for msg in response
            if isinstance(msg.get("args"), list) and msg["args"]
    ))
    
    def test_play_again_both_choose_play_again_after_setter_win(self):
        self.client1.emit("username", "Setter")
        self.client2.emit("username", "Guesser")
        self.client1.emit("join_queue")
        self.client2.emit("join_queue")

        self.client1.emit("set_number", {"number": 7})
        self.client2.emit("guess_number", {"guess": 7})
        self.client1.emit("play_again", {"response": "play again"})
        self.client2.emit("play_again", {"response": "play again"})

        response = self.client1.get_received() + self.client2.get_received()
        self.assertTrue(any(
            "New game started!" in msg.get("args", [{}])[0].get("message", "")
            for msg in response
            if isinstance(msg.get("args"), list) and msg["args"]
    ))
        
    def test_play_again_both_choose_play_again_after_setter_loses(self):
        self.client1.emit("username", "Setter")
        self.client2.emit("username", "Guesser")
        self.client1.emit("join_queue")
        self.client2.emit("join_queue")

        self.client1.emit("set_number", {"number": 7})
        self.client2.emit("guess_number", {"guess": 7})

        self.client1.emit("play_again", {"response": "play again"})
        self.client2.emit("play_again", {"response": "play again"})

        response = self.client1.get_received() + self.client2.get_received()
        self.assertTrue(any(
            "New game started!" in msg.get("args", [{}])[0].get("message", "")
            for msg in response
            if isinstance(msg.get("args"), list) and msg["args"]
    ))
        
    def test_round_limit_setter_wins(self):
        self.client1.emit("username", "Setter")
        self.client2.emit("username", "Guesser")
        self.client1.emit("join_queue")
        self.client2.emit("join_queue")

        for x in range(5):
            self.client1.emit("set_number", {"number": 7})
            self.client2.emit("guess_number", {"guess": 8})

        response = self.client1.get_received() + self.client2.get_received()

        self.assertTrue(any(
            "Player 1 wins. Player 2 failed to guess in 5 rounds." in msg.get("args", [{}])[0].get("message", "")
            for msg in response
            if isinstance(msg.get("args"), list) and msg["args"]
    ))

if __name__ == "__main__":
    unittest.main()
