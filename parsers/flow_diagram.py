from .java_parser import ClassInfo, MethodInfo
from .base_generator import DiagramGenerator


class FlowDiagramGenerator(DiagramGenerator):
    """Generates PlantUML activity diagrams from parsed Java method bodies."""

    @property
    def diagram_type(self) -> str:
        return "flow"

    def _body(self, classes: list[ClassInfo]) -> list[str]:
        lines: list[str] = []
        for cls in classes:
            interesting_methods = [
                m for m in cls.methods
                if m.body_statements and len(m.body_statements) > 1
            ]
            if not interesting_methods:
                interesting_methods = cls.methods[:3]

            for method in interesting_methods:
                lines.extend(self._render_method(cls.name, method))
                lines.append("")

        return lines

    def _render_method(self, class_name: str, method: MethodInfo) -> list[str]:
        params = ", ".join(f"{p.type} {p.name}" for p in method.parameters)
        lines = [
            f"partition \"{class_name}.{method.name}({params})\" {{",
            "  start",
        ]

        if not method.body_statements:
            lines.append("  :No body;")
        else:
            lines.extend(self._render_statements(method.body_statements))

        lines.append("  stop")
        lines.append("}")
        return lines

    def _render_statements(self, statements: list[str]) -> list[str]:
        lines = []
        i = 0
        while i < len(statements):
            stmt = statements[i]

            if stmt.startswith("IF:"):
                condition = stmt[3:]
                lines.append(f"  if ({condition}) then (yes)")
                i += 1
                while i < len(statements) and statements[i] != "ENDIF":
                    if statements[i] == "ELSE":
                        lines.append("  else (no)")
                        i += 1
                        while i < len(statements) and statements[i] != "ENDELSE":
                            lines.extend(self._render_single(statements[i]))
                            i += 1
                        i += 1  # skip ENDELSE
                        continue
                    lines.extend(self._render_single(statements[i]))
                    i += 1
                if i < len(statements):
                    i += 1  # skip ENDIF
                lines.append("  endif")

            elif stmt.startswith("FOR:") or stmt.startswith("WHILE:"):
                tag = "FOR" if stmt.startswith("FOR:") else "WHILE"
                condition = stmt.split(":", 1)[1]
                end_tag = f"END{tag}"
                lines.append(f"  while ({condition}) is (true)")
                i += 1
                while i < len(statements) and statements[i] != end_tag:
                    lines.extend(self._render_single(statements[i]))
                    i += 1
                if i < len(statements):
                    i += 1
                lines.append("  endwhile (false)")

            elif stmt.startswith("TRY"):
                lines.append("  group Try")
                i += 1
                while i < len(statements) and statements[i] != "ENDTRY":
                    lines.extend(self._render_single(statements[i]))
                    i += 1
                if i < len(statements):
                    i += 1  # skip ENDTRY
                lines.append("  end group")
                while i < len(statements) and statements[i].startswith("CATCH:"):
                    exc = statements[i][6:]
                    lines.append(f"  group Catch ({exc})")
                    i += 1
                    while i < len(statements) and statements[i] != "ENDCATCH":
                        lines.extend(self._render_single(statements[i]))
                        i += 1
                    if i < len(statements):
                        i += 1
                    lines.append("  end group")

            elif stmt.startswith("SWITCH:"):
                expr = stmt[7:]
                lines.append(f"  switch ({expr})")
                i += 1
                while i < len(statements) and statements[i] != "ENDSWITCH":
                    if statements[i].startswith("CASE:"):
                        label = statements[i][5:]
                        lines.append(f'  case ( {label} )')
                        i += 1
                        while i < len(statements) and not statements[i].startswith("CASE:") and statements[i] != "ENDSWITCH":
                            lines.extend(self._render_single(statements[i]))
                            i += 1
                    else:
                        i += 1
                if i < len(statements):
                    i += 1
                lines.append("  endswitch")
            else:
                lines.extend(self._render_single(stmt))
                i += 1

        return lines

    def _render_single(self, stmt: str) -> list[str]:
        if stmt.startswith("IF:") or stmt.startswith("FOR:") or stmt.startswith("WHILE:") \
                or stmt.startswith("TRY") or stmt.startswith("SWITCH:"):
            return self._render_statements([stmt])

        if stmt.startswith("CALL:"):
            action = stmt[5:]
            return [f"  :{action};"]
        elif stmt.startswith("VAR:"):
            decl = stmt[4:]
            return [f"  :Declare {decl};"]
        elif stmt.startswith("RETURN:"):
            val = stmt[7:]
            return [f"  :Return {val};"] if val else ["  :Return;"]
        elif stmt.startswith("THROW:"):
            val = stmt[6:]
            return [f"  #pink:Throw {val};"]
        elif stmt in ("ENDIF", "ENDELSE", "ENDFOR", "ENDWHILE", "ENDTRY", "ENDCATCH", "ENDSWITCH"):
            return []
        elif stmt.startswith("ELSE"):
            return []
        elif stmt.startswith("CATCH:"):
            return []
        elif stmt.startswith("CASE:"):
            return []
        else:
            return [f"  :{stmt};"]
