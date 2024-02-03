import socket
from _thread import *
import pickle
import threading
import random

PORT = 5555

class Lobby:
    game_arr = []

    def __init__(self, host_name, lobby_name, max_players, host_id = 0):
        self.host_name = host_name
        self.host_id = host_id
        self.lobby_name = lobby_name
        self.max_players = max_players

        self.player_colors = []
        self.players = {}
        self.game_actions = {}
        self.cache = []

        # Randomize the board
        self.token_img_indices = ["2", "3","3", "4","4","5","5","6","6", "8","8","9","9","10","10","11","11","12"]
        self.tile_img_indices = ["grain","grain","grain","grain","wool","wool","wool","wool","lumber","lumber","lumber","lumber","brick","brick","brick","ore","ore","ore"]

        # Randomize tiles and add desert in the middle
        random.shuffle(self.tile_img_indices)
        random.shuffle(self.token_img_indices)

        # Add desert tile to the center
        self.tile_img_indices.insert(9,"desert")
        self.token_img_indices.insert(9,"0")


        # Initial command for client initialization on connection to a lobby
        self.cache.append(f"server.initialize_lobby({host_id}, \"{self.lobby_name}\", {str(self.token_img_indices)}, {str(self.tile_img_indices)})")


    def info(self):
        # num_players = len(self.players.values())
        return [self.lobby_name, self.host_name, len(self.players.values()), self.max_players]
    

    @staticmethod
    def create_game_string():
        ret = []
        for i, game in enumerate(Lobby.game_arr):
            new = [i]
            new.extend(game.info())
            new.append(game.player_colors)
            ret.append(new)

        return ret 


def threaded_client(conn, p, game_idx):       
    game = Lobby.game_arr[game_idx]
    print("Player", p, "has joined lobby no.", game_idx)   
    
    game.players[p] = conn
    game.game_actions[p] = []
   
    for data in game.cache:
        game.game_actions[p].append(data)

    while True:
        try:
            # Listen for incoming commands (per game) and add them to a queue of commands each player should execute
            data = conn.recv(2048*5).decode()
 
            if data != "Sync" and data != "Join":
                game.cache.append(data)

                for player in game.game_actions.keys():
                    game.game_actions[player].append(data)

            if game.game_actions[p] != []:
                game.players[p].sendall(pickle.dumps(game.game_actions[p].pop(0)))

            else:
                conn.sendall(pickle.dumps("Sync"))

        except Exception as e:
            print("Error in lobby:", e)
            break

    print("Closing connection for player ", p)
    conn.close()


def threaded_menu(conn, p):
    in_menu = True

    print("Player_id: ", p , " is in menu screen")
    conn.send(str.encode(str(p)))   # SEND THE PLAYER_ID STRING on connection

    while in_menu:
        try:
            data = conn.recv(2048*5).decode()
         
            if "Join" in data:
                in_menu = False
                data = data.split("\n")

                print("Player", p, "(", data[2], ") is joining lobby", data[1])

                Lobby.game_arr[int(data[1])].player_colors.append(data[2])

                second_thread = threading.Thread(target=threaded_client, args=(conn, p, int(data[1]))) #FIXME
                second_thread.start()

            elif "Host" in data:
                in_menu = False
                data = data.split("\n")
                
                new_game = Lobby(data[1], data[2], int(data[3]), p)
                Lobby.game_arr.append(new_game)

                print("Player", p, "(", data[4], ") is hosting lobby", (len(Lobby.game_arr) - 1))

                Lobby.game_arr[len(Lobby.game_arr) - 1].player_colors.append(data[4])

                second_thread = threading.Thread(target=threaded_client, args=(conn, p, len(Lobby.game_arr) - 1))
                second_thread.start()



            elif "Left" in data:
                data = data.split("\n") #TODO implement that when a player leaves a game, that color is now available to join in for that game


            conn.sendall(pickle.dumps(Lobby.create_game_string()))

        except Exception as e:
            print("Error 1")
            print(e)
            break
    print("Menu thread terminated")


def listen_for_connections():
    pid = 0

    while True:
        # Listen for games trying to connect
        conn, addr = s.accept()
        print("Connected to host: ", conn, " on port ", addr)

        start_new_thread(threaded_menu, (conn, pid))

        pid += 1    # Increase the player ID after a new connection




hostname = socket.gethostname()
ip_add = socket.gethostbyname(hostname)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((ip_add, PORT))
except Exception as e:
    print(e, "Unable to create server")

s.listen()
print("Server Started")

listen_for_connections()




