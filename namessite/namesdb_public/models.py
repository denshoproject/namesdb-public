from collections import OrderedDict
from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)
import os
import sys

logging.getLogger("elasticsearch").setLevel(logging.WARNING)

from django.conf import settings
from rest_framework.exceptions import NotFound
from rest_framework.reverse import reverse

from elastictools import docstore
from elastictools.docstore import elasticsearch_dsl as dsl

from . import definitions

INDEX_PREFIX = 'names'

# see if cluster is available, quit with nice message if not
docstore.Docstore(INDEX_PREFIX, settings.DOCSTORE_HOST, settings).start_test()

MAX_SIZE = 1000

MODELS = [
    'person',
    'farrecord',
    'wrarecord',
]
SEARCH_MODELS = MODELS
DOCTYPES = [f'{INDEX_PREFIX}{model}' for model in MODELS]
MODELS_DOCTYPES = {model: f'{INDEX_PREFIX}{model}' for model in MODELS}


def _hitvalue(hit, field):
    """Extract list-wrapped values from their lists.
    
    For some reason, Search hit objects wrap values in lists.
    returns the value inside the list.
    
    @param hit: Elasticsearch search hit object
    @param field: str field name
    @return: value
    """
    if hit.get(field) \
       and isinstance(hit[field], list):
        value = hit[field][0]
    elif hit.get(field):
        value = hit[field]
    return None


class Record(dsl.Document):
    """Base record type
    """
    fulltext = dsl.Text()  # see Record.assemble_fulltext()
    
    #class Index:
    #    name = ???
    # We could define Index here but we don't because we want to be consistent
    # with ddr-local and ddr-public.
    
    @staticmethod
    def from_dict(class_, fieldnames, record_id, data):
        """
        @param class_: Person, FarRecord, WraRecord
        @param fieldnames: list
        @param record_id: str
        @param data: dict
        @returns: Record
        """
        #print(f'  from_dict({class_}, {fieldnames}, {record_id}, data)')
        # Elasticsearch 7 chokes on empty ('') dates so remove from rowd
        empty_dates = [
            fieldname for fieldname,val in data.items()
            if ('date' in fieldname) and (val == '')
        ]
        for fieldname in empty_dates:
            data.pop(fieldname)
        # set values
        record = class_(meta={
            'id': record_id
        })
        record.errors = []
        for field in fieldnames:
            #print(f'    field {field}')
            if data.get(field):
                try:
                    #print(f'      data[field] {data[field]}')
                    setattr(record, field, data[field])
                    #print('       ok')
                except dsl.exceptions.ValidationException:
                    err = ':'.join([field, data[field]])
                    record.errors.append(err)
                    #print(f'       err {err}')
        return record
    
    @staticmethod
    def from_hit(class_, hit):
        """Build Record object from Elasticsearch hit
        @param class_: Person, FarRecord, WraRecord
        @param hit
        @returns: Record
        """
        hit_d = hit.__dict__['_d_']
        if record_id:
            record = class_(meta={
                'id': record_id
            })
            for field in definitions.FIELDS_MASTER:
                setattr(record, field, _hitvalue(hit_d, field))
            record.assemble_fulltext()
            return record
        record.assemble_fulltext(fieldnames)
        return None
     
    @staticmethod
    def field_values(class_, field, es=None, index=None):
        """Returns unique values and counts for specified field.
        """
        if es and index:
            s = dsl.Search(using=es, index=index)
        else:
            s = dsl.Search()
        s = s.doc_type(class_)
        s.aggs.bucket('bucket', 'terms', field=field, size=1000)
        response = s.execute()
        return [
            (x['key'], x['doc_count'])
            for x in response.aggregations['bucket']['buckets']
        ]

    @staticmethod
    def fields_enriched(record, label=False, description=False, list_fields=[]):
        """Returns dict for each field with value and label etc for display
        
        # list fields and values in order
        >>> for field in record.details.values:
        >>>     print(field.label, field.value)
        
        # access individual values
        >>> record.details.m_dataset.label
        >>> record.details.m_dataset.value
        
        @param record: dict (not an elasticsearch_dsl..Hit)
        @param label: boolean Get pretty label for fields.
        @param description: boolean Get pretty description for fields. boolean
        @param list_fields: list If non-blank get pretty values for these fields.
        @returns: dict
        """
        details = []
        model = record.__class__.Index.model
        fieldnames = FIELDS_BY_MODEL[model]
        for n,fieldname in enumerate(fieldnames):
            try:
                value = getattr(record, fieldname)
            except AttributeError:
                continue
            field_def = definitions.FIELD_DEFINITIONS[model].get(fieldname, {})
            display = field_def.get('display', None)
            if value and display:
                # display datetimes as dates
                if isinstance(value, datetime):
                    value = value.date()
                data = {
                    'field': fieldname,
                    'label': fieldname,
                    'description': '',
                    'value_raw': value,
                    'value': value,
                }
                if (not list_fields) or (fieldname in list_fields):
                    # get pretty value from FIELD_DEFINITIONS
                    choices = field_def.get('choices', {})
                    if choices and choices.get(value, None):
                        data['value'] = choices[value]
                if label:
                    data['label'] = field_def.get('label', fieldname)
                if description:
                    data['description'] = field_def.get('description', '')
                item = (fieldname, data)
                details.append(item)
        return OrderedDict(details)


