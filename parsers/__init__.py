from .java_parser import JavaParser
from .base_generator import DiagramGenerator
from .class_diagram import ClassDiagramGenerator
from .usecase_diagram import UseCaseDiagramGenerator
from .flow_diagram import FlowDiagramGenerator
from .generator_factory import DiagramGeneratorFactory

# Register generators with the factory
DiagramGeneratorFactory.register("class", ClassDiagramGenerator)
DiagramGeneratorFactory.register("usecase", UseCaseDiagramGenerator)
DiagramGeneratorFactory.register("flow", FlowDiagramGenerator)
