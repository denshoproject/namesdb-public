from datetime import datetime
import json
import logging
logger = logging.getLogger(__name__)
import os
import sys

from elasticsearch.exceptions import NotFoundError
import elasticsearch_dsl as dsl

from . import definitions

DOC_TYPE = 'names-record'


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
    """FAR/WRA record model
    
    m_pseudoid = m_camp + lastname + birthyear + firstname
    """
    m_pseudoid = dsl.Keyword()
    m_dataset = dsl.Keyword()
    m_camp = dsl.Keyword()
    m_lastname = dsl.Text()
    m_firstname = dsl.Text()
    m_birthyear = dsl.Keyword()
    m_gender = dsl.Keyword()
    m_familyno = dsl.Keyword()
    m_individualno = dsl.Keyword()
    m_originalstate = dsl.Keyword()
    errors = dsl.Text()
    
    f_originalcity = dsl.Keyword()
    f_othernames = dsl.Keyword()
    f_maritalstatus = dsl.Keyword()
    f_citizenship = dsl.Keyword()
    f_alienregistration = dsl.Keyword()
    f_entrytype = dsl.Keyword()
    f_entrydate = dsl.Date()
    f_departuretype = dsl.Keyword()
    f_departuredate = dsl.Date()
    f_destinationstate = dsl.Keyword()
    f_destinationcity = dsl.Keyword()
    f_campaddress = dsl.Keyword()
    f_farlineid = dsl.Keyword()
    
    w_assemblycenter = dsl.Keyword()
    w_originaladdress = dsl.Keyword()
    w_birthcountry = dsl.Keyword()
    w_fatheroccup = dsl.Keyword()
    w_fatheroccupcat = dsl.Keyword()
    w_yearsschooljapan = dsl.Keyword()
    w_gradejapan = dsl.Keyword()
    w_schooldegree = dsl.Keyword()
    w_yearofusarrival = dsl.Keyword()
    w_timeinjapan = dsl.Keyword()
    w_notimesinjapan = dsl.Keyword()
    w_ageinjapan = dsl.Keyword()
    w_militaryservice = dsl.Keyword()
    w_maritalstatus = dsl.Keyword()
    w_ethnicity = dsl.Keyword()
    w_birthplace = dsl.Keyword()
    w_citizenshipstatus = dsl.Keyword()
    w_highestgrade = dsl.Keyword()
    w_language = dsl.Keyword()
    w_religion = dsl.Keyword()
    w_occupqual1 = dsl.Keyword()
    w_occupqual2 = dsl.Keyword()
    w_occupqual3 = dsl.Keyword()
    w_occuppotn1 = dsl.Keyword()
    w_occuppotn2 = dsl.Keyword()
    w_filenumber = dsl.Keyword()
    
    fulltext = dsl.Text()  # see Record.assemble_fulltext()
    
    #class Index:
    #    name = ???
    # We could define Index here but we don't because we want to be consistent
    # with ddr-local and ddr-public.
    
    class Meta:
        doc_type = DOC_TYPE
    
    def __repr__(self):
        return "<Record %s>" % Record.make_id(self.m_dataset, self.m_pseudoid)

    @staticmethod
    def make_id(m_dataset, m_pseudoid):
        return ':'.join([m_dataset, m_pseudoid])
    
    @staticmethod
    def from_dict(fieldnames, m_dataset, m_pseudoid, data):
        """
        @param fieldnames: list
        @param m_dataset: str
        @param m_pseudoid: str
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
        record = Record(meta={
            'id': Record.make_id(m_dataset, m_pseudoid)
        })
        record.errors = []
        for field in fieldnames:
            if data.get(field):
                try:
                    setattr(record, field, data[field])
                except dsl.exceptions.ValidationException:
                    err = ':'.join([field, data[field]])
                    record.errors.append(err)
        record.m_dataset = m_dataset
        record.assemble_fulltext()
        return record
    
    @staticmethod
    def from_hit(hit):
        """Build Record object from Elasticsearch hit
        @param hit
        @returns: Record
        """
        hit_d = hit.__dict__['_d_']
        m_pseudoid = _hitvalue(hit_d, 'm_pseudoid')
        m_dataset = _hitvalue(hit_d, 'm_dataset')
        if m_dataset and m_pseudoid:
            record = Record(meta={
                'id': Record.make_id(m_dataset, m_pseudoid)
            })
            for field in definitions.FIELDS_MASTER:
                setattr(record, field, _hitvalue(hit_d, field))
            record.m_dataset = m_dataset
            record.assemble_fulltext()
            return record
        record.assemble_fulltext()
        return None
     
    @staticmethod
    def field_values(field, es=None, index=None):
        """Returns unique values and counts for specified field.
        """
        if es and index:
            s = dsl.Search(using=es, index=index)
        else:
            s = dsl.Search()
        s = s.doc_type(Record)
        s.aggs.bucket('bucket', 'terms', field=field, size=1000)
        response = s.execute()
        return [
            (x['key'], x['doc_count'])
            for x in response.aggregations['bucket']['buckets']
        ]
        
    def assemble_fulltext(self):
        """Assembles single fulltext search field from all string fields
        """
        fields = [
            self.m_pseudoid,
            self.m_dataset,
            self.m_camp,
            self.m_lastname,
            self.m_firstname,
            self.m_birthyear,
            self.m_gender,
            self.m_familyno,
            self.m_individualno,
            self.m_originalstate,
            self.f_originalcity,
            self.f_othernames,
            self.f_maritalstatus,
            self.f_citizenship,
            self.f_alienregistration,
            self.f_entrytype,
            self.f_entrydate,
            #self.f_entrydate.isoformat(),              # multiple data formats
            #self.f_entrydate.strftime('%d-%m-%Y'),     #
            #self.f_entrydate.strftime('%m-%d-%Y'),     #
            self.f_departuretype,
            self.f_departuredate,
            self.f_destinationstate,
            self.f_destinationcity,
            self.f_campaddress,
            self.f_farlineid,
            self.w_assemblycenter,
            self.w_originaladdress,
            self.w_birthcountry,
            self.w_fatheroccup,
            self.w_fatheroccupcat,
            self.w_yearsschooljapan,
            self.w_gradejapan,
            self.w_schooldegree,
            self.w_yearofusarrival,
            self.w_timeinjapan,
            self.w_notimesinjapan,
            self.w_ageinjapan,
            self.w_militaryservice,
            self.w_maritalstatus,
            self.w_ethnicity,
            self.w_birthplace,
            self.w_citizenshipstatus,
            self.w_highestgrade,
            self.w_language,
            self.w_religion,
            self.w_occupqual1,
            self.w_occupqual2,
            self.w_occupqual3,
            self.w_occuppotn1,
            self.w_occuppotn2,
            self.w_filenumber,
        ]
        self.fulltext = ' '.join([
            f.lower() for f in fields if isinstance(f, str)
        ])