def assemble_fulltext(record, fieldnames):
    """Assembles single fulltext search field from all string fields
    """
    values = []
    for fieldname in fieldnames:
        value = getattr(record, fieldname, '')
        if value:
            if isinstance(value, str):
                value = value.lower()
            else:
                continue
            values.append(value)
    return ' '.join(values)


FIELDS_PERSON = [
    'nr_id', 'family_name', 'given_name', 'given_name_alt', 'other_names',
    'middle_name', 'prefix_name', 'suffix_name', 'jp_name', 'preferred_name',
    'birth_date', 'birth_date_text', 'birth_place', 'death_date',
    'death_date_text', 'wra_family_no', 'wra_individual_no', 'citizenship',
    'alien_registration_no', 'gender', 'preexclusion_residence_city',
    'preexclusion_residence_state', 'postexclusion_residence_city',
    'postexclusion_residence_state', 'exclusion_order_title',
    'exclusion_order_id', 'timestamp',
    'facilities', 'far_records', 'wra_records',
]

SEARCH_EXCLUDE_FIELDS_PERSON = [
    'birth_date', 'death_date', 'timestamp',  # can't search fulltext on dates
    'facilities', 'far_records', 'wra_records', 'family',  # relation pointers
]

INCLUDE_FIELDS_PERSON = [
    'nr_id', 'family_name', 'given_name', 'given_name_alt', 'other_names',
    'middle_name', 'prefix_name', 'suffix_name', 'jp_name', 'preferred_name',
    'wra_family_no', 'wra_individual_no', 'alien_registration_no',
    'preexclusion_residence_city', 'postexclusion_residence_city',
    'exclusion_order_title',
]

EXCLUDE_FIELDS_PERSON = []

AGG_FIELDS_PERSON = {
    'citizenship': 'citizenship',
    'gender': 'gender',
    'preexclusion_residence_city': 'preexclusion_residence_city',
    'preexclusion_residence_state': 'preexclusion_residence_state',
    'postexclusion_residence_city': 'postexclusion_residence_city',
    'postexclusion_residence_state': 'postexclusion_residence_state',
    'exclusion_order_title': 'exclusion_order_title',
    'exclusion_order_id': 'exclusion_order_id',
}

HIGHLIGHT_FIELDS_PERSON = [
    'birth_date_text', 'birth_place',
    'family_name', 'given_name', 'other_names', 'preferred_name',
    'preexclusion_residence_city', 'postexclusion_residence_city',
]

class ListFacility(dsl.InnerDoc):
    person_nr_id = dsl.Keyword()
    facility_id = dsl.Keyword()
    entry_date = dsl.Date()
    exit_date = dsl.Date()

