from .java_parser import ClassInfo
from .base_generator import DiagramGenerator


VISIBILITY_MAP = {
    "public": "+",
    "private": "-",
    "protected": "#",
}


class ClassDiagramGenerator(DiagramGenerator):
    """Generates PlantUML class diagram markup from parsed Java classes."""

    @property
    def diagram_type(self) -> str:
        return "class"

    def _directives(self) -> list[str]:
        return ["skinparam classAttributeIconSize 0"]

    def _body(self, classes: list[ClassInfo]) -> list[str]:
        lines: list[str] = []
        for cls in classes:
            lines.extend(self._render_class(cls))
            lines.append("")
        lines.extend(self._render_relationships(classes))
        return lines

    def _render_class(self, cls: ClassInfo) -> list[str]:
        lines = []

        if cls.kind == "interface":
            lines.append(f"interface {cls.name} {{")
        elif cls.kind == "enum":
            lines.append(f"enum {cls.name} {{")
            for const in cls.enum_constants:
                lines.append(f"  {const}")
            if cls.enum_constants and (cls.fields or cls.methods):
                lines.append("  --")
        elif "abstract" in cls.modifiers:
            lines.append(f"abstract class {cls.name} {{")
        else:
            lines.append(f"class {cls.name} {{")

        for field in cls.fields:
            vis = self._get_visibility(field.modifiers)
            static = " {static}" if "static" in field.modifiers else ""
            lines.append(f"  {vis}{field.name} : {field.type}{static}")

        if cls.fields and cls.methods:
            lines.append("  --")

        for method in cls.methods:
            vis = self._get_visibility(method.modifiers)
            static = " {static}" if "static" in method.modifiers else ""
            abstract = " {abstract}" if "abstract" in method.modifiers else ""
            params = ", ".join(f"{p.name}: {p.type}" for p in method.parameters)
            lines.append(f"  {vis}{method.name}({params}) : {method.return_type}{static}{abstract}")

        lines.append("}")
        return lines

    def _get_visibility(self, modifiers: list[str]) -> str:
        for mod in modifiers:
            if mod in VISIBILITY_MAP:
                return VISIBILITY_MAP[mod]
        return "~"

    def _render_relationships(self, classes: list[ClassInfo]) -> list[str]:
        lines = []
        class_names = {cls.name for cls in classes}

        for cls in classes:
            if cls.extends and cls.extends in class_names:
                lines.append(f"{cls.extends} <|-- {cls.name}")

            for iface in cls.implements:
                if iface in class_names:
                    lines.append(f"{iface} <|.. {cls.name}")

            for field in cls.fields:
                base_type = field.type.split("<")[0]
                if base_type in class_names and base_type != cls.name:
                    lines.append(f'{cls.name} --> {base_type} : {field.name}')

        return lines
