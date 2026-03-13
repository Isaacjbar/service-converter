from django.urls import path
from . import views

urlpatterns = [
    path('convert/', views.ConvertView.as_view(), name='convert'),
    path('examples/', views.ExamplesView.as_view(), name='examples'),
]
