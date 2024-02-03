
class Resource:
    GRAIN = 0
    LUMBER = 1
    WOOL = 2
    ORE = 3
    BRICK = 4

    card_list = {}

    @staticmethod
    def initialize(card_images):
        # Initialize cards
        Resource.card_list["grain"] = Resource(Resource.GRAIN, card_images["grain"], 9,480)
        Resource.card_list["wool"] = Resource(Resource.WOOL, card_images["wool"], 57,480)
        Resource.card_list["lumber"] = Resource(Resource.LUMBER, card_images["lumber"], 105,480)
        Resource.card_list["brick"] = Resource(Resource.BRICK, card_images["brick"], 153,480)
        Resource.card_list["ore"] = Resource(Resource.ORE, card_images["ore"], 201,480)


    def __init__(self, type, img, x, y):
        self.type = type
        self.img = img

        #bottom left corner
        self.x = x
        self.y = y

        self.amount = 0


    def add_resource(self, num):
        self.amount += num


    def remove_resource(self, num): 
        # Returns true if that amount can be removed, false otherwise
        if self.amount - num >= 0:
            self.amount -= num
            return True

        return False


    def draw(self, win, font):
        if self.amount >= 3:
            rect = self.img.get_rect(bottomleft = (self.x + 12, self.y - 12))
            win.blit(self.img, rect)

        if self.amount >= 2:
            rect = self.img.get_rect(bottomleft = (self.x + 6, self.y - 6))
            win.blit(self.img, rect)

        if self.amount >= 1:
            rect = self.img.get_rect(bottomleft = (self.x, self.y))
            win.blit(self.img, rect)

            num = font.render("x " + str(self.amount), 1, (200,0,0))
            win.blit(num, num.get_rect(topleft = (self.x + 32, self.y - 5 )))

