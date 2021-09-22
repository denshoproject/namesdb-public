"""
    searcher = search.Searcher()
    searcher.prepare(
        params=request.GET.copy(),
        params_allowlist=models.SEARCH_INCLUDE_FIELDS,
        search_models=models.SEARCH_MODELS,
        fields=models.SEARCH_INCLUDE_FIELDS,
        fields_nested=models.SEARCH_NESTED_FIELDS,
        fields_agg=models.SEARCH_AGG_FIELDS,
    )
    limit,offset = _limit_offset(request)
    results = searcher.execute(limit, offset)
"""


# -*- coding: utf-8 -*-

from collections import OrderedDict
from copy import deepcopy
import json
import logging
logger = logging.getLogger(__name__)
import os
import re
from urllib.parse import urlparse, urlunsplit

from elasticsearch_dsl import Index, Search, A, Q
from elasticsearch_dsl.query import Match, MultiMatch, QueryString
from elasticsearch_dsl.connections import connections

from rest_framework.request import Request as RestRequest
from rest_framework.reverse import reverse

from django.conf import settings
from django.http.request import HttpRequest

from . import docstore
from . import models

#SEARCH_LIST_FIELDS = models.all_list_fields()
DEFAULT_LIMIT = 500

DOCSTORE = docstore.Docstore()

# fields where the relevant value is nested e.g. topics.id
# TODO move to ddr-defs/repo_models/elastic.py?
SEARCH_NESTED_FIELDS = []

# TODO move to ddr-defs/repo_models/elastic.py?
SEARCH_AGG_FIELDS = models.SEARCH_AGG_FIELDS

SEARCH_MODELS = models.DOCTYPES

# fields searched by query e.g. query will find search terms in these fields
# IMPORTANT: These are used for fulltext search so they must ALL be TEXT fields
# TODO move to ddr-defs/repo_models/elastic.py?
SEARCH_INCLUDE_FIELDS = models.SEARCH_INCLUDE_FIELDS

SEARCH_FORM_LABELS = {
    'camp': 'Camp',
}


def es_offset(pagesize, thispage):
    """Convert Django pagination to Elasticsearch limit/offset
    
    >>> es_offset(pagesize=10, thispage=1)
    0
    >>> es_offset(pagesize=10, thispage=2)
    10
    >>> es_offset(pagesize=10, thispage=3)
    20
    
    @param pagesize: int Number of items per page
    @param thispage: int The current page (1-indexed)
    @returns: int offset
    """
    page = thispage - 1
    if page < 0:
        page = 0
    return pagesize * page

def start_stop(limit, offset):
    """Convert Elasticsearch limit/offset to Python slicing start,stop
    
    >>> start_stop(10, 0)
    0,9
    >>> start_stop(10, 1)
    10,19
    >>> start_stop(10, 2)
    20,29
    """
    start = int(offset)
    stop = (start + int(limit))
    return start,stop
    
def django_page(limit, offset):
    """Convert Elasticsearch limit/offset pagination to Django page
    
    >>> django_page(limit=10, offset=0)
    1
    >>> django_page(limit=10, offset=10)
    2
    >>> django_page(limit=10, offset=20)
    3
    
    @param limit: int Number of items per page
    @param offset: int Start of current page
    @returns: int page
    """
    return divmod(offset, limit)[0] + 1

def es_host_name(conn):
    """Extracts host:port from Elasticsearch conn object.
    
    >>> es_host_name(Elasticsearch(settings.DOCSTORE_HOSTS))
    "<Elasticsearch([{'host': '192.168.56.1', 'port': '9200'}])>"
    
    @param conn: elasticsearch.Elasticsearch with hosts/port
    @returns: str e.g. "192.168.56.1:9200"
    """
    start = conn.__repr__().index('[') + 1
    end = conn.__repr__().index(']')
    text = conn.__repr__()[start:end].replace("'", '"')
    hostdata = json.loads(text)
    return ':'.join([hostdata['host'], hostdata['port']])

