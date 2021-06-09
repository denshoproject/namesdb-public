from collections import OrderedDict


FIELDS_MASTER = [
    'm_dataset', 'm_pseudoid', 'm_camp', 'm_lastname', 'm_firstname', 'm_birthyear',
    'm_gender', 'm_originalstate', 'm_familyno', 'm_individualno',
    'm_altfamilyid', 'm_altindividualid', 'm_ddrreference', 'm_notes',
]

# order of fields in far-ancestry.csv
FIELDS_ANCESTRY = [
    'm_pseudoid', 'm_camp', 'm_lastname', 'm_firstname', 'm_birthyear', 'm_gender',
    'm_originalstate', 'm_familyno', 'm_individualno',
    'f_othernames', 'f_maritalstatus', 'f_citizenship', 'f_alienregistration',
    'f_entrytype', 'f_entrydate', 'f_departuretype', 'f_departuredate',
    'f_destinationcity', 'f_destinationstate', 'f_campaddress', 'f_farlineid',
]

# order of fields in far-manzanar.csv, far-minidoka.csv, far-poston.csv
FIELDS_CAMPS = [
    'm_dataset', 'm_pseudoid', 'm_camp', 'm_lastname', 'm_firstname', 'm_birthyear',
    'm_gender', 'm_originalstate', 'm_familyno', 'm_individualno',
    'm_altfamilyid', 'm_altindividualid', 'm_ddrreference', 'm_notes',
    'f_othernames', 'f_maritalstatus', 'f_citizenship', 'f_alienregistration',
    'f_entrytype', 'f_entrydate', 'f_originalcity', 'f_departuretype',
    'f_departuredate', 'f_destinationcity', 'f_destinationstate', 'f_campaddress',
    'f_farlineid',
]

FIELDS_WRA = [
    'm_dataset', 'm_pseudoid', 'm_camp', 'm_lastname', 'm_firstname', 'm_birthyear',
    'm_gender', 'm_originalstate', 'm_familyno', 'm_individualno',
    'm_altfamilyid', 'm_altindividualid', 'm_ddrreference', 'm_notes',
    'w_assemblycenter', 'w_originaladdress', 'w_birthcountry', 'w_fatheroccupus',
    'w_fatheroccupabr', 'w_yearsschooljapan', 'w_gradejapan', 'w_schooldegree',
    'w_yearofusarrival', 'w_timeinjapan', 'w_notimesinjapan', 'w_ageinjapan',
    'w_militaryservice', 'w_maritalstatus', 'w_ethnicity', 'w_birthplace',
    'w_citizenshipstatus', 'w_highestgrade', 'w_language', 'w_religion',
    'w_occupqual1', 'w_occupqual2', 'w_occupqual3', 'w_occuppotn1', 'w_occuppotn2',
    'w_filenumber',
]

DATASETS = {
    'far-ancestry': FIELDS_CAMPS,
    'far-manzanar': FIELDS_CAMPS,
    'far-minidoka': FIELDS_CAMPS,
    'far-poston': FIELDS_CAMPS,
    'wra-master': FIELDS_WRA,
}

