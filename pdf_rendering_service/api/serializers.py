from rest_framework import serializers
from api.models import Document


class DocumentStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ["status","n_pages"]


class DocumentIdSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = ["id"]

