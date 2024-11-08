
import random
import socket
import pygame
import os
import math

from Tile import Tile
from Vertex import Point
from Vertex import State
from Player import Player
from ChatManager import ChatManager
from Button import Button
from Resource import Resource
from Network import Network


# TODO if there is a turn timer, make an animation (go around the boarder) for how much time is left (with an actual timer)

# TODO make a class to contain all of the logic for the game board / points (vertices) / robber
# TODO make sure text is only rendered once, not every time a draw call is made

# TODO DFS for finding the longest path
# TODO implement logic for a player leaving
# TODO for specific draw calls, use pygame.update(Rect) to speed up computation (only updates part of the screen)
# TODO add escape menu to go to lobby (added a button, but buggy on connections)

# TODO add trade boats 
# TODO add a connection attempt after entering an IPV4 address in the fail to connect screen (I think this is done? Double check)

# TODO change text boxes so you dont have to pass in all that info

# TODO make an independent method for adding messages to the main chatbox, so the exec calls can be simplified

class Game:
    IP_ADDRESS = socket.gethostbyname(socket.gethostname())
    PORT = 5555

    PLAYER_COLOR_VALUES = { None: [(233,155,4), (233,155,4)],
                            "red": [(226,5,5), (82,0,0)],
                            "blue": [(5,107,226),(0,33,82)],
                            "orange": [(226,124,5), (82,49,0)],
                            "purple" : [(155,5,226), (46,0,82)],
                            "white": [(244,244,244), (105,105,105)],
                            "black": [(53,53,53), (0,0,0)]}
    
    def __init__(self):
        self.lobbys = []
        self.selected_lobby = None
        self.cur_turn = 0
        self.players =  {}

        self.msgs = ["Sync"]

        for player in self.players.keys():
            self.players[player].add_images(load_images("assets\\" + self.players[player].color))

        self.vertex_list = []
        self.tile_list = []


    def connect(self):
        try:
            self.n = Network(Game.IP_ADDRESS, Game.PORT)  
            self.player_id = int(self.n.getP())
            self.cur_turn = self.player_id
            return True

        except Exception as e:
            print(e)
            return False


    def set_player(self, p_id, p_name, p_color):
        self.players[p_id] = Player(p_id, p_name, p_color, Game.PLAYER_COLOR_VALUES[p_color][0], Game.PLAYER_COLOR_VALUES[p_color][1])
        self.players[p_id].add_images(load_images("assets\\" + self.players[p_id].color))
    

    def get_player(self, p_id):
        return self.players[p_id]
    
    def get_players(self):
        return list(self.players.values())
    

    def is_turn(self):
        return self.player_id == self.cur_turn

    def next_turn(self):    #FIXME make this a method outside of the Game object

        # Change the turn counter to the next player
        player_keys = list(self.players.keys())
        cur_idx = player_keys.index(self.cur_turn)
        self.cur_turn = player_keys[(cur_idx + 1) % len(self.players)]


        #TODO add changes for if its your turn here
        if not self.is_turn():
            next_turn_btn.img_u = pygame.transform.flip(self.players[self.cur_turn].banner, True, False)  
            next_turn_btn.set_pos(center[0] + 109, center[1] - 186)   # TODO positioning hack
            next_turn_btn.clear(win)
        else:
            next_turn_btn.img_u = turn_img
            next_turn_btn.set_pos(center[0] + 105, center[1] - 185)

            next_turn_btn.clear(win)
            Dice.reset_dice(win)

    
    def add_msg(self, command):
        self.msgs.append(command)


    def sync_with_server(self):
        while True:
            if len(self.msgs) > 1:
                responce = self.n.send(self.msgs.pop())
            else:
                responce = self.n.send(self.msgs[0])
 
            if  "Sync" in responce:
                break
            
            print("     cmd:",responce)
            try:
                exec(responce)  #FIXME maybe dont do this? (make a parsing function on the client side)
            except Exception as e:
                print(responce, e)

    def get_lobbys(self):
        self.lobbys = self.n.send(self.msgs[0])

    def get_selected_lobby_colors(self):
        if self.selected_lobby == None:
            return []
        
        return self.lobbys[self.selected_lobby][5]
    
    def remove_player(self, pid):
        print("Trying to remove player")
        if pid == self.cur_turn:
            self.next_turn()
        self.players[pid] = None
        self.selected_lobby = None



    def initialize_lobby(self, host_id, lobby_name, token_img_indices,tile_img_indices):
        pygame.display.set_caption(lobby_name)
        self.create_tiles(token_img_indices, tile_img_indices)
        self.create_vertices()
        self.cur_turn = host_id


    def create_tiles(self, token_img_indices,tile_img_indices):
        # Location of the tiles (in x,y,z coords)
        tile_positions = [[-1,1,0],[-1,0,0],[-1,-1,0],[0,2,-1],[0,1,-1],[0,-1,-1],[0,-2,-1],[0,2,0],[0,1,0],[0,0,0],[0,-1,0],[0,-2,0],[0,2,1],[0,1,1],[0,-1,1],[0,-2,1],[1,1,0],[1,0,0],[1,-1,0]]

        # Create the tile objects
        for i in range(len(tile_positions)):
            self.tile_list.append(Tile(tile_positions[i], center, tile_img_indices[i], int(token_img_indices[i]),tile_images[tile_img_indices[i]], token_images[token_img_indices[i]], robber_img))

        self.tile_list[9].robber = True
            #TODO make sure you set the global variabel for the robber position here as well


    def create_vertices(self):   #TODO combine this method into the above method
        # Tiles that are created to get position for points on the outer edge of the grid
        hidden_vertices = []
        tmp_tile_positions = [[0,3,0],[0,3,1],[1,2,0],[0,1,3],[0,0,3],[0,-2,3],[0,-3,3],[1,-2,0],[0,-3,1],[0,-3,0],[0,-3,-1],[-1,-2,0],[0,-3,-3],[0,-2,-3],[0,0,-3],[0,1,-3],[-1,2,0],[0,3,-1]]

        # Groups of indexes for tiles to create the vertex objects in the correct positions
        vertex_groups = [[0,3,4],[0,1,4],[1,4,5],[1,2,5],[2,5,6],[3,7,8],[3,4,8],[4,8,9],[4,5,9],[5,9,10],[5,6,10],[6,10,11],[7,8,12],[8,12,13],[8,9,13],[9,13,14],[9,10,14],[10,14,15],[10,11,15],[12,13,16],[13,16,17],[13,14,17],[14,17,18],[14,15,18],
        [0,1,33],[1,2,32],[1,32,33],[2,6,30],[2,31,32],[2,30,31],[6,29,30],[6,11,29],[11,28,29],[11,27,28],[11,15,27],[15,26,27],[15,18,26],[18,25,26],[18,24,25],[17,18,24],[17,23,24],[16,17,23],[16,22,23],[16,21,22],[12,16,21],[12,20,21],[7,12,20],[7,19,20],[7,19,36],[3,7,36],[3,35,36],[0,3,35],[0,34,35],[0,33,34]]

        # Populate the hidden_vertices 
        for i in range(len(tmp_tile_positions)):
            t = Tile(tmp_tile_positions[i], center, None, 19 + i, tile_images["desert"], None, None)
            hidden_vertices.append(t.center)

        # Create the vertiex objects
        for group in vertex_groups:
            if group[1] >= 19:
                self.vertex_list.append( Point(vertex_img, [self.tile_list[group[0]]],hidden_vertices[group[1] - 19], hidden_vertices[group[2] - 19]))

            elif group[2] >= 19:
                self.vertex_list.append( Point(vertex_img, [self.tile_list[group[0]], self.tile_list[group[1]]], hidden_vertices[group[2] - 19]))

            else:
                self.vertex_list.append( Point(vertex_img, [self.tile_list[group[0]], self.tile_list[group[1]], self.tile_list[group[2]]]))

        for point in self.vertex_list:
            for pt in self.vertex_list:
                if pt != point and point.dist_to(pt) < 70:
                    point.add_neighbor(pt)


  