def es_search():
    return Search(using=DOCSTORE.es)


class SearchResults(object):
    """Nicely packaged search results for use in API and UI.
    
    >>> from rg import search
    >>> q = {"fulltext":"minidoka"}
    >>> sr = search.run_search(request_data=q, request=None)
    """

    def __init__(self, params={}, query={}, count=0, results=None, objects=[], limit=DEFAULT_LIMIT, offset=0):
        self.params = deepcopy(params)
        self.query = query
        self.aggregations = None
        self.objects = []
        self.total = 0
        try:
            self.limit = int(limit)
        except:
            self.limit = settings.ELASTICSEARCH_MAX_SIZE
        try:
            self.offset = int(offset)
        except:
            self.offset = 0
        self.start = 0
        self.stop = 0
        self.prev_offset = 0
        self.next_offset = 0
        self.prev_api = u''
        self.next_api = u''
        self.page_size = 0
        self.this_page = 0
        self.prev_page = 0
        self.next_page = 0
        self.prev_html = u''
        self.next_html = u''
        self.errors = []
        
        if results:
            # objects
            self.objects = [hit for hit in results]
            if results.hits.total:
                self.total = results.hits.total.value

            # aggregations
            self.aggregations = {}
            if hasattr(results, 'aggregations'):
                for field in results.aggregations.to_dict().keys():

                    # NOTE: Elasticsearch can only run fulltext queries on text
                    # fields.  Missing aggregations data here may be caused
                    # by non-text fields in SEARCH_INCLUDE_FIELDS.
                    # Elasticsearch will not throw an error. Aggregations will
                    # just not have the data that should be there.
                    # See https://github.com/denshoproject/ddr-public/issues/161

                    # simple aggregations
                    aggs = results.aggregations[field]
                    self.aggregations[field] = aggs.buckets

        elif objects:
            # objects
            self.objects = objects
            self.total = len(objects)

        else:
            self.total = count

        # elasticsearch
        self.prev_offset = self.offset - self.limit
        self.next_offset = self.offset + self.limit
        if self.prev_offset < 0:
            self.prev_offset = None
        if self.next_offset >= self.total:
            self.next_offset = None

        # django
        self.page_size = self.limit
        self.this_page = django_page(self.limit, self.offset)
        self.prev_page = u''
        self.next_page = u''
        # django pagination
        self.page_start = (self.this_page - 1) * self.page_size
        self.page_next = self.this_page * self.page_size
        self.pad_before = range(0, self.page_start)
        self.pad_after = range(self.page_next, self.total)
    
    def __repr__(self):
        try:
            q = self.params.dict()
        except:
            q = dict(self.params)
        if self.total:
            return u"<SearchResults [%s-%s/%s] %s>" % (
                self.offset, self.offset + self.limit, self.total, q
            )
        return u"<SearchResults [%s] %s>" % (self.total, q)

    def _make_prevnext_url(self, query, request):
        if request:
            return urlunsplit([
                request.META['wsgi.url_scheme'],
                request.META.get('HTTP_HOST', 'testserver'),
                request.META['PATH_INFO'],
                query,
                None,
            ])
        return '?%s' % query
    
    def to_dict(self, request, format_functions):
        """Express search results in API and Redis-friendly structure
        
        @param request: HttpRequest or RestRequest
        @param format_functions: dict
        returns: dict
        """
        if isinstance(request, HttpRequest):
            params = request.GET.copy()
        elif isinstance(request, RestRequest):
            params = request.query_params.dict()
        elif hasattr(self, 'params') and self.params:
            params = deepcopy(self.params)
        return self._dict(params, {}, format_functions, request)
    
    def ordered_dict(self, request, format_functions, pad=False):
        """Express search results in API and Redis-friendly structure
        
        @param request: HttpRequest or RestRequest
        @param format_functions: dict
        returns: OrderedDict
        """
        if isinstance(request, HttpRequest):
            params = request.GET.copy()
        elif isinstance(request, RestRequest):
            params = request.query_params.dict()
        elif hasattr(self, 'params') and self.params:
            params = deepcopy(self.params)
        return self._dict(params, OrderedDict(), format_functions, request, pad=pad)
    
    def _dict(self, params, data, format_functions, request, pad=False):
        """
        @param params: dict
        @param data: dict
        @param format_functions: dict
        @param pad: bool
        """
        data['total'] = self.total
        data['limit'] = self.limit
        data['offset'] = self.offset
        data['prev_offset'] = self.prev_offset
        data['next_offset'] = self.next_offset
        data['page_size'] = self.page_size
        data['this_page'] = self.this_page
        data['num_this_page'] = len(self.objects)
        if params.get('page'): params.pop('page')
        if params.get('limit'): params.pop('limit')
        if params.get('offset'): params.pop('offset')
        qs = [key + '=' + val for key,val in params.items() if isinstance(val,str)]
        query_string = '&'.join(qs)
        data['prev_api'] = ''
        data['next_api'] = ''
        data['objects'] = []
        data['query'] = self.query
        data['aggregations'] = self.aggregations
        
        # pad before
        if pad:
            data['objects'] += [{'n':n} for n in range(0, self.page_start)]
        # page
        for n,o in enumerate(self.objects):
            format_function = format_functions[o.meta.index]
            odict = o.to_dict()
            odict.pop('index')
            if not odict:
                continue
            highlights = None
            if hasattr(o.meta, 'highlight'):
                highlights = getattr(o.meta, 'highlight')
            data['objects'].append(format_function(
                document=odict,
                request=request,
                highlights=highlights,
                listitem=True,
            ))
        # pad after
        if pad:
            data['objects'] += [{'n':n} for n in range(self.page_next, self.total)]
        
        # API prev/next
        if self.prev_offset != None:
            data['prev_api'] = self._make_prevnext_url(
                u'%s&limit=%s&offset=%s' % (
                    query_string, self.limit, self.prev_offset
                ),
                request
            )
        if self.next_offset != None:
            data['next_api'] = self._make_prevnext_url(
                u'%s&limit=%s&offset=%s' % (
                    query_string, self.limit, self.next_offset
                ),
                request
            )
        
        return data