FIELD_DEFINITIONS = {}
FIELD_DEFINITIONS['person'] = {}
FIELD_DEFINITIONS['person']['nr_id'] = {
    'label': "Person ID",
    'description': "Names Registry Person identifier",
    'type': 'string',
    'required': True,
    'display': True,
    'sample': 'SAMPLE GOES HERE',
    'notes': 'NOTES GO HERE',
}
FIELD_DEFINITIONS['person']['family_name']                   = {'label': 'Last Name',                 'description': 'Preferred family or last name',}
FIELD_DEFINITIONS['person']['given_name']                    = {'label': 'First Name',                'description': 'Preferred given or first name',}
FIELD_DEFINITIONS['person']['given_name_alt']                = {'label': 'Alternative First Names',   'description': 'List of alternative first names',}
FIELD_DEFINITIONS['person']['other_names']                   = {'label': 'Other Names',               'description': 'List of other names',}
FIELD_DEFINITIONS['person']['middle_name']                   = {'label': 'Middle Name',               'description': 'Middle name or initial',}
FIELD_DEFINITIONS['person']['prefix_name']                   = {'label': 'Name Prefix',               'description': 'Professional/titular prefix. E.g., "Dr.", "Rev."',}
FIELD_DEFINITIONS['person']['suffix_name']                   = {'label': 'Name Suffix',               'description': 'Name suffix. E.g., "Jr.", "Esq."',}
FIELD_DEFINITIONS['person']['jp_name']                       = {'label': 'Japanese Name',             'description': 'Name in kana',}
FIELD_DEFINITIONS['person']['preferred_name']                = {'label': 'Preferred Full Name',       'description': 'Preferred form of full name for display',}
FIELD_DEFINITIONS['person']['birth_date']                    = {'label': 'Date of Birth',             'description': 'Full birthdate',}
FIELD_DEFINITIONS['person']['birth_date_text']               = {'label': 'Birthdate Text',            'description': 'Text representation of birthdate, if necessary',}
FIELD_DEFINITIONS['person']['birth_place']                   = {'label': 'Birthplace',                'description': 'Place of birth',}
FIELD_DEFINITIONS['person']['death_date']                    = {'label': 'Date of Death',             'description': 'Date of death',}
FIELD_DEFINITIONS['person']['death_date_text']               = {'label': 'Death Date Text',           'description': 'Text representation of death date, if necessary',}
FIELD_DEFINITIONS['person']['wra_family_no']                 = {'label': 'Family Number',             'description': 'WRA-assigned family number',}
FIELD_DEFINITIONS['person']['wra_individual_no']             = {'label': 'Individual Number',         'description': 'WRA-assigned individual number',}
FIELD_DEFINITIONS['person']['citizenship']                   = {'label': 'Country of Citizenship',    'description': 'Country of citizenship',}
FIELD_DEFINITIONS['person']['alien_registration_no']         = {'label': 'Alien Registration Number', 'description': 'INS-assigned alien registration number',}
FIELD_DEFINITIONS['person']['gender']                        = {'label': 'Gender',                    'description': 'Gender',}
FIELD_DEFINITIONS['person']['preexclusion_residence_city']   = {'label': 'Pre-exclusion City',        'description': 'Last city of residence prior to exclusion',}
FIELD_DEFINITIONS['person']['preexclusion_residence_state']  = {'label': 'Pre-exclusion State',       'description': 'Last state of residence prior to exclusion',}
FIELD_DEFINITIONS['person']['postexclusion_residence_city']  = {'label': 'Post-detention City',       'description': 'City of residence immediately following detention',}
FIELD_DEFINITIONS['person']['postexclusion_residence_state'] = {'label': 'Post-detention State',      'description': 'State of residence immediately following detention',}
FIELD_DEFINITIONS['person']['exclusion_order_title']         = {'label': 'Exclusion Order',           'description': 'Name of U.S. Army exclusion order',}
FIELD_DEFINITIONS['person']['exclusion_order_id']            = {'label': 'Exclusion Order ID',        'description': 'Order ID ',}
# facility
# timestamp