WIDTH, HEIGHT = 870, 500

center = (480, 250) #FIXME is there a better way to do this?

win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

pygame.display.set_caption("Settlers of Catan")

pygame.font.init()
font_10 =  pygame.font.Font('assets\\istok-web\\IstokWeb-Bold.ttf', 10)
font_30 =  pygame.font.Font('assets\\istok-web\\IstokWeb-Bold.ttf', 20)
font_60 = pygame.font.Font('assets\\istok-web\\IstokWeb-Bold.ttf', 60)    

pygame.key.start_text_input()
pygame.key.set_repeat(120)


tile_images = {}
token_images = {"0": None}  #Add key for no token

dice_images = {}
build_btn_images = {}
card_images = {}





def load_images(path):
    dst = []
    for filename in os.listdir(path):
        dst.append(pygame.image.load(path + "\\" + filename).convert_alpha())
    return dst

def load_images_to(path, dst):
    for filename in os.listdir(path):
        key = filename[:-4]
        dst[key] = pygame.image.load(path + "\\" + filename).convert_alpha()







# Load image assets
load_images_to("assets\\tiles", tile_images)
load_images_to("assets\\tokens", token_images)
load_images_to("assets\\dice", dice_images)
load_images_to("assets\\build_btns", build_btn_images)
load_images_to("assets\\cards", card_images)

# TODO make a GUI folder and include all of these so they can be accessed through a dictionary?
vertex_img = pygame.image.load("assets/vertex.png").convert_alpha()
robber_img = pygame.image.load("assets/robber.png").convert_alpha()


chat_img =  pygame.image.load("assets/chat.png").convert_alpha()
scroll_bar =  pygame.image.load("assets/scroll_bar.png").convert_alpha()
scroll_point =  pygame.image.load("assets/scroll_point.png").convert_alpha()

settings_img =  pygame.image.load("assets/settings.png").convert_alpha()

turn_img = pygame.image.load("assets/turn.png").convert_alpha()
robber_btn_img = pygame.image.load("assets/robber_btn.png").convert_alpha()


server = Game()








# win.blit(Build.reg_img, Build.rect)






class DevCard:
    dev_cards = {"knight":   14,
                 "vp":       5,
                 "monopoly": 2,
                 "harvest":  2,
                 "road":     2
                }
    
    drawn_cards = []
    selected = None

    
    def __init__(self, type):
        self.type = type
        self.img = card_images[type]
        self.rect = None

        DevCard.drawn_cards.append(self)

        DevCard.adjust_card_offset()

    @staticmethod 
    def adjust_card_offset():
        # Adjust offsets in cards
        offset = 200 / (len(DevCard.drawn_cards))

        for i, card in enumerate(DevCard.drawn_cards):
            card.rect = card.img.get_rect(center = ( 30 + i * offset, 375))

    @staticmethod
    def draw_dev_card():
        if sum(DevCard.dev_cards.values()) != 0:
            idx = random.randint(0,4)

            for i in range(5):
                key = list(DevCard.dev_cards.keys())[(idx + i) % 5]
                if DevCard.dev_cards[key] != 0:
                    DevCard.dev_cards[key] -= 1
                    DevCard(key)
                    return

    @staticmethod
    def draw(win):
        for card in DevCard.drawn_cards:
            if card != DevCard.selected:
                win.blit(card.img, card.rect)

        if DevCard.selected != None:
            win.blit(DevCard.selected.img, (DevCard.selected.rect.x, DevCard.selected.rect.y - 10))

    def use_card(self):
        DevCard.drawn_cards.remove(self)
        if len(DevCard.drawn_cards) > 0:
            DevCard.adjust_card_offset()
        DevCard.selected = None

 
        server.add_msg("main.chatboxes[\"chatbox\"].render_chat(\"" + player.name + "\" + \" has used a \" + \"" + self.type +"\"+ \" card!\", ChatManager.GAME_MSG_COLOR)")

        # DevCard.draw(win)
        # TODO finish the logic for using each dev card

        match (self.type):
            case "knight":
                player.num_knights += 1 #FIXME
                pass

            case "vp":
                # player.vp += 1  #FIXME
                server.add_msg("add_vp(server.player_id)")

            case "monopoly":
                pass

            case "harvest":
                pass

            case "road":
                pass

        



