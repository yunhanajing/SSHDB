from django.urls import path

from .views import ExampleProteinAPIView, ProteinEmbeddingSearchAPIView


app_name = "search"

urlpatterns = [
    path(
        "protein-embedding/",
        ProteinEmbeddingSearchAPIView.as_view(),
        name="protein-embedding-search",
    ),
    path(
        "protein-example/",
        ExampleProteinAPIView.as_view(),
        name="protein-example",
    ),
]
