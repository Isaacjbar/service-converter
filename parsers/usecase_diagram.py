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
        actor_names = {cls.name for cls in actors}
        lines = self._render_actors(actors)
        lines.append("")
        for sys_cls in systems:
            lines.extend(self._render_system_block(sys_cls))
            lines.append("")
        lines.extend(self._render_links(systems, actor_names))
        return lines

    def _render_actors(self, actors: list) -> list[str]:
        return [f'actor "{cls.name}" as {cls.name}' for cls in actors]

    def _render_system_block(self, sys_cls) -> list[str]:
        lines = [f'rectangle "{sys_cls.name}" {{']
        for method in sys_cls.methods:
            if "public" in method.modifiers or not method.modifiers:
                uc_id = f"{sys_cls.name}_{method.name}"
                label = self._humanize(method.name)
                lines.append(f'  usecase "{label}" as {uc_id}')
        lines.append("}")
        return lines

    def _render_links(self, systems: list, actor_names: set) -> list[str]:
        lines = []
        for sys_cls in systems:
            for method in sys_cls.methods:
                if "public" not in method.modifiers and method.modifiers:
                    continue
                lines.extend(self._render_method_links(sys_cls.name, method, actor_names))
        return lines

    def _render_method_links(self, sys_name: str, method, actor_names: set) -> list[str]:
        uc_id = f"{sys_name}_{method.name}"
        lines = []
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
        """
        Separa las clases en sistemas (contienen lógica) y actores (entidades externas).
        Clases con sufijo Service/Controller/Handler/Manager/Facade → sistema.
        El resto → actores. Si no hay sistemas, usa la clase con más métodos públicos.
        Returns: tuple (systems: list[ClassInfo], actors: list[ClassInfo])
        """
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
