import pygame, sys
import random
from collections import namedtuple

GREEN = [(0, 100, 0), (89, 204, 0)]
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (35, 35, 35)
RED = (255, 0, 0)

WINDOW_SIZE = (660, 500)
BLOCK_SIZE = 20

AGENT_DIRECTION = {"up":[1,0,0,0], "down":[0,1,0,0], "left":[0,0,1,0], "right":[0,0,0,1]}

Position = namedtuple('Position', 'x, y')

class GameAI():
    """Game field class"""

    def __init__(self):
        """Initializes the game board"""
        # Pygame
        self.screen = pygame.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1]))
        self.clock = pygame.time.Clock()

        self.direction = "right" # Initial snake direction
        self.score = 0
        self.frame = 0
        self.game_over = False

        # Grid 
        self.n_blocks_col = WINDOW_SIZE[0] // BLOCK_SIZE
        self.n_blocks_row = WINDOW_SIZE[1] // BLOCK_SIZE
        self.draw_grid()

        # Entities
        self.snake = Snake(self.screen)
        self.apple = None
        self.spawn_apple()

        pygame.display.update()

    def spawn_apple(self):
        """Spawns apple in the game in a position that isn't a barrier or the snake"""
        while True:
            # Make sure apple cannot spawn in barrier
            x = random.randrange(BLOCK_SIZE, (WINDOW_SIZE[0]-BLOCK_SIZE), BLOCK_SIZE)
            y = random.randrange(BLOCK_SIZE,(WINDOW_SIZE[1]-BLOCK_SIZE), BLOCK_SIZE)

            # Check apple position is not snake
            if self.not_snake(Position(x, y)):
                self.apple = Position(x, y)
                self.draw_apple(self.apple)
                break

    def draw_apple(self, position):
        """Draws the apple in game
        
        Parameters
            position: (x, y) position to spawn the apple"""
        x = position.x
        y = position.y 
        pygame.draw.rect(self.screen, RED, ((x, y, BLOCK_SIZE, BLOCK_SIZE)), 2)
    
    def not_snake(self, position):
        """Returns whether a certain position is a snake or not
        
        Parameters
            position: (x, y) position to check
        
        Returns:
            bool: True of the given position is not a snake"""
        if position in self.snake.get_position():
            return False
        
        return True

    def draw_grid(self):
        """Draws the playing field into grid format
        
        Parameters
            screen: Game window
        """
        print(self.n_blocks_row-1, self.n_blocks_col-1)
        for x in range(self.n_blocks_col):
            for y in range(self.n_blocks_row):
                rect = pygame.Rect(x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)

                # Create padding/barriers on the outer edge
                if x == 0 or y == 0 or x == self.n_blocks_col-1 or y == self.n_blocks_row-1:
                    pygame.draw.rect(self.screen, WHITE, ((x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)), 2)
                else:
                    pygame.draw.rect(self.screen, GREY, rect, 1)
    
    def move_snake(self, ate_apple):
        """Moves the snake towards the current direction
        
        Parameters
            ate_apple: Boolean value if an apple was eaten"""
    
        snake_head = self.snake.get_position()[0]
        x = snake_head.x
        y = snake_head.y

        if self.direction == "up":
            y -= BLOCK_SIZE
        elif self.direction == "down":
            y += BLOCK_SIZE
        elif self.direction == "left":
            x -= BLOCK_SIZE
        elif self.direction == "right":
            x += BLOCK_SIZE
        
        self.snake.move(Position(x, y), ate_apple)
    
    def step(self):
        """Steps the game by 1 tick"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.snake.possible_move("up"):
                    self.direction = "up"
                elif event.key == pygame.K_DOWN and self.snake.possible_move("down"):
                    self.direction = "down"
                elif event.key == pygame.K_LEFT and self.snake.possible_move("left"):
                    self.direction = "left"
                elif event.key == pygame.K_RIGHT and self.snake.possible_move("right"):
                    self.direction = "right"

        if self.snake.snake_died():
            self.game_over = True
        
        if self.snake.get_position()[0] == self.apple:
            self.score += 1
            self.spawn_apple()
            self.move_snake(True)
        else:
            self.move_snake(False)
            
        
        pygame.display.update()
        self.clock.tick(20)

        return self.game_over, self.score
        
class Snake():
    """Represents the snake that the player will move in the game"""
    
    def __init__(self, screen):
        """Initializes snake at a given position

        Parameters
            screen: Game screen
        """
        self.screen = screen
        self.head = Position(6*BLOCK_SIZE, 10*BLOCK_SIZE)
        self.body = [self.head]
        self.colour = (0, 100, 0) 

        for i in range(4):
            self.body.append(Position(self.head.x-((i+1)*BLOCK_SIZE), self.head.y))
        
        self.draw()
        
    def draw(self):
        """Draws the snake on the game board within its current position"""
        for body in self.body:
            pygame.draw.rect(self.screen, self.colour, pygame.Rect(body.x, body.y, BLOCK_SIZE, BLOCK_SIZE))
    
    def delete_tail(self):
        """Deletes the tail of the snake when it's moved out of it's past position"""
        x = self.body[-1].x
        y = self.body[-1].y

        rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
        pygame.Surface.fill(self.screen, BLACK, rect)
        pygame.draw.rect(self.screen, GREY, rect, 1)

    def get_position(self):
        """Returns the position of the snake in list format"""
        return self.body
    
    def move(self, position, ate_apple):
        """Updates the position of the snake by 1 block
        
        Parameters
            position: new (x, y) head position of snake after moving 1 block
            ate_apple: Whether the snake ate an apple
        """

        # Update head
        self.head = position
        self.body.insert(0, self.head)

        # If an apple isn't eaten delete the tail
        if not ate_apple:
            self.delete_tail()
            self.body.pop(-1)
        
        self.draw()

    def snake_died(self):
        """Returns True if the snake has died
           1. Snake will die if it collides with itself
           2. Snake will die if it collides with a barrier
        """
        # Check if snake has eaten itself
        if self.head in self.body[1:]:
            return True

        # Check if it has hit the barriers
        if self.head.x < BLOCK_SIZE or self.head.y < BLOCK_SIZE or self.head.x > WINDOW_SIZE[0] - BLOCK_SIZE*2 or self.head.y > WINDOW_SIZE[1] - BLOCK_SIZE*2:
            return True

        return False
    
    def possible_move(self, direction):
        """Checks if a certain movement is possible for this snake. 
           1. If the snake is in an upwards position it cannot move down
           2. If the snake is in a downwards position it cannot move up
           3. If the snake is moving left it cannot move right
           4. If the snake is moving right it cannot move left
           
        Parameters
            direction: Direction to move the snake
            
        Returns
            bool: Whether moving in the direction in the current position is possible
        """

        can_move = True
        x = self.body[0].x
        y = self.body[0].y
        
        if direction == "up":
            y -= BLOCK_SIZE
        elif direction == "down":
            y += BLOCK_SIZE
        elif direction == "left":
            x -= BLOCK_SIZE 
        elif direction == "right":
            x += BLOCK_SIZE
        
        if Position(x, y) == self.body[1]:
            can_move = False
        
        return can_move

def main():
    game = GameAI()

    while True:
        game_over, score = game.step()

        if game_over == True:
            break
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
    

        