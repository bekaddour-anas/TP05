"""
1. Factory Method Pattern: Different Monsters on Demand.

Creates different types of monsters during the game (Zombie, Dragon, Robot),
allowing multiple distinct monster types to coexist in the same session.
"""
from abc import ABC, abstractmethod
from settings import WIDTH, HEIGHT
from models.monster_model import MonsterModel, MonsterProfile


class MonsterCreator(ABC):
    """Abstract Creator declaring the Factory Method `create_monster`."""

    @abstractmethod
    def create_monster(self, spawn_pos: tuple[int, int] | None = None,
                       width: int = WIDTH, height: int = HEIGHT) -> MonsterModel:
        raise NotImplementedError


class ZombieCreator(MonsterCreator):
    """Concrete Creator producing Zombie monsters (slow, high HP, toxic whip)."""

    def create_monster(self, spawn_pos: tuple[int, int] | None = None,
                       width: int = WIDTH, height: int = HEIGHT) -> MonsterModel:
        profile = MonsterProfile(
            name="Toxic Zombie",
            archetype="Zombie",
            speed=1,
            max_hp=3,
            whip_range=160,
            whip_cooldown=68,
            body_color=(95, 190, 95),
            whip_color=(130, 245, 90),
        )
        return MonsterModel(width, height, profile, spawn_pos)


class DragonCreator(MonsterCreator):
    """Concrete Creator producing Dragon monsters (medium speed, long fire whip)."""

    def create_monster(self, spawn_pos: tuple[int, int] | None = None,
                       width: int = WIDTH, height: int = HEIGHT) -> MonsterModel:
        profile = MonsterProfile(
            name="Inferno Dragon",
            archetype="Dragon",
            speed=2,
            max_hp=2,
            whip_range=230,
            whip_cooldown=55,
            body_color=(215, 65, 35),
            whip_color=(255, 115, 20),
        )
        return MonsterModel(width, height, profile, spawn_pos)


class RobotCreator(MonsterCreator):
    """Concrete Creator producing Robot monsters (fast speed, rapid plasma beam)."""

    def create_monster(self, spawn_pos: tuple[int, int] | None = None,
                       width: int = WIDTH, height: int = HEIGHT) -> MonsterModel:
        profile = MonsterProfile(
            name="Cyber Robot",
            archetype="Robot",
            speed=3,
            max_hp=2,
            whip_range=200,
            whip_cooldown=46,
            body_color=(85, 180, 245),
            whip_color=(90, 245, 255),
        )
        return MonsterModel(width, height, profile, spawn_pos)


class MonsterFactoryRegistry:
    """Dispatcher mapping monster type names to their Factory Method creators."""

    _creators: dict[str, MonsterCreator] = {
        "zombie": ZombieCreator(),
        "dragon": DragonCreator(),
        "robot": RobotCreator(),
    }

    @classmethod
    def create(cls, monster_type: str, spawn_pos: tuple[int, int] | None = None) -> MonsterModel:
        key = monster_type.strip().lower()
        if key not in cls._creators:
            raise ValueError(f"Unsupported monster type: {monster_type}")
        return cls._creators[key].create_monster(spawn_pos=spawn_pos)
