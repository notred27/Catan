
![](assets//title_screen//title.png)
# Catan

An implementation of the classic game $\textit{Settlers of Catan}$ using Python and socket programming. 
Play with up to 4 people in a single game over a local network.



## Tasks

- [x] Implement client-server connections using sockets
- [x] Add menu to host and join different sessions
- [ ] Add option to rejoin a game you have left
- [x] Implement a chatroom
- [x] Create assets for the game
- [x] Add basic functionality (next turn, building structures)
- [x] Implement resource gain per turn and costs for structures 
- [ ] Implement all development cards
- [ ] Implement largest road and largest army cards
- [x] Implement trading between players
- [ ] Implement game over conditions (winner has reached 10 pts, etc.)
- [ ] Add a "How to Play" screen



## How to Run

To run this application, first ensure that the server is running with 
```bash
  python Server.py
```


Then, any number of clients can connect with
```bash
  python Client.py
```