class Dice: # Includes roll button
    rolled = False
    values = [random.randint(1,6), random.randint(1,6)]
    display = str(values[0] + values[1])
    x = 0
    y = 0
    static_y = 0
    frames = 0
    MAX_FRAMES = 20


    reg_img = pygame.image.load("assets/roll.png").convert_alpha()
    gray_img = pygame.image.load("assets/roll_g.png").convert_alpha()
    btn = None

    def initialize(center):
        Dice.btn = Button(Dice.roll, None, center[0] + 105, center[1] + 185, Dice.reg_img, Dice.gray_img)
        Dice.btn.func_d = Dice.btn.press

        Dice.x = center[0] + 300
        Dice.y = center[1] + 210
        Dice.static_y = center[1] + 210

    @staticmethod
    def reset_dice(win):
        Dice.rolled = False
        Dice.btn.clear(win)


    @staticmethod
    def roll():
        if Dice.frames == 0 and not Dice.rolled:
            Dice.frames = Dice.MAX_FRAMES
            Dice.rolled = True
    
    @staticmethod
    def check_collide(x, y):
        Dice.btn.click(x,y)


    @staticmethod
    def roll_result(name, v1, v2):
        global robber_moved
        Dice.values[0] = v1
        Dice.values[1] = v2
        Dice.display = str(Dice.values[0] + Dice.values[1])

        # Send a message of what number was rolled
        main.chatboxes["chatbox"].render_chat(name + " rolled a " + Dice.display + "!", (0,0,0))
        # server.add_msg("chatbox.render_chat(\"" + player.name + "\" +\" rolled a \" + Dice.display + \"!\",(0,0,0))")

        
        # Add resources based on number that was rolled
        for pt in server.vertex_list:  # FIXME hack for testing cards (only adds cards to the currently selected player)
            if server.player_id in pt.players:
                for tile in pt.tiles:
                    if tile.number == int(Dice.display):
                        if pt.state == State.TOWN:
                            Resource.card_list[tile.type].add_resource(1)
                        elif pt.state == State.CITY:
                            Resource.card_list[tile.type].add_resource(2)

        if Dice.values[0] + Dice.values[1] == 7:    # A 7 was rolled, make player move the knight
            next_turn_btn.pressed = True
            next_turn_btn.draw(win)
            robber_moved = False



    @staticmethod
    def animate():
        if Dice.frames != 0:    #Animation loop
            Dice.y -= math.sin((Dice.MAX_FRAMES - Dice.frames)  * 2 * 3.14 / Dice.MAX_FRAMES) * 5 # Adjust hight at which to draw the dice
            
            if Dice.frames == 1:    # End of the roll
                # Dice.roll_result(player.name, Dice.values[0] , Dice.values[1])
                server.add_msg("Dice.roll_result(\"" + player.name + "\" ," + str(Dice.values[0]) + "," + str(Dice.values[1]) + ")")

            elif Dice.frames % 5 == 0:    # Change displayed value while rolling
                Dice.values = [random.randint(1,6), random.randint(1,6)]
                
            Dice.frames -= 1


    @staticmethod
    def draw(win):
        # Check if the dice need to be moved according to their animation frame
        Dice.animate()

        # Draw the dice images to the screen
        img1 = dice_images["dice " + str(Dice.values[0])]
        img_rect = img1.get_rect(center = (Dice.x - 60, Dice.y))
        win.blit(img1,img_rect)

        img2 = dice_images["dice " + str(Dice.values[1])]
        img_rect = img2.get_rect(center = (Dice.x + 60, Dice.y))
        win.blit(img2,img_rect)

        # Draw the dice roll value to the screen
        text = render_outlined_text(Dice.display, font_60, (255,186,186),(192,15,3),  5)
        win.blit(text, text.get_rect(center=(Dice.x, Dice.static_y)))

        # Display the roll button
        Dice.btn.draw(win)