class ListFarRecord(dsl.InnerDoc):
    far_record_id = dsl.Keyword()
    last_name = dsl.Text()
    first_name = dsl.Text()

class ListWraRecord(dsl.InnerDoc):
    wra_record_id = dsl.Keyword()
    lastname = dsl.Text()
    firstname = dsl.Text()
    middleinitial = dsl.Text()

class ListFamily(dsl.InnerDoc):
    wra_family_no = dsl.Keyword()
    nr_id = dsl.Keyword()
    preferred_name = dsl.Text()

class Person(Record):
    """Person record model
    TODO review field types for aggs,filtering
    """
    nr_id                         = dsl.Keyword()
    family_name                   = dsl.Text()
    given_name                    = dsl.Text()
    given_name_alt                = dsl.Text()
    other_names                   = dsl.Text()
    middle_name                   = dsl.Text()
    prefix_name                   = dsl.Text()
    suffix_name                   = dsl.Text()
    jp_name                       = dsl.Text()
    preferred_name                = dsl.Text()
    birth_date                    = dsl.Date()
    birth_date_text               = dsl.Text()
    birth_place                   = dsl.Text()
    death_date                    = dsl.Date()
    death_date_text               = dsl.Text()
    wra_family_no                 = dsl.Text()
    wra_individual_no             = dsl.Text()
    citizenship                   = dsl.Keyword()
    alien_registration_no         = dsl.Text()
    gender                        = dsl.Keyword()
    preexclusion_residence_city   = dsl.Keyword()
    preexclusion_residence_state  = dsl.Keyword()
    postexclusion_residence_city  = dsl.Keyword()
    postexclusion_residence_state = dsl.Keyword()
    exclusion_order_title         = dsl.Keyword()
    exclusion_order_id            = dsl.Keyword()
    timestamp                     = dsl.Date()
    facilities                    = dsl.Nested(ListFacility)
    far_records                   = dsl.Nested(ListFarRecord)
    wra_records                   = dsl.Nested(ListWraRecord)
    family                        = dsl.Nested(ListFamily)
    
    class Index:
        model = 'person'
        name = f'{INDEX_PREFIX}person'
    
    def __repr__(self):
        return f'<Person {self.nr_id}>'
    
    @staticmethod
    def get(oid, request):
        """Get record for web app"""
        return docstore_object(request, 'person', oid)
    
    @staticmethod
    def from_dict(nr_id, data):
        """
        @param nr_id: str
        @param data: dict
        @returns: Person
        """
        # exclude private fields
        fieldnames = [
            f for f in FIELDS_PERSON if f not in EXCLUDE_FIELDS_PERSON
        ]
        record = Record.from_dict(Person, fieldnames, nr_id, data)
        assemble_fulltext(record, fieldnames)
        record.family = []
        if data.get('family'):
            record.family = [
                {
                    'nr_id':         person['nr_id'],
                    'preferred_name': person['preferred_name'],
                }
                for person in data['family']
            ]
        return record
    
    @staticmethod
    def from_hit(hit):
        """Build Person object from Elasticsearch hit
        @param hit
        @returns: Person
        """
        return Record.from_hit(Person, hit)

    @staticmethod
    def from_id(nr_id):
        return Person.get(nr_id)
     
    @staticmethod
    def field_values(field, es=None, index=None):
        """Returns unique values and counts for specified field.
        """
        return Record.field_values(Person, field, es, index)


FIELDS_PERSONFACILITY = [
    'person_id', 'facility_id', 'entry_date', 'exit_date',
]

class PersonFacility(Record):
    """PersonFacility record model
    """
    person_id                     = dsl.Keyword()
    facility_id                   = dsl.Keyword()
    entry_date                    = dsl.Date()
    exit_date                     = dsl.Date()
    
    class Index:
        model = 'personfacility'
        name = f'{INDEX_PREFIX}personfacility'
    
    def __repr__(self):
        return f'<PersonFacility {self.person_id},{self.facility_id}>'


