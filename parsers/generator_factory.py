from __future__ import annotations

from .base_generator import DiagramGenerator


class DiagramGeneratorFactory:
    """Factory for creating diagram generators by name."""

    _registry: dict[str, type[DiagramGenerator]] = {}

    @classmethod
    def register(cls, name: str, generator_cls: type[DiagramGenerator]) -> None:
        """Register a generator class under the given name."""
        cls._registry[name] = generator_cls

    @classmethod
    def create(cls, name: str) -> DiagramGenerator:
        """Create a single generator by name."""
        if name not in cls._registry:
            raise ValueError(f"Unknown generator: {name}. Available: {cls.available()}")
        return cls._registry[name]()

    @classmethod
    def create_all(cls) -> dict[str, DiagramGenerator]:
        """Create one instance of every registered generator."""
        return {name: gen_cls() for name, gen_cls in cls._registry.items()}

    @classmethod
    def available(cls) -> list[str]:
        """Return names of all registered generators."""
        return list(cls._registry.keys())
