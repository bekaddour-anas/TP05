"""
Game Model integrating ONLY the 3 requested Creational Design Patterns:
1. Factory Method   (MonsterFactoryRegistry -> Zombie, Dragon, Robot on demand)
2. Abstract Factory (FantasyWorldFactory, SpaceWorldFactory)
3. Builder          (LevelBuilder, LevelDirector)
"""
import random
import pygame
from settings import WIDTH, HEIGHT, PLAYER_START, INITIAL_HEALTH, LIGHTNING_RANGE
from models.player_model import PlayerModel
from models.monster_factory import MonsterFactoryRegistry
from models.world_factory import FantasyWorldFactory, SpaceWorldFactory
from models.level_builder import LevelBuilder, LevelDirector, GameLevel


class GameModel:
    def __init__(self) -> None:
        self.screen_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.fantasy_factory = FantasyWorldFactory()
        self.space_factory = SpaceWorldFactory()
        self.builder = LevelBuilder()
        self.director = LevelDirector(self.builder)
        self.current_level_num = 1
        self.reset(level_num=1)

    def _create_level(self, level_num: int) -> GameLevel:
        if level_num == 1:
            return self.director.build_fantasy_level(self.fantasy_factory)
        return self.director.build_space_level(self.space_factory)

    def reset(self, level_num: int | None = None) -> None:
        if level_num is not None:
            self.current_level_num = level_num

        self.player = PlayerModel(*PLAYER_START)
        self.active_level = self._create_level(self.current_level_num)

        # Equip the world-compatible weapon built for this level
        self.player.equip_weapon(self.active_level.weapon)

        self.monsters = self.active_level.monsters
        self.rewards = self.active_level.rewards
        self.score = 0
        self.health = INITIAL_HEALTH
        self.game_over = False
        self.hit_flash_timer = 0
        self.events: list[str] = []
        self.status_message = f"{self.active_level.title} ({self.active_level.background.name})"

    def switch_world_level(self) -> None:
        """Switches between Level 1 (Fantasy World) and Level 2 (Space World)."""
        next_lvl = 2 if self.current_level_num == 1 else 1
        self.reset(level_num=next_lvl)

    def spawn_monster_on_demand(self, monster_type: str) -> None:
        """Factory Method: spawns Zombie, Dragon, or Robot into the active session."""
        if self.game_over or len(self.monsters) >= 6:
            return
        spawn_pos = (
            random.randint(WIDTH // 2 + 20, WIDTH - 270),
            random.randint(45, HEIGHT - 220),
        )
        new_monster = MonsterFactoryRegistry.create(monster_type, spawn_pos=spawn_pos)
        self.monsters.append(new_monster)
        self.status_message = f"Spawned {new_monster.profile.name} (Factory Method)"

    @property
    def monster(self):
        return self.monsters[0] if self.monsters else None

    def update(self, move_dx: int, move_dy: int) -> None:
        self.events = []
        if self.game_over:
            return
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1

        self.player.move(move_dx, move_dy, self.screen_rect)
        self.player.update(self.screen_rect)

        for monster in self.monsters:
            monster.update(self.player)

        # Reward pickup check
        for reward in self.rewards:
            if not reward.collected and self.player.rect.colliderect(reward.rect):
                reward.collected = True
                self.score += reward.points
                self.health = min(INITIAL_HEALTH + 3, self.health + reward.heal_amount)
                self.status_message = f"Collected {reward.name} (+{reward.points} pts, +{reward.heal_amount} HP)"

        # Projectile collisions
        for bullet in self.player.bullets[:]:
            target = next((m for m in self.monsters if bullet["rect"].colliderect(m.rect)), None)
            if target is not None:
                self.player.bullets.remove(bullet)
                defeated = target.take_damage(bullet["damage"])
                self.score += 5 if defeated else 1
                self.events.append("monster_hit")

        # Lightning ability affects every monster in range
        if self.player.lightning_timer == 27:
            targets = [
                m for m in self.monsters
                if pygame.Vector2(self.player.rect.center).distance_to(m.rect.center) <= LIGHTNING_RANGE
            ]
            if targets:
                self.score += 10 * len(targets)
                self.events.append("lightning_finish")
                for monster in targets:
                    monster.respawn()

        # Monster whip or body contact damages player
        for monster in self.monsters:
            if monster.is_whipping and not monster.whip_hit_registered:
                if any(box.colliderect(self.player.rect) for box in monster.get_whip_hit_rects()):
                    monster.whip_hit_registered = True
                    self.apply_damage_to_player(1)
                    break

            player_core = self.player.rect.inflate(-35, -30)
            monster_core = monster.rect.inflate(-90, -40)
            if player_core.colliderect(monster_core):
                self.apply_damage_to_player(1)
                monster.respawn()
                break

    def apply_damage_to_player(self, amount: int) -> None:
        self.health = max(0, self.health - amount)
        self.hit_flash_timer = 12
        self.events.append("player_hit")
        if self.health <= 0:
            self.game_over = True
