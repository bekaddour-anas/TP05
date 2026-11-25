"""Monster Model: holds monster pursuit, respawn, and attack state for Zombie, Dragon, and Robot."""
import math
import random
from dataclasses import dataclass
import pygame
from settings import (
    MONSTER_SPEED, MONSTER_SIZE, WIDTH, HEIGHT,
    WHIP_RANGE, WHIP_COOLDOWN, WHIP_ATTACK_DURATION
)


@dataclass(frozen=True)
class MonsterProfile:
    name: str
    archetype: str      # "Zombie", "Dragon", or "Robot"
    speed: int
    max_hp: int
    whip_range: int
    whip_cooldown: int
    body_color: tuple[int, int, int]
    whip_color: tuple[int, int, int]


class MonsterModel:
    def __init__(self, width: int = WIDTH, height: int = HEIGHT,
                 profile: MonsterProfile | None = None,
                 spawn_pos: tuple[int, int] | None = None) -> None:
        self.width = width
        self.height = height
        self.profile = profile or MonsterProfile(
            "Inferno Dragon", "Dragon", MONSTER_SPEED, 2,
            WHIP_RANGE, WHIP_COOLDOWN, (210, 65, 35), (255, 110, 20)
        )
        self.speed = self.profile.speed
        self.max_hp = self.profile.max_hp
        self.hp = self.max_hp

        sx = spawn_pos[0] if spawn_pos is not None else width - 280
        sy = spawn_pos[1] if spawn_pos is not None else height // 2 - MONSTER_SIZE[1] // 2
        self.rect = pygame.Rect(sx, sy, *MONSTER_SIZE)
        self.facing_left = True

        # Whip / plasma beam attack state
        self.is_whipping = False
        self.whip_timer = 0
        self.whip_cooldown = random.randint(15, 35)
        self.whip_phase = random.uniform(0.0, 3.14)
        self.whip_extension = 0.0
        self.whip_hit_registered = False
        self.whip_target_angle = math.pi

    def take_damage(self, amount: int) -> bool:
        """Applies damage; returns True if monster was defeated and respawned."""
        self.hp -= amount
        if self.hp <= 0:
            self.respawn()
            return True
        return False

    def update(self, player: "PlayerModel") -> None:
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        self.facing_left = dx <= 0

        if self.whip_cooldown > 0:
            self.whip_cooldown -= 1

        if not self.is_whipping and self.whip_cooldown <= 0 and distance <= self.profile.whip_range + 80:
            self.is_whipping = True
            self.whip_timer = WHIP_ATTACK_DURATION
            self.whip_cooldown = self.profile.whip_cooldown
            self.whip_hit_registered = False
            start_x, start_y = self._get_hand_anchor()
            self.whip_target_angle = math.atan2(player.rect.centery - start_y, player.rect.centerx - start_x)

        if self.is_whipping:
            progress = 1.0 - (self.whip_timer / WHIP_ATTACK_DURATION)
            self.whip_extension = math.sin(progress * math.pi)
            self.whip_phase += 0.45
            start_x, start_y = self._get_hand_anchor()
            self.whip_target_angle = math.atan2(player.rect.centery - start_y, player.rect.centerx - start_x)
            self.whip_timer -= 1
            if self.whip_timer <= 0:
                self.is_whipping = False
                self.whip_extension = 0.0
        else:
            self.whip_phase += 0.18
            if distance > self.profile.whip_range * 0.75 and distance > 0:
                self.rect.x += round(dx / distance * self.speed)
                self.rect.y += round(dy / distance * self.speed)

    def _get_hand_anchor(self) -> tuple[float, float]:
        direction = -1 if self.facing_left else 1
        start_x = self.rect.centerx + direction * (self.rect.width * 0.22)
        start_y = self.rect.centery + 5
        return start_x, start_y

    def get_whip_points(self) -> list[tuple[float, float]]:
        start_x, start_y = self._get_hand_anchor()
        if not self.is_whipping or self.whip_extension <= 0.02:
            idle_len = 42.0
            direction = -1 if self.facing_left else 1
            points = []
            for i in range(9):
                t = i / 8
                px = start_x + direction * (idle_len * t)
                py = start_y - 18 * t + math.sin(t * 5.0 - self.whip_phase) * (8.0 * t)
                points.append((px, py))
            return points

        current_len = self.profile.whip_range * self.whip_extension
        cos_a = math.cos(self.whip_target_angle)
        sin_a = math.sin(self.whip_target_angle)
        perp_x = -sin_a
        perp_y = cos_a

        points = []
        segments = 22
        wave_amp = 10.0 if self.profile.archetype == "Robot" else 28.0
        for i in range(segments + 1):
            t = i / segments
            base_x = start_x + cos_a * (current_len * t)
            base_y = start_y + sin_a * (current_len * t)
            wave_offset = math.sin(t * 8.0 - self.whip_phase) * (wave_amp * t * self.whip_extension)
            px = base_x + perp_x * wave_offset
            py = base_y + perp_y * wave_offset
            points.append((px, py))
        return points

    def get_whip_hit_rects(self) -> list[pygame.Rect]:
        if not self.is_whipping or self.whip_extension < 0.35:
            return []
        points = self.get_whip_points()
        active_points = points[len(points) // 2:]
        return [pygame.Rect(int(px - 12), int(py - 12), 24, 24) for px, py in active_points]

    def respawn(self) -> None:
        self.hp = self.max_hp
        self.rect.x = random.randint(self.width // 2, max(self.width // 2 + 1, self.width - self.rect.width - 20))
        self.rect.y = random.randint(40, max(45, self.height - self.rect.height - 40))
        self.is_whipping = False
        self.whip_extension = 0.0
        self.whip_cooldown = 20
