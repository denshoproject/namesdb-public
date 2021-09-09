from collections import OrderedDict

from django.conf import settings

from elasticsearch import Elasticsearch

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request as RestRequest
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from namesdb.definitions import SEARCH_FIELDS as NAMESDB_SEARCH_FIELDS
from . import docstore
from . import search
from . import models

# set default hosts and index
DOCSTORE = docstore.Docstore()

DEFAULT_LIMIT = 25


# views ----------------------------------------------------------------

@api_view(['GET'])
def index(request, format=None):
    """Swagger UI: /api/swagger/
    """
    data = {
        'persons': reverse('namesdb-api-persons', request=request),
        'farrecords': reverse('namesdb-api-farrecords', request=request),
        'wrarecords': reverse('namesdb-api-wrarecords', request=request),
        'search': reverse('namesdb-api-search', request=request),
    }
    return Response(data)


@api_view(['GET'])
def object_nodes(request, object_id):
    return files(request._request, object_id)

def _list(request, data):
    host = request.META.get('HTTP_HOST')
    path = request.META['PATH_INFO']
    if data.get('prev'):
        data['prev'] = 'http://%s%s%s' % (host, path, data['prev'])
    if data.get('next'):
        data['next'] = 'http://%s%s%s' % (host, path, data['next'])
    return Response(data)

@api_view(['GET'])
def persons(request, format=None):
    """List multiple Persons with filtering by most fields (exact values)
    """
    filters = _list_filters(request)
    return _list(request, search.model_objects(
        request, ['person'], filters, sort_fields=['id']
    ))

@api_view(['GET'])
def farrecords(request, format=None):
    """List multiple FarRecords with filtering by most fields (exact values)
    """
    filters = _list_filters(request)
    return _list(request, search.model_objects(
        request, ['farrecord'], filters, sort_fields=['id']
    ))

@api_view(['GET'])
def wrarecords(request, format=None):
    """List multiple WraRecords with filtering by most fields (exact values)
    """
    filters = _list_filters(request)
    return _list(request, search.model_objects(
        request, ['wrarecord'], filters, sort_fields=['id']
    ))

def _list_filters(request):
    return {
        field: request.GET[field]
        for field in search.SEARCH_PARAM_ALLOWLIST
        if request.GET.get(field)
    }

def _detail(request, data):
    """Common function for detail views.
    """
    if not data:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(data)

@api_view(['GET'])
def person(request, naan, noid, format=None):
    object_id = '/'.join([naan, noid])
    return _detail(request, models.Person.get(object_id, request))

@api_view(['GET'])
def farrecord(request, object_id, format=None):
    return _detail(request, models.FarRecord.get(object_id, request))

@api_view(['GET'])
def wrarecord(request, object_id, format=None):
    return _detail(request, models.WraRecord.get(object_id, request))


class Search(APIView):
    
    def get(self, request, format=None):
        """Search the Names Database; good for simpler searches.
        
        `fulltext`: Search string using Elasticsearch query_string syntax.
        `m_camp`: One or more camp IDs e.g. "9-rohwer".
        `page`: Selected results page (default: 0).

        Search API help: /api/search/help/
        """
        if request.GET.get('fulltext'):
            return self.grep(request)
        return Response({})
    
    def post(self, request, format=None):
        """Search the Names Database; good for more complicated custom searches.
        
        `fulltext`: Search string using Elasticsearch query_string syntax.
        `m_camp`: One or more camp IDs e.g. "9-rohwer".
        `page`: Selected results page (default: 0).
        
        Search API help: /api/search/help/
        """
        if request.data.get('fulltext'):
            return self.grep(request)
        return Response({})
    
    def grep(self, request):
        """NamesDB search
        """
        def reget(request, field):
            if request.GET.get(field):
                return request.GET[field]
            elif request.data.get(field):
                return request.data[field]
            return None
        
        fulltext = reget(request, 'fulltext')
        offset = reget(request, 'offset')
        limit = reget(request, 'limit')
        page = reget(request, 'page')
        
        if offset:
            # limit and offset args take precedence over page
            if not limit:
                limit = settings.RESULTS_PER_PAGE
            offset = int(offset)
        elif page:
            limit = settings.RESULTS_PER_PAGE
            thispage = int(page)
            offset = search.es_offset(limit, thispage)
        else:
            limit = settings.RESULTS_PER_PAGE
            offset = 0
        
        searcher = search.Searcher()
        if isinstance(request, HttpRequest):
            params = request.GET.copy()
        elif isinstance(request, RestRequest):
            params = request.query_params.dict()
        searcher.prepare(
            params=params,
            params_allowlist=['fulltext', 'm_camp'],
            search_models=['names-record'],
            fields=NAMESDB_SEARCH_FIELDS,
            fields_nested=[],
            fields_agg={'m_camp':'m_camp'},
        )
        results = searcher.execute(limit, offset)
        return Response(
            results.ordered_dict(request, format_functions=models.FORMATTERS)
        )
