from django.urls import path


from . import views


urlpatterns = [
    path("sequence/align/", views.protein_alignment_api, name="protein_alignment_api"),
    path("structure/align/", views.structure_align_view, name="structure_align_view"),
]

