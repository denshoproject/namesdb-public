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
        api.person, name='namesdb-api-person'
    ),
    re_path(
        r'^api/1.0/farrecords/(?P<object_id>[0-9a-zA-Z_:-]+)',
        api.farrecord, name='namesdb-api-farrecord'
    ),
    re_path(
        r'^api/1.0/wrarecords/(?P<object_id>[0-9a-zA-Z_:-]+)',
        api.wrarecord, name='namesdb-api-wrarecord'
    ),
    path('api/1.0/persons/', api.persons, name='namesdb-api-persons'),
    path('api/1.0/farrecords/', api.farrecords, name='namesdb-api-farrecords'),
    path('api/1.0/wrarecords/', api.wrarecords, name='namesdb-api-wrarecords'),
    path('api/1.0/search/', api.Search.as_view(), name='namesdb-api-search'),
    path('api/1.0/', api.index, name='namesdb-api-index'),
    
    path('search/', views.search_ui, name='namesdb-search'),
    re_path(
        r'^persons/(?P<naan>[0-9a-zA-Z_:-]+)/(?P<noid>[0-9a-zA-Z_:-]+)',
        views.person, name='namesdb-person'
    ),
    re_path(
        r'^farrecords/(?P<object_id>[0-9a-zA-Z_:-]+)',
        views.farrecord, name='namesdb-farrecord'
    ),
    re_path(
        r'^wrarecords/(?P<object_id>[0-9a-zA-Z_:-]+)',
        views.wrarecord, name='namesdb-wrarecord'
    ),
    path('persons/', views.persons, name='namesdb-persons'),
    path('farrecords/', views.farrecords, name='namesdb-farrecords'),
    path('wrarecords/', views.wrarecords, name='namesdb-wrarecords'),
    path('', views.search_ui, name='namesdb-index'),
]
