from abc import ABC, abstractmethod

from .java_parser import ClassInfo


class DiagramGenerator(ABC):
    """Abstract base class for all diagram generators.

    Implements the Strategy pattern (interchangeable generators) and the
    Template Method pattern (common generate flow with customisable steps).
    """

    def generate(self, classes: list[ClassInfo]) -> str:
        """Template method: header -> directives -> body -> footer."""
        lines = ["@startuml"]
        lines.extend(self._directives())
        lines.append("")
        lines.extend(self._body(classes))
        lines.append("@enduml")
        return "\n".join(lines)

    def _directives(self) -> list[str]:
        """Optional PlantUML directives (skinparam, direction, etc.)."""
        return []

    @abstractmethod
    def _body(self, classes: list[ClassInfo]) -> list[str]:
        """Generate the main diagram content."""
        ...

    @property
    @abstractmethod
    def diagram_type(self) -> str:
        """Unique key for this generator (e.g. 'class', 'usecase', 'flow')."""
        ...
