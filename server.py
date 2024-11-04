from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit

app = Flask(__name__, static_folder='static')
socketio = SocketIO(app)

clients = {}
queue = []
game_state = {}

@app.route('/')
def index():
    return render_template('game.html')

@socketio.on('connect')
def connect():
    client_id = request.sid
    clients[client_id] = {"username": None, "state": "connected", "room": None}
    print(f"Client {client_id} has connected.")
    emit('request_username', {"message": "enter your username:"}, to=client_id)

@socketio.on('disconnect')
def disconnect():
    client_id = request.sid
    if client_id in clients:
        username = clients[client_id]['username'] or f"Client {client_id}"
        room = clients[client_id]['room']
        
        if client_id in queue:
            queue.remove(client_id)
        
        if room:
            other_player = game_state[room]["player2"] if game_state[room]["player1"] == client_id else game_state[room]["player1"]
            emit('game_status', {"message": f"{username} has disconnected. Returning to the lobby.", "showGuessInput": False}, to=other_player)
            leave_room(room, sid=other_player)
            clients[other_player]['room'] = None
            del game_state[room]

        del clients[client_id]
        disconnect_message = {
            "user": "Server",
            "message": f"{username} has left the chat."
        }
        send(disconnect_message, broadcast=True)
    print(f"{username} has disconnected.")

@socketio.on('username')
def username(username):
    client_id = request.sid
    if client_id in clients:
        clients[client_id]['username'] = username
        print(f"Client {client_id} set their username to: {username}")
        welcome_message = {
            "user": "Server",
            "message": f"{username} has entered the chat"
        }
        send(welcome_message, broadcast=True)

@socketio.on('join_queue')
def join_queue():
    client_id = request.sid
    username = clients[client_id]['username']

    if client_id not in queue:
        queue.append(client_id)
        emit('queue_status', {"message": "You have joined the queue. Waiting for another player."}, to=client_id)

    if len(queue) >= 2:
        player1 = queue.pop(0)
        player2 = queue.pop(0)
        room = f"room_{player1}_{player2}"
        clients[player1]['room'] = room
        clients[player2]['room'] = room

        join_room(room, sid=player1)
        join_room(room, sid=player2)

        game_state[room] = {
            "player1": player1,
            "player2": player2,
            "turn": player1,
            "number_to_guess": None,
            "round_count": 0,
        }

        emit('paired', {"message": "You have been paired with another player. Start chatting", "isPlayer1": True}, to=player1)
        emit('paired', {"message": "You have been paired with another player. Start chatting", "isPlayer1": False}, to=player2)
        print(f"Paired {clients[player1]['username']} and {clients[player2]['username']} in room {room}")

@socketio.on('chat_message')
def chat_message(msg_data):
    client_id = request.sid
    username = clients[client_id].get('username', f"Client {client_id}")
    room = clients[client_id]['room']
    
    response = {
        "user": username,
        "message": msg_data['message']
    }
    
    if room:
        send(response, to=room)
    else:
        for client_id, client_data in clients.items():
            if client_data['room'] is None:
                send(response, to=client_id)
    print(f"Received message from {username}: {msg_data['message']}")

@socketio.on('set_number')
def set_number(data):
    client_id = request.sid
    room = clients[client_id]['room']
    
    if room in game_state and game_state[room]["turn"] == client_id:
        try:
            number = int(data["number"])
            if 1 <= number <= 10:
                game_state[room]["number_to_guess"] = number
                game_state[room]["turn"] = game_state[room]["player2"]
                game_state[room]["round_count"] += 1
                emit('game_status', {"message": "Number set, Waiting for Player 2 to guess.", "showGuessInput": False}, to=client_id)
                emit('game_status', {"message": "Guess the number Player 1 set between 1 and 10.", "showGuessInput": True}, to=game_state[room]["player2"])
                print(f"{clients[client_id]['username']} set the number {number} in room {room}")
            else:
                emit('game_status', {"message": "choose a number 1 to 10."}, to=client_id)
        except ValueError:
            emit('game_status', {"message": "Invalid number format."}, to=client_id)

@socketio.on('guess_number')
def guess_number(data):
    client_id = request.sid
    room = clients[client_id]['room']
    
    if room in game_state and game_state[room]["turn"] == client_id:
        try:
            guess = int(data["guess"])
            number_to_guess = game_state[room]["number_to_guess"]
            if guess == number_to_guess:
                emit('game_status', {"message": f"{clients[client_id]['username']} guessed correctly and wins the game", "showGuessInput": False}, to=room)
                end_game(room, winner_message=f"{clients[client_id]['username']} wins!")
            elif game_state[room]["round_count"] == 5:
                emit('game_status', {"message": "Player 1 wins Player 2 failed to guess in 5 rounds.", "showGuessInput": False}, to=room)
                end_game(room, winner_message="Player 1 wins")
            else:
                remaining_rounds = 5 - game_state[room]["round_count"]
                emit('game_status', {"message": f"Wrong guess {remaining_rounds} rounds remaining. Player 1, set a new number.", "showGuessInput": True}, to=game_state[room]["player1"])
                emit('game_status', {"message": "Waiting for Player 1 to set a new number.", "showGuessInput": False}, to=client_id)
                game_state[room]["turn"] = game_state[room]["player1"]
                game_state[room]["number_to_guess"] = None
        except ValueError:
            emit('game_status', {"message": "Invalid guess format."}, to=client_id)
    else:
        emit('game_status', {"message": "Wait for your turn"}, to=client_id)

def end_game(room, winner_message):
    if room in game_state:
        player1 = game_state[room]["player1"]
        player2 = game_state[room]["player2"]
        
        emit('game_status', {"message": winner_message + " The game has ended. Returning to the lobby.", "showGuessInput": False}, to=room)
        
        leave_room(room, sid=player1)
        leave_room(room, sid=player2)
        clients[player1]['room'] = None
        clients[player2]['room'] = None

        del game_state[room]

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)