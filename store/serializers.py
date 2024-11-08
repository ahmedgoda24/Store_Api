from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import Cart, CartItem, Customer, Order, OrderItem, Product, Collection, Review


class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory',
                  'unit_price', 'price_with_tax', 'collection','reviews']

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')
    
    def to_representation(self, instance):
        data= super().to_representation(instance)
        data.update({
           'review':instance.reviews.count(),
           
        })
        # data['reviews']=instance.reviews.count()
        # data['collection']=instance.collection.title


        return data
    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)
    
class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)

class ReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model=Review
        fields = ['id', 'name', 'description', 'date', 'product_id']
        read_only_fields = ['product_id']


    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)
    
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']




class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    total_price=serializers.SerializerMethodField()

    def get_total_price(self,cart_item:CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items=CartItemSerializer(many=True,read_only=True)
    total_price=serializers.SerializerMethodField()

    def get_total_price(self,cart:Cart):
        return sum( [item.quantity * item.product.unit_price for item in cart.items.all()])
    class Meta:
        model=Cart
        fields = ['id','items','total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given ID was found.')
        return value

    def save(self, **kwargs):
        cart_id=self.context['cart_id']
        product_id=self.validated_data['product_id']
        quantity=self.validated_data['quantity']


        try:
            cart_item=CartItem.objects.get(cart_id=cart_id,product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance=cart_item
        except CartItem.DoesNotExist:
            CartItem.objects.create(cart_id=cart_id, **self.validated_data)
            return self.instance
  
    class Meta:
        model=CartItem
        fields= ['id','product_id','quantity']



class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

    


# class AddCartItemSerializer(serializers.ModelSerializer):
#     product_id = serializers.IntegerField()


#     def validate_product_id(self, value):
#         if not Product.objects.filter(pk=value).exists():
#             raise serializers.ValidationError('No product with the given ID was found.')
#         return value
#     def save(self, **kwargs):
#         cart_id=self.context['cart_id']
#         product_id=self.validated_data['product_id']
#         quantity=self.validated_data['quantity']

#         try:
#             cart_item=CartItem.objects.get(cart_id=cart_id,product_id=product_id)
#             cart_item.quantity += quantity
#             cart_item.save()
#             self.instance=cart_item
#         except CartItem.DoesNotExist:
#             CartItem.objects.create(cart_id=cart_id,product_id=product_id,quantity=quantity)
#             return self.instance
#     class Meta:
#         model = CartItem
#         fields = ['id', 'product_id', 'quantity']


