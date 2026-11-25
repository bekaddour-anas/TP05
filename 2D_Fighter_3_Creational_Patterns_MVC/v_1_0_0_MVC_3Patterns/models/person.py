"""Person data model."""
from dataclasses import dataclass


@dataclass
class Person:
    name: str
    score: int
    speed: float

    def greet(self) -> str:
        return f"Hello, my name is {self.name} and I have a score of {self.score}."