class Build:
    NOT_SELECTED = 4
    INITIAL_PERIOD = 5
    ROAD = 0
    TOWN = 1
    CITY = 2
    CARD = 3

    state = INITIAL_PERIOD


    btns = []


    @staticmethod
    def initialize():
        Build.btns = [Button(Build.show_road_buildpoints, Build.hide_points, 750,62,build_btn_images["road_u"],build_btn_images["road_d"]),
        Button(Build.show_town_buildpoints, Build.hide_points, 750,164,build_btn_images["town_u"],build_btn_images["town_d"]),
        Button(Build.show_city_buildpoints, Build.hide_points, 750,266,build_btn_images["city_u"],build_btn_images["city_d"]),
        Button(Build.draw_dev_card, Build.hide_points, 750,368,build_btn_images["card_u"],build_btn_images["card_d"])]


    road_start = None

    @staticmethod
    def show_road_buildpoints():
        if Build.state == Build.INITIAL_PERIOD or Dice.rolled == False or not server.is_turn(): 
            Build.btns[Build.ROAD].clear(win)
            return
        
        Build.state = Build.ROAD
        Build.btns[Build.TOWN].clear(win)
        Build.btns[Build.CITY].clear(win)
        Build.btns[Build.CARD].clear(win)

        #FIXME bug with two players building a road to the same point, but only 1 player can build to the third road from the intersection

        if Build.road_start == None:
            for point in server.vertex_list:
                point.show = False

                if player.id in point.players and point.roads < len(point.neighbors):
                        point.show = True

        else:
            for point in server.vertex_list:
                point.show = False

                # if point.state == State.EMPTY or point.player == player.id:
            # connected = False
            for pt in Build.road_start.neighbors:
                if not Point.road_exists(Build.road_start, pt):
                    pt.show = True

            # if connected and point != Build.road_start:
                

            

    @staticmethod
    def show_town_buildpoints():
        if Build.state == Build.INITIAL_PERIOD or Dice.rolled == False or not server.is_turn():
            Build.btns[Build.TOWN].clear(win)
            return
        
        Build.state = Build.TOWN
        Build.btns[Build.ROAD].clear(win)
        Build.btns[Build.CITY].clear(win)
        Build.btns[Build.CARD].clear(win)
        

        for point in server.vertex_list:
            point.show = False

            if point.state == State.ROAD and player.id in point.players:
                buildable = True
                for pt in point.neighbors:
                    if pt.state == State.TOWN or pt.state == State.CITY:
                        buildable = False

                if buildable:
                    point.show = True

    @staticmethod
    def show_city_buildpoints():
        if Build.state == Build.INITIAL_PERIOD or Dice.rolled == False or not server.is_turn():
            Build.btns[Build.CITY].clear(win)
            return
        
        Build.state = Build.CITY
        Build.btns[Build.ROAD].clear(win)
        Build.btns[Build.TOWN].clear(win)
        Build.btns[Build.CARD].clear(win)
        

        for point in server.vertex_list:
            point.show = False

            if point.state == State.TOWN and player.id in point.players:
                point.show = True

    @staticmethod
    def draw_dev_card():
        if Build.state == Build.INITIAL_PERIOD or Dice.rolled == False or not server.is_turn():
            Build.btns[Build.CARD].clear(win)
            return
        
        Build.state = Build.CARD
        Build.btns[Build.ROAD].clear(win)
        Build.btns[Build.TOWN].clear(win)
        Build.btns[Build.CITY].clear(win)
        

        DevCard.draw_dev_card()
        Build.btns[Build.CARD].timer = 15



    @staticmethod
    def hide_points():
        if Build.state == Build.INITIAL_PERIOD:
            return

        Build.state = Build.NOT_SELECTED
        for point in server.vertex_list:
            point.show = False

        Build.btns[Build.ROAD].clear(win)
        Build.btns[Build.TOWN].clear(win)
        Build.btns[Build.CITY].clear(win)
        Build.btns[Build.CARD].clear(win)
        


    @staticmethod
    def add_building(x, y):
        for point in server.vertex_list:
            if point.rect.collidepoint(x, y) and point.show: 
                if point.state == State.EMPTY and Build.state == Build.INITIAL_PERIOD:
                    # point.to_town(player)
                    server.add_msg("add_building(" + str(player.id) + "," + str(server.vertex_list.index(point)) + "," + str(State.TOWN) + ")")


                elif Build.state == Build.ROAD:
                    if Build.road_start == None:
                        Build.road_start = point                #TODO add check to remove this point if the button is switched 
                        Build.show_road_buildpoints()
                        Build.show_road_buildpoints()

                    else:
                        # Point.add_road(player, point, Build.road_start)

                        # Send new road construction out to server
                        server.add_msg("add_road(" + str(player.id) + "," + str(server.vertex_list.index(point)) + "," + str(server.vertex_list.index(Build.road_start)) + ")")


                        point.state = State.ROAD

                        Build.road_start = None
                        Build.hide_points()


                        


                elif Build.state == Build.TOWN:
                    # point.to_town(player)

                    # Send new town construction out to server
                    # add_building(player_id, point_idx, type)
                    server.add_msg("add_building(" + str(player.id) + "," + str(server.vertex_list.index(point)) + "," + str(State.TOWN) + ")")

                    server.add_msg("main.chatboxes[\"chatbox\"].render_chat(\"" + player.name + "\" +\" built a town!\",ChatManager.GAME_MSG_COLOR)")

                    Build.hide_points()

                            

                elif Build.state == Build.CITY:
                    # point.to_city(player)

                    server.add_msg("add_building(" + str(player.id) + "," + str(server.vertex_list.index(point)) + "," + str(State.CITY) + ")")


                    


                    server.add_msg("main.chatboxes[\"chatbox\"].render_chat(\"" + player.name + "\" +\" built a city!\",ChatManager.GAME_MSG_COLOR)")
                    Build.hide_points()



                if Build.state == Build.ROAD:
                    Build.show_road_buildpoints()
                    Build.show_road_buildpoints()

                elif Build.state == Build.TOWN:
                    Build.show_town_buildpoints()
                    Build.show_town_buildpoints()



    @staticmethod
    def draw(win):
        for btn in Build.btns:
            btn.draw(win)

    




# Found function to create outlined text
_circle_cache = {}
def _circlepoints(r):
    r = int(round(r))
    if r in _circle_cache:
        return _circle_cache[r]
    x, y, e = r, 0, 1 - r
    _circle_cache[r] = points = []
    while x >= y:
        points.append((x, y))
        y += 1
        if e < 0:
            e += 2 * y - 1
        else:
            x -= 1
            e += 2 * (y - x) - 1
    points += [(y, x) for x, y in points if x > y]
    points += [(-x, y) for x, y in points if x]
    points += [(x, -y) for x, y in points if y]
    points.sort()
    return points

# Found function to create outlined text
def render_outlined_text(text, font, gfcolor=(255,255,255), ocolor=(0, 0, 0), opx=2):
    textsurface = font.render(text, True, gfcolor).convert_alpha()
    w = textsurface.get_width() + 2 * opx
    h = font.get_height()

    osurf = pygame.Surface((w, h + 2 * opx)).convert_alpha()
    osurf.fill((0, 0, 0, 0))

    surf = osurf.copy()

    osurf.blit(font.render(text, True, ocolor).convert_alpha(), (0, 0))

    for dx, dy in _circlepoints(opx):
        surf.blit(osurf, (dx + opx, dy + opx))

    surf.blit(textsurface, (opx, opx))
    return surf









    





# METHODS TO BE CALLED BY THE SERVER (AFTER VALIDITY CHECKS ARE DONE)
# FIXME change htis to player_id's so the player object doesn't need to be stored in the server
robber_idx = 9
robber_moved = True




def call_move_robber(tile):
    global robber_moved

    if not robber_moved and server.tile_list.index(tile) != robber_idx:
        server.add_msg("move_robber(" + str(server.tile_list.index(tile)) + ")")
        robber_moved = True
        next_turn_btn.pressed = False



def move_robber(tile_idx):
    global robber_idx
    server.tile_list[robber_idx].robber = False
    server.tile_list[tile_idx].robber = True
    robber_idx = tile_idx



def add_building(player_id, point_idx, type):
    if type == State.TOWN:
        server.vertex_list[point_idx].to_town(server.get_player(player_id))
    elif type == State.CITY:
        server.vertex_list[point_idx].to_city(server.get_player(player_id))

    server.get_player(player_id).vp += 1  #TODO move this logic somewhere else?
    


def add_road(player_id, pt1_idx, pt2_idx):
    Point.add_road(server.get_player(player_id), server.vertex_list[pt1_idx], server.vertex_list[pt2_idx])


def add_resources(dice_val): #TODO do I need the player passed in for this method?
    for pt in server.vertex_list:  
        if pt.player == player.id:  # Only check points where the player has a building
            for tile in pt.tiles:   # Check the 3 tiles that surround that point
                if tile.number == dice_val and not tile.robber: #Add the resource to the player if the value rolled matches, and there's no robber
                    if pt.state == State.TOWN:
                        Resource.card_list[tile.type].add_resource(1)
                    elif pt.state == State.CITY:
                        Resource.card_list[tile.type].add_resource(2)