FIELDS_FARRECORD = [
    'far_record_id', 'facility', 'original_order', 'family_number',
    'far_line_id', 'last_name', 'first_name', 'other_names', 'date_of_birth',
    'year_of_birth', 'sex', 'marital_status', 'citizenship',
    'alien_registration', 'entry_type_code', 'entry_type', 'entry_category',
    'entry_facility', 'pre_evacuation_address', 'pre_evacuation_state',
    'date_of_original_entry', 'departure_type_code', 'departure_type',
    'departure_category', 'departure_facility', 'departure_date',
    'departure_state', 'camp_address_original', 'camp_address_block',
    'camp_address_barracks', 'camp_address_room', 'reference', 'original_notes',
    'person', 'timestamp',
]

SEARCH_EXCLUDE_FIELDS_FARRECORD = [
    'timestamp', # can't fulltext search on dates
    'person',  # relation pointers
]

INCLUDE_FIELDS_FARRECORD = [
    'far_record_id', 'family_number', 'far_line_id', 'last_name', 'first_name',
    'other_names', 'date_of_birth', 'original_notes',
    ]

EXCLUDE_FIELDS_FARRECORD = []

AGG_FIELDS_FARRECORD = {
    'facility': 'facility',
    'sex': 'sex',
    'marital_status': 'marital_status',
    'citizenship': 'citizenship',
    'alien_registration': 'alien_registration',
    'entry_type_code': 'entry_type_code',
    'entry_type': 'entry_type',
    'entry_category': 'entry_category',
    'entry_facility': 'entry_facility',
    'pre_evacuation_state': 'pre_evacuation_state',
    'departure_type_code': 'departure_type_code',
    'departure_type': 'departure_type',
    'departure_category': 'departure_category',
    'departure_facility': 'departure_facility',
    'departure_state': 'departure_state',
    'camp_address_original': 'camp_address_original',
    'camp_address_block': 'camp_address_block',
    'camp_address_barracks': 'camp_address_barracks',
    'camp_address_room': 'camp_address_room',
}

HIGHLIGHT_FIELDS_FARRECORD = [
]

class NestedPerson(dsl.InnerDoc):
    nr_id = dsl.Keyword()
    preferred_name = dsl.Text()

class ListFamily(dsl.InnerDoc):
    family_number = dsl.Keyword()
    far_record_id = dsl.Keyword()
    last_name = dsl.Text()
    first_name = dsl.Text()

class FarRecord(Record):
    """FarRecord model
    TODO review field types for aggs,filtering
    """
    far_record_id           = dsl.Keyword()
    facility                = dsl.Keyword()
    original_order          = dsl.Keyword()
    family_number           = dsl.Keyword()
    far_line_id             = dsl.Keyword()
    last_name               = dsl.Text()
    first_name              = dsl.Text()
    other_names             = dsl.Text()
    date_of_birth           = dsl.Keyword()
    year_of_birth           = dsl.Keyword()
    sex                     = dsl.Keyword()
    marital_status          = dsl.Keyword()
    citizenship             = dsl.Keyword()
    alien_registration      = dsl.Keyword()
    entry_type_code         = dsl.Keyword()
    entry_type              = dsl.Keyword()
    entry_category          = dsl.Keyword()
    entry_facility          = dsl.Keyword()
    pre_evacuation_address  = dsl.Keyword()
    pre_evacuation_state    = dsl.Keyword()
    date_of_original_entry  = dsl.Keyword()
    departure_type_code     = dsl.Keyword()
    departure_type          = dsl.Keyword()
    departure_category      = dsl.Keyword()
    departure_facility      = dsl.Keyword()
    departure_date          = dsl.Keyword()
    departure_state         = dsl.Keyword()
    camp_address_original   = dsl.Keyword()
    camp_address_block      = dsl.Keyword()
    camp_address_barracks   = dsl.Keyword()
    camp_address_room       = dsl.Keyword()
    reference               = dsl.Keyword()
    original_notes          = dsl.Text()
    person                  = dsl.Nested(NestedPerson)
    family                  = dsl.Nested(ListFamily)
    timestamp               = dsl.Date()
    
    class Index:
        model = 'farrecord'
        name = f'{INDEX_PREFIX}farrecord'
    
    def __repr__(self):
        return f'<FarRecord {self.far_record_id}>'
    
    @staticmethod
    def get(oid, request):
        """Get record for web app"""
        return docstore_object(request, 'farrecord', oid)
    
    @staticmethod
    def from_dict(far_record_id, data):
        """
        @param far_record_id: str
        @param data: dict
        @returns: FarRecord
        """
        # exclude private fields
        fieldnames = [
            f for f in FIELDS_FARRECORD if f not in EXCLUDE_FIELDS_FARRECORD
        ]
        record = Record.from_dict(FarRecord, fieldnames, far_record_id, data)
        assemble_fulltext(record, fieldnames)
        record.family = []
        if data.get('family'):
            record.family = [
                {
                    'far_record_id': person['far_record_id'],
                    'last_name': person['last_name'],
                    'first_name': person['first_name'],
                }
                for person in data['family']
            ]
        return record
    
    @staticmethod
    def from_hit(hit):
        """Build FarRecord object from Elasticsearch hit
        @param hit
        @returns: FarRecord
        """
        return Record.from_hit(FarRecord, hit)
     
    @staticmethod
    def field_values(field, es=None, index=None):
        """Returns unique values and counts for specified field.
        """
        return Record.field_values(FarRecord, field, es, index)


