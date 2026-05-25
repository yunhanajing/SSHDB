from django.urls import path

from .views import ProteinEmbeddingSearchAPIView


app_name = "search"

urlpatterns = [
    path(
        "protein-embedding/",
        ProteinEmbeddingSearchAPIView.as_view(),
        name="protein-embedding-search",
    ),
]

