"""
3. Builder Pattern: Building a Game Level.

Constructs a complex GameLevel progressively by defining its:
- Background
- Monsters and their positions
- Weapons
- Rewards and their positions
"""
from __future__ import annotations
from models.world_factory import (
    WorldAbstractFactory, WorldBackground, WorldWeapon, WorldReward
)
from models.monster_model import MonsterModel
from models.monster_factory import MonsterFactoryRegistry


class GameLevel:
    """Complex Product constructed progressively by LevelBuilder."""

    def __init__(self, level_number: int = 1, title: str = "Level 1") -> None:
        self.level_number = level_number
        self.title = title
        self.background: WorldBackground = WorldBackground("Default", (0, 0, 0, 0), (255, 255, 255))
        self.weapon: WorldWeapon = WorldWeapon("Standard Blaster", 1, 11, (255, 225, 100))
        self.monsters: list[MonsterModel] = []
        self.rewards: list[WorldReward] = []


class LevelBuilder:
    """Builder providing a fluent step-by-step interface to construct a GameLevel."""

    def __init__(self) -> None:
        self._level = GameLevel()

    def reset(self, level_number: int, title: str) -> LevelBuilder:
        self._level = GameLevel(level_number=level_number, title=title)
        return self

    def define_background(self, background: WorldBackground) -> LevelBuilder:
        self._level.background = background
        return self

    def define_weapon(self, weapon: WorldWeapon) -> LevelBuilder:
        self._level.weapon = weapon
        return self

    def add_world_monster(self, world_factory: WorldAbstractFactory, position: tuple[int, int]) -> LevelBuilder:
        monster = world_factory.create_monster(spawn_pos=position)
        self._level.monsters.append(monster)
        return self

    def add_monster(self, monster_type: str, position: tuple[int, int]) -> LevelBuilder:
        monster = MonsterFactoryRegistry.create(monster_type, spawn_pos=position)
        self._level.monsters.append(monster)
        return self

    def add_reward(self, world_factory: WorldAbstractFactory, position: tuple[int, int]) -> LevelBuilder:
        reward = world_factory.create_reward(pos=position)
        self._level.rewards.append(reward)
        return self

    def get_result(self) -> GameLevel:
        built_level = self._level
        self._level = GameLevel()
        return built_level


class LevelDirector:
    """Director orchestrating progressive level construction using LevelBuilder & WorldAbstractFactory."""

    def __init__(self, builder: LevelBuilder) -> None:
        self.builder = builder

    def build_fantasy_level(self, factory: WorldAbstractFactory) -> GameLevel:
        return (
            self.builder.reset(1, "Level 1: Fantasy Realm")
            .define_background(factory.create_background())
            .define_weapon(factory.create_weapon())
            .add_world_monster(factory, (520, 120))
            .add_monster("zombie", (560, 340))
            .add_reward(factory, (340, 170))
            .add_reward(factory, (400, 410))
            .get_result()
        )

    def build_space_level(self, factory: WorldAbstractFactory) -> GameLevel:
        return (
            self.builder.reset(2, "Level 2: Space Station")
            .define_background(factory.create_background())
            .define_weapon(factory.create_weapon())
            .add_world_monster(factory, (510, 110))
            .add_monster("dragon", (550, 345))
            .add_reward(factory, (320, 190))
            .add_reward(factory, (410, 390))
            .get_result()
        )
