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

        # Game variables
        self.score = 0
        self.level = 1
        self.playerx = 400
        self.playery = 400
        self.platforms = [[400, 500]]
        self.cameray = 0
        self.jump = 0
        self.gravity = 0
        self.xmovement = 0
        self.achievements = []

    def draw_background(self):
        # Create a gradient effect for the sky background
        for y in range(600):
            ratio = y / 600
            color = (
                self.bg_color_top[0] * (1 - ratio) + self.bg_color_bottom[0] * ratio,
                self.bg_color_top[1] * (1 - ratio) + self.bg_color_bottom[1] * ratio,
                self.bg_color_top[2] * (1 - ratio) + self.bg_color_bottom[2] * ratio,
            )
            pygame.draw.line(self.screen, color, (0, y), (800, y))

    def update_player(self):
        # Handle player physics
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

        # Wrap the player around screen edges
        if self.playerx > 800:
            self.playerx = -50
        elif self.playerx < -50:
            self.playerx = 800

        # Move the camera up if the player gets too high
        if self.playery - self.cameray <= 200:
            self.cameray -= 10

        # Draw the player (star)
        self.screen.blit(self.star, (self.playerx, self.playery - self.cameray))

    def update_platforms(self):
        # Update platforms and check collisions
        for p in self.platforms:
            rect = pygame.Rect(p[0], p[1], 100, 10)
            player_rect = pygame.Rect(self.playerx, self.playery, self.star.get_width(), self.star.get_height())
            if rect.colliderect(player_rect) and self.gravity > 0 and self.playery < p[1] - self.cameray:
                self.jump = 15
                self.gravity = 0

        # Add new platforms based on level
        if self.platforms[-1][1] - self.cameray > 0:
            x = random.randint(50, 750)
            y = self.platforms[-1][1] - random.randint(50, 100)
            self.platforms.append([x, y])

        # Remove platforms that are off-screen
        if self.platforms[0][1] - self.cameray > 600:
            self.platforms.pop(0)

    def draw_platforms(self):
        for p in self.platforms:
            pygame.draw.rect(self.screen, self.platform_color, (p[0], p[1] - self.cameray, 100, 10))

    def game_over(self):
        game_over_font = pygame.font.SysFont("Arial", 50)
        game_over_text = game_over_font.render("Game Over!", True, (255, 0, 0))
        self.screen.blit(game_over_text, (300, 200))

        final_score = self.font.render(f"Final Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(final_score, (300, 250))

        restart_text = self.font.render("Press R to Restart or Q to Quit", True, (0, 0, 0))
        self.screen.blit(restart_text, (250, 300))

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
        self.score = 0
        self.level = 1
        self.playerx = 400
        self.playery = 400
        self.platforms = [[400, 500]]
        self.cameray = 0
        self.jump = 0
        self.gravity = 0
        self.xmovement = 0

    def update_level(self):
        # Increase level after every 100 points
        new_level = self.score // 100 + 1
        if new_level > self.level:
            self.level = new_level
            self.achievements.append(f"Level {self.level} Reached!")

    def draw_main_menu(self):
        menu_font = pygame.font.SysFont("Arial", 50)
        title_text = menu_font.render("Sky Leaf", True, (0, 0, 0))
        self.screen.blit(title_text, (300, 200))

        start_text = self.font.render("Press Enter to Start", True, (0, 0, 0))
        self.screen.blit(start_text, (300, 270))

        quit_text = self.font.render("Press Q to Quit", True, (0, 0, 0))
        self.screen.blit(quit_text, (300, 300))

        pygame.display.flip()

    def main_menu(self):
        # Main menu loop
        while True:
            self.screen.fill((255, 255, 255))  # White background for the menu
            self.draw_main_menu()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Start the game
                        return
                    elif event.key == pygame.K_q:  # Quit the game
                        pygame.quit()
                        sys.exit()

    def run(self):
        self.main_menu()  # Show the main menu before starting the game

        # Main game loop
        while True:
            self.clock.tick(30)
            self.draw_background()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.update_player()
            self.update_platforms()
            self.draw_platforms()

            # Score and achievements
            self.score += 1
            self.update_level()

            # Check if player falls below the screen
            if self.playery - self.cameray > 600:
                self.game_over()

            # Display score and level
            score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
            level_text = self.font.render(f"Level: {self.level}", True, (0, 0, 0))
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(level_text, (10, 40))

            pygame.display.flip()

if __name__ == "__main__":
    game = SkyLeaf()
    game.run()
