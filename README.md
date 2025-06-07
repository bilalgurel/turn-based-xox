Turn Based XOX Game

Overview
This game is a console-based, turn-based multiplayer game implemented in Python using a client-server architecture. The project focuses on real-time communication, concurrency, fault tolerance, and rule enforcement.

Project Structure
/turn-based-xox
├── server.py  
├── client.py
└── README.md

Implementation Details
Client-Server Communication: Built on TCP sockets for stable and ordered message delivery.
Concurrency: Server handles multiple clients using the threading module. Each connection is managed in a separate thread.
Disconnection Handling: Unexpected exits are managed with exception handling; the game informs other players and terminates safely.
Game Logic: All moves are validated server-side. Illegal actions are rejected with appropriate feedback.
Interface: The game runs fully in the console. Inputs, turn indicators, and outcomes are clearly printed.
Code Quality: Modular and structured design separating UI, logic, and networking components.

Demonstration Highlights
Full walkthrough of a sample game session.
Justification for TCP and multithreading choices.
Input validation and rejection mechanisms shown live.

Documentation
Concurrency Tools: Python socket, threading, try/except for error handling.
External Libraries: None used beyond Python’s standard library.

Team Contributions:
Bilal Gürel: Client UI, socket connection management, input/output structure
Furkan Cetin: Client UI, Server threading