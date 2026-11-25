"""Controller: input, model updates, and presentation coordination."""
import pygame
from settings import WIDTH, HEIGHT, FPS, CAPTION
from models.game_model import GameModel
from views.game_view import GameView


class GameController:
    def __init__(self) -> None:
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            pass
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.model = GameModel()
        self.view = GameView(self.screen)
        self.view.start_music()

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if event.key == pygame.K_n:
                    self.model.switch_world_level()
                    continue

                if not self.model.game_over:
                    if event.key == pygame.K_SPACE:
                        self.model.player.shoot()
                        self.view.play_sound("shoot")
                    elif event.key == pygame.K_e:
                        if self.model.player.cast_lightning():
                            self.view.play_sound("lightning")
                    # Factory Method: create Zombie, Dragon, or Robot on demand
                    elif event.key == pygame.K_1:
                        self.model.spawn_monster_on_demand("zombie")
                    elif event.key == pygame.K_2:
                        self.model.spawn_monster_on_demand("dragon")
                    elif event.key == pygame.K_3:
                        self.model.spawn_monster_on_demand("robot")
                elif event.key == pygame.K_r:
                    self.model.reset()
                    self.view.start_music()
        return True

    def get_movement_input(self) -> tuple[int, int]:
        keys = pygame.key.get_pressed()
        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_q])
        dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_z])
        return dx, dy

    def run(self) -> None:
        running = True
        while running:
            self.clock.tick(FPS)
            running = self.handle_events()
            dx, dy = self.get_movement_input()
            was_over = self.model.game_over
            self.model.update(dx, dy)
            for sound_event in self.model.events:
                self.view.play_sound(sound_event)
            if self.model.game_over and not was_over:
                self.view.stop_music()
            self.view.render(self.model)
        pygame.quit()
