# The-Number-Game

This is a game of guessing your opponents number before they guess yours using Python and sockets.

**How to play**
1. **Start the server:** Run the 'server.py' script.
2. **Connect clients:** Run the 'client.py' script on two different machines or terminals.
3. **Play the game:** Players take turns choosing a number for the opponent to try and guess from 1 to 10. The player to guess the opponents number first wins!

**Technologies used**
* Python
* Sockets

**Additional resources:**
### Project Statement of Work (SOW)
**Project Title:** The Number Game
**Team:** Tristan Truxal
**Project Objective:** The goal of this project is to develop a simple turn-based number guessing game where two players compete to guess each other's chosen number. The functionality I am aiming to achieve is a effective interaction between two players, while also effectivly using multiplayer capabilities and error handling.

**Scope:**
* Inclusion:
  1. Server and client software to manage game states and user inputs.
  2. ClI interfaces for both server and client to facilitate game setup and play.
  3. Networking capability to handle simultaneous games in isolated sessions

* Exclusions:
  1. Graphical user interface (GUI)
  2. Tournaments
  3. Advanced statstics or player profiles
 
**Deliverables:**
1. Fully functional server script in Python
2. Client script in Python for players to connect and play the game
3. documentation including setup instructions, game rules, and troubleshooting.
4. basic unit tets to ensure functionality of the components.

**Timeline:**
* Key Milestones:
  1. Setting up server-client connectivity with test (3 days)
  2. Implement game logic along with implementing test (5 days)
  3. Error handling and edge case testing ( 3 days)
  4. Finish documentation and testing ( 3 days)
 
* Task Breakdown:
  1. Setting up enviornment (4 hours)
  2. Design Server and Client interaction protocol (8 hours)
  3. Implement Server Logic ( 12 hours)
  4. Implement Client Logic ( 10 hours)
  5. Unit Testing and Debugging ( 16 hours)
  6. Documentation ( 6 hours)
  7. Final Integration and Testing (8 hours)

**Technical Requirements:**
* Hardware:
    1. Server capable of running Python and handling multiple client connections.
    2. Client devices (laptop or computer) with network access
 
* Software:
  1. Programming Language: Python 3.8 or Higher.
  2. Libraries: Socket for networking, Threading to manage client sessions, and Argparse for command line arguments, Selectors for multiple connections, Along with threading for effective message sending.
  3. Development Tools: Git for version control, and VS Code as IDE

**Assumptions:**
  1. Stable network connectivity between clients and the server.
  2. Clients have basic technical knowledge to operate a command line interface.
  3. Python and necessary libraries are installed on both server and client machines

**Roles and Responsibilities:**
1. Project Manager: Tristan Truxal
2. Developers: Tristan Truxal
3. Testers: Tristan Truxal

**Communication Plan**
1. Email

**Message Protocol**
1. The program uses Json in order to serialize and deseralize the messages being passed using threading

### Playing The Game
1. Start the server using "python server.py"
2. Connect 2 clients using "python client.py 127.0.0.1 12358"
3. communicate with each other using -chat with what you want to say. (more messages types to be added)
