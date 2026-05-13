from rest_framework import serializers
from .models import Category, Produit, Commande, CommandeItem, Favori

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProduitSerializer(serializers.ModelSerializer):
    categorie_nom = serializers.CharField(source='categorie.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    prix_final = serializers.FloatField(read_only=True)

    class Meta:
        model = Produit
        fields = ['id', 'libelle', 'description', 'prix', 'prix_final', 'solde',
                  'type', 'categorie', 'categorie_nom', 'image', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class CommandeItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommandeItem
        fields = ['produit_nom', 'quantite', 'prix_unitaire']

class CommandeSerializer(serializers.ModelSerializer):
    items = CommandeItemSerializer(many=True, read_only=True)

    class Meta:
        model = Commande
        fields = ['id', 'nom', 'email', 'telephone', 'adresse', 'dateCde', 'totalCde', 'items']

class FavoriSerializer(serializers.ModelSerializer):
    produit = ProduitSerializer(read_only=True)

    class Meta:
        model = Favori
        fields = ['id', 'produit']
