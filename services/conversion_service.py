import hashlib
from collections import OrderedDict

from parsers.java_parser import JavaParser
from parsers.generator_factory import DiagramGeneratorFactory


class ConversionService:
    """Facade that orchestrates Java parsing and diagram generation.

    Provides a single entry point for converting Java source code into
    multiple UML diagram formats.  Results are cached by content hash
    (LRU eviction, max 128 entries).
    """

    _MAX_CACHE = 128

    def __init__(self) -> None:
        self._parser = JavaParser()
        self._generators = DiagramGeneratorFactory.create_all()
        self._cache: OrderedDict[str, dict] = OrderedDict()

    def convert(self, sources: list[tuple[str, str]]) -> dict:
        """Convert a list of (filename, java_code) pairs into UML diagrams.

        Returns a dict with keys: diagrams, errors, sources.
        """
        cache_key = self._hash(sources)
        if cache_key in self._cache:
            self._cache.move_to_end(cache_key)
            return self._cache[cache_key]

        all_classes = []
        errors: list[str] = []

        for filename, code in sources:
            try:
                classes = self._parser.parse(code)
                all_classes.extend(classes)
            except Exception as exc:
                errors.append(f"{filename}: {exc}")

        diagrams: dict[str, str] = {}
        for name, gen in self._generators.items():
            diagrams[name] = gen.generate(all_classes) if all_classes else ""

        result = {
            "diagrams": diagrams,
            "errors": errors,
            "sources": [{"filename": fn, "code": code} for fn, code in sources],
        }

        self._cache[cache_key] = result
        if len(self._cache) > self._MAX_CACHE:
            self._cache.popitem(last=False)

        return result

    @staticmethod
    def _hash(sources: list[tuple[str, str]]) -> str:
        content = "".join(f"{n}:{c}" for n, c in sorted(sources))
        return hashlib.sha256(content.encode()).hexdigest()
