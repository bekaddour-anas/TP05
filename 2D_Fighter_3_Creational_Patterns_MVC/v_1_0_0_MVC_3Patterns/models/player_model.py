"""Player state and projectile abilities (Model only)."""
import pygame
from settings import PLAYER_SPEED, PLAYER_SIZE, BULLET_SPEED, BULLET_COOLDOWN, LIGHTNING_COOLDOWN


class PlayerModel:
    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, *PLAYER_SIZE)
        self.speed = PLAYER_SPEED
        self.facing_right = True
        self.bullets: list[dict] = []
        self.bullet_cooldown = 0
        self.lightning_cooldown = 0
        self.lightning_timer = 0

        # World-compatible weapon attributes (supplied by Abstract Factory via LevelBuilder)
        self.weapon_name = "Standard Blaster"
        self.weapon_color = (255, 225, 100)
        self.weapon_damage = 1
        self.bullet_speed = BULLET_SPEED

    def equip_weapon(self, weapon) -> None:
        """Equips a WorldWeapon instance onto the player."""
        self.weapon_name = weapon.name
        self.weapon_color = weapon.color
        self.weapon_damage = weapon.damage
        self.bullet_speed = weapon.speed

    def move(self, dx: int, dy: int, screen_rect: pygame.Rect) -> None:
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.clamp_ip(screen_rect)

    def shoot(self) -> None:
        if self.bullet_cooldown <= 0:
            direction = 1 if self.facing_right else -1
            bullet = pygame.Rect(0, 0, 22, 8)
            bullet.center = (self.rect.centerx + direction * (self.rect.width // 2), self.rect.centery)
            self.bullets.append({
                "rect": bullet,
                "direction": direction,
                "color": self.weapon_color,
                "damage": self.weapon_damage,
            })
            self.bullet_cooldown = BULLET_COOLDOWN

    def cast_lightning(self) -> bool:
        if self.lightning_cooldown > 0:
            return False
        self.lightning_cooldown = LIGHTNING_COOLDOWN
        self.lightning_timer = 28
        return True

    def update(self, screen_rect: pygame.Rect) -> None:
        self.bullet_cooldown = max(0, self.bullet_cooldown - 1)
        self.lightning_cooldown = max(0, self.lightning_cooldown - 1)
        self.lightning_timer = max(0, self.lightning_timer - 1)
        for bullet in self.bullets:
            bullet["rect"].x += bullet["direction"] * self.bullet_speed
        self.bullets = [b for b in self.bullets if screen_rect.colliderect(b["rect"])]
