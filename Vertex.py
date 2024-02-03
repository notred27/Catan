import math

class State:
    EMPTY = 0
    ROAD = 1
    TOWN = 2
    CITY = 3


class Point:
    _road_list = []
    MAX_FRAMES = 20

    @staticmethod
    def draw_roads(win, players):    # TODO make 4 different Surfaces to draw to to make this more efficient
        for p in players:
            for road in Point._road_list:
                if p.id == road.player:
                    road.draw(win)

            for road in Point._road_list:
                if p.id == road.player:
                    road.draw_covers(win)


    @staticmethod
    def road_exists(pt1, pt2):
        x = (pt2.x + pt1.x) / 2
        y = (pt2.y + pt1.y) / 2

        for road in Point._road_list:
            if road.x == x and road.y == y:
                return True
            
        return False

    #p1 is new point, pt2 is the source
    @staticmethod
    def add_road(player, pt1, pt2):
        pt1.roads += 1
        pt2.roads += 1

        if pt1.state == State.EMPTY:
            pt1.state = State.ROAD
        pt1.players.append(player.id)

        if pt1.y > pt2.y:
            if pt1.x > pt2.x:
                Point._road_list.insert(0, Road(player.road_u, pt1, pt2, "SE", player.road_uC, player.id))
            else:
                Point._road_list.insert(0, Road(player.road_d, pt1, pt2, "SW", player.road_dC, player.id)) 

        elif pt1.y < pt2.y:
            if pt1.x < pt2.x:
                Point._road_list.insert(0, Road(player.road_u, pt1, pt2, "NW", player.road_uC, player.id))
            else:
                Point._road_list.insert(0, Road(player.road_d, pt1, pt2, "NE", player.road_dC, player.id))

        else:
            if pt1.x < pt2.x:
                Point._road_list.insert(0, Road(player.road_r, pt1, pt2, "L", player.road_rC, player.id)) 
            else:
                Point._road_list.insert(0, Road(player.road_r, pt1, pt2, "R", player.road_rC, player.id)) 

    

    def __init__(self, img, tiles, pt1 = None, pt2 = None):
        self.tiles = tiles  # The neighboring tiles to each point
        self.x, self.y = self.calculate_center(pt1, pt2)
        self.neighbors = [] #The neighboring points reachable from this one



        self.state = State.EMPTY
        self.show = True    # TO show the point or not

        self.players = []      # Players that have a structure involving this vertex





        self.roads = 0


        self.pt_img = img   # To store the image for the vertex
        self.pt_rect = self.pt_img.get_rect(center = (self.x, self.y))

        self.img = None      # To store the images from buildings
        self.rect = self.pt_img.get_rect(center = (self.x, self.y))
        


        self.frame = 0
        self.y_off = 0


        

    def calculate_center(self, pt1, pt2):
        x, y = 0, 0

        match (len(self.tiles)):
            case 3:
                x = (self.tiles[0].center[0] + self.tiles[1].center[0] + self.tiles[2].center[0]) / 3
                y = (self.tiles[0].center[1] + self.tiles[1].center[1] + self.tiles[2].center[1]) / 3

            case 2:
                x = (self.tiles[0].center[0] + self.tiles[1].center[0] + pt1[0]) / 3
                y = (self.tiles[0].center[1] + self.tiles[1].center[1] + pt1[1]) / 3
            
            case _:
                x = (self.tiles[0].center[0] + pt2[0] + pt1[0]) / 3
                y = (self.tiles[0].center[1] + pt2[1] + pt1[1]) / 3

        return (x, y)


    def draw(self, win):
        self.animate()

        if self.img != None:
            win.blit(self.img,self.rect)

        if self.show:
            win.blit(self.pt_img,self.pt_rect)


    def animate(self):
        if self.frame != 0: # Animation check
            self.y_off -= math.sin( (Point.MAX_FRAMES - self.frame)  * 2 * 3.14 / Point.MAX_FRAMES) * 2 
            self.rect = self.img.get_rect(center = (self.x, self.y + self.y_off))
            self.frame -= 1

            

    def to_town(self, player):
        self.players.append(player.id)
        self.state = State.TOWN
        self.img = player.town_img
        self.y_off = -7
        self.frame = self.MAX_FRAMES


    def to_city(self, player):
        if not player.id in self.players:
            return

        self.state = State.CITY
        self.img = player.city_img
        self.y_off = -10
        self.frame = self.MAX_FRAMES


    def dist_to(self, point):
        return math.sqrt((self.x - point.x) * (self.x - point.x) + (self.y - point.y) * (self.y - point.y))


    def add_neighbor(self, point):
        self.neighbors.append(point)


    


    





class Road:
    def __init__(self, img, pt1,pt2, orient, cover, player):
        self.player = player
        self.x = (pt2.x + pt1.x) / 2
        self.y = (pt2.y + pt1.y) / 2

        self.img = img
        self.rect = img.get_rect(center = (self.x, self.y))

        self.pt1 = pt1
        self.pt2 = pt2
        self.frame = Point.MAX_FRAMES 

        self.cover = cover

        #TODO Adjust covers to better fit roads (also make sure images are standardized)
        if orient == "SE":
            self.cover_rect = self.cover.get_rect(center = (pt2.x + 2, pt2.y + 2))
        elif orient == "SW":
            self.cover_rect = self.cover.get_rect(center = (pt2.x - 3, pt2.y + 2))

        elif orient == "NE":
            self.cover_rect = self.cover.get_rect(center = (pt2.x +1, pt2.y - 4))

        elif orient == "NW":
            self.cover_rect = self.cover.get_rect(center = (pt2.x -2, pt2.y -4))

        elif orient == "R":
            self.cover_rect = self.cover.get_rect(center = (pt2.x + 2, pt2.y + 1))

        elif orient == "L":
            self.cover_rect = self.cover.get_rect(center = (pt2.x - 4, pt2.y + 1))

        else:
            self.cover_rect = self.cover.get_rect(center = (pt2.x, pt2.y))


    def draw(self, win):
        self.animate()
        win.blit(self.img, self.rect)


    def animate(self):
        if self.frame != 0: # Animation check
    
            self.rect = self.img.get_rect(center = (self.x, self.y - math.sin( (Point.MAX_FRAMES - self.frame)  * 2 * 3.14 / Point.MAX_FRAMES) * 2))
            self.frame -= 1


    def draw_covers(self, win):
        if self.cover != None and self.frame == 0:
            win.blit(self.cover, self.cover_rect)

