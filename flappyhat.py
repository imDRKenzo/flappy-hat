import pygame
from sys import exit
import random

GAME_WIDTH = 360
GAME_HEIGHT = 640
GROUND_Y = GAME_HEIGHT - 80 

pygame.init() 
window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption("Flappy Hat")
clock = pygame.time.Clock()

title_font = pygame.font.SysFont("Comic Sans MS", 55, bold=True)
game_font = pygame.font.SysFont("Comic Sans MS", 35)
score_font = pygame.font.SysFont("Comic Sans MS", 45)

background_image = pygame.image.load("flappyhatbg.png").convert()

hat_images = [
    pygame.transform.scale(pygame.image.load("flappyhat1.png").convert_alpha(), (48, 42)),
    pygame.transform.scale(pygame.image.load("flappyhat2.png").convert_alpha(), (48, 42)),
    pygame.transform.scale(pygame.image.load("flappyhat3.png").convert_alpha(), (48, 42))
]

top_ruler_image = pygame.image.load("topruler.png").convert_alpha()
top_ruler_image = pygame.transform.scale(top_ruler_image, (68, 512))
bottom_ruler_image = pygame.image.load("bottomruler.png").convert_alpha()
bottom_ruler_image = pygame.transform.scale(bottom_ruler_image, (68, 512))


class Hat:
    def __init__(self, images, x, y):
        self.images = images
        self.image_index = 0
        self.animation_timer = 0
        self.original_img = self.images[self.image_index]
        self.img = self.original_img
        
        self.exact_y = float(y)
        self.rect = self.img.get_rect(center=(x, int(self.exact_y)))
        self.hitbox = self.rect.inflate(-16, -12) 
        
        self.velocity_y = 0
        self.gravity = 0.55
        self.jump_strength = -7.5 

    def animate(self):
        self.animation_timer += 1
        if self.animation_timer >= 5:
            self.animation_timer = 0
            self.image_index += 1
            if self.image_index > 2:
                self.image_index = 0
            self.original_img = self.images[self.image_index]
            self.img = self.original_img 

    def jump(self):
        self.velocity_y = self.jump_strength

    def move(self):
        self.animate()
        
        self.velocity_y += self.gravity
        self.exact_y += self.velocity_y
        self.rect.y = int(self.exact_y) 
        
        if self.rect.top < 0:
            self.rect.top = 0
            self.exact_y = float(self.rect.y)
            self.velocity_y = 0
            
        self.hitbox.center = self.rect.center

        rotation = self.velocity_y * -3
        rotation = max(-90, min(rotation, 25))
        self.img = pygame.transform.rotate(self.original_img, rotation)

    def draw(self, surface):
        rotated_rect = self.img.get_rect(center=self.rect.center)
        surface.blit(self.img, rotated_rect.topleft)


class Ruler:
    def __init__(self, img, x, y):
        self.img = img
        self.exact_x = float(x)
        self.rect = self.img.get_rect(topleft=(int(self.exact_x), y))
        self.passed = False

    def move(self, speed):
        self.exact_x += speed
        self.rect.x = int(self.exact_x)

    def draw(self, surface):
        surface.blit(self.img, self.rect)


