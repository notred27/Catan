import math



class Tile:
    def __init__(self, pos, board_center,type, number, tile_img, token_img, robber_img):
        
        # Offset for edge case around symmetry of 0
        if pos[1] >= 0 and pos[2] != 0:
            pos[1] -= 1

        # Find the center of the tile (based on the baord position)
        self.center = (board_center[0] - 5 + pos[0] * 136 + pos[2]*68, board_center[1] + pos[1] * -78 + abs(pos[2]) * -39)
        self.type = type
        self.number = number
        self.tile_img = tile_img
        self.token_img = token_img
        self.robber = False
        self.robber_img = robber_img
        # self.circle = self.token_img.get_rect(center = self.center)
        

        

    # Draw this tile to the game board (based on the board's location in the window)
    def draw(self, win):
        # Draw tile's image
        img_rect = self.tile_img.get_rect(center = self.center)
        win.blit(self.tile_img,img_rect)

        # Draw token's image (if one exists)
        if self.token_img != None:
            img_rect = self.token_img.get_rect(center = self.center)
            win.blit(self.token_img,img_rect)
            # font = pygame.font.SysFont("timesnewromans", 60)
            # text = font.render(str(self.number), 1, (251, 255, 103))
            # win.blit(text, text.get_rect(center=self.center))

        if self.robber:
            rob_rect = self.robber_img.get_rect(center = self.center)
            win.blit(self.robber_img,rob_rect)


    def is_clicked(self,x,y):
        if math.sqrt((x - self.center[0]) * (x - self.center[0]) + (y - self.center[1]) * (y - self.center[1])) <= 38:
            return True
        return False


