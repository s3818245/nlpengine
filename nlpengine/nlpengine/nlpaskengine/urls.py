from multiprocessing.forkserver import connect_to_new_process
from django.urls import path
from . import views
urlpatterns = [
    path('query/', views.get_query, name="query"),
    path('database/', views.connect_database, name="database")
]