from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)
import os
import sys

from elasticsearch.exceptions import NotFoundError
import elasticsearch_dsl as dsl
logging.getLogger("elasticsearch").setLevel(logging.WARNING)

from . import definitions

PREFIX = 'names'
DOCTYPES = [
    f'{PREFIX}person',
    f'{PREFIX}farrecord',
    f'{PREFIX}wrarecord',
]


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
            if data.get(field):
                try:
                    setattr(record, field, data[field])
                except dsl.exceptions.ValidationException:
                    err = ':'.join([field, data[field]])
                    record.errors.append(err)
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


def assemble_fulltext(record, fieldnames):
    """Assembles single fulltext search field from all string fields
    """
    values = []
    for fieldname in fieldnames:
        value = getattr(record, fieldname, '')
        if value:
            if isinstance(value, datetime):
                continue
            elif isinstance(value, str):
                value = value.lower()
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
    'exclusion_order_id', 'timestamp', 'facility',
]

class Person(Record):
    """Person record model
    """
    nr_id                         = dsl.Keyword()
    family_name                   = dsl.Keyword()
    given_name                    = dsl.Keyword()
    given_name_alt                = dsl.Text()
    other_names                   = dsl.Text()
    middle_name                   = dsl.Keyword()
    prefix_name                   = dsl.Keyword()
    suffix_name                   = dsl.Keyword()
    jp_name                       = dsl.Keyword()
    preferred_name                = dsl.Keyword()
    birth_date                    = dsl.Date()
    birth_date_text               = dsl.Keyword()
    birth_place                   = dsl.Keyword()
    death_date                    = dsl.Date()
    death_date_text               = dsl.Keyword()
    wra_family_no                 = dsl.Keyword()
    wra_individual_no             = dsl.Keyword()
    citizenship                   = dsl.Keyword()
    alien_registration_no         = dsl.Keyword()
    gender                        = dsl.Keyword()
    preexclusion_residence_city   = dsl.Keyword()
    preexclusion_residence_state  = dsl.Keyword()
    postexclusion_residence_city  = dsl.Keyword()
    postexclusion_residence_state = dsl.Keyword()
    exclusion_order_title         = dsl.Keyword()
    exclusion_order_id            = dsl.Keyword()
    #timestamp                     = dsl.DateTime()
    #facility = models.ManyToManyField(Facility, through='PersonFacility')
    
    class Index:
        name = f'{PREFIX}person'
    
    def __repr__(self):
        return f'<Person {self.nr_id}>'
    
    @staticmethod
    def from_dict(nr_id, data):
        """
        @param fieldnames: list
        @param nr_id: str
        @param data: dict
        @returns: Person
        """
        record = Record.from_dict(
            Person, FIELDS_PERSON, nr_id, data
        )
        assemble_fulltext(record, FIELDS_PERSON)
        return record
    
    @staticmethod
    def from_hit(hit):
        """Build Person object from Elasticsearch hit
        @param hit
        @returns: Person
        """
        return Record.from_hit(Person, hit)
     
    @staticmethod
    def field_values(field, es=None, index=None):
        """Returns unique values and counts for specified field.
        """
        return Record.field_values(Person, field, es, index)


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

class FarRecord(Record):
    """FarRecord model
    """
    far_record_id           = dsl.Keyword()
    facility                = dsl.Keyword()
    original_order          = dsl.Keyword()
    family_number           = dsl.Keyword()
    far_line_id             = dsl.Keyword()
    last_name               = dsl.Keyword()
    first_name              = dsl.Keyword()
    other_names             = dsl.Keyword()
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
    original_notes          = dsl.Keyword()
    person                  = dsl.Keyword()
    #timestamp               = dsl.DateTime()
    
    class Index:
        name = f'{PREFIX}farrecord'
    
    def __repr__(self):
        return f'<FarRecord {self.far_record_id}>'
    
    @staticmethod
    def from_dict(far_record_id, data):
        """
        @param far_record_id: str
        @param data: dict
        @returns: FarRecord
        """
        record = Record.from_dict(
            FarRecord, FIELDS_FARRECORD, far_record_id, data
        )
        assemble_fulltext(record, FIELDS_FARRECORD)
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
    'martitalstatus', 'ethnicity', 'birthplace', 'citizenshipstatus',
    'highestgrade', 'language', 'religion', 'occupqual1', 'occupqual2',
    'occupqual3', 'occupotn1', 'occupotn2', 'wra_filenumber', 'person',
    'timestamp',
]

class WraRecord(Record):
    """WraRecord model
    """
    wra_record_id     = dsl.Integer()
    facility          = dsl.Keyword()
    lastname          = dsl.Keyword()
    firstname         = dsl.Keyword()
    middleinitial     = dsl.Keyword()
    birthyear         = dsl.Keyword()
    gender            = dsl.Keyword()
    originalstate     = dsl.Keyword()
    familyno          = dsl.Keyword()
    individualno      = dsl.Keyword()
    notes             = dsl.Keyword()
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
    martitalstatus    = dsl.Keyword()
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
    person            = dsl.Keyword()
    #timestamp         = dsl.DateTime()
    
    class Index:
        name = f'{PREFIX}wrarecord'
    
    def __repr__(self):
        return f'<WraRecord {self.wra_record_id}>'
    
    @staticmethod
    def from_dict(wra_record_id, data):
        """
        @param fieldnames: list
        @param wra_record_id: str
        @param data: dict
        @returns: WraRecord
        """
        record = Record.from_dict(
            WraRecord, FIELDS_WRARECORD, wra_record_id, data
        )
        assemble_fulltext(record, FIELDS_WRARECORD)
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


ELASTICSEARCH_CLASSES_BY_MODEL = {
    'person': Person,
    'farrecord': FarRecord, 'far': FarRecord,
    'wrarecord': WraRecord, 'wra': WraRecord,
}

FIELDS_BY_MODEL = {
    'person': FIELDS_PERSON,
    'farrecord': FIELDS_FARRECORD, 'far': FIELDS_FARRECORD,
    'wrarecord': FIELDS_WRARECORD, 'wra': FIELDS_WRARECORD,
}
