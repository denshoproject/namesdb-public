from collections import OrderedDict

from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request as RestRequest
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from django.http.request import HttpRequest

from elastictools import docstore, search

from . import models

DEFAULT_LIMIT = 25


# views ----------------------------------------------------------------

@api_view(['GET'])
def index(request, format=None):
    """Swagger UI: /api/swagger/
    """
    data = {
        'persons': reverse('namespub-api-persons', request=request),
        'farrecords': reverse('namespub-api-farrecords', request=request),
        'wrarecords': reverse('namespub-api-wrarecords', request=request),
        'search': reverse('namespub-api-search', request=request),
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
    return _list(request, model_objects(
        request, 'person', filters, sort_fields=['id']
    ))

@api_view(['GET'])
def farrecords(request, format=None):
    """List multiple FarRecords with filtering by most fields (exact values)
    """
    filters = _list_filters(request)
    return _list(request, model_objects(
        request, 'farrecord', filters, sort_fields=['id']
    ))

@api_view(['GET'])
def wrarecords(request, format=None):
    """List multiple WraRecords with filtering by most fields (exact values)
    """
    filters = _list_filters(request)
    return _list(request, model_objects(
        request, 'wrarecord', filters, sort_fields=['id']
    ))

def _list_filters(request):
    return {
        field: request.GET[field]
        for field in models.SEARCH_INCLUDE_FIELDS
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
        return self.grep(request)
    
    def post(self, request, format=None):
        """Search the Names Database; good for more complicated custom searches.
        
        `fulltext`: Search string using Elasticsearch query_string syntax.
        `m_camp`: One or more camp IDs e.g. "9-rohwer".
        `page`: Selected results page (default: 0).
        
        Search API help: /api/search/help/
        """
        return self.grep(request)
    
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
        
        if isinstance(request, HttpRequest):
            params = request.GET.copy()
        elif isinstance(request, RestRequest):
            params = request.query_params.dict()
        searcher = search.Searcher(
            docstore.Docstore(
                models.INDEX_PREFIX, settings.DOCSTORE_HOST, settings
            )
        )
        searcher.prepare(
            params=params,
            params_whitelist=['fulltext'] + models.SEARCH_INCLUDE_FIELDS_PERSON,
            search_models=['namesperson'],
            sort=[],
            #fields=models.SEARCH_INCLUDE_FIELDS_PERSON,
            fields=['id','model','nr_id','preferred_name'],
            fields_nested=[],
            fields_agg=models.AGG_FIELDS_PERSON,
            #highlight_fields=highlight_fields,
            wildcards=False,
        )
        results = searcher.execute(limit, offset)
        data = results.to_dict(
            request=request,
            format_functions=models.FORMATTERS,
            #pad=True,
        )
        return Response(data)


def model_objects(
        request, model, filters={}, sort_fields=[],
        fields=models.SEARCH_INCLUDE_FIELDS, limit=DEFAULT_LIMIT, offset=0,
        just_count=False
):
    """Return all documents in MODEL index (paged)
    
    Returns a paged list with count/prev/next metadata
    
    @param request: Django request object.
    @param model: str
    @param sort_fields: list
    @param fields: list
    @param limit: int
    @param offset: int
    @param just_count: boolean
    @returns: dict
    """
    if model in ['person', 'persons']:
        search_models = ['namesperson']
        params_allowlist = models.SEARCH_INCLUDE_FIELDS_PERSON
        search_include_fields = models.SEARCH_INCLUDE_FIELDS_PERSON
        agg_fields = models.AGG_FIELDS_PERSON
        highlight_fields = models.HIGHLIGHT_FIELDS_PERSON
    elif model in ['farrecord', 'farrecords']:
        search_models = ['namesfarrecord']
        params_allowlist = models.SEARCH_INCLUDE_FIELDS_FARRECORD
        search_include_fields = models.SEARCH_INCLUDE_FIELDS_FARRECORD
        agg_fields = models.AGG_FIELDS_FARRECORD
        highlight_fields = models.HIGHLIGHT_FIELDS_FARRECORD
    elif model in ['wrarecord', 'wrarecords']:
        search_models = ['nameswrarecord']
        params_allowlist = models.SEARCH_INCLUDE_FIELDS_WRARECORD
        search_include_fields = models.INCLUDE_FIELDS_WRARECORD
        agg_fields = models.AGG_FIELDS_WRARECORD
        highlight_fields = models.HIGHLIGHT_FIELDS_WRARECORD
    
    params=request.GET.copy()
    searcher = search.Searcher(
        docstore.Docstore(
            models.INDEX_PREFIX, settings.DOCSTORE_HOST, settings
        )
    )
    searcher.prepare(
        params=params,
        params_whitelist=['fulltext'] + params_allowlist,
        search_models=search_models,
        sort=[],
        fields=search_include_fields,
        fields_nested=[],
        fields_agg=agg_fields,
        #highlight_fields=highlight_fields,
        wildcards=False,
    )
    results = searcher.execute(limit, offset)
    return results.ordered_dict(
        request, format_functions=models.FORMATTERS
    )