FIELDS_WRARECORD = [
    'wra_record_id', 'facility', 'lastname', 'firstname', 'middleinitial',
    'birthyear', 'gender', 'originalstate', 'familyno', 'individualno', 'notes',
    'assemblycenter', 'originaladdress', 'birthcountry', 'fatheroccupus',
    'fatheroccupabr', 'yearsschooljapan', 'gradejapan', 'schooldegree',
    'yearofusarrival', 'timeinjapan', 'ageinjapan', 'militaryservice',
    'maritalstatus', 'ethnicity', 'birthplace', 'citizenshipstatus',
    'highestgrade', 'language', 'religion', 'occupqual1', 'occupqual2',
    'occupqual3', 'occupotn1', 'occupotn2', 'wra_filenumber', 'person',
    'timestamp',
]

SEARCH_EXCLUDE_FIELDS_WRARECORD = [
    'timestamp', # can't fulltext search on dates
    'person',  # relation pointers
]

INCLUDE_FIELDS_WRARECORD = [
    'wra_record_id',
    'lastname', 'firstname', 'middleinitial',
    'familyno', 'individualno',
]

EXCLUDE_FIELDS_WRARECORD = []

AGG_FIELDS_WRARECORD = {
    'facility': 'facility',
    'birthyear': 'birthyear',
    'gender': 'gender',
    'originalstate': 'originalstate',
    'assemblycenter': 'assemblycenter',
    'birthcountry': 'birthcountry',
    'fatheroccupus': 'fatheroccupus',
    'fatheroccupabr': 'fatheroccupabr',
    'yearsschooljapan': 'yearsschooljapan',
    'gradejapan': 'gradejapan',
    'schooldegree': 'schooldegree',
    'yearofusarrival': 'yearofusarrival',
    'timeinjapan': 'timeinjapan',
    'ageinjapan': 'ageinjapan',
    'militaryservice': 'militaryservice',
    'maritalstatus': 'maritalstatus',
    'ethnicity': 'ethnicity',
    'birthplace': 'birthplace',
    'citizenshipstatus': 'citizenshipstatus',
    'highestgrade': 'highestgrade',
    'language': 'language',
    'religion': 'religion',
    'occupqual1': 'occupqual1',
    'occupqual2': 'occupqual2',
    'occupqual3': 'occupqual3',
    'occupotn1': 'occupotn1',
    'occupotn2': 'occupotn2',
}

HIGHLIGHT_FIELDS_WRARECORD = [
]

class ListFamily(dsl.InnerDoc):
    familyno = dsl.Keyword()
    wra_record_id = dsl.Keyword()
    lastname = dsl.Keyword()
    firstname = dsl.Keyword()

