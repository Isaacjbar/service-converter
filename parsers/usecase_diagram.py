from .java_parser import ClassInfo
from .base_generator import DiagramGenerator


class UseCaseDiagramGenerator(DiagramGenerator):
    """Generates PlantUML use case diagram from parsed Java classes.

    Heuristic:
    - Classes with 'Service', 'Controller', or 'Handler' suffix are treated as systems.
    - Public methods on those classes become use cases.
    - Other classes become actors.
    - If no service/controller classes found, the class with most public methods is the system.
    """

    SYSTEM_SUFFIXES = ("Service", "Controller", "Handler", "Manager", "Facade")

    @property
    def diagram_type(self) -> str:
        return "usecase"

    def _directives(self) -> list[str]:
        return ["left to right direction"]

    def _body(self, classes: list[ClassInfo]) -> list[str]:
        systems, actors = self._classify(classes)
        lines: list[str] = []

        actor_names = set()
        for cls in actors:
            lines.append(f'actor "{cls.name}" as {cls.name}')
            actor_names.add(cls.name)

        lines.append("")

        for sys_cls in systems:
            lines.append(f'rectangle "{sys_cls.name}" {{')
            for method in sys_cls.methods:
                if "public" in method.modifiers or not method.modifiers:
                    uc_id = f"{sys_cls.name}_{method.name}"
                    label = self._humanize(method.name)
                    lines.append(f'  usecase "{label}" as {uc_id}')
            lines.append("}")
            lines.append("")

        for sys_cls in systems:
            for method in sys_cls.methods:
                if "public" not in method.modifiers and method.modifiers:
                    continue
                uc_id = f"{sys_cls.name}_{method.name}"
                linked = False
                for param in method.parameters:
                    base_type = param.type.split("<")[0]
                    if base_type in actor_names:
                        lines.append(f"{base_type} --> {uc_id}")
                        linked = True
                if not linked and actor_names:
                    first_actor = next(iter(actor_names))
                    lines.append(f"{first_actor} --> {uc_id}")

        return lines

    def _classify(self, classes: list[ClassInfo]):
        systems = []
        actors = []
        for cls in classes:
            if any(cls.name.endswith(s) for s in self.SYSTEM_SUFFIXES):
                systems.append(cls)
            else:
                actors.append(cls)

        if not systems and classes:
            best = max(classes, key=lambda c: sum(
                1 for m in c.methods if "public" in m.modifiers or not m.modifiers
            ))
            systems = [best]
            actors = [c for c in classes if c is not best]

        return systems, actors

    def _humanize(self, name: str) -> str:
        """Convert camelCase to human-readable string."""
        result = []
        for i, ch in enumerate(name):
            if ch.isupper() and i > 0:
                result.append(" ")
            result.append(ch)
        return "".join(result).capitalize()
