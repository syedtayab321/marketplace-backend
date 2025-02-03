from rest_framework import serializers
from .models import Product, ProductImage
from decimal import Decimal

# Product Image Serializer
class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context["product_id"]
        return ProductImage.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = ProductImage
        fields = ["id", "image"]


# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    vendor = serializers.StringRelatedField(read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory',
                  'unit_price', 'price_with_tax', 'images', 'vendor', 'average_rating']

    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)

    def get_average_rating(self, product: Product):
        # Assuming `average_rating` is calculated as an aggregation of related reviews
        return product.reviews.aggregate(average=Avg('rating'))['average'] or 0.0


# Simple Product Serializer (For quick display of essential info)
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']
