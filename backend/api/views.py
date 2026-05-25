from django.shortcuts import render

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from collections import defaultdict
from rest_framework import status
from django.views.decorators.http import require_GET
from .models import GeneInfo
from .models import SpeciesInfo
from .models import SearchResult
from .models import ProteinInfo

import re

class GeneUniqueListAPIView(APIView):
    def get(self, request):
        genes = (
            GeneInfo.objects
            .values_list("gene", flat=True)
            .distinct()
            .order_by("gene")
        )
        return Response({
            "code": 200,
            "message": "success",
            "data": list(genes)
        }, status=status.HTTP_200_OK)
        

class SpeciesGenomeVersionListAPIView(APIView):
    def get(self, request):
        queryset = (
            SpeciesInfo.objects
            .values(
                "family",
                "species",
                "genome_version",
                "conservatory_genome_name"
            )
            .order_by("species", "genome_version")
        )

        species_map = defaultdict(lambda: {
            "family": "",
            "species": "",
            "genome_versions": []
        })

        for item in queryset:
            species = item["species"]

            species_map[species]["family"] = item["family"]
            species_map[species]["species"] = species
            species_map[species]["genome_versions"].append({
                "genome_version": item["genome_version"],
                "conservatory_genome_name": item["conservatory_genome_name"]
            })

        return Response({
            "code": 200,
            "message": "success",
            "data": list(species_map.values())
        }, status=status.HTTP_200_OK)
        

class SearchResultAPIView(APIView):
    def get(self, request):
        genes = [
            g.strip()
            for g in request.GET.getlist("gene")
            if g.strip()
        ]

        species_names = [
            s.strip()
            for s in request.GET.getlist("species")
            if s.strip()
        ]

        categories = [
            c.strip().upper()
            for c in request.GET.getlist("category")
            if c.strip()
        ]

        conservatory_genome_names = [
            g.strip()
            for g in request.GET.getlist("conservatory_genome_name")
            if g.strip()
        ]

        if not genes:
            return Response({
                "code": 400,
                "message": "at least one gene is required",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        if not species_names:
            return Response({
                "code": 400,
                "message": "at least one species is required",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        if not conservatory_genome_names:
            return Response({
                "code": 400,
                "message": "genome version is required",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        species_info_qs = (
            SpeciesInfo.objects
            .filter(
                species__in=species_names,
                conservatory_genome_name__in=conservatory_genome_names
            )
            .values(
                "species",
                "genome_version",
                "conservatory_genome_name"
            )
        )

        species_info_list = list(species_info_qs)

        if not species_info_list:
            return Response({
                "code": 400,
                "message": "no valid species or genome version found",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        valid_species_codes = {
            item["conservatory_genome_name"]
            for item in species_info_list
            if item["conservatory_genome_name"]
        }

        if not valid_species_codes:
            return Response({
                "code": 400,
                "message": "no valid conservatory genome name found",
                "data": []
            }, status=status.HTTP_400_BAD_REQUEST)

        gene_query = Q()

        for gene in genes:
            pattern = rf'^[A-Za-z]{{2}}{re.escape(gene)}__'
            gene_query |= Q(query_protein_name__regex=pattern)

        queryset = (
            SearchResult.objects
            .filter(species_code__in=valid_species_codes)
            .filter(gene_query)
        )

        if categories:
            valid_categories = {"A", "B", "C"}
            categories = [
                c for c in categories
                if c in valid_categories
            ]

            if categories:
                category_query = Q()

                if "A" in categories:
                    category_query |= Q(
                        tm_score__gte=50,
                        sequence_similarity__gte=50
                    )

                if "B" in categories:
                    category_query |= Q(
                        tm_score__gte=50,
                        sequence_similarity__gte=30,
                        sequence_similarity__lt=50
                    )

                if "C" in categories:
                    category_query |= Q(
                        tm_score__gte=50,
                        sequence_similarity__lt=30
                    )

                queryset = queryset.filter(category_query)

        queryset = queryset.order_by(
            "species_code",
            "query_protein_name"
        )

        data = list(queryset.values(
            "id",
            "species_code",
            "query_protein_name",
            "hit_protein_name",
            "tm_score",
            "sequence_similarity",
            "query_protein_length",
            "hit_protein_length"
        ))

        return Response({
            "code": 200,
            "message": "success",
            "data": data
        }, status=status.HTTP_200_OK)
        
class ProteinInfoAPIView(APIView):
    def get(self, request):
        gene_ids = request.GET.getlist('gene_id')
        organisms = request.GET.getlist('organism')

        gene_ids = [item.strip() for item in gene_ids if item.strip()]
        organisms = [item.strip() for item in organisms if item.strip()]

        queryset = ProteinInfo.objects.all()

        if gene_ids:
            gene_query = Q()

            for gene_id in gene_ids:
                # 输入 ACP，可以匹配：
                # ACP
                # GMACP
                # ACP_
                # ACP_001
                # GMACP_
                # GMACP_001
                #
                # 不匹配：
                # ACP12
                # GMACP12
                gene_query |= Q(gene_id__iendswith=gene_id)
                gene_query |= Q(gene_id__icontains=f'{gene_id}_')

            queryset = queryset.filter(gene_query)

        if organisms:
            queryset = queryset.filter(organism__in=organisms)

        queryset = queryset.order_by('gene_id', 'organism', 'protein_id')

        data = [
            {
                'protein_id': item.protein_id,
                'protein_class': item.protein_class,
                'amino_acids': item.amino_acids,
                'gene_id': item.gene_id,
                'organism': item.organism,
                'domain': item.domain,
            }
            for item in queryset
        ]

        return Response({
            'data': data,
            'total': len(data),
        })
        
class ProteinSequenceAPIView(APIView):
    def get(self, request):
        protein_id = request.GET.get('protein_id', '').strip()

        if not protein_id:
            return Response({
                'message': 'Missing protein_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        item = ProteinInfo.objects.filter(protein_id=protein_id).first()

        if not item:
            return Response({
                'message': 'Protein not found'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'data': {
                'protein_id': item.protein_id,
                'gene_id': item.gene_id,
                'organism': item.organism,
                'protein_sequence': item.sequencs or '',
            }
        })
        
