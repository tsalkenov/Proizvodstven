from django.urls import path
from . import views
urlpatterns = [
    path('map/', views.figure_map,name='map')
]
