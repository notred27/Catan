
class Button:
    def __init__(self, func_u, func_d, x, y, img_u, img_d):
        self.func_u = func_u
        self.func_d = func_d


        self.img_u = img_u
        self.img_d = img_d

        self.rect = img_u.get_rect(center = (x,y))

        self.pressed = False
        self.timer = 0

    def clear(self, win):
        self.pressed = False
        self.draw(win)

    def draw(self, win): 

        if self.timer > 0:
            self.timer -= 1

            if self.timer == 0:
                self.pressed = False

        if self.pressed:
            win.blit(self.img_d, self.rect)
        else:
            win.blit(self.img_u, self.rect)

    def set_pos(self, x, y):
        self.rect = self.img_u.get_rect(center = (x,y))


    def click(self, x, y, *args): 
        if self.rect.collidepoint(x, y):
            if self.img_u.get_at((x - self.rect.topleft[0], y - self.rect.topleft[1]))[3]:
                self.pressed = not self.pressed

                if self.func_u != None and self.pressed:
                    return self.func_u(*args)

                elif self.func_d != None and not self.pressed:
                    return self.func_d(*args)

    def press(self):
        self.pressed = not self.pressed

    def is_pressed(self):
        return self.pressed