def add_vp(player_id):
    server.get_player(player_id).vp += 1


# TODO Make a method to decrease the dev cards when one is drawn by any player

def tmp():
    print("A button has been clicked")
    server.selected_lobby = None



  




# Make this into a state machine so you aren't calling all of these methods on top of one another


class SceneWrapper:
    def __init__(self, initial_func, draw_func):
        self.initial_func = initial_func
        self.draw = draw_func
        
        self.events = {pygame.QUIT: quit_game}
        self.images = {}
        self.btns = {}
        self.chatboxes = {}
        self.variables = {}
        self.running = False

    def add_event(self, key, func):
        self.events[key] = func

    def run(self, *args):
        self.running = True

        if self.initial_func != None:
            self.initial_func(self, *args) #TODO maybe change this so it isn't initialized every time(i.e. you only need to load assets once)

        while self.running:
            self.draw(win, self)

            #Update the display
            pygame.display.update()
        
            #Update the clock
            clock.tick(60)

            for event in pygame.event.get():
                if event.type in self.events.keys():
                    self.events[event.type](self, event)

#FIXME make sure that this is the last event that is processed??
def quit_game(scene, event):
    scene.running = False
    pygame.quit()


#==== TITLE SCENE ====#
def init_title(title):
    load_images_to("assets\\title_screen", title.images)

    title.btns["start_btn"] = Button(connect_to_server, None, WIDTH/2, 350, title.images["start_btn"], title.images["start_btn"])
    title.btns["info_btn"] = Button(None, None, WIDTH/2, 410, title.images["info_btn"], title.images["info_btn"])

def draw_title_screen(win, title_screen):
    win.fill((255, 228, 159))

    win.blit(title_screen.images["title"], title_screen.images["title"].get_rect(center = (WIDTH / 2, 170)))

    for btn in title_screen.btns.values():
        btn.draw(win)

def title_mousebuttondown(title, event):
    x,y = pygame.mouse.get_pos()
    title.btns["start_btn"].click(x,y)


title = SceneWrapper(init_title, draw_title_screen)
title.add_event(pygame.MOUSEBUTTONDOWN, title_mousebuttondown)


#==== FIND_SERVER SCENE ====#
def init_find_server(scene):
    load_images_to("assets\\fail_screen", scene.images)
    
    scene.chatboxes["ip_entry"] = ChatManager(font_60, [scene.images["entry"],scene.images["entry"],scene.images["entry"]], (WIDTH / 2, 250), (WIDTH / 2 - 260, 210), 520, "Enter host IPV4")

    scene.btns["back_btn"] = Button(title.run, None, WIDTH/2 - 90, 350, scene.images["back"],scene.images["back"])
    scene.btns["connect_btn"] = Button(change_ip_and_connect, None, WIDTH/2 + 90, 350, scene.images["connect"],scene.images["connect"])

    scene.images["msg"] = render_outlined_text("Failed to connect to server.", font_60, ocolor = (69, 1, 0), opx = 4)
    scene.images["msg2"] = render_outlined_text("Please check that a server is running or enter host IP address.", font_30, ocolor = (69, 1, 0))

def draw_find_server(win, scene):
    win.fill((255, 228, 159))

    for btn in scene.btns.values():
        btn.draw(win)
   
    scene.chatboxes["ip_entry"].draw(win)

    win.blit(scene.images["msg"], scene.images["msg"].get_rect(center = (WIDTH/2, 120)))
    win.blit(scene.images["msg2"], scene.images["msg2"].get_rect(center = (WIDTH/2, 180)))

def find_server_mousebuttondown(scene, event):
    x,y = pygame.mouse.get_pos()
    
    scene.btns["back_btn"].click(x,y)
    scene.btns["connect_btn"].click(x,y, scene.chatboxes["ip_entry"])

    scene.chatboxes["ip_entry"].check_focus(x,y)

def find_server_keydown(scene, event):
    if scene.chatboxes["ip_entry"].in_focus:
        if event.key == pygame.K_BACKSPACE:
            scene.chatboxes["ip_entry"].msg = scene.chatboxes["ip_entry"].msg[0:-1]
            scene.chatboxes["ip_entry"].render_current_line()

def find_server_textinput(scene, event):
    if scene.chatboxes["ip_entry"].in_focus:
        scene.chatboxes["ip_entry"].add_char(event.text)

find_server = SceneWrapper(init_find_server, draw_find_server)
find_server.add_event(pygame.MOUSEBUTTONDOWN, find_server_mousebuttondown)
find_server.add_event(pygame.KEYDOWN, find_server_keydown)
find_server.add_event(pygame.TEXTINPUT, find_server_textinput)



# Find server helper functions (to transition between title, find_server, and select screens)
def change_ip_and_connect(chatbox):
    Game.IP_ADDRESS = chatbox.msg
    print("Connecting to ip:", chatbox.msg)  #TODO remove this
    connect_to_server()

def connect_to_server():
    conn = server.connect()
    if conn:
        title.running = False
        find_server.running = False
        select.run()
    
    title.running = False
    find_server.run()


