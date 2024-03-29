import json
from urllib.parse import urlparse, urlunparse

from django.conf import settings
from django.core.paginator import Paginator
from django.http.request import HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from elastictools import docstore
from elastictools import search

from . import forms
from . import models
from . import api

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
        'api_url': reverse('namespub-api-index'),
    })

def persons(request, template_name='namesdb_public/persons.html'):
    return search_ui(request, 'person')

def farrecords(request, template_name='namesdb_public/farrecords.html'):
    return search_ui(request, 'farrecord')

def wrarecords(request, template_name='namesdb_public/wrarecords.html'):
    return search_ui(request, 'wrarecord')

def person(request, naan, noid, template_name='namesdb_public/person.html'):
    nr_id = '/'.join([naan, noid])
    ddrobjects_ui_url,ddrobjects_api_url,ddrobjects_status,ddrobjects = models.Person.ddr_objects(nr_id, request)
    return render(request, template_name, {
        'display_fields_person': models.DISPLAY_FIELDS_PERSON,
        'record': models.Person.get(nr_id, request),
        'locations': models.Person.locations(nr_id, request),
        'ddrobjects_ui_url': ddrobjects_ui_url,
        'ddrobjects_api_url': ddrobjects_api_url,
        'ddrobjects_status': ddrobjects_status,
        'ddrobjects': ddrobjects,
        'api_url': reverse('namespub-api-person', args=[naan,noid]),
    })

def farrecord(request, object_id, template_name='namesdb_public/farrecord.html'):
    return render(request, template_name, {
        'record': models.FarRecord.get(object_id, request),
        'api_url': reverse('namespub-api-farrecord', args=[object_id]),
    })

def wrarecord(request, object_id, template_name='namesdb_public/wrarecord.html'):
    return render(request, template_name, {
        'record': models.WraRecord.get(object_id, request),
        'api_url': reverse('namespub-api-wrarecord', args=[object_id]),
    })

def farpages(request, template_name='namesdb_public/farpages.html'):
    return render(request, template_name, {
        'facilities': models.FarPage.facilities(),
    })

def farpage(request, facility_id, far_page, template_name='namesdb_public/farpage.html'):
    farpage = models.FarPage.get(facility_id, far_page, request)
    farrecords = models.FarPage.farrecords(facility_id, far_page, request)
    return render(request, template_name, {
        'farpage': farpage,
        'farpage_prev': int(far_page) - 1,
        'farpage_next': int(far_page) + 1,
        'farrecords': farrecords,
        'api_url': reverse('namespub-api-farpage', args=[facility_id, far_page]),
    })

def search_ui(request, model=None):
    template = 'namesdb_public/search.html'
    if model == 'person':
        template = 'namesdb_public/person-search.html'
        search_models = ['namesperson']
        params_allowlist = models.SEARCH_INCLUDE_FIELDS_PERSON
        search_include_fields = models.SEARCH_INCLUDE_FIELDS_PERSON
        agg_fields = models.AGG_FIELDS_PERSON
        highlight_fields = models.HIGHLIGHT_FIELDS_PERSON
        api_url = f"{reverse('namespub-api-persons')}?{request.META['QUERY_STRING']}"
    elif model == 'farrecord':
        search_models = ['namesfarrecord']
        params_allowlist = models.SEARCH_INCLUDE_FIELDS_FARRECORD
        search_include_fields = models.SEARCH_INCLUDE_FIELDS_FARRECORD
        agg_fields = models.AGG_FIELDS_FARRECORD
        highlight_fields = models.HIGHLIGHT_FIELDS_FARRECORD
        api_url = f"{reverse('namespub-api-farrecords')}?{request.META['QUERY_STRING']}"
    elif model == 'wrarecord':
        search_models = ['nameswrarecord']
        params_allowlist = models.SEARCH_INCLUDE_FIELDS_WRARECORD
        search_include_fields = models.INCLUDE_FIELDS_WRARECORD
        agg_fields = models.AGG_FIELDS_WRARECORD
        highlight_fields = models.HIGHLIGHT_FIELDS_WRARECORD
        api_url = f"{reverse('namespub-api-wrarecords')}?{request.META['QUERY_STRING']}"

    context = {
        'model': model,
        'searching': False,
        'filters': True,
        'api_url': api_url,
    }
    
    if request.GET.get('fulltext'):
        context['searching'] = True
        
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
        # filter on denormalized values for birth_date and PersonFacility
        # TODO integrate into elastictools.search.prepare or hard-code
        if model == 'person':
            if 'birth_year' in params.keys():
                searcher.s = searcher.s.filter(
                    'term', **{'birth_year': params['birth_year']}
                )
            if 'facility_id' in params.keys():
                searcher.s = searcher.s.filter(
                    'term', **{'facility_id': params['facility_id']}
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

    return render(request, template, context)

def internal_url(request, path, query=None):
    """Internal version of reversed URL
    """
    port = request.META.get('SERVER_PORT')
    return urlunparse((
        'http',
        f'127.0.0.1:{port}',
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
