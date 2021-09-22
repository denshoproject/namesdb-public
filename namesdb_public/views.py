import json
from urllib.parse import urlparse, urlunparse

from django.conf import settings
from django.core.paginator import Paginator
from django.http.request import HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

import requests

from . import forms
from . import models
from . import api
from . import docstore
from . import search

PAGE_SIZE = 20
CONTEXT = 3
DEFAULT_FILTERS = [
    'm_dataset',
    'm_camp',
    'm_originalstate',
]
NON_FILTER_FIELDS = [
    'query'
]


def index(request, template_name='namesdb_public/index.html'):
    return render(request, template_name, {
    })

def persons(request, template_name='namesdb_public/persons.html'):
    return search_ui(request, 'person')

def farrecords(request, template_name='namesdb_public/farrecords.html'):
    return search_ui(request, 'farrecord')

def wrarecords(request, template_name='namesdb_public/wrarecords.html'):
    return search_ui(request, 'wrarecord')

def person(request, naan, noid, template_name='namesdb_public/person.html'):
    object_id = '/'.join([naan, noid])
    url = _mkurl(
        request, reverse('namesdb-api-person', args=[naan, noid])
    )
    r = requests.get(url)
    if not r.status_code == 200:
        raise Http404
    return render(request, template_name, {
        'record': r.json(),
    })

def farrecord(request, object_id, template_name='namesdb_public/farrecord.html'):
    url = _mkurl(
        request, reverse('namesdb-api-farrecord', args=[object_id])
    )
    r = requests.get(url)
    if not r.status_code == 200:
        raise Http404
    return render(request, template_name, {
        'record': r.json(),
    })

def wrarecord(request, object_id, template_name='namesdb_public/wrarecord.html'):
    url = _mkurl(
        request, reverse('namesdb-api-wrarecord', args=[object_id])
    )
    r = requests.get(url)
    if not r.status_code == 200:
        raise Http404
    return render(request, template_name, {
        'record': r.json(),
    })

def search_ui(request, model=None):
    if model == 'person':
        search_models = ['namesperson']
        params_allowlist = models.SEARCH_INCLUDE_FIELDS_PERSON
        search_include_fields = models.SEARCH_INCLUDE_FIELDS_PERSON
        agg_fields = models.AGG_FIELDS_PERSON
        highlight_fields = models.HIGHLIGHT_FIELDS_PERSON
    elif model == 'farrecord':
        search_models = ['namesfarrecord']
        params_allowlist = models.SEARCH_INCLUDE_FIELDS_FARRECORD
        search_include_fields = models.SEARCH_INCLUDE_FIELDS_FARRECORD
        agg_fields = models.AGG_FIELDS_FARRECORD
        highlight_fields = models.HIGHLIGHT_FIELDS_FARRECORD
    elif model == 'wrarecord':
        search_models = ['nameswrarecord']
        params_allowlist = models.SEARCH_INCLUDE_FIELDS_WRARECORD
        search_include_fields = models.INCLUDE_FIELDS_WRARECORD
        agg_fields = models.AGG_FIELDS_WRARECORD
        highlight_fields = models.HIGHLIGHT_FIELDS_WRARECORD
    
    api_url = '%s?%s' % (
        _mkurl(request, reverse('names-api-search')),
        request.META['QUERY_STRING']
    )
    context = {
        'model': model,
        'searching': False,
        'filters': True,
        'api_url': api_url,
    }
    
    if request.GET.get('fulltext'):
        context['searching'] = True
        
        searcher = search.Searcher()
        params=request.GET.copy()
        
        searcher.prepare(
            params=params,
            params_allowlist=['fulltext'] + params_allowlist,
            search_models=search_models,
            fields=search_include_fields,
            fields_nested=[],
            fields_agg=agg_fields,
            highlight_fields=highlight_fields,
        )
        limit,offset = _limit_offset(request)
        results = searcher.execute(limit, offset)
        paginator = Paginator(
            results.ordered_dict(
                request=request,
                format_functions=models.FORMATTERS,
                pad=True,
            )['objects'],
            results.page_size,
        )
        page = paginator.page(results.this_page)
        
        form = forms.SearchForm(
            data=request.GET.copy(),
            search_results=results,
        )
        
        context['results'] = results
        context['paginator'] = paginator
        context['page'] = page
        context['form'] = form

    else:
        context['form'] = forms.SearchForm()

    return render(request, 'namesdb_public/search.html', context)

def _mkurl(request, path, query=None):
    return urlunparse((
        request.META['wsgi.url_scheme'],
        request.META.get('HTTP_HOST'),
        path, None, query, None
    ))

def _limit_offset(request):
    if request.GET.get('offset'):
        # limit and offset args take precedence over page
        limit = request.GET.get(
            'limit', int(request.GET.get('limit', settings.RESULTS_PER_PAGE))
        )
        offset = request.GET.get('offset', int(request.GET.get('offset', 0)))
    elif request.GET.get('page'):
        limit = settings.RESULTS_PER_PAGE
        thispage = int(request.GET['page'])
        offset = search.es_offset(limit, thispage)
    else:
        limit = settings.RESULTS_PER_PAGE
        offset = 0
    return limit,offset
