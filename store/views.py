from django.db.models.aggregates import Count
from django.db.models import ProtectedError
from rest_framework.exceptions import NotFound

from rest_framework.mixins import CreateModelMixin ,RetrieveModelMixin,DestroyModelMixin
from rest_framework.viewsets import ModelViewSet , GenericViewSet
from rest_framework.permissions import AllowAny, DjangoModelPermissions, DjangoModelPermissionsOrAnonReadOnly, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Cart, CartItem, Collection, Customer, Order, OrderItem, Product, Review
from .serializers import UpdateCartItemSerializer,AddCartItemSerializer, CartItemSerializer,CartSerializer ,CollectionSerializer, ProductSerializer, ReviewsSerializer

from .filters import ProductFilter
from .pagination import DefaultPagination

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']


    


    def get_serializer_context(self):
        return {'request': self.request}
    
    
    
      

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer




    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']):
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)
    
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewsSerializer


    def create(self, request, *args, **kwargs):

        product_id = self.kwargs['product_pk']
        try:
            Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise NotFound(detail="Product not found.")
            # return Response({'error': 'This Prdouct  Not Found .'}, status=status.HTTP_404_NOT_FOUND)

        return super().create(request, *args, **kwargs)
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
    

class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
 
    queryset=Cart.objects.prefetch_related('items__product').all()
    serializer_class=CartSerializer

    

    


# class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        return {
            'POST': AddCartItemSerializer,
            'PATCH': UpdateCartItemSerializer,
        }.get(self.request.method, CartItemSerializer)

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
   

    def get_queryset(self):
        return CartItem.objects.select_related('product') .filter(cart_id=self.kwargs['cart_pk'])     
    

        
    # http_method_names = ['get', 'post', 'patch', 'delete']
    # # serializer_class=CartItemSerializer
    # def get_serializer_class(self):
    #     if self.request.method == 'POST':
    #         return AddCartItemSerializer
    #     elif self.request.method == 'PATCH':
    #         return UpdateCartItemSerializer
    #     return CartItemSerializer
    
    # def get_serializer_context(self):
    #     return {'cart_id': self.kwargs['cart_pk']}

 

#    def get_queryset(self):
#         return CartItem.objects \
#             .filter(cart_id=self.kwargs['cart_pk'])\
#             .select_related('product')


