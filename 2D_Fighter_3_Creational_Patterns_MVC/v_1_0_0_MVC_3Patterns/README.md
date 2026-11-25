# 2D Fighter Game — MVC + 3 Creational Design Patterns

This project implements the **three selected Creational Design Patterns** from Workshop 3.6 (p. 75):

1. **Factory Method (`models/monster_factory.py`)**
   - `MonsterCreator` declares `create_monster()`.
   - Concrete creators: `ZombieCreator`, `DragonCreator`, and `RobotCreator`.
   - Multiple distinct monster types (`Zombie`, `Dragon`, `Robot`) coexist in the same session and can be spawned on demand during gameplay using keys **`1`**, **`2`**, and **`3`**.

2. **Abstract Factory (`models/world_factory.py`)**
   - `WorldAbstractFactory` creates compatible families of world elements (`WorldBackground`, `MonsterModel`, `WorldWeapon`, `WorldReward`).
   - Concrete factories:
     - `FantasyWorldFactory`: Fantasy World background, Elder Dragon, Sunfire Crossbow, Dragon Ruby.
     - `SpaceWorldFactory`: Space World background, Orbital Robot, Ion Plasma Rifle, Quantum Core.

3. **Builder (`models/level_builder.py`)**
   - `LevelBuilder` and `LevelDirector` construct complex `GameLevel` objects progressively by defining their background, weapons, monsters, rewards, and exact positions.

## Controls
- **Arrows / WASD / ZQSD:** Move
- **SPACE:** Shoot (uses the current World's weapon)
- **E:** Lightning
- **1 / 2 / 3:** Spawn Zombie / Dragon / Robot on demand (Factory Method)
- **N:** Switch between Fantasy World (Level 1) and Space World (Level 2)
- **R:** Restart after Game Over
- **ESC:** Quit

## Run
```bash
python -m pip install pygame
python main.py
```