class WraRecord(Record):
    """WraRecord model
    TODO review field types for aggs,filtering
    """
    wra_record_id     = dsl.Keyword()
    facility          = dsl.Keyword()
    lastname          = dsl.Text()
    firstname         = dsl.Text()
    middleinitial     = dsl.Text()
    birthyear         = dsl.Keyword()
    gender            = dsl.Keyword()
    originalstate     = dsl.Keyword()
    familyno          = dsl.Keyword()
    individualno      = dsl.Keyword()
    notes             = dsl.Text()
    assemblycenter    = dsl.Keyword()
    originaladdress   = dsl.Keyword()
    birthcountry      = dsl.Keyword()
    fatheroccupus     = dsl.Keyword()
    fatheroccupabr    = dsl.Keyword()
    yearsschooljapan  = dsl.Keyword()
    gradejapan        = dsl.Keyword()
    schooldegree      = dsl.Keyword()
    yearofusarrival   = dsl.Keyword()
    timeinjapan       = dsl.Keyword()
    ageinjapan        = dsl.Keyword()
    militaryservice   = dsl.Keyword()
    maritalstatus     = dsl.Keyword()
    ethnicity         = dsl.Keyword()
    birthplace        = dsl.Keyword()
    citizenshipstatus = dsl.Keyword()
    highestgrade      = dsl.Keyword()
    language          = dsl.Keyword()
    religion          = dsl.Keyword()
    occupqual1        = dsl.Keyword()
    occupqual2        = dsl.Keyword()
    occupqual3        = dsl.Keyword()
    occupotn1         = dsl.Keyword()
    occupotn2         = dsl.Keyword()
    wra_filenumber    = dsl.Keyword()
    person            = dsl.Nested(NestedPerson)
    family            = dsl.Nested(ListFamily)
    timestamp         = dsl.Date()
    
    class Index:
        model = 'wrarecord'
        name = f'{INDEX_PREFIX}wrarecord'
    
    def __repr__(self):
        return f'<WraRecord {self.wra_record_id}>'
    
    @staticmethod
    def get(oid, request):
        """Get record for web app"""
        return docstore_object(request, 'wrarecord', oid)

    @staticmethod
    def from_dict(wra_record_id, data):
        """
        @param wra_record_id: str
        @param data: dict
        @returns: WraRecord
        """
        # exclude private fields
        fieldnames = [
            f for f in FIELDS_WRARECORD if f not in EXCLUDE_FIELDS_WRARECORD
        ]
        record = Record.from_dict(WraRecord, fieldnames, wra_record_id, data)
        assemble_fulltext(record, fieldnames)
        record.family = []
        if data.get('family'):
            record.family = [
                {
                    'wra_record_id': person['wra_record_id'],
                    'lastname': person['lastname'],
                    'firstname': person['firstname'],
                }
                for person in data['family']
            ]
        return record
    
    @staticmethod
    def from_hit(hit):
        """Build WraRecord object from Elasticsearch hit
        @param hit
        @returns: WraRecord
        """
        return Record.from_hit(WraRecord, hit)
     
    @staticmethod
    def field_values(field, es=None, index=None):
        """Returns unique values and counts for specified field.
        """
        return Record.field_values(WraRecord, field, es, index)


DOCTYPES_BY_MODEL = {
    'person':    f'{INDEX_PREFIX}person',
    'farrecord': f'{INDEX_PREFIX}farrecord',
    'wrarecord': f'{INDEX_PREFIX}wrarecord',
}

ELASTICSEARCH_CLASSES_BY_MODEL = {
    'person': Person,
    'farrecord': FarRecord,
    'wrarecord': WraRecord,
}

FIELDS_BY_MODEL = {
    'person': FIELDS_PERSON,
    'farrecord': FIELDS_FARRECORD,
    'wrarecord': FIELDS_WRARECORD,
}

