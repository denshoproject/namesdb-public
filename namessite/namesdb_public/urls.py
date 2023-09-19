from django.urls import include, path, re_path
from drf_yasg import views as yasg_views
from drf_yasg import openapi
from rest_framework import permissions

from . import api
from . import views


schema_view = yasg_views.get_schema_view(
   openapi.Info(
      title="Densho Digital Repository API",
      default_version='0.2',
      description='"namesdb" is the new app; "names" is the old one',
      terms_of_service="http://ddr.densho.org/terms/",
      contact=openapi.Contact(email="info@densho.org"),
      #license=openapi.License(name="TBD"),
   ),
   #validators=['flex', 'ssv'],
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/swagger.json',
         schema_view.without_ui(cache_timeout=0), name='schema-json'
    ),
    path('api/swagger.yaml',
         schema_view.without_ui(cache_timeout=0), name='schema-yaml'
    ),
    path('api/swagger/',
         schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'
    ),
    path('api/redoc/',
         schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'
    ),
    
    re_path(
        r'^api/1.0/persons/(?P<naan>[0-9a-zA-Z_:-]+)/(?P<noid>[0-9a-zA-Z_:-]+)',
        api.person, name='namespub-api-person'
    ),
    re_path(
        r'^api/1.0/farrecords/(?P<object_id>[0-9a-zA-Z_:-]+)',
        api.farrecord, name='namespub-api-farrecord'
    ),
    re_path(
        r'^api/1.0/wrarecords/(?P<object_id>[0-9a-zA-Z_:-]+)',
        api.wrarecord, name='namespub-api-wrarecord'
    ),
    path('api/1.0/persons/', api.persons, name='namespub-api-persons'),
    path('api/1.0/farrecords/', api.farrecords, name='namespub-api-farrecords'),
    path('api/1.0/wrarecords/', api.wrarecords, name='namespub-api-wrarecords'),
    re_path(
        r'^api/1.0/farpages/(?P<facility_id>[0-9a-zA-Z_:-]+)/(?P<far_page>[0-9]+)',
        api.farpage, name='namespub-api-farpage'
    ),
    path('api/1.0/farpages/', api.farpages, name='namespub-api-farpages'),
    path('api/1.0/search/', api.Search.as_view(), name='namespub-api-search'),
    path('api/1.0/', api.index, name='namespub-api-index'),
    
    path('search/', views.search_ui, name='namespub-search'),
    re_path(
        r'^persons/(?P<naan>[0-9a-zA-Z_:-]+)/(?P<noid>[0-9a-zA-Z_:-]+)',
        views.person, name='namespub-person'
    ),
    re_path(
        r'^farrecords/(?P<object_id>[0-9a-zA-Z_:-]+)',
        views.farrecord, name='namespub-farrecord'
    ),
    re_path(
        r'^wrarecords/(?P<object_id>[0-9a-zA-Z_:-]+)',
        views.wrarecord, name='namespub-wrarecord'
    ),
    path('persons/', views.persons, name='namespub-persons'),
    path('farrecords/', views.farrecords, name='namespub-farrecords'),
    path('wrarecords/', views.wrarecords, name='namespub-wrarecords'),
    re_path(
        r'^farpages/(?P<facility_id>[0-9a-zA-Z_:-]+)/(?P<far_page>[0-9]+)',
        views.farpage, name='namespub-farpage'
    ),
    path('farpages/', views.farpages, name='namespub-farpages'),
    path('', views.index, name='namespub-index'),
]