#==== SELECT SCENE ====#
def init_select(scene):
    load_images_to("assets\\select_screen", scene.images)

    scene.variables["select_color_btn"] = None
    scene.variables["player_colors"] = ["red", "blue", "orange", "purple","white","black"]

    # Create the color buttons 
    for i, name in enumerate(scene.variables["player_colors"]):
        if i < 3:
            x, y =  i * 75 + 640, 240
        else:
            x, y = (i - 3) * 75 + 640, 315

        cpy = scene.images[name].copy()
        cpy.set_alpha(100)
        scene.btns[name] = (Button(select_color_btn, select_color_btn, x,y, scene.images[name], cpy))

    scene.btns["back_btn"] = Button(title.run, None, 715, 450, scene.images["back"], scene.images["back"])
    scene.btns["join_btn"] = Button(join_game, join_game, 715, 390, scene.images["join_btn"], scene.images["join_btn"])
    scene.btns["join_tab"] = Button(None, None, 92,50, scene.images["join_d"], scene.images["join_u"])
    scene.btns["host_tab"] = Button(None, None, 220,50, scene.images["host_d"], scene.images["host_u"])
    scene.btns["host_tab"].pressed = True

    # Set functions for some buttons (FIXME since they are now not direct refs, put these statements back above?)
    scene.btns["join_tab"].func_d = lambda: change_win(scene.btns["host_tab"])    
    scene.btns["join_tab"].func_u = scene.btns["join_tab"].press

    scene.btns["host_tab"].func_d = lambda: change_win(scene.btns["join_tab"])
    scene.btns["host_tab"].func_u = scene.btns["host_tab"].press


    scene.chatboxes["name_entry"] = ChatManager(font_30, [scene.images["name_select"],scene.images["name_select"],scene.images["name_select"]], (715, 100),(615, 102), 200)
    scene.chatboxes["lobby_name_entry"]  = ChatManager(font_30, [scene.images["entry_long"],scene.images["entry_long"],scene.images["entry_long"]], (225, 180),(95, 165), 260, empty_msg="Enter a lobby name:")
    scene.chatboxes["num_player_entry"]  = ChatManager(font_30, [scene.images["entry_short"],scene.images["entry_short"],scene.images["entry_short"]], (115, 260),(100, 245), 40, empty_msg="4")
    scene.chatboxes["vp_limit_entry"]  = ChatManager(font_30, [scene.images["entry_short"],scene.images["entry_short"],scene.images["entry_short"]], (115, 340),(100, 325), 40, empty_msg="10")
    scene.chatboxes["turn_timer_entry"]  = ChatManager(font_30, [scene.images["entry_short"],scene.images["entry_short"],scene.images["entry_short"]], (405, 260),(390, 245), 40, empty_msg="120")
    scene.chatboxes["max_turns_entry"]  = ChatManager(font_30, [scene.images["entry_short"],scene.images["entry_short"],scene.images["entry_short"]], (405, 340),(390, 325), 40, empty_msg="50")

    scene.images["forward_txt"] = render_outlined_text("Select a Game!", font_30, (255,255,255),(142,5,2),4)
    scene.images["back_txt"] = render_outlined_text("Back", font_30, (255,255,255),(69,1,0),4)
    scene.images["choose_color_txt"] = render_outlined_text("Choose Your Color!", font_30, (255,255,255),Game.PLAYER_COLOR_VALUES[scene.variables["select_color_btn"]][1],4)

def change_win(button):
    server.selected_lobby = None
    button.press()

def draw_select(win, scene):
    server.get_lobbys()     #TODO maybe make this into a different function?

    win.fill((255, 228, 159))

    # Draw the window background
    win.blit(scene.images["menu"], scene.images["menu"].get_rect(center = (300,270)))

    # Draw all buttons
    for btn in scene.btns.values():
        btn.draw(win)

    # Draw x's over unavailable colors
    for color in server.get_selected_lobby_colors():
        pos = scene.btns[color].rect
        win.blit(scene.images["x"], pos)

    # Draw text over the buttons
    win.blit(scene.images["back_txt"], scene.images["back_txt"].get_rect(center = (715, 450)))
    win.blit(scene.images["choose_color_txt"], scene.images["choose_color_txt"].get_rect(center = (715, 190)))
    win.blit(scene.images["name_select"], scene.images["name_select"].get_rect(center = (715, 100)))

    #switch between displaying the host and join screens
    if not scene.btns["join_tab"].is_pressed():    

        # Draw the chat box for the player to enter their name
        select.chatboxes["name_entry"].draw(win)

        # Draw the join overlay on the window
        win.blit(scene.images["join_overlay"], scene.images["join_overlay"].get_rect(center = (300, 270)))

        # Update the text over the main button as needed
        if server.selected_lobby == None:
            scene.images["forward_txt"] = render_outlined_text("Select a Game!", font_30, (255,255,255),(142,5,2),4)
        else:
            # Draw the backing to the selected lobby
            pygame.draw.rect(win, (200,200,200), (64, 125 + 25 * server.selected_lobby, 472,25 ))

            scene.images["forward_txt"] = render_outlined_text("Join Game " + str(server.selected_lobby) + "!", font_30, (255,255,255),(142,5,2),4)
        win.blit(scene.images["forward_txt"], scene.images["forward_txt"].get_rect(center = (715, 390)))
        
        # Draw the text relating to the available lobbies
        draw_lobbies(font_30, 3)

    else:
        # Draw the host overlay on the window
        win.blit(scene.images["host_overlay"], scene.images["host_overlay"].get_rect(center = (280, 230)))

        # Draw all chat boxes
        for chat in select.chatboxes.values():
            chat.draw(win)

        # Update the text over the main button
        scene.images["forward_txt"] = render_outlined_text("Host Game!", font_30, (255,255,255),(142,5,2),4)
        win.blit(scene.images["forward_txt"], scene.images["forward_txt"].get_rect(center = (715, 390)))

# Helper function for draw_select()
def draw_lobbies(font, outline):
    for i, game in enumerate(server.lobbys):
        game_id = render_outlined_text(str(game[0]), font, (255,255,255),(69,1,0),outline)
        win.blit(game_id, game_id.get_rect(topleft = (80, 120 + 25 * i)))

        lobby_name = render_outlined_text(game[1], font, (255,255,255),(69,1,0),outline)
        win.blit(lobby_name, lobby_name.get_rect(topleft = (130, 120 + 25 * i)))

        host_name = render_outlined_text(game[2], font, (255,255,255),(69,1,0),outline)
        win.blit(host_name, host_name.get_rect(topleft = (330, 120 + 25 * i)))

        players = render_outlined_text(str(game[3]) + " / " + str(game[4]), font, (255,255,255),(69,1,0),outline)
        win.blit(players, players.get_rect(topleft = (450, 120 + 25 * i)))

def select_keydown(scene, event):   #TODO make this a general method
    for chat in scene.chatboxes.values():
        if chat.in_focus:
            if event.key == pygame.K_BACKSPACE:
                chat.msg = chat.msg[0:-1]
                chat.render_current_line()

def select_textinput(scene, event):
    for chat in scene.chatboxes.values():
        if chat.in_focus:
            chat.add_char(event.text)