SEARCH_INCLUDE_FIELDS_PERSON    = [x for x in FIELDS_PERSON    if (x not in SEARCH_EXCLUDE_FIELDS_PERSON)]
SEARCH_INCLUDE_FIELDS_FARRECORD = [x for x in FIELDS_FARRECORD if (x not in SEARCH_EXCLUDE_FIELDS_FARRECORD)]
SEARCH_INCLUDE_FIELDS_WRARECORD = [x for x in FIELDS_WRARECORD if (x not in SEARCH_EXCLUDE_FIELDS_WRARECORD)]

SEARCH_INCLUDE_FIELDS = list(set(
      SEARCH_INCLUDE_FIELDS_PERSON
    + SEARCH_INCLUDE_FIELDS_FARRECORD
    + SEARCH_INCLUDE_FIELDS_WRARECORD
))

SEARCH_AGG_FIELDS = {}
for fieldset in [AGG_FIELDS_PERSON, AGG_FIELDS_FARRECORD, AGG_FIELDS_WRARECORD]:
    for key,val in fieldset.items():
        SEARCH_AGG_FIELDS[key] = val

SEARCH_FORM_LABELS = {}

def docstore_object(request, model, oid):
    data = docstore.Docstore(
        INDEX_PREFIX, settings.DOCSTORE_HOST, settings
    ).es.get(
        index=MODELS_DOCTYPES[model],
        id=oid
    )
    return format_object_detail(data, request)

def format_object_detail(document, request, listitem=False):
    """Formats repository objects, adds list URLs,
    """
    if document.get('_source'):
        oid = document['_id']
        model = document['_index']
        document = document['_source']
    else:
        if document.get('wra_record_id'):
            oid = document['wra_record_id']
            model = 'nameswrarecord'
        elif document.get('far_record_id'):
            oid = document['far_record_id']
            model = 'namesfarrecord'
        elif document.get('nr_id'):
            oid = document['nr_id']
            model = 'namesperson'
    if model:
        model = model.replace(INDEX_PREFIX, '')
    # accomodate naan/noids
    if '/' in oid:
        naan,noid = oid.split('/')
    else:
        naan,noid = None,None
    
    d = OrderedDict()
    d['id'] = oid
    d['model'] = model
    if document.get('index'):
        d['index'] = document.pop('index')
    d['links'] = OrderedDict()
    # accomodate ark/noids
    if model == 'person':
        d['links']['html'] = reverse('namespub-person', args=[naan,noid], request=request)
        d['links']['json'] = reverse('namespub-api-person', args=[naan,noid], request=request)
    elif model == 'farrecord':
        d['links']['html'] = reverse('namespub-farrecord', args=[oid], request=request)
        d['links']['json'] = reverse('namespub-api-farrecord', args=[oid], request=request)
    elif model == 'wrarecord':
        d['links']['html'] = reverse('namespub-wrarecord', args=[oid], request=request)
        d['links']['json'] = reverse('namespub-api-wrarecord', args=[oid], request=request)
    d['title'] = ''
    d['description'] = ''
    
    for field in FIELDS_BY_MODEL[model]:
        if document.get(field):
            d[field] = document[field]
    
    if document.get('far_records'):
        for p in document['far_records']:
            p['links'] = {}
            p['links']['html'] = reverse('namespub-farrecord', args=[p['far_record_id']], request=request)
            p['links']['json'] = reverse('namespub-api-farrecord', args=[p['far_record_id']], request=request)
    if document.get('wra_records'):
        for p in document['wra_records']:
            p['links'] = {}
            p['links']['html'] = reverse('namespub-wrarecord', args=[p['wra_record_id']], request=request)
            p['links']['json'] = reverse('namespub-api-wrarecord', args=[p['wra_record_id']], request=request)
    if document.get('person'):
        naan,noid = document['person']['id'].split('/')
        document['person']['links'] = {}
        document['person']['links']['html'] = reverse('namespub-person', args=[naan,noid], request=request)
        document['person']['links']['json'] = reverse('namespub-api-person', args=[naan,noid], request=request)
    
    def add_links(p, idfield, value=None):
        if not value:
            value = idfield
        p['links'] = {}
        if idfield == 'far_record_id' and p.get(idfield):
            p['links']['html'] = reverse('namespub-farrecord', args=[p[idfield]], request=request)
            p['links']['json'] = reverse('namespub-api-farrecord', args=[p[idfield]], request=request)
        elif idfield == 'wra_record_id' and p.get(idfield):
            p['links']['html'] = reverse('namespub-wrarecord', args=[p[idfield]], request=request)
            p['links']['json'] = reverse('namespub-api-wrarecord', args=[p[idfield]], request=request)
        elif idfield == 'nr_id' and p.get(idfield):
            naan,noid = p[idfield].split('/')
            p['links'] = {}
            p['links']['html'] = reverse('namespub-person', args=[naan,noid], request=request)
            p['links']['json'] = reverse('namespub-api-person', args=[naan,noid], request=request)
        return p
    
    if document.get('family'):
        d['family'] = []
        for p in document['family']:
            # exclude self from family list
            if document.get('nr_id') and (p['nr_id'] == document['nr_id']):
                continue
            elif document.get('far_record_id') and (p['far_record_id'] == document['far_record_id']):
                continue
            elif document.get('wra_record_id') and (p['wra_record_id'] == document['wra_record_id']):
                continue
            if p.get('far_record_id'): add_links(p, 'far_record_id')
            if p.get('wra_record_id'): add_links(p, 'wra_record_id')
            if p.get('nr_id'):         add_links(p, 'nr_id')
            d['family'].append(p)
    
    return d

