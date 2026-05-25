from django.db import models

class GeneInfo(models.Model):
    raw_name = models.CharField(max_length=255)
    species_code = models.CharField(max_length=10)
    gene = models.CharField(max_length=100)
    locus_id = models.CharField(max_length=255)

    class Meta:
        db_table = "gene_info"
        verbose_name = "Gene Info"
        verbose_name_plural = "Gene Info"

    def __str__(self):
        return f"{self.gene} ({self.locus_id})"

class SpeciesInfo(models.Model):
    family = models.CharField(max_length=100, db_column="family")
    species = models.CharField(max_length=150, db_column="species")
    genome_version = models.CharField(max_length=100, db_column="genome_version")
    conservatory_genome_name = models.CharField(max_length=100,unique=True,db_column="conservatory_genome_name")

    class Meta:
        db_table = "species_info"
        verbose_name = "Species Info"
        verbose_name_plural = "Species Info"
        indexes = [
            models.Index(fields=["family"], name="idx_family"),
            models.Index(fields=["species"], name="idx_species"),
        ]

    def __str__(self):
        return f"{self.species} ({self.genome_version})"
    
class SearchResult(models.Model):
    species_code = models.CharField(max_length=50)
    query_protein_name = models.CharField(max_length=255)
    hit_protein_name = models.CharField(max_length=255, null=True, blank=True)
    tm_score = models.FloatField(null=True, blank=True)
    sequence_similarity = models.FloatField(null=True, blank=True)
    query_protein_length = models.IntegerField(null=True, blank=True)
    hit_protein_length = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "search_result"
        verbose_name = "Search Result"
        verbose_name_plural = "Search Results"

    def __str__(self):
        return f"{self.species_code} - {self.query_protein_name}"  
    
class ProteinInfo(models.Model):
    protein_id = models.CharField(max_length=100, db_index=True, verbose_name='Protein ID')
    protein_class = models.CharField(max_length=255, blank=True, null=True, verbose_name='Protein class')
    amino_acids = models.PositiveIntegerField(blank=True, null=True, verbose_name='Amino acids')
    gene_id = models.CharField(max_length=100, db_index=True, blank=True, null=True, verbose_name='Gene ID')
    organism = models.CharField(max_length=255, db_index=True, blank=True, null=True, verbose_name='Organism')
    sequencs = models.TextField(blank=True,null=True,verbose_name='Sequencs')

    domain = models.CharField(max_length=500, blank=True, null=True, verbose_name='Domain')

    class Meta:
        db_table = 'protein_info'
        ordering = ['id']

    def __str__(self):
        return f'{self.protein_id} - {self.gene_id}'