class Searcher(object):
    """Wrapper around elasticsearch_dsl.Search
    
    >>> s = Searcher(index)
    >>> s.prep(request_data)
    'ok'
    >>> r = s.execute()
    'ok'
    >>> d = r.to_dict(request)
    """
    params = {}
    
    def __init__(self, conn=DOCSTORE.es, search=None):
        """
        @param conn: elasticsearch.Elasticsearch with hosts/port
        @param index: str Elasticsearch index name
        """
        self.conn = conn
        self.s = search
        fields = []
        params = {}
        q = OrderedDict()
        query = {}
        sort_cleaned = None
    
    def __repr__(self):
        return u"<Searcher '%s', %s>" % (
            es_host_name(self.conn), self.params
        )

    def prepare(
            self,
            params={},
            params_allowlist=models.SEARCH_INCLUDE_FIELDS,
            search_models=SEARCH_MODELS,
            fields=SEARCH_INCLUDE_FIELDS,
            fields_nested=SEARCH_NESTED_FIELDS,
            fields_agg=SEARCH_AGG_FIELDS,
            highlight_fields=[],
    ):
        """Assemble elasticsearch_dsl.Search object
        
        @param params:           dict
        @param params_allowlist: list Accept only these (SEARCH_INCLUDE_FIELDS)
        @param search_models:    list Limit to these ES doctypes (SEARCH_MODELS)
        @param fields:           list Retrieve these fields (SEARCH_INCLUDE_FIELDS)
        @param fields_nested:    list See SEARCH_NESTED_FIELDS
        @param fields_agg:       dict See SEARCH_AGG_FIELDS
        @param highlight_fields: list
        @returns: 
        """

        # gather inputs ------------------------------
        
        # self.params is a copy of the params arg as it was passed
        # to the method.  It is used for informational purposes
        # and is passed to SearchResults.
        # Sanitize while copying.
        if params:
            self.params = {
                key: val
                for key,val in params.items()
            }
        params = deepcopy(self.params)
        
        # scrub fields not in allowlist
        bad_fields = [
            key for key in params.keys()
            if key not in params_allowlist + ['page']
        ]
        for key in bad_fields:
            params.pop(key)
        
        indices = search_models
        if params.get('models'):
            indices = ','.join([DOCSTORE.index_name(model) for model in models])
        
        s = Search(using=self.conn, index=indices)
        
        # only return specified fields
        s = s.source(fields)
        
        # sorting
        if params.get('sort'):
            args = params.pop('sort')
            s = s.sort(*args)
        
        if params.get('match_all'):
            s = s.query('match_all')
        elif params.get('fulltext'):
            fulltext = params.pop('fulltext')
            # MultiMatch chokes on lists
            if isinstance(fulltext, list) and (len(fulltext) == 1):
                fulltext = fulltext[0]
            # fulltext search
            s = s.query(
                QueryString(
                    query=fulltext,
                    fields=fields,
                    analyze_wildcard=False,
                    allow_leading_wildcard=False,
                    default_operator='AND',
                )
            )
        # filters
        for key,val in params.items():
            if key in fields_nested:
                # Instead of nested search on topics.id or facility.id
                # search on denormalized topics_id or facility_id fields.
                fieldname = '%s_id' % key
                s = s.filter('term', **{fieldname: val})
            elif (key in params_allowlist) and val:
                s = s.filter('term', **{key: val})
                # 'term' search is for single choice, not multiple choice fields(?)
        
        # highlighting
        for field in highlight_fields:
            s = s.highlight(field, fragment_size=50)
        
        # aggregations
        for fieldname,field in fields_agg.items():
            # simple aggregations
            s.aggs.bucket(fieldname, 'terms', field=field)
        
        self.s = s
    
    def execute(self, limit, offset):
        """Execute a query and return SearchResults
        
        @param limit: int
        @param offset: int
        @returns: SearchResults
        """
        if not self.s:
            raise Exception('Searcher has no ES Search object.')
        start,stop = start_stop(limit, offset)
        self_s_start_stop = self.s[start:stop]
        response = self.s[start:stop].execute()
        for n,hit in enumerate(response.hits):
            hit.index = '%s %s/%s' % (n, int(offset)+n, response.hits.total)
        return SearchResults(
            params=self.params,
            query=self.s.to_dict(),
            results=response,
            limit=limit,
            offset=offset,
        )

def model_objects(
        request, modelnames, filters={}, sort_fields=[],
        fields=models.SEARCH_INCLUDE_FIELDS, limit=DEFAULT_LIMIT, offset=0,
        just_count=False
):
    """Return all documents in MODEL index (paged)
    
    Returns a paged list with count/prev/next metadata
    
    @param request: Django request object.
    @param modelnames: list
    @param sort_fields: list
    @param fields: list
    @param limit: int
    @param offset: int
    @param just_count: boolean
    @returns: dict
    """
    indices = ','.join([DOCSTORE.index_name(model) for model in modelnames])
    params={
        'match_all': {},
        'sort': sort_fields,
    }
    if filters:
        for key,val in filters.items():
            params[key] = val
    searcher = Searcher()
    searcher.prepare(
        params=params,
        search_models=indices,
        fields=fields,
        fields_nested=[],
        fields_agg={},
    )
    s = searcher.s.to_dict()
    results = searcher.execute(limit, offset)
    return results.ordered_dict(
        request, format_functions=models.FORMATTERS
    )
