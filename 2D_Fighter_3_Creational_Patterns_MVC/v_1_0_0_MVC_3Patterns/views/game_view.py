"""View: draws world background tint, rewards, player, coexisting monsters, and HUD."""
from pathlib import Path
import pygame
from settings import WIDTH, HEIGHT, BLACK, WHITE, GREEN, RED, GOLD, CYAN, PLAYER_BLUE, PLAYER_SIZE, MONSTER_SIZE
from models.game_model import GameModel


class GameView:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.small_font = pygame.font.SysFont(None, 23)
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 62)

        assets = Path(__file__).resolve().parent.parent / "assets"
        self.assets = assets
        self.background = self._load_background(assets / "game_bg.jpg", (WIDTH, HEIGHT))
        self.player_img = self._load_sprite(assets / "player.png", PLAYER_SIZE)
        self.monster_img = self._load_sprite(assets / "monster.png", MONSTER_SIZE)
        self.sounds = {}
        if pygame.mixer.get_init():
            for name in ("shoot", "player_hit", "monster_hit", "lightning"):
                path = assets / "audio" / f"{name}.wav"
                try:
                    self.sounds[name] = pygame.mixer.Sound(str(path))
                except pygame.error:
                    pass

    @staticmethod
    def _load_sprite(path: Path, size: tuple[int, int]):
        if not path.is_file():
            return None
        return pygame.transform.smoothscale(pygame.image.load(str(path)).convert_alpha(), size)

    @staticmethod
    def _load_background(path: Path, size: tuple[int, int]):
        if not path.is_file():
            return None
        return pygame.transform.scale(pygame.image.load(str(path)).convert(), size)

    def start_music(self) -> None:
        if pygame.mixer.get_init():
            music = self.assets / "audio" / "background_music.wav"
            try:
                pygame.mixer.music.load(str(music))
                pygame.mixer.music.set_volume(0.28)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass

    @staticmethod
    def stop_music() -> None:
        if pygame.mixer.get_init():
            pygame.mixer.music.fadeout(700)

    def play_sound(self, name: str) -> None:
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def render(self, model: GameModel) -> None:
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BLACK)

        # World Background atmospheric tint (Abstract Factory + Builder)
        tint = model.active_level.background.tint_color
        if tint[3] > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill(tint)
            self.screen.blit(overlay, (0, 0))

        # World Rewards
        for reward in model.rewards:
            if not reward.collected:
                pygame.draw.circle(self.screen, reward.color, reward.rect.center, 15)
                pygame.draw.circle(self.screen, WHITE, reward.rect.center, 15, 2)
                lbl = self.small_font.render(reward.name, True, WHITE)
                self.screen.blit(lbl, (reward.rect.centerx - lbl.get_width() // 2, reward.rect.top - 18))

        self._draw_player(model.player, model.monsters, model.hit_flash_timer > 0)
        for monster in model.monsters:
            self._draw_monster(monster)
        self._draw_hud(model)
        pygame.display.flip()

    def _draw_player(self, player, monsters, is_hit: bool) -> None:
        if self.player_img:
            sprite = self.player_img if player.facing_right else pygame.transform.flip(self.player_img, True, False)
            if is_hit:
                tinted = sprite.copy()
                tinted.fill((255, 80, 80, 180), special_flags=pygame.BLEND_RGBA_MULT)
                self.screen.blit(tinted, player.rect)
            else:
                self.screen.blit(sprite, player.rect)
        else:
            pygame.draw.rect(self.screen, RED if is_hit else PLAYER_BLUE, player.rect)

        for bullet in player.bullets:
            r = bullet["rect"]
            pygame.draw.ellipse(self.screen, bullet["color"], r.inflate(8, 6))
            pygame.draw.ellipse(self.screen, WHITE, r)

        if player.lightning_timer > 0:
            for monster in monsters:
                x, y = monster.rect.center
                points = [(x - 16, 0), (x + 12, 90), (x - 20, 165),
                          (x + 15, 245), (x - 8, y - 55), (x, y)]
                pygame.draw.lines(self.screen, (45, 135, 255), False, points, 18)
                pygame.draw.lines(self.screen, (235, 250, 255), False, points, 7)
                pygame.draw.circle(self.screen, (120, 210, 255), (x, y), 42, 5)

    def _draw_monster(self, monster) -> None:
        if self.monster_img:
            sprite = self.monster_img if monster.facing_left else pygame.transform.flip(self.monster_img, True, False)
            sprite = sprite.copy()
            tint = (*monster.profile.body_color, 255)
            overlay = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
            overlay.fill(tint)
            sprite.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(sprite, monster.rect)
        else:
            pygame.draw.rect(self.screen, monster.profile.body_color, monster.rect)

        label = f"{monster.profile.name} ({monster.profile.archetype}) HP:{monster.hp}/{monster.max_hp}"
        name_surf = self.small_font.render(label, True, WHITE)
        self.screen.blit(name_surf, (monster.rect.centerx - name_surf.get_width() // 2, monster.rect.top - 22))

        points = monster.get_whip_points()
        if len(points) >= 2:
            whip = monster.profile.whip_color
            dark = tuple(max(0, c // 2) for c in whip)
            pygame.draw.lines(self.screen, dark, False, points, 15 if monster.is_whipping else 7)
            pygame.draw.lines(self.screen, whip, False, points, 8 if monster.is_whipping else 4)
            pygame.draw.circle(self.screen, (255, 245, 210), (int(points[-1][0]), int(points[-1][1])), 8 if monster.is_whipping else 4)

    def _draw_hud(self, model: GameModel) -> None:
        self.screen.blit(self.font.render(f"Score: {model.score}   Health: {model.health}", True, WHITE), (18, 14))
        world_info = f"{model.active_level.title} | Weapon: {model.active_level.weapon.name} | Monsters: {len(model.monsters)}"
        self.screen.blit(self.small_font.render(world_info, True, model.active_level.background.accent_color), (18, 44))
        self.screen.blit(self.small_font.render(model.status_message, True, GOLD), (18, 66))

        controls_1 = "Move: Arrows/WASD | Shoot: SPACE | Lightning: E"
        controls_2 = "Spawn [1] Zombie  [2] Dragon  [3] Robot  |  [N] Switch World Level  [R] Restart"
        self.screen.blit(self.small_font.render(controls_1, True, WHITE), (18, HEIGHT - 46))
        self.screen.blit(self.small_font.render(controls_2, True, CYAN), (18, HEIGHT - 24))

        if model.game_over:
            title = self.big_font.render("GAME OVER", True, RED)
            restart = self.font.render("Press R to restart", True, WHITE)
            self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
            self.screen.blit(restart, restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25)))
