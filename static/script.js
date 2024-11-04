const socket = io();
let username = null;
let isPlayer1 = false;

socket.on('request_username', function(data) {
    username = prompt(data.message);
    socket.emit('username', username);
});

socket.on('message', function(msg) {
    const messagesDiv = document.getElementById('messages');
    const newMsg = document.createElement('div');
    newMsg.textContent = `${msg.user}: ${msg.message}`;
    messagesDiv.appendChild(newMsg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
});

function joinQueue() {
    socket.emit('join_queue');
}

socket.on('queue_status', function(data) {
    const queueStatusElement = document.getElementById('queue-status');
    if (queueStatusElement) {
        queueStatusElement.textContent = data.message;
    } else {
        console.error("Element queue-status not found.");
    }
});

socket.on('paired', function(data) {
    const gameStatusElement = document.getElementById('game-status');
    
    if (gameStatusElement) {
        gameStatusElement.textContent = data.message;
        isPlayer1 = data.isPlayer1;

        if (isPlayer1) {
            document.getElementById('guessInput').classList.remove('hidden');
            document.getElementById('submitGuessButton').classList.remove('hidden');
            gameStatusElement.textContent = "You are Player 1. Set a number between 1 and 10 for Player 2 to guess.";
        } else {
            gameStatusElement.textContent = "Waiting for Player 1 to set a number.";
        }
    } else {
        console.error("Element game-status not found.");
    }
});

socket.on('game_status', function(data) {
    document.getElementById('game-status').textContent = data.message;
    document.getElementById('guessInput').classList.toggle('hidden', !data.showGuessInput);
    document.getElementById('submitGuessButton').classList.toggle('hidden', !data.showGuessInput);
});

function sendChatMessage() {
    const message = document.getElementById('chatMessage').value;
    if (username && message) {
        socket.emit('chat_message', { message: message });
        document.getElementById('chatMessage').value = '';
    } else {
        alert('Please enter your message.');
    }
}

function submitGuess() {
    const guess = document.getElementById('guessInput').value;
    if (isPlayer1) {
        socket.emit('set_number', { number: guess });
    } else {
        socket.emit('guess_number', { guess: guess });
    }
    document.getElementById('guessInput').value = '';
}

function showSettings() {
    document.getElementById('settings-modal').style.display = 'block';
    fetchServerInfo();
}

function closeSettings() {
    document.getElementById('settings-modal').style.display = 'none';
}

function fetchServerInfo() {
    const serverInfo = document.getElementById('server-info');
    const ip = location.hostname;
    const port = location.port;

    serverInfo.innerHTML = `
        <strong>IP Address:</strong> ${ip}<br>
        <strong>Port:</strong> ${port}<br>
    `;
}
