import javalang
from dataclasses import dataclass, field


@dataclass
class FieldInfo:
    name: str
    type: str
    modifiers: list[str] = field(default_factory=list)


@dataclass
class ParameterInfo:
    name: str
    type: str


@dataclass
class MethodInfo:
    name: str
    return_type: str
    parameters: list[ParameterInfo] = field(default_factory=list)
    modifiers: list[str] = field(default_factory=list)
    body_statements: list[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    name: str
    kind: str  # "class", "interface", "enum"
    modifiers: list[str] = field(default_factory=list)
    extends: str | None = None
    implements: list[str] = field(default_factory=list)
    fields: list[FieldInfo] = field(default_factory=list)
    methods: list[MethodInfo] = field(default_factory=list)
    enum_constants: list[str] = field(default_factory=list)


class JavaParser:
    """Parses Java source files and extracts class/method/field information."""

    def parse(self, source_code: str) -> list[ClassInfo]:
        """
        Parsea código fuente Java y retorna la lista de clases encontradas.

        Params:
            source_code -- cadena con el contenido completo del archivo .java.
        Returns:
            list[ClassInfo] con clases, interfaces y enums extraídos del AST.
        Raises:
            javalang.parser.JavaSyntaxError si el código no es Java válido.
        """
        tree = javalang.parse.parse(source_code)
        classes = []

        for _, node in tree.filter(javalang.tree.ClassDeclaration):
            classes.append(self._parse_class(node))

        for _, node in tree.filter(javalang.tree.InterfaceDeclaration):
            classes.append(self._parse_interface(node))

        for _, node in tree.filter(javalang.tree.EnumDeclaration):
            classes.append(self._parse_enum(node))

        return classes

    def _parse_class(self, node: javalang.tree.ClassDeclaration) -> ClassInfo:
        info = ClassInfo(
            name=node.name,
            kind="class",
            modifiers=list(node.modifiers) if node.modifiers else [],
            extends=node.extends.name if node.extends else None,
            implements=[impl.name for impl in (node.implements or [])],
        )
        self._extract_fields(node, info)
        self._extract_methods(node, info)
        return info

    def _parse_interface(self, node: javalang.tree.InterfaceDeclaration) -> ClassInfo:
        info = ClassInfo(
            name=node.name,
            kind="interface",
            modifiers=list(node.modifiers) if node.modifiers else [],
            extends=node.extends[0].name if node.extends else None,
        )
        self._extract_methods(node, info)
        return info

    def _parse_enum(self, node: javalang.tree.EnumDeclaration) -> ClassInfo:
        info = ClassInfo(
            name=node.name,
            kind="enum",
            modifiers=list(node.modifiers) if node.modifiers else [],
            implements=[impl.name for impl in (node.implements or [])],
            enum_constants=[c.name for c in (node.body.constants or [])],
        )
        self._extract_fields(node, info)
        self._extract_methods(node, info)
        return info

    def _extract_fields(self, node, info: ClassInfo):
        for field_decl in (node.fields or []):
            type_name = self._resolve_type(field_decl.type)
            modifiers = list(field_decl.modifiers) if field_decl.modifiers else []
            for declarator in field_decl.declarators:
                info.fields.append(FieldInfo(
                    name=declarator.name,
                    type=type_name,
                    modifiers=modifiers,
                ))

    def _extract_methods(self, node, info: ClassInfo):
        for method in (node.methods or []):
            params = []
            for param in (method.parameters or []):
                params.append(ParameterInfo(
                    name=param.name,
                    type=self._resolve_type(param.type),
                ))
            body_stmts = self._extract_body_statements(method.body) if method.body else []
            info.methods.append(MethodInfo(
                name=method.name,
                return_type=self._resolve_type(method.return_type) if method.return_type else "void",
                parameters=params,
                modifiers=list(method.modifiers) if method.modifiers else [],
                body_statements=body_stmts,
            ))

    def _resolve_type(self, type_node) -> str:
        """
        Convierte un nodo de tipo del AST de javalang a su representación en string.
        Maneja tipos básicos (int, boolean), tipos de referencia (String, List<T>)
        y tipos genéricos con argumentos anidados.
        """
        if type_node is None:
            return "void"
        if isinstance(type_node, javalang.tree.BasicType):
            return type_node.name
        if isinstance(type_node, javalang.tree.ReferenceType):
            name = type_node.name
            if type_node.arguments:
                args = ", ".join(
                    self._resolve_type(arg.type) for arg in type_node.arguments
                    if hasattr(arg, "type") and arg.type
                )
                if args:
                    name += f"<{args}>"
            return name
        return str(type_node)

    def _extract_body_statements(self, body) -> list[str]:
        """Extract statement types from a method body for flow diagram generation."""
        statements = []
        if not body:
            return statements
        for stmt in body:
            statements.extend(self._classify_statement(stmt))
        return statements

    def _classify_statement(self, stmt) -> list[str]:
        """
        Clasifica un statement del AST en tokens de control de flujo legibles
        (IF:, FOR:, WHILE:, RETURN:, CALL:, etc.) para uso en FlowDiagramGenerator.
        Procesa recursivamente bloques anidados.
        """
        if isinstance(stmt, javalang.tree.IfStatement):
            return self._classify_if(stmt)
        if isinstance(stmt, javalang.tree.ForStatement):
            return self._classify_for(stmt)
        if isinstance(stmt, javalang.tree.WhileStatement):
            return self._classify_while(stmt)
        if isinstance(stmt, javalang.tree.ReturnStatement):
            val = self._expression_to_str(stmt.expression) if stmt.expression else ""
            return [f"RETURN:{val}"]
        if isinstance(stmt, javalang.tree.TryStatement):
            return self._classify_try(stmt)
        if isinstance(stmt, javalang.tree.SwitchStatement):
            return self._classify_switch(stmt)
        if isinstance(stmt, javalang.tree.StatementExpression):
            return [f"CALL:{self._expression_to_str(stmt.expression)}"]
        if isinstance(stmt, javalang.tree.LocalVariableDeclaration):
            type_name = self._resolve_type(stmt.type)
            return [f"VAR:{type_name} {decl.name}" for decl in stmt.declarators]
        if isinstance(stmt, javalang.tree.ThrowStatement):
            return [f"THROW:{self._expression_to_str(stmt.expression)}"]
        return []

    def _extract_block(self, block) -> list[str]:
        if isinstance(block, javalang.tree.BlockStatement):
            results = []
            for s in block.statements:
                results.extend(self._classify_statement(s))
            return results
        return self._classify_statement(block)

    def _classify_if(self, stmt) -> list[str]:
        condition = self._expression_to_str(stmt.condition)
        results = [f"IF:{condition}"]
        if stmt.then_statement:
            results.extend(self._extract_block(stmt.then_statement))
        results.append("ENDIF")
        if stmt.else_statement:
            results.append("ELSE")
            results.extend(self._extract_block(stmt.else_statement))
            results.append("ENDELSE")
        return results

    def _classify_for(self, stmt) -> list[str]:
        results = ["FOR:loop"]
        if isinstance(stmt.body, javalang.tree.BlockStatement):
            for s in stmt.body.statements:
                results.extend(self._classify_statement(s))
        results.append("ENDFOR")
        return results

    def _classify_while(self, stmt) -> list[str]:
        condition = self._expression_to_str(stmt.condition)
        results = [f"WHILE:{condition}"]
        if isinstance(stmt.body, javalang.tree.BlockStatement):
            for s in stmt.body.statements:
                results.extend(self._classify_statement(s))
        results.append("ENDWHILE")
        return results

    def _classify_try(self, stmt) -> list[str]:
        results = ["TRY"]
        for s in (stmt.block or []):
            results.extend(self._classify_statement(s))
        results.append("ENDTRY")
        for catch in (stmt.catches or []):
            name = catch.parameter.name if catch.parameter else 'e'
            results.append(f"CATCH:{name}")
            for s in (catch.block or []):
                results.extend(self._classify_statement(s))
            results.append("ENDCATCH")
        return results

    def _classify_switch(self, stmt) -> list[str]:
        expr = self._expression_to_str(stmt.expression)
        results = [f"SWITCH:{expr}"]
        for case in (stmt.cases or []):
            label = ", ".join(self._expression_to_str(c) for c in case.case) if case.case else "default"
            results.append(f"CASE:{label}")
            for s in (case.statements or []):
                results.extend(self._classify_statement(s))
        results.append("ENDSWITCH")
        return results

    def _expression_to_str(self, expr) -> str:
        if expr is None:
            return ""
        if isinstance(expr, javalang.tree.MemberReference):
            qualifier = f"{expr.qualifier}." if expr.qualifier else ""
            return f"{qualifier}{expr.member}"
        if isinstance(expr, javalang.tree.MethodInvocation):
            qualifier = f"{expr.qualifier}." if expr.qualifier else ""
            return f"{qualifier}{expr.member}()"
        if isinstance(expr, javalang.tree.BinaryOperation):
            left = self._expression_to_str(expr.operandl)
            right = self._expression_to_str(expr.operandr)
            return f"{left} {expr.operator} {right}"
        if isinstance(expr, javalang.tree.Literal):
            return str(expr.value)
        if isinstance(expr, javalang.tree.This):
            return "this"
        if isinstance(expr, javalang.tree.ClassCreator):
            return f"new {expr.type.name}()"
        return type(expr).__name__
