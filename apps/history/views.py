from rest_framework import generics
from .models import DiagramHistory
from .serializers import DiagramHistoryListSerializer, DiagramHistoryDetailSerializer


class HistoryListView(generics.ListAPIView):
    """
    Lista todas las conversiones del usuario autenticado.

    GET /history/
    Permisos: usuario autenticado.
    Returns: lista de entradas con id, filename, version y created_at.
    El queryset filtra por request.user para aislar el historial por cuenta.
    """

    serializer_class = DiagramHistoryListSerializer

    def get_queryset(self):
        return DiagramHistory.objects.filter(user=self.request.user)


class HistoryDetailView(generics.RetrieveDestroyAPIView):
    """
    Recupera o elimina una conversión específica del usuario autenticado.

    GET    /history/<id>/  — retorna source_code y los tres diagramas PlantUML.
    DELETE /history/<id>/  — elimina el registro permanentemente.
    Permisos: usuario autenticado y propietario del registro.
    El queryset filtra por request.user para evitar acceso cruzado entre cuentas.
    """

    serializer_class = DiagramHistoryDetailSerializer

    def get_queryset(self):
        return DiagramHistory.objects.filter(user=self.request.user)
