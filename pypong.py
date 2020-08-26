import pygame
import os


running = True
width = None
height = None
fore_color = (100, 100, 0)
back_color = (0, 0, 0)


def main():
    window = init_display("PyPong")
    play(window)
    

def play(window):
    global running
    global width
    global height
    global fore_color
    global back_color
    
    # create and draw ball and paddles
    ball = Ball(int(width / 400), (int(width / 2), int(height / 2)), int(height / 30))
    paddle1 = Paddle((int(width * 0.05), int(height / 2)), int(height / 5))
    paddle2 = Paddle((int(width * 0.95), int(height / 2)), int(height / 5))
    
    while running:
        pygame.time.wait(10)
        
        window.fill(back_color, rect=ball.rect)
        window.fill(back_color, rect=paddle1.rect)
        window.fill(back_color, rect=paddle2.rect)
        
        ball.step_position()
        
        check_collide(ball, paddle1)
        check_collide(ball, paddle2)
        
        window.fill(fore_color, rect=ball.rect)
        window.fill(fore_color, rect=paddle1.rect)
        window.fill(fore_color, rect=paddle2.rect)
        
        pygame.display.update()
        
        quit_events = pygame.event.get(pygame.QUIT)
        if len(quit_events) > 0:
            running = False
            

def check_collide(ball, paddle):
    if paddle.rect.colliderect(ball.rect):
        ball_position_y = ball.position[1]
        paddle_position_y = paddle.position[1]
        paddle_height = paddle.paddle_height
        offset = ball_position_y - paddle_position_y
        deflect_value = offset / (paddle_height / 2)
        ball.paddle_bounce(deflect_value)
    

# returns a window for the game
def init_display(title):
    global width
    global height
    
    #os.environ["SDL_VIDEO_CENTERED"] = "1"  # centers window in screen
    pygame.init()
    display_info = pygame.display.Info()    # object with display info
    pygame.display.set_caption(title)       # set title
    
    # load and set icon
    icon = pygame.image.load(os.path.join("assets", "pypong_icon.png"))
    pygame.display.set_icon(icon)
    
    # set window size w/ info from display_info
    width = display_info.current_w
    height = display_info.current_h
    
    return pygame.display.set_mode((width, height))


class Ball:
    def __init__(self, speed, init_position, size):
        self.speed = speed                  # total speed
        self.x_spd = speed                  # x-component of total speed, initially equal to total speed
        self.y_spd = 0                      # y-component of total speed, initially 0
        self.init_position = init_position  # initial position, expressed as (int, int)
        self.position = init_position       # tuple representing current position
        self.size = int(size)               # ball is a square, and size is the length in px of each side
        self.set_rect()                     # rectangle representing the space occupied by the ball onscreen
        
    # updates the position and corresponding rect for the ball
    def step_position(self):
        self.position = self.position[0] + self.x_spd, self.position[1] + self.y_spd
        self.set_rect()
    
    # mirrors y_spd (for bounces off top & bottom walls, where x_spd doesn't change)
    def wall_bounce(self):
        self.y_spd = 0 - self.y_spd
    
    # changes x_spd & y_spd based on angle leaving the paddle
    def paddle_bounce(self, deflect_value):
        if self.x_spd > 0:
            self.x_spd = 0 - int((self.speed * (1 - deflect_value)))
        else:
            self.x_spd = int(self.speed * (1 - deflect_value))
        
        if self.y_spd > 0:
            self.y_spd = 0 - int((self.speed * deflect_value))
        else:
            self.y_spd = int(self.speed * deflect_value)
    
    # resets position and speed of ball to initial values
    def reset_ball(self):
        self.x_spd = self.speed
        self.y_spd = 0
        self.rect = self.set_rect()
    
    # creates a Rect based on the size and position of the Ball
    def set_rect(self):
        self.rect = pygame.Rect(int(self.position[0] - (0.5 * self.size)), int(self.position[1] - (0.5 * self.size)), self.size, self.size)
        

class Paddle:
    def __init__(self, init_position, paddle_height):
        self.init_position = init_position                  # tuple that represents starting position of paddle
        self.position = init_position                       # tuple that represents current position of paddle
        self.paddle_height = int(paddle_height)             # height of paddle
        self.paddle_width = int(self.paddle_height * 0.15)  # width is 10% of height
        self.set_rect()
    
    def reset_paddle(self):
        self.position = self.init_position
        self.set_rect()
    
    # makes a Rect based on dimensions and position of Paddle
    def set_rect(self):
        self.rect = pygame.Rect(int(self.position[0] - (0.5 * self.paddle_width)), 
                                int(self.position[1] - (0.5 * self.paddle_height)), 
                                self.paddle_width, self.paddle_height)


if __name__ == "__main__":
    main()
