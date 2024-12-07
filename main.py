import pygame
import sys
import random

class SkyLeaf:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Sky Leaf")
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 25)

        # Colors
        self.bg_color_top = (135, 206, 250)  # Sky blue
        self.bg_color_bottom = (255, 255, 255)  # White

        # Game objects
        self.star = pygame.image.load("star.png").convert_alpha()  # Load star image
        self.star = pygame.transform.scale(self.star, (30, 30))  # Resize star to 30x30 pixels
        self.platform_color = (34, 139, 34)  # Green for platforms
        self.coin_image = pygame.image.load("coin.png").convert_alpha()  # Load coin image
        self.coin_image = pygame.transform.scale(self.coin_image, (20, 20))  # Resize coin to 20x20 pixels
        self.obstacle_image = pygame.image.load("obstacle.png").convert_alpha()  # Load obstacle image
        self.obstacle_image = pygame.transform.scale(self.obstacle_image, (30, 30))  # Resize obstacle

        # Game variables
        self.score = 0  # Total score (including time survival and coins)
        self.coins_collected = 0  # Number of coins collected
        self.level = 1
        self.playerx = 400
        self.playery = 400
        self.platforms = [[400, 500]]  # Initial platform
        self.coins = []  # List to hold coins
        self.obstacles = []  # List to hold obstacles
        self.cameray = 0
        self.jump = 0  # Jump height (force applied to player)
        self.gravity = 0  # Gravity effect
        self.xmovement = 0
        self.time_survived = 0  # Track time survived for scoring
        self.time_score_increment = 0  # Track time for score increment from survival

        # Coin collection indicator
        self.coin_collected = False  # To track when a coin is collected
        self.coin_collected_time = 0  # Time to show the coin collected message
        self.coin_message_duration = 30  # How many frames to display the message

    def draw_background(self):
        """Create a gradient effect for the sky background."""
        for y in range(600):
            ratio = y / 600
            color = (
                int(self.bg_color_top[0] * (1 - ratio) + self.bg_color_bottom[0] * ratio),
                int(self.bg_color_top[1] * (1 - ratio) + self.bg_color_bottom[1] * ratio),
                int(self.bg_color_top[2] * (1 - ratio) + self.bg_color_bottom[2] * ratio),
            )
            pygame.draw.line(self.screen, color, (0, y), (800, y))

    def update_player(self):
        """Handle player physics (jumping, gravity, and movement)."""
        if not self.jump:
            self.playery += self.gravity
            self.gravity += 1
        else:
            self.playery -= self.jump
            self.jump -= 1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            self.xmovement = 7
        elif keys[pygame.K_LEFT]:
            self.xmovement = -7
        else:
            self.xmovement = 0

        self.playerx += self.xmovement

        # Wrap player around screen edges
        if self.playerx > 800:
            self.playerx = -50
        elif self.playerx < -50:
            self.playerx = 800

        # Move the camera up if the player gets too high
        if self.playery - self.cameray <= 200:
            self.cameray -= 10

        # Draw the player
        self.screen.blit(self.star, (self.playerx, self.playery - self.cameray))

    def update_platforms(self):
        """Update platforms and handle player collisions."""
        for p in self.platforms:
            rect = pygame.Rect(p[0], p[1], 100, 10)
            player_rect = pygame.Rect(self.playerx, self.playery, self.star.get_width(), self.star.get_height())
            if rect.colliderect(player_rect) and self.gravity > 0 and self.playery < p[1] - self.cameray:
                self.jump = 20
                self.gravity = 0

        # Add new platforms
        if self.platforms[-1][1] - self.cameray > 0:
            x = random.randint(50, 750)
            y = self.platforms[-1][1] - random.randint(50, 100)
            self.platforms.append([x, y])

            # Spawn a coin on the new platform
            if random.random() < 0.5:
                coin_x = random.randint(x, x + 80)  # Coin within platform bounds
                coin_y = y - 30  # Slightly above the platform
                self.spawn_coin(coin_x, coin_y)

            # Spawn an obstacle on the new platform (with 30% probability)
            if random.random() < 0.3:
                obstacle_x = random.randint(x, x + 80)  # Obstacle within platform bounds
                obstacle_y = y - 30  # Slightly above the platform
                self.spawn_obstacle(obstacle_x, obstacle_y)

        # Remove platforms off-screen
        if self.platforms[0][1] - self.cameray > 600:
            self.platforms.pop(0)

    def spawn_coin(self, x, y):
        """Spawn a coin, checking if it overlaps with an obstacle."""
        for coin in self.coins:
            coin_rect = pygame.Rect(coin[0], coin[1], 20, 20)
            new_coin_rect = pygame.Rect(x, y, 20, 20)
            if coin_rect.colliderect(new_coin_rect):
                # Adjust the coin's position if it overlaps with another
                y -= 10  # Shift the coin's Y position a bit
        self.coins.append([x, y])

    def spawn_obstacle(self, x, y):
        """Spawn an obstacle, checking if it overlaps with another obstacle."""
        while any(pygame.Rect(x, y, 30, 30).colliderect(pygame.Rect(obstacle[0], obstacle[1], 30, 30)) for obstacle in self.obstacles):
            x = random.randint(50, 750)
            y = self.platforms[-1][1] - random.randint(50, 100)
        self.obstacles.append([x, y])

    def check_coin_collection(self):
        """Check if the player collects a coin."""
        player_rect = pygame.Rect(self.playerx, self.playery - self.cameray, self.star.get_width(), self.star.get_height())
        for coin in self.coins[:]:
            coin_rect = pygame.Rect(coin[0], coin[1] - self.cameray, 20, 20)
            if player_rect.colliderect(coin_rect):
                self.coins.remove(coin)
                self.score += 10  # Increment score by 10 for each coin collected
                self.coins_collected += 1  # Track the number of coins collected
                self.coin_collected = True  # Trigger the coin collection indicator
                self.coin_collected_time = self.coin_message_duration  # Set the time for the message

    def check_obstacle_collision(self):
        """Check if the player collides with an obstacle."""
        player_rect = pygame.Rect(self.playerx, self.playery - self.cameray, self.star.get_width(), self.star.get_height())
        for obstacle in self.obstacles[:]:
            obstacle_rect = pygame.Rect(obstacle[0], obstacle[1] - self.cameray, 30, 30)
            if player_rect.colliderect(obstacle_rect):
                self.game_over()  # Game over if player hits an obstacle

    def draw_platforms(self):
        """Draw the platforms."""
        for p in self.platforms:
            pygame.draw.rect(self.screen, self.platform_color, (p[0], p[1] - self.cameray, 100, 10))

    def draw_coins(self):
        """Draw the coins."""
        for coin in self.coins:
            self.screen.blit(self.coin_image, (coin[0], coin[1] - self.cameray))

    def draw_obstacles(self):
        """Draw the obstacles."""
        for obstacle in self.obstacles:
            self.screen.blit(self.obstacle_image, (obstacle[0], obstacle[1] - self.cameray))

    def display_coin_collected_indicator(self):
        """Display a brief 'Coin Collected!' indicator."""
        if self.coin_collected:
            coin_collected_text = self.font.render("Coin Collected!", True, (255, 215, 0))  # Golden color
            self.screen.blit(coin_collected_text, (320, 250))  # Show it at the center of the screen
            self.coin_collected_time -= 1  # Decrease the time until it disappears

            # If the message duration is over, reset the flag
            if self.coin_collected_time <= 0:
                self.coin_collected = False

    def game_over(self):
        """Display the game over screen."""
        self.screen.fill((255, 255, 255))
        game_over_font = pygame.font.SysFont("Arial", 50)
        game_over_text = game_over_font.render("Game Over!", True, (255, 0, 0))
        self.screen.blit(game_over_text, (300, 200))

        final_score = self.font.render(f"Final Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(final_score, (300, 250))

        final_coins = self.font.render(f"Coins Collected: {self.coins_collected}", True, (0, 0, 0))
        self.screen.blit(final_coins, (300, 300))

        restart_text = self.font.render("Press R to Restart or Q to Quit", True, (0, 0, 0))
        self.screen.blit(restart_text, (250, 350))

        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        waiting = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def reset_game(self):
        """Reset the game variables."""
        self.score = 0
        self.coins_collected = 0
        self.level = 1
        self.playerx = 400
        self.playery = 400
        self.platforms = [[400, 500]]
        self.coins = []
        self.obstacles = []  # Reset obstacles
        self.cameray = 0
        self.jump = 0
        self.gravity = 0
        self.xmovement = 0
        self.time_survived = 0
        self.time_score_increment = 0  # Reset score increment timer
        self.coin_collected = False  # Reset the coin collected indicator
        self.coin_collected_time = 0

    def update_level(self):
        """Increase the level based on score."""
        if self.score >= 100 * self.level:
            self.level += 1

    def show_instructions(self):
        """Show the instructions screen before starting the game."""
        self.screen.fill((255, 255, 255))  # White background
        instruction_font = pygame.font.SysFont("Arial", 30)
        
        instructions_text = [
            "Welcome to Sky Leaf!",
            "Use Arrow Keys to move left and right.",
            "Press SPACE to jump.",
            "Collect coins to increase your score.",
            "Avoid obstacles!",
            "Press ENTER to Start!"
        ]
        
        y_pos = 150
        for line in instructions_text:
            instruction_surface = instruction_font.render(line, True, (0, 0, 0))
            self.screen.blit(instruction_surface, (150, y_pos))
            y_pos += 40
        
        pygame.display.flip()

        # Wait for the player to press ENTER to start the game
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Start the game
                        waiting = False

    def run(self):
        """Run the game loop."""
        self.show_instructions()  # Display the instructions before starting

        while True:
            self.clock.tick(30)
            self.draw_background()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.update_player()
            self.update_platforms()
            self.check_coin_collection()
            self.check_obstacle_collision()  # Check if player hits any obstacle
            self.draw_platforms()
            self.draw_coins()
            self.draw_obstacles()  # Draw obstacles
            self.display_coin_collected_indicator()

            # Increment score for survival time
            self.time_survived += 1
            if self.time_survived % 30 == 0:
                self.time_score_increment += 1
                if self.time_score_increment % 2 == 0:
                    self.score += 5  # Increment score for survival every 2 seconds

            # Update the level based on the score
            self.update_level()

            # Check if player falls below screen
            if self.playery - self.cameray > 600:
                self.game_over()

            # Display score, level, and coins collected
            score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
            level_text = self.font.render(f"Level: {self.level}", True, (0, 0, 0))
            coins_text = self.font.render(f"Coins: {self.coins_collected}", True, (0, 0, 0))
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(level_text, (10, 40))
            self.screen.blit(coins_text, (10, 70))

            pygame.display.flip()

if __name__ == "__main__":
    game = SkyLeaf()
    game.run()
