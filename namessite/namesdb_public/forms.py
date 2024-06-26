from collections import OrderedDict
from copy import deepcopy
import logging
logger = logging.getLogger(__name__)

from django import forms
from django.conf import settings
from django.core.cache import cache

from . import models

# sorted version of facility and topics tree as choice fields
# {
#     'topics-choices': [
#         [u'topics-1', u'Immigration and citizenship'],
#         ...
#     ],
#     'facility-choices: [...],
# }
#FORMS_CHOICES = docstore.Docstore().es.get(
#    doc_type='forms',
#    id='forms-choices'
#)['_source']
# TODO should not be hard-coded - move to ddr-vocabs?
if settings.DOCSTORE_ENABLED:
    FORMS_CHOICES = {
        'facility_id-choices': [
            (f['facility_id'], f['title']) for f in models.Facility.facilities()
        ],
    }
else:
    FORMS_CHOICES = {'facility_id-choices': []}
FORMS_CHOICES_DEFAULT = {
    'facility': [
        ('', 'All Camps'),
    ],
}

# Pretty labels for multiple choice fields
# (After initial search the choice lists come from search aggs lists
# which only include IDs and doc counts.)
# {
#     'topics': {
#         '1': u'Immigration and citizenship',
#         ...
#     },
#     'facility: {...},
# }
FORMS_CHOICE_LABELS = {}
for key in FORMS_CHOICES.keys():
    field = key.replace('-choices','')
    FORMS_CHOICE_LABELS[field] = {
        key: val
        for key,val in FORMS_CHOICES[key]
    }


class SearchForm(forms.Form):
    #field_order = models.SEARCH_INCLUDE_FIELDS
    search_results = None
    
    def __init__( self, *args, **kwargs ):
        if kwargs.get('search_results'):
            self.search_results = kwargs.pop('search_results')
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields = self.construct_form(self.search_results)

    def construct_form(self, search_results):
        fields = [
            (
                'fulltext',
                forms.CharField(
                    max_length=255,
                    required=False,
                    widget=forms.TextInput(
                        attrs={
                            'id': 'id_query',
                            'class': 'form-control',
                            'placeholder': 'Search...',
                        }
                    ),
                )
            ),
        ]
        
        # fill in options and doc counts from aggregations
        if search_results and search_results.aggregations:
            for fieldname,aggs in search_results.aggregations.items():
                choices = []
                for item in aggs:
                    try:
                        label = FORMS_CHOICE_LABELS[fieldname][item['key']]
                    except:
                        label = item['key']
                    choice = (
                        item['key'],
                        '%s (%s)' % (label, item['doc_count'])
                    )
                    choices.append(choice)
                if choices:
                    fields.append((
                        fieldname,
                        forms.MultipleChoiceField(
                            label=models.SEARCH_FORM_LABELS.get(
                                fieldname, fieldname),
                            choices=choices,
                            required=False,
                        ),
                    ))
        
        # Django Form object takes an OrderedDict rather than list
        fields = OrderedDict(fields)
        return fields
