| Input Space Partitioning                  |                                       |                     |                                                           |
| :---------------------------------------: | :-----------------------------------: | :-----------------: | :------------------------------------------------------:  |
| Variable                                  | Characteristic                        | Partition           | Value                                                     |
| User.connect                              | A) Connected                          | A1) server          | clients[client_id] = {"username": None, "state": "connected", "room": None} |
|                                           |                                       |                     |                                                           |
| User.disconnected                         | B) Disconnected                       | B1) server          | disconnect_message = { "user": "Server", "message": f"{username} has left the chat."} |
|                                           |                                       | B2) lobby           | ('game_status', {"message": f"{username} has disconnected. Returning to the lobby.", "showGuessInput": False}, to=other_player) |
|                                           |                                       |                     |                                                           |
| User.message                              | C) Message                            | C1) server          | (response, to=client_id)                                  |
|                                           |                                       | C2) lobby           | (response, to=room)                                       |
|                                           |                                       |                     |                                                           |
| User.lobby                                | D) Join_Lobby                         | D1) alone           | ('queue_status', {"message": "You have joined the queue. Waiting for another player."}, to=client_id) |
|                                           |                                       | D2) paired (player1)| ('paired', {"message": "You have been paired with another player. Start chatting", "isPlayer1": True}, to=player1) |
|                                           |                                       | D3) paired (player2)| ('paired', {"message": "You have been paired with another player. Start chatting", "isPlayer1": False}, to=player2) |
|                                           |                                       | D4) leave           | ('game_status', {"message": f"{username} has left the room. Returning you to the lobby.", "showGuessInput": False}, to=other_player) |
|                                           |                                       |                     |                                                           |
| User.game_start                           | E) start_game                         | E1) player1         | ('game_status', {"message": "You are Player 1. Set a number between 1 and 10 for Player 2 to guess.","showGuessInput": True,"showEndButtons": False}, to=player1) |
|                                           |                                       | E2) player2         | ('game_status', {"message": "Waiting for Player 1 to set a number.","showGuessInput": False,"showEndButtons": False}, to=player2) |
|                                           |                                       |                     |                                                           |
| User.set_number                           | F) set_number                         | F1) invalid_num     | ('game_status', {"message": "Invalid number. Please choose a number between 1 and 10."}, to=client_id) |
|                                           |                                       | F2) invalid_input   | ('game_status', {"message": "Invalid number format. Please enter a valid number."}, to=client_id) |
|                                           |                                       | F3) set (player1)   | ('game_status', {"message": "Number set, Waiting for Player 2 to guess.", "showGuessInput": False}, to=client_id) |
|                                           |                                       | F4) guess (player2) | ('game_status', {"message": "Guess the number Player 1 set between 1 and 10.", "showGuessInput": True}, to=game_state[room]["player2"]) |
|                                           |                                       |                     |                                                           |
| User.guess_number                         | G) guess_number                       | G1) invalid_num     | ('game_status', {"message": "Invalid number. Please choose a number between 1 and 10."}, to=client_id) |
|                                           |                                       | G2) invalid_input   | ('game_status', {"message": "Invalid number format. Please enter a valid number."}, to=client_id) |
|                                           |                                       | G3) guess_wrong     | ('game_status', {"message": f"Wrong guess. {remaining_rounds} rounds remaining. Player 1, set a new number.", "showGuessInput": True}, to=game_state[room]["player1"]) |
|                                           |                                       | G4) guess_right     | ('game_status', {"message": f"{clients[client_id]['username']} guessed correctly and wins the game", "showGuessInput": False}, to=room) |
|                                           |                                       | G5) guess_limit     | ('game_status', {"message": "Player 1 wins. Player 2 failed to guess in 5 rounds.", "showGuessInput": False}, to=room) |
|                                           |                                       |                     |                                                           |
| User.play_again                           | H) play_again                         | H1) player1         | ('game_status', {"message": "New game started! Player 1, set a number between 1 and 10.","showGuessInput": True,"showEndButtons": False}, to=game_state[room]["player1"]) |
|                                           |                                       | H2) player2         | emit('game_status', {"message": "Waiting for Player 1 to set a number.","showGuessInput": False,"showEndButtons": False}, to=game_state[room]["player2"]) |
|                                           |                                       |                     |                                                           |
| User.quit                                 | I) quit                               | I1) quit            | ('game_status', {"message": "One or both players chose to quit. Returning to the lobby.", "showGuessInput": False}, to=room) |
|                                           |                                       |                     |                                                           |

| Base Choice Coverage Test Set                      |      |      |     |     |     |     |                                 |
| :------------------------------------------------: | :--: | :--: | :-: | :-: | :-: | :-: | :-----------------------------: |
| Test                                               |      |      |     |     |     |     | Oracle                          |
| User.connect                                       | A1   |      |     |     |     |     | pass as connected               |
| User.disconnect                                    | B1   |      |     |     |     |     | pass as disconnection           |
| User.disconnect_from_lobby                         | B2   |      |     |     |     |     | pass as exit from room          |
| User.send_message_to_lobby                         | C1   |      |     |     |     |     | pass as message to lobby        |
| User.send_message_to_room                          | C2   |      |     |     |     |     | pass as message to room         |
| User.join_queue                                    | D1   |      |     |     |     |     | pass as waiting for room        |
| User.paired                                        | D2   | D3   |     |     |     |     | pass as paired                  |
| User.start_game                                    | E1   | E2   |     |     |     |     | pass as game started            |
| User.set_number_wrong                              | F1   |      |     |     |     |     | pass as exception               |
| User.set_wrong_input                               | F2   |      |     |     |     |     | pass as exception               |
| User.set_number                                    | F3   | F4   |     |     |     |     | pass as number set              |
| User.guess_number_wrong_limit                      | f3   | f4   | g1  |     |     |     | pass as exception               |
| User.guess_wrong_format                            | f3   | f4   | g2  |     |     |     | pass as exception               |
| User.guess_number_wrong                            | f3   | f4   | g3  |     |     |     | pass as next round              |
| User.guess_number_right                            | f3   | f4   | g4  |     |     |     | pass as winner                  |
| User.guess_number_limit                            | f3   | f4   | g5  |     |     |     | pass as loser                   |
| User.play_again_after_win                          | f3   | f4   | g4  | h1  | h2  |     | pass as play again after win    |
| User.play_again_after_lose                         | f3   | f4   | g5  | h1  | h2  |     | pass as play again after lose   |
| User.quit_after_game_win                           | f3   | f4   | g4  | i1  |     |     | pass as quit after win          |
| User.quit_after_game_lose                          | f3   | f4   | g5  | i1  |     |     | pass as quit after lose         |
| User.rejoins_queue_mid_match_guesser               | f3   | f4   | d4  |     |     |     | pass as rejoin queue during match |
| User.rejoins_queue_mid_match_setter                | f3   | f4   | g3  | d4  |     |     | pass as rejoin queue during match |
