from rest_framework import generics
from .models import DiagramHistory
from .serializers import DiagramHistoryListSerializer, DiagramHistoryDetailSerializer


class HistoryListView(generics.ListAPIView):
    serializer_class = DiagramHistoryListSerializer

    def get_queryset(self):
        return DiagramHistory.objects.filter(user=self.request.user)


class HistoryDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = DiagramHistoryDetailSerializer

    def get_queryset(self):
        return DiagramHistory.objects.filter(user=self.request.user)
