from django.db import models

class ProteinEmbedding(models.Model):
    id = models.BigAutoField(primary_key=True)

    species = models.ForeignKey(
        "api.SpeciesInfo",
        db_column="species_id",
        on_delete=models.RESTRICT,
        related_name="protein_embeddings",
    )

    protein_id = models.CharField(max_length=100)

    embedding_norm = models.BinaryField(max_length=2048)

    dim = models.SmallIntegerField(default=512)

    class Meta:
        managed = False
        db_table = "protein_embedding"
        constraints = [
            models.UniqueConstraint(
                fields=["species", "protein_id"],
                name="uniq_species_protein",
            )
        ]
        indexes = [
            models.Index(fields=["protein_id"], name="idx_protein_id"),
        ]

    def __str__(self):
        return f"{self.species_id} - {self.protein_id}"