FIELD_DEFINITIONS['farrecord'] = {}
FIELD_DEFINITIONS['farrecord']['far_record_id'] = {
    'label': "FAR Record ID",
    'description': "Derived from FAR ledger id + line id ('original_order'",
    'type': 'string',
    'required': True,
    'display': True,
    'sample': 'SAMPLE GOES HERE',
    'notes': 'NOTES GO HERE',
}
FIELD_DEFINITIONS['farrecord']['facility']                      = {'label': 'Facility',                  'description': 'Identifier of WRA facility'}
FIELD_DEFINITIONS['farrecord']['original_order']                = {'label': 'Original Order',            'description': 'Absolute line number in physical FAR ledger'}
FIELD_DEFINITIONS['farrecord']['family_number']                 = {'label': 'WRA Family Number',         'description': 'WRA-assigned family number'}
FIELD_DEFINITIONS['farrecord']['far_line_id']                   = {'label': 'FAR Line Number',           'description': 'Line number in FAR ledger, recorded in original ledger'}
FIELD_DEFINITIONS['farrecord']['last_name']                     = {'label': 'Last Name',                 'description': 'Last name corrected by transcription team'}
FIELD_DEFINITIONS['farrecord']['first_name']                    = {'label': 'First Name',                'description': 'First name corrected by transcription team'}
FIELD_DEFINITIONS['farrecord']['other_names']                   = {'label': 'Other Names',               'description': 'Alternate first names'}
FIELD_DEFINITIONS['farrecord']['date_of_birth']                 = {'label': 'Birthdate',                 'description': 'Full birth date'}
FIELD_DEFINITIONS['farrecord']['year_of_birth']                 = {'label': 'Year of Birth',             'description': 'Year of birth'}
FIELD_DEFINITIONS['farrecord']['sex']                           = {'label': 'Gender',                    'description': 'Gender identifier'}
FIELD_DEFINITIONS['farrecord']['marital_status']                = {'label': 'Marital Status',            'description': 'Marital status'}
FIELD_DEFINITIONS['farrecord']['citizenship']                   = {'label': 'Citizenship Status',        'description': 'Citizenship status'}
FIELD_DEFINITIONS['farrecord']['alien_registration']            = {'label': 'Alien Registration Number', 'description': 'INS-assigned Alien Registration number'}
FIELD_DEFINITIONS['farrecord']['entry_type_code']               = {'label': 'Entry Type (Coded)',        'description': 'Coded type of original admission and assignment to facility'}
FIELD_DEFINITIONS['farrecord']['entry_type']                    = {'label': 'Entry Type',                'description': 'Normalized type of original entry'}
FIELD_DEFINITIONS['farrecord']['entry_category']                = {'label': 'Entry Category',            'description': 'Category of entry type; assigned by Densho'}
FIELD_DEFINITIONS['farrecord']['entry_facility']                = {'label': 'Entry Facility',            'description': 'Last facility prior to entry'}
FIELD_DEFINITIONS['farrecord']['pre_evacuation_address']        = {'label': 'Pre-exclusion Address',     'description': 'Address at time of removal; city and state'}
FIELD_DEFINITIONS['farrecord']['pre_evacuation_state']          = {'label': 'Pre-exclusion State',       'description': 'Address at time of removal, state-only'}
FIELD_DEFINITIONS['farrecord']['date_of_original_entry']        = {'label': 'Entry Date',                'description': 'Date of arrival at facility'}
FIELD_DEFINITIONS['farrecord']['departure_type_code']           = {'label': 'Departure Type (Coded)',    'description': 'Coded type of leave or reason for departure from facility'}
FIELD_DEFINITIONS['farrecord']['departure_type']                = {'label': 'Departure Type',            'description': 'Normalized type of final departure'}
FIELD_DEFINITIONS['farrecord']['departure_category']            = {'label': 'Departure Category',        'description': 'Category of departure type'}
FIELD_DEFINITIONS['farrecord']['departure_facility']            = {'label': 'Departure Facility',        'description': 'Departure facility, if applicable'}
FIELD_DEFINITIONS['farrecord']['departure_date']                = {'label': 'Departure Date',            'description': 'Date of departure from facility'}
FIELD_DEFINITIONS['farrecord']['departure_state']               = {'label': 'Departure Destination',     'description': 'Destination after departure; state-only'}
FIELD_DEFINITIONS['farrecord']['camp_address_original']         = {'label': 'Camp Address',              'description': 'Physical address in camp in the form, "Block-Barrack-Room"'}
FIELD_DEFINITIONS['farrecord']['camp_address_block']            = {'label': 'Camp Address Block',        'description': 'Block identifier of camp address'}
FIELD_DEFINITIONS['farrecord']['camp_address_barracks']         = {'label': 'Camp Address Barrack',      'description': 'Barrack identifier of camp address'}
FIELD_DEFINITIONS['farrecord']['camp_address_room']             = {'label': 'Camp Address Room',         'description': 'Room identifier of camp address'}
FIELD_DEFINITIONS['farrecord']['reference']                     = {'label': 'Internal FAR Reference',    'description': 'Pointer to another row in the roster; page number in source pdf and the original order inthe consolidated roster for the camp'}
FIELD_DEFINITIONS['farrecord']['original_notes']                = {'label': 'Original Notes', 'description': 'Notes from original statistics section recorder, often a reference to another name in the roster'}
#person
#timestamp

