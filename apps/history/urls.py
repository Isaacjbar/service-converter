from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.HistoryListView.as_view(), name='history-list'),
    path('history/<int:pk>/', views.HistoryDetailView.as_view(), name='history-detail'),
]
