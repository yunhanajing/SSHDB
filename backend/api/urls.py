from django.urls import path
from .views import GeneUniqueListAPIView,SpeciesGenomeVersionListAPIView,SearchResultAPIView,ProteinInfoAPIView,ProteinSequenceAPIView,ProteinCifFileAPIView

urlpatterns = [
    path("genes/unique/", GeneUniqueListAPIView.as_view(), name="gene-unique-list"),
    path("species/names/", SpeciesGenomeVersionListAPIView.as_view(), name="species-name-list"),
    path("search/results/", SearchResultAPIView.as_view(), name="search-result-list"),
    path("protein/info/", ProteinInfoAPIView.as_view(), name="protein-info-list"),
    path("protein/sequence/", ProteinSequenceAPIView.as_view(), name="protein-sequence"),
    path("protein/cif/", ProteinCifFileAPIView.as_view(), name="protein-cif-file"),
]