def select_mousebuttondown(scene, event):
    x,y = pygame.mouse.get_pos()

    #FIXME is there a better way to do this logic? (also account for clicks that don't select buttons)
    select = None
    for key in scene.variables["player_colors"]:
        btn = scene.btns[key]
        
        color = btn.click(x,y, btn, scene.variables["select_color_btn"], [scene.btns[x] for x in scene.variables["player_colors"]], key)
        if color != None:
            select = color

    if select != None:
        if select == False:
            scene.variables["select_color_btn"] = None
            scene.images["choose_color_txt"] = render_outlined_text("Choose Your Color!", font_30, (255,255,255),Game.PLAYER_COLOR_VALUES[scene.variables["select_color_btn"]][1],4)
        else:
            scene.variables["select_color_btn"] = select
            scene.images["choose_color_txt"] = render_outlined_text("Choose Your Color!", font_30, (255,255,255),Game.PLAYER_COLOR_VALUES[select][1],4)

    scene.btns["back_btn"].click(x,y)

    host_entrys = [scene.chatboxes["lobby_name_entry"], scene.chatboxes["num_player_entry"], scene.chatboxes["vp_limit_entry"], scene.chatboxes["turn_timer_entry"], scene.chatboxes["max_turns_entry"]]
    scene.btns["join_btn"].click(x,y, scene.btns["join_tab"], center, [scene.chatboxes["name_entry"].msg, scene.variables["select_color_btn"]], host_entrys)    #FIXME

    scene.btns["join_tab"].click(x,y)
    scene.btns["host_tab"].click(x,y)

    # Check if the chat box has been pressed (start recieving text entry)
    for chat in scene.chatboxes.values():
        chat.check_focus(x,y)

    # Select a certain lobby
    if 65 <= x <= 535 and not scene.btns["join_tab"].is_pressed():
        if 0 <= (y - 120) // 25 <= len(server.lobbys)-1:
            server.selected_lobby = (y - 120) // 25

            scene.variables["select_color_btn"] = None
            scene.images["choose_color_txt"] = render_outlined_text("Choose Your Color!", font_30, (255,255,255),Game.PLAYER_COLOR_VALUES[scene.variables["select_color_btn"]][1],4)

            for btn in [scene.btns[x] for x in scene.variables["player_colors"]]:
                btn.clear(win)

            for k in server.get_selected_lobby_colors():
                scene.btns[k].pressed = True

# Helper method for select_mousebuttondown
def select_color_btn(clicked_btn, selected_color, player_color_btns, key_color):    # the clicked btn, the selected bu8tton, all of the color buttons , the current buttons string
    if key_color in server.get_selected_lobby_colors():  # get index color (string) of the clicked button
        clicked_btn.pressed = True
        return None

    if selected_color != None:
        if  select.btns[selected_color] == clicked_btn: # Unselect the current color
            for btn in player_color_btns:
                btn.clear(win)

            selected_color = False
        else:
            for btn in player_color_btns:
                if clicked_btn != btn:
                    btn.pressed = True
                else:
                    btn.clear(win)
            selected_color = key_color

    else:   #FIXME get rid of this duplicate code
        for btn in player_color_btns:
            if clicked_btn != btn:
                btn.pressed = True
            else:
                btn.clear(win)
        selected_color = key_color

    for k in server.get_selected_lobby_colors():
        select.btns[k].pressed = True

    return selected_color


select = SceneWrapper(init_select, draw_select)
select.add_event(pygame.MOUSEBUTTONDOWN, select_mousebuttondown)
select.add_event(pygame.KEYDOWN, select_keydown)
select.add_event(pygame.TEXTINPUT, select_textinput)




def add_host_game(idx, lobby_name, host_name, num_players, max_players):    #FIXME make sure this gets rid of closed lobbys
    server.lobbys[idx] = [idx, lobby_name, host_name, num_players, max_players]

def join_game(join_btn, center, player_info, host_info = None):    #TODO
    # General escape cases
    if player_info[0] == "" or player_info[1] == None :
        return
 
    if join_btn.pressed:

        if host_info[1].msg.isdigit() and host_info[1].msg != "":
            if int(host_info[1].msg) < 0 or int(host_info[1].msg) > 4 or host_info[0].msg == "":
                return
        else:
            return

        print("Hosting a game")
        server.add_msg(f"Host\n{player_info[0]}\n{host_info[0].msg}\n{host_info[1].msg}\n{player_info[1]}")   #TODO add player color here
    else:   
        # Join escape cases
        if server.selected_lobby == None or server.lobbys[server.selected_lobby][3] >= server.lobbys[server.selected_lobby][4]:
            return 

        print("Joining a game")
        
        server.add_msg("Join\n" + str(server.selected_lobby)+ "\n" + player_info[1])

    main.run(player_info)



#==== MAIN SCENE ====#
def init_main(scene, player_info):
    global player, players              #TODO make it so these aren't global??
    
    load_images_to("assets\\main_screen", scene.images)

    server.sync_with_server()
    
    Build.initialize()
    Resource.initialize(card_images)
    Dice.initialize(center)

    server.set_player(server.player_id, player_info[0], player_info[1])

    # Send a message to the connected lobby to add this player to the game
    server.add_msg("server.set_player(" +  str(server.player_id) +  ",\"" + player_info[0] + "\",\"" + player_info[1] + "\")")

    player = server.get_player(server.player_id)
    players = server.get_players()

    scene.chatboxes["chatbox"] = ChatManager(font_10, [chat_img, scroll_bar, scroll_point], (130,94), (20,165), 220, "Enter a message:")

def draw_main(win, scene):
    server.sync_with_server()
    
    win.fill((255, 228, 159))


    board_backing_rect = server.get_player(server.cur_turn).board.get_rect(center = (center[0] - 5, center[1]))
    win.blit(server.get_player(server.cur_turn).board,board_backing_rect)

  
    win.blit(scene.images["board"],scene.images["board"].get_rect(center = center))
    
    

    # Draw the player triangle
    player_rect = player.banner.get_rect(center = (center[0] - 120, center[1] - 185))
    win.blit(player.banner, player_rect)


    # Render the player's name and # of victory points TODO make these text objects in the scene
    text = render_outlined_text(player.name, font_30, (255,255,255), player.scolor, 3)
    win.blit(text, text.get_rect(topleft=(player_rect.topleft[0] + 10, player_rect.topleft[1] + 5)))

    text = render_outlined_text(str(server.get_player(server.player_id).vp) + " VP", font_30, (255,255,255), player.scolor, 3)
    win.blit(text, text.get_rect(topleft=(player_rect.topleft[0] + 10, player_rect.topleft[1] + 30)))

    # Draw the tiles on the board
    for tile in server.tile_list:
        tile.draw(win)
 
    # Draw all of the road bases, and road covers
    Point.draw_roads(win, server.get_players())

    # Draw the vertiex points and buildings
    for point in server.vertex_list:
        point.draw(win)

    # Draw the chatroom
    scene.chatboxes["chatbox"].draw(win)

    # Draw other UI Elements
    Dice.draw(win)
    Build.draw(win)

    next_turn_btn.draw(win)
    settings_btn.draw(win)

    #FIXME make a trade class and put this in there
    win.blit(scene.images["trade"], scene.images["trade"].get_rect(center = (center[0] - 115, center[1] + 185)))

    
    win.blit(scene.images["card_rect"], scene.images["card_rect"].get_rect(center = (130,410)))

   

    # Render opponent name tiles #TODO make this a list of opponents in the game, so this loop doesn't need to exist
    idx = 0
    for p in server.get_players():
        if p != server.get_player(server.player_id):        
            draw_player_tokens(win, p, 44 + idx * 87, 300)
            idx += 1

    # Draw the resource and dev cards
    for card in Resource.card_list.values():
        card.draw(win, font_10)

    DevCard.draw(win)

