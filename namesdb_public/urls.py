from django.urls import include, path, re_path

from . import api
from . import views


urlpatterns = [
    re_path(
        r'^api/1.0/persons/(?P<object_id>[0-9a-zA-Z_:-]+)',
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
        r'^persons/(?P<object_id>[0-9a-zA-Z_:-]+)',
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