FIELD_DEFINITIONS['wrarecord'] = {}
FIELD_DEFINITIONS['wrarecord']['wra_record_id'] = {
    'label': "WRA Form 26 ID",
    'description': 'Unique identifier; absolute row in original RG210.JAPAN.WRA26 datafile',
    'type': 'string',
    'required': True,
    'display': True,
    'sample': 'SAMPLE GOES HERE',
    'notes': 'NOTES GO HERE',
}
FIELD_DEFINITIONS['wrarecord']['facility']                      = {'label': 'Facility identifier',       'description': 'Facility identifier'}
FIELD_DEFINITIONS['wrarecord']['lastname']                      = {'label': 'Last name, truncated to 10 chars', 'description': 'Last name, truncated to 10 chars'}
FIELD_DEFINITIONS['wrarecord']['firstname']                     = {'label': 'First name, truncated to 8 chars', 'description': 'First name, truncated to 8 chars'}
FIELD_DEFINITIONS['wrarecord']['middleinitial']                 = {'label': 'Middle initial',            'description': 'Middle initial'}
FIELD_DEFINITIONS['wrarecord']['birthyear']                     = {'label': 'Year of birth',             'description': 'Year of birth'}
FIELD_DEFINITIONS['wrarecord']['gender']                        = {'label': 'Gender',                    'description': 'Gender'}
FIELD_DEFINITIONS['wrarecord']['originalstate']                 = {'label': 'State of residence immediately prior to census', 'description': 'State of residence immediately prior to census'}
FIELD_DEFINITIONS['wrarecord']['familyno']                      = {'label': 'WRA-assigned family identifier',                 'description': 'WRA-assigned family identifier'}
FIELD_DEFINITIONS['wrarecord']['individualno']                  = {'label': 'Family identifier + alpha char by birthdate',    'description': 'Family identifier + alpha char by birthdate'}
FIELD_DEFINITIONS['wrarecord']['notes']                         = {'label': 'Notes added by Densho during processing',        'description': 'Notes added by Densho during processing'}
FIELD_DEFINITIONS['wrarecord']['assemblycenter']                = {'label': 'Assembly center prior to camp',                  'description': 'Assembly center prior to camp'}
FIELD_DEFINITIONS['wrarecord']['originaladdress']               = {'label': 'County/city + state of pre-exclusion address (coded)', 'description': 'County/city + state of pre-exclusion address; coded by WRA'}
FIELD_DEFINITIONS['wrarecord']['birthcountry']                  = {'label': 'Birth countries of father and mother (coded)',   'description': 'Birth countries of father and mother; coded by WRA'}
FIELD_DEFINITIONS['wrarecord']['fatheroccupus']                 = {'label': "Father's occupation in the US (coded)",          'description': "Father's occupation in the US; coded by WRA"}
FIELD_DEFINITIONS['wrarecord']['fatheroccupabr']                = {'label': "Father's occupation pre-emigration (coded)",     'description': "Father's occupation pre-emigration; coded by WRA"}
FIELD_DEFINITIONS['wrarecord']['yearsschooljapan']              = {'label': 'Years of school attended in Japan',              'description': 'Years of school attended in Japan'}
FIELD_DEFINITIONS['wrarecord']['gradejapan']                    = {'label': 'Highest grade of schooling attained in Japan (coded)', 'description': 'Highest grade of schooling attained in Japan; coded by WRA'}
FIELD_DEFINITIONS['wrarecord']['schooldegree']                  = {'label': 'Highest educational degree attained (coded)',    'description': 'Highest educational degree attained; coded by WRA'}
FIELD_DEFINITIONS['wrarecord']['yearofusarrival']               = {'label': 'Year of immigration to US, if applicable',       'description': 'Year of immigration to US, if applicable'}
FIELD_DEFINITIONS['wrarecord']['timeinjapan']                   = {'label': 'Time in Japan',                                  'description': 'Description of time in Japan'}
FIELD_DEFINITIONS['wrarecord']['ageinjapan']                    = {'label': 'Oldest age visiting or living in Japan',         'description': 'Age while visiting or living in Japan'}
FIELD_DEFINITIONS['wrarecord']['militaryservice']               = {'label': 'Military service, pensions and disabilities',    'description': 'Military service, public assistance status and major disabilities'}
FIELD_DEFINITIONS['wrarecord']['martitalstatus']                = {'label': 'Marital status',            'description': 'Marital status'}
FIELD_DEFINITIONS['wrarecord']['ethnicity']                     = {'label': 'Ethnicity',                 'description': 'Ethnicity'}
FIELD_DEFINITIONS['wrarecord']['birthplace']                    = {'label': 'Birthplace',                'description': 'Birthplace'}
FIELD_DEFINITIONS['wrarecord']['citizenshipstatus']             = {'label': 'Citizenship status',        'description': 'Citizenship status'}
FIELD_DEFINITIONS['wrarecord']['highestgrade']                  = {'label': 'Highest degree achieved',   'description': 'Highest degree achieved'}
FIELD_DEFINITIONS['wrarecord']['language']                      = {'label': 'Languages spoken',          'description': 'Languages spoken'}
FIELD_DEFINITIONS['wrarecord']['religion']                      = {'label': 'Religion',                  'description': 'Religion'}
FIELD_DEFINITIONS['wrarecord']['occupqual1']                    = {'label': 'Primary qualified occupation',   'description': 'Primary qualified occupation'}
FIELD_DEFINITIONS['wrarecord']['occupqual2']                    = {'label': 'Secondary qualified occupation', 'description': 'Secondary qualified occupation'}
FIELD_DEFINITIONS['wrarecord']['occupqual3']                    = {'label': 'Tertiary qualified occupation',  'description': 'Tertiary qualified occupation'}
FIELD_DEFINITIONS['wrarecord']['occupotn1']                     = {'label': 'Primary potential occupation',   'description': 'Primary potential occupation'}
FIELD_DEFINITIONS['wrarecord']['occupotn2']                     = {'label': 'Secondary potential occupation', 'description': 'Secondary potential occupation'}
FIELD_DEFINITIONS['wrarecord']['wra_filenumber']                = {'label': 'WRA Filenumber',            'description': 'WRA-assigned 6-digit filenumber identifier'}
#person
#timestamp

# set default values until we need to do something else
for model in FIELD_DEFINITIONS.keys():
    for key in FIELD_DEFINITIONS[model].keys():
        item = FIELD_DEFINITIONS[model][key]
        item['type'] = 'string'
        item['required'] = True
        item['display'] = True
        item['sample'] = 'SAMPLE GOES HERE'
        item['notes'] = 'NOTES GO HERE'
         