def draw_player_tokens(win, player, x, y):  #FIXME make sure text isn't rendered every frame?
    # Draw the trapizoid base
    op_rect = player.op.get_rect(center = (x, y))
    win.blit(player.op, op_rect)

    # Render and draw the opponent's name
    text = render_outlined_text(player.name, font_10, (255,255,255), player.scolor, 2)
    win.blit(text, text.get_rect(center = (x,  y - 10)))

    # Render and draw the opponent's # of victory points
    text = render_outlined_text( str(player.vp) + " VP", font_10, (255,255,255), player.scolor, 2)
    win.blit(text, text.get_rect(center = (x, y + 5)))
    
    # Render and draw the opponent's # of knight cards played
    win.blit(pygame.transform.scale_by(robber_img, 0.5), pygame.transform.scale_by(robber_img, 0.5).get_rect(center = (x - 25, y - 40)))
    text = render_outlined_text("x " + str(player.num_knights), font_10, (255,255,255), player.scolor, 2)
    win.blit(text, text.get_rect(center = (x - 10, y -50)))

    # Render and draw the opponent's longest road info
    win.blit(pygame.transform.rotozoom(player.road_r, 90, 0.4), pygame.transform.rotozoom(player.road_r, 90, 0.4).get_rect(center = (x + 10, y - 40)))
    text = render_outlined_text("x " + str(player.longest_road), font_10, (255,255,255), player.scolor, 2)
    win.blit(text, text.get_rect(center = (x + 25, y -50)))

def main_mousedown(scene, event):
    x,y = pygame.mouse.get_pos()

    # Check if Roll btn pressed
    Dice.check_collide(x,y)         

    next_turn_btn.click(x, y, next_turn_btn)       

    # Check if any of the build btns are pressed
    for btn in Build.btns:
        btn.click(x, y)

    # Check for build events
    Build.add_building(x,y)

    # Check if the chat box has been pressed (start recieving text entry)
    scene.chatboxes["chatbox"].check_focus(x,y)

    settings_btn.click(x,y)

    # Check to see if a dev card has been clicked
    if DevCard.selected:
        DevCard.selected.use_card()

    # Move the robber   #TODO remove this later when other logic is in place
    for tile in server.tile_list:
        if tile.is_clicked(x,y):
            # move_robber(tile_list.index(tile))
            call_move_robber(tile)

def main_textinput(scene, event):
    if scene.chatboxes["chatbox"].in_focus:
        scene.chatboxes["chatbox"].add_char(event.text)

def main_keydown(scene, event):
    global player, chatbox # TODO this will be removed in the future

    if scene.chatboxes["chatbox"].in_focus:
        if event.key == pygame.K_BACKSPACE:
            scene.chatboxes["chatbox"].msg = scene.chatboxes["chatbox"].msg[0:-1]
            scene.chatboxes["chatbox"].render_current_line()

        elif event.key == pygame.K_RETURN:
            if scene.chatboxes["chatbox"].msg != "":
  
                server.add_msg("main.chatboxes[\"chatbox\"].render_chat(\"" + player.name + "\" + \": \" +\""+ scene.chatboxes["chatbox"].msg + "\",(0,0,0))")

                scene.chatboxes["chatbox"].msg = ""
                scene.chatboxes["chatbox"].render_current_line()
 
    else:   
        if event.key == pygame.K_w:
            Build.state = Build.NOT_SELECTED
            for point in server.vertex_list:
                point.show = False

def main_mousemotion(scene, event):
    x,y  = pygame.mouse.get_pos()

     # if 10 <= x <= 250 and 320 <= y <= 380:    #FIXME
    collided = False
    for card in DevCard.drawn_cards:
        if card.rect.collidepoint(x,y):
            DevCard.selected = card
            collided = True

    if not collided:
        DevCard.selected = None

def main_mousewheel(scene, event):
    if event.y == -1 and scene.chatboxes["chatbox"].chat_offset > 0: 
        scene.chatboxes["chatbox"].chat_offset -= 1

    elif event.y == 1 and len(scene.chatboxes["chatbox"].chat_log) - scene.chatboxes["chatbox"].chat_offset - scene.chatboxes["chatbox"].NUM_CHAT_LINES > 0: 
        scene.chatboxes["chatbox"].chat_offset += 1

main = SceneWrapper(init_main, draw_main)
main.add_event(pygame.MOUSEBUTTONDOWN, main_mousedown)
main.add_event(pygame.KEYDOWN, main_keydown)
main.add_event(pygame.TEXTINPUT, main_textinput)
main.add_event(pygame.MOUSEMOTION, main_mousemotion)
main.add_event(pygame.MOUSEWHEEL, main_mousewheel)




# def leave_game(): #FIXME make this the method passed into the settigns button
#     server.add_msg(f"server.remove_player({server.player_id})")
#     title_screen()

settings_btn = Button(title.run, None, 840, 30, settings_img, settings_img)

def click_next_turn_btn(btn):
    if Dice.rolled and robber_moved:
        server.add_msg("server.next_turn()")

    btn.press()


next_turn_btn = Button(click_next_turn_btn, click_next_turn_btn, center[0] + 105, center[1] - 185, turn_img, robber_btn_img)



#TODO make scene objects for the below functions?
# FIXME make this a state machine, and not a function calling other functions





title.run()
