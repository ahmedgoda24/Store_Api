from django.urls import path
from django.urls.conf import include
# from rest_framework_nested import routers
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
urlpatterns = router.urls 