class FlappyHatGame:
    def __init__(self):
        self.state = "MENU"
        self.scroll_speed = -3.8 
        self.ground_scroll = 0
        
        self.start_btn = pygame.Rect(GAME_WIDTH/2 - 80, GAME_HEIGHT/2 + 20, 160, 60)
        self.ok_btn = pygame.Rect(GAME_WIDTH/2 - 60, GAME_HEIGHT/2 + 60, 120, 60)
        
        self.reset_game()

    def reset_game(self):
        self.hat = Hat(hat_images, GAME_WIDTH / 8 + 24, GAME_HEIGHT / 2)
        self.rulers = []
        self.score = 0
        self.distance_traveled = 240 

    def create_rulers(self):
        ruler_height = 512
        random_ruler_y = -ruler_height/4 - random.random()*(ruler_height/2)
        opening_space = GAME_HEIGHT / 5.2 

        top_ruler = Ruler(top_ruler_image, GAME_WIDTH, random_ruler_y)
        self.rulers.append(top_ruler)

        bottom_ruler = Ruler(bottom_ruler_image, GAME_WIDTH, top_ruler.rect.bottom + opening_space)
        self.rulers.append(bottom_ruler)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "MENU" and self.start_btn.collidepoint(event.pos):
                    self.reset_game()
                    self.state = "READY"
                elif self.state == "GAMEOVER" and self.ok_btn.collidepoint(event.pos):
                    self.state = "MENU"
            
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_x, pygame.K_UP):
                    if self.state == "READY":
                        self.state = "PLAYING"
                        self.hat.jump()
                    elif self.state == "PLAYING":
                        self.hat.jump()

    def update(self):
        if self.state == "PLAYING":
            self.ground_scroll += self.scroll_speed
            if self.ground_scroll <= -GAME_WIDTH:
                self.ground_scroll = 0

        if self.state == "READY":
            self.hat.animate()

        elif self.state == "PLAYING":
            self.hat.move()

            self.distance_traveled += abs(self.scroll_speed)
            if self.distance_traveled >= 240: 
                self.create_rulers()
                self.distance_traveled = 0

            for ruler in self.rulers:
                ruler.move(self.scroll_speed)

                if not ruler.passed and self.hat.rect.left > ruler.rect.right:
                    self.score += 0.5 
                    ruler.passed = True
                
                if self.hat.hitbox.colliderect(ruler.rect):
                    self.state = "FALLING"

            if self.hat.hitbox.bottom >= GROUND_Y:
                self.hat.rect.bottom = GROUND_Y + (self.hat.rect.height - self.hat.hitbox.height)/2
                self.state = "GAMEOVER"

            while len(self.rulers) > 0 and self.rulers[0].rect.right < 0:
                self.rulers.pop(0)

        elif self.state == "FALLING":
            self.hat.move() 
            if self.hat.hitbox.bottom >= GROUND_Y:
                self.hat.rect.bottom = GROUND_Y + (self.hat.rect.height - self.hat.hitbox.height)/2
                self.state = "GAMEOVER"


    def draw(self):
        window.blit(background_image, (0, 0))
        
        for ruler in self.rulers:
            ruler.draw(window)
            
        pygame.draw.rect(window, (222, 216, 149), (0, GROUND_Y, GAME_WIDTH, GAME_HEIGHT - GROUND_Y))
        pygame.draw.rect(window, (115, 191, 46), (0, GROUND_Y, GAME_WIDTH, 12)) 
        
        for i in range(25):
            line_x = self.ground_scroll + (i * 30)
            if -20 < line_x < GAME_WIDTH + 20: 
                pygame.draw.line(window, (90, 160, 30), (line_x, GROUND_Y), (line_x - 12, GROUND_Y + 12), 4)

        if self.state != "MENU":
            self.hat.draw(window)

        if self.state == "MENU":
            title_text = title_font.render("Flappy Hat", True, "white")
            window.blit(title_text, (GAME_WIDTH/2 - title_text.get_width()/2, GAME_HEIGHT/3))
            
            mouse_pos = pygame.mouse.get_pos()
            btn_color = (255, 165, 0) if self.start_btn.collidepoint(mouse_pos) else (200, 100, 0) 
            
            pygame.draw.rect(window, btn_color, self.start_btn, border_radius=10)
            pygame.draw.rect(window, "white", self.start_btn, 4, border_radius=10) 
            
            start_txt = game_font.render("START", True, "white")
            window.blit(start_txt, (self.start_btn.centerx - start_txt.get_width()/2, self.start_btn.centery - start_txt.get_height()/2))

        elif self.state == "READY":
            ready_txt = title_font.render("Get Ready!", True, "white")
            space_txt = game_font.render("Press SPACE", True, "white")
            window.blit(ready_txt, (GAME_WIDTH/2 - ready_txt.get_width()/2, GAME_HEIGHT/4))
            window.blit(space_txt, (GAME_WIDTH/2 - space_txt.get_width()/2, GAME_HEIGHT/2 + 50))

        elif self.state in ["PLAYING", "FALLING"]:
            score_str = score_font.render(str(int(self.score)), True, "white")
            window.blit(score_str, (GAME_WIDTH/2 - score_str.get_width()/2, 50))

        elif self.state == "GAMEOVER":
            over_text = title_font.render("Game Over!", True, "white")
            final_score_text = game_font.render(f"Score: {int(self.score)}", True, "white")
            
            window.blit(over_text, (GAME_WIDTH/2 - over_text.get_width()/2, GAME_HEIGHT/4 - 20))
            window.blit(final_score_text, (GAME_WIDTH/2 - final_score_text.get_width()/2, GAME_HEIGHT/2 - 40))
            
            mouse_pos = pygame.mouse.get_pos()
            btn_color = (255, 165, 0) if self.ok_btn.collidepoint(mouse_pos) else (200, 100, 0)
            
            pygame.draw.rect(window, btn_color, self.ok_btn, border_radius=10)
            pygame.draw.rect(window, "white", self.ok_btn, 4, border_radius=10)
            
            ok_txt = game_font.render("OK", True, "white")
            window.blit(ok_txt, (self.ok_btn.centerx - ok_txt.get_width()/2, self.ok_btn.centery - ok_txt.get_height()/2))


    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.update()
            clock.tick(60)

if __name__ == "__main__":
    game = FlappyHatGame()
    game.run()