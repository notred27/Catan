class Player:
    def __init__(self, id, name, color, pcolor = (250,250,250), scolor = (0,0,0)):
        self.id = id
        self.name = name
        self.color = color 
        
        self.pcolor = pcolor 
        self.scolor = scolor 

        self.vp = 0
        self.num_knights = 0
        self.longest_road = 0

       

    def add_images(self, images):
        self.town_img = images[0]
        self.city_img = images[1]
        
        self.road_u = images[2]
        self.road_d = images[3]
        self.road_r = images[4]

        self.road_uC = images[5]
        self.road_dC = images[6]
        self.road_rC = images[7]

        self.banner = images[8]
        self.op = images[9]
        self.board = images[10]
        self.trade = images[11]


    def __str__(self):
        return f"Player ({self.name}, {self.id}, {self.color})"
        
    def __repr__(self):
        return f"Player ({self.name}, {self.id}, {self.color})"