def format_person(document, request, highlights=None, listitem=False):
    oid = document['nr_id']
    naan,noid = oid.split('/')
    model = 'person'
    d = OrderedDict()
    d['id'] = oid
    d['model'] = model
    if document.get('index'):
        d['index'] = document.pop('index')
    d['links'] = OrderedDict()
    d['links']['html'] = reverse('namespub-person', args=[naan,noid], request=request)
    d['links']['json'] = reverse('namespub-api-person', args=[naan,noid], request=request)
    d['title'] = ''
    d['description'] = ''
    for field in FIELDS_BY_MODEL[model]:
        if document.get(field):
            d[field] = document.pop(field)
    d['highlights'] = join_highlight_text(model, highlights)
    return d

def format_farrecord(document, request, highlights=None, listitem=False):
    oid = document['far_record_id']
    model = 'farrecord'
    d = OrderedDict()
    d['id'] = oid
    d['model'] = model
    if document.get('index'):
        d['index'] = document.pop('index')
    d['links'] = OrderedDict()
    d['links']['html'] = reverse('namespub-farrecord', args=[oid], request=request)
    d['links']['json'] = reverse('namespub-api-farrecord', args=[oid], request=request)
    d['title'] = ''
    d['description'] = ''
    for field in FIELDS_BY_MODEL[model]:
        if document.get(field):
            d[field] = document.pop(field)
    d['highlights'] = join_highlight_text(model, highlights)
    return d

def format_wrarecord(document, request, highlights=None, listitem=False):
    oid = document['wra_record_id']
    model = 'wrarecord'
    d = OrderedDict()
    d['id'] = oid
    d['model'] = model
    if document.get('index'):
        d['index'] = document.pop('index')
    d['links'] = OrderedDict()
    d['links']['html'] = reverse('namespub-wrarecord', args=[oid], request=request)
    d['links']['json'] = reverse('namespub-api-wrarecord', args=[oid], request=request)
    d['title'] = ''
    d['description'] = ''
    for field in FIELDS_BY_MODEL[model]:
        if document.get(field):
            d[field] = document.pop(field)
    d['highlights'] = join_highlight_text(model, highlights)
    return d

def join_highlight_text(model, highlights):
    """Concatenate highlight text for various fields into one str
    """
    snippets = []
    for field in FIELDS_BY_MODEL[model]:
        if hasattr(highlights, field):
            vals = ' / '.join(getattr(highlights,field))
            text = f'{field}: "{vals}"'
            snippets.append(text)
    return ', '.join(snippets)

FORMATTERS = {
    'namesperson':    format_person,
    'namesfarrecord': format_farrecord,
    'nameswrarecord': format_wrarecord,
}
