# FIXME make this non static
class ChatManager:  # TODO call this a chat box? (make a new class just for the chat box, another for the chat manager?)
    # msg = ""
        
    # curr_line = None
    # # msg_offset = 0

    # chat_log = []           # List of all of the lines that have been sent 
    # chat_offset = 0

    # WIDTH = 220
    # NUM_CHAT_LINES = 14
    # in_focus = False

    BLINK_RATE = 60


    GAME_MSG_COLOR = (42, 138, 222)
    # font = None


    # window_img = None
    # scroll_bar_img = None
    # scroll_pt_img = None




    def __init__(self,font, images, window_center, curr_line_topleft, width, empty_msg = ""):   
        self.font = font
        self.in_focus = False
        self.frame_num = ChatManager.BLINK_RATE
        
        self.WIDTH = width
        self.NUM_CHAT_LINES = 14

        self.window_img = images[0]
        self.scroll_bar_img = images[1]
        self.scroll_pt_img = images[2]

        self.empty_msg = empty_msg
        self.curr_line = font.render(empty_msg, 1, (150, 150, 150))


        self.window_center = window_center


        self.cl_tl = curr_line_topleft
        self.msg = ""
        self.curr_line = None
        self.chat_log = []           # List of all of the lines that have been sent 
        self.chat_offset = 0







    # TODO change this to render a 2d array of words, so individual words can have different colors / formatting
    # @staticmethod
    def render_chat(self, msg, color, initial_call = True):
        if initial_call:
            msg = msg.split(" ")

        txt = None
        for i in range(len(msg) + 1):
            if initial_call:
                text = self.font.render(" ".join(msg[:i]), 1, color)
            else:
                text = self.font.render("   " + " ".join(msg[:i]), 1, color)

            if text.get_width() > 210:
                break

            txt = text

        self.chat_log.append(txt)

        msg = msg[i - 1:]
        if len(msg) != 1:
            self.render_chat(msg, color, False)



    # @staticmethod
    # Only call this when the current line text is changed
    def render_current_line(self):
        # Try to render the whole message
        self.curr_line = self.font.render(self.msg, 1, (0,0,0))

        # Case where line extends off of the chatroom
        if self.curr_line.get_width() >= self.WIDTH: 

            for i in range(len(self.msg)):
                self.curr_line = self.font.render(self.msg[i:], 1, (0,0,0))

                if self.curr_line.get_width() <= self.WIDTH:
                    break

    
  


    # @staticmethod
    def draw(self, win):
        # Draw the chat window background
        chat_rect = self.window_img.get_rect(center = self.window_center)
        win.blit(self.window_img,chat_rect)

        # Draw the scroll bar if there are more lines than available
        if len(self.chat_log) > self.NUM_CHAT_LINES:
            self.scroll_bar_img_rect = self.scroll_bar_img.get_rect(center = (240,80))
            win.blit(self.scroll_bar_img, self.scroll_bar_img_rect)
            
            self.scroll_pt_img_rect = self.scroll_pt_img.get_rect(center = (240, 8 + 144 * ( len(self.chat_log) - self.chat_offset - self.NUM_CHAT_LINES) / (len(self.chat_log) - self.NUM_CHAT_LINES)))
            win.blit(self.scroll_pt_img, self.scroll_pt_img_rect)


        # Draw text in chatbox
        if len(self.chat_log) < self.NUM_CHAT_LINES:
            for i in range(len(self.chat_log)):
                win.blit(self.chat_log[i], self.chat_log[i].get_rect(topleft=(20, 11 * i)))

        else:
            for i in range(self.NUM_CHAT_LINES):
                win.blit(self.chat_log[-(i + self.chat_offset + 1)], self.chat_log[-(i + self.chat_offset)].get_rect(topleft=(20, 11 * (self.NUM_CHAT_LINES - 1 - i))))


        if self.curr_line != None:
        # ChatManager.render_current_line(win)
            win.blit(self.curr_line, self.curr_line.get_rect(topleft = self.cl_tl))


        # Blink curor animation
        if self.frame_num >= ChatManager.BLINK_RATE / 2 and self.in_focus:
            cursor = self.font.render("|", 1, (0,0,0))
            win.blit(cursor, cursor.get_rect(topleft = (self.cl_tl[0] + self.curr_line.get_width(), self.cl_tl[1])))

        # Update the cursor frame number
        if self.frame_num != 0:
            self.frame_num -= 1
        else:
            self.frame_num = ChatManager.BLINK_RATE


    # @staticmethod
    def add_char(self, c):
        try:
            self.msg += c
            self.render_current_line()
        except:
            print("key not supported :(")



    # @staticmethod
    def check_focus(self, x,y):   #FIXME make this a transparent surface???
        if self.window_img.get_rect(center = self.window_center).collidepoint(x,y):
            self.in_focus = True
            self.frame_num = ChatManager.BLINK_RATE
            self.render_current_line()

        else:
            self.in_focus = False

            if self.msg == "":
                self.curr_line = self.font.render(self.empty_msg, 1, (150, 150, 150))


