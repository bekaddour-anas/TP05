"""
2. Abstract Factory Pattern: Different Worlds.

Each level has its own world containing a compatible set of:
- Background (WorldBackground)
- Monsters   (MonsterModel)
- Weapons    (WorldWeapon)
- Rewards    (WorldReward)

Concrete Factories:
- FantasyWorldFactory
- SpaceWorldFactory
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
import pygame
from settings import WIDTH, HEIGHT, ITEM_SIZE
from models.monster_model import MonsterModel, MonsterProfile


@dataclass
class WorldBackground:
    name: str
    tint_color: tuple[int, int, int, int]
    accent_color: tuple[int, int, int]


@dataclass
class WorldWeapon:
    name: str
    damage: int
    speed: int
    color: tuple[int, int, int]


class WorldReward:
    def __init__(self, name: str, points: int, heal_amount: int,
                 color: tuple[int, int, int], pos: tuple[int, int]) -> None:
        self.name = name
        self.points = points
        self.heal_amount = heal_amount
        self.color = color
        self.rect = pygame.Rect(pos[0], pos[1], *ITEM_SIZE)
        self.collected = False


class WorldAbstractFactory(ABC):
    """Abstract Factory creating a compatible family of world objects."""

    @abstractmethod
    def create_background(self) -> WorldBackground:
        raise NotImplementedError

    @abstractmethod
    def create_monster(self, spawn_pos: tuple[int, int]) -> MonsterModel:
        raise NotImplementedError

    @abstractmethod
    def create_weapon(self) -> WorldWeapon:
        raise NotImplementedError

    @abstractmethod
    def create_reward(self, pos: tuple[int, int]) -> WorldReward:
        raise NotImplementedError


class FantasyWorldFactory(WorldAbstractFactory):
    """Creates a cohesive Fantasy World (Elder Dragon, Sunfire Bow, Dragon Ruby)."""

    def create_background(self) -> WorldBackground:
        return WorldBackground(
            name="Fantasy World",
            tint_color=(255, 190, 130, 45),
            accent_color=(255, 175, 65),
        )

    def create_monster(self, spawn_pos: tuple[int, int]) -> MonsterModel:
        profile = MonsterProfile(
            name="Elder Dragon",
            archetype="Dragon",
            speed=2,
            max_hp=2,
            whip_range=230,
            whip_cooldown=55,
            body_color=(220, 70, 35),
            whip_color=(255, 125, 25),
        )
        return MonsterModel(WIDTH, HEIGHT, profile, spawn_pos)

    def create_weapon(self) -> WorldWeapon:
        return WorldWeapon(
            name="Sunfire Crossbow",
            damage=1,
            speed=11,
            color=(255, 200, 70),
        )

    def create_reward(self, pos: tuple[int, int]) -> WorldReward:
        return WorldReward(
            name="Dragon Ruby",
            points=15,
            heal_amount=1,
            color=(235, 60, 95),
            pos=pos,
        )


class SpaceWorldFactory(WorldAbstractFactory):
    """Creates a cohesive Space World (Cyber Robot, Ion Plasma Rifle, Quantum Core)."""

    def create_background(self) -> WorldBackground:
        return WorldBackground(
            name="Space World",
            tint_color=(100, 175, 255, 65),
            accent_color=(85, 235, 255),
        )

    def create_monster(self, spawn_pos: tuple[int, int]) -> MonsterModel:
        profile = MonsterProfile(
            name="Orbital Robot",
            archetype="Robot",
            speed=3,
            max_hp=3,
            whip_range=200,
            whip_cooldown=48,
            body_color=(85, 180, 245),
            whip_color=(95, 245, 255),
        )
        return MonsterModel(WIDTH, HEIGHT, profile, spawn_pos)

    def create_weapon(self) -> WorldWeapon:
        return WorldWeapon(
            name="Ion Plasma Rifle",
            damage=2,
            speed=14,
            color=(95, 245, 255),
        )

    def create_reward(self, pos: tuple[int, int]) -> WorldReward:
        return WorldReward(
            name="Quantum Core",
            points=20,
            heal_amount=1,
            color=(80, 245, 210),
            pos=pos,
        )
