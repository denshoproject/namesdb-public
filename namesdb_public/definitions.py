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

FIELD_DEFINITIONS = OrderedDict()
FIELD_DEFINITIONS['m_dataset'] = {
    'label': "Data source",
    'description': "Parent dataset of the record",
    'type': 'string',
    'required': True,
    'display': True,
    'sample': 'far-ancestry',
    'notes': 'far-ancestry|far-poston|far-minidoka|far-manzanar|wra',
    'choices': OrderedDict([
        ('far-ancestry', 'FAR Ancestry'),
        ('far-manzanar', 'FAR Manzanar'),
        ('far-minidoka', 'FAR Minidoka'),
        ('far-poston', 'FAR Poston'),
        ('wra-master', 'WRA Form 26'),
    ]),
}
FIELD_DEFINITIONS['m_pseudoid'] = {
    'label': "Names ID",
    'description': "Names Registry identifier",
    'type': 'string',
    'required': True,
    'display': True,
    'sample': '2-poston_akiyama_1888_kiyomi',
    'notes': "Derived from m_camp, m_lastname, m_birthyear, m_firstname",
}
FIELD_DEFINITIONS['m_camp'] = {
    'label': 'Camp',
    'description': "Primary concentration camp. Uses Densho shared controlled vocabulary.",
    'type': 'string',
    'required': True,
    'display': True,
    'sample': '2-poston',
    'choices': OrderedDict([
        ('1-topaz', 'Topaz'),
        ('2-poston', 'Poston'),
        ('3-gilariver', 'Gila River'),
        ('4-amache', 'Amache'),
        ('5-heartmountain', 'Heart Mountain'),
        ('6-jerome', 'Jerome'),
        ('7-manzanar', 'Manzanar'),
        ('8-minidoka', 'Minidoka'),
        ('9-rohwer', 'Rohwer'),
        ('10-tulelake', 'Tule Lake'),
    ]),
    'notes': '',
}
FIELD_DEFINITIONS['m_lastname'] = {
    'label': 'Last Name',
    'description': 'Last name',
    'type': 'string',
    'required': False,
    'display': True,
    'sample': 'Miura',
    'notes': '',
}
FIELD_DEFINITIONS['m_firstname'] = {
    'label': 'First Name',
    'description': 'First name',
    'type': 'string',
    'required': False,
    'display': True,
    'sample': 'George',
    'notes': '',
}
FIELD_DEFINITIONS['m_birthyear'] = {
    'label': 'Birth Year',
    'description': 'Birth year',
    'type': 'number',
    'required': False,
    'display': True,
    'sample': '1921',
    'notes': '',
}
FIELD_DEFINITIONS['m_gender'] = {
    'label': 'Gender',
    'description': 'Gender',
    'type': 'string',
    'required': True,
    'display': True,
    'sample': 'M',
    'choices': OrderedDict([
        ('F', 'Female'),
        ('M', 'Male'),
    ]),
    'notes': '',
}
FIELD_DEFINITIONS['m_originalstate'] = {
    'label': 'Home State',
    'description': "State of residence at time of removal",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': 'UT',
    'choices': OrderedDict([]),
    'notes': "Use two-digit code for US states. Not included in far-ancestry data",
}
FIELD_DEFINITIONS['m_familyno'] = {
    'label': 'WRA Family No.',
    'description': "WRA-assigned family ID (Form 26 - Item 14)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '34339',
    'notes': "Not included in far-ancestry data",
}
FIELD_DEFINITIONS['m_individualno'] = {
    'label': 'WRA Individual No.',
    'description': "WRA-assigned individual ID (Form 26 - Item 14)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '34339B',
    'notes': "Not included in far-ancestry data",
}
FIELD_DEFINITIONS['m_altfamilyid'] = {
    'label': "Alternate Family ID",
    'description': "Alternate family identifier. Supports Ancestry dataset.",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['m_altindividualid'] = {
    'label': "Alternate Individual ID",
    'description': "Alternate individual identifier. Supports Ancestry dataset.",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['m_ddrreference'] = {
    'label': "DDR Reference",
    'description': "Reference in DDR",
    'type': 'string',
    'required': False,
    'display': False,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['m_notes'] = {
    'label': "Notes",
    'description': 'Notes',
    'type': 'string',
    'required': False,
    'display': False,
    'sample': '',
    'notes': '',
}

FIELD_DEFINITIONS['f_originalcity'] = {
    'label': "Home City",
    'description': "City of residence at time of removal",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['f_othernames'] = {
    'label': "Alternate Names",
    'description': "Alternate and middle names",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['f_maritalstatus'] = {
    'label': "Marital Status",
    'description': "Marital status",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['f_citizenship'] = {
    'label': "Citizenship Status",
    'description': "Citizenship status",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['f_alienregistration'] = {
    'label': "Alien Registration",
    'description': "Alien registration status and number",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['f_entrytype'] = {
    'label': "Entry Type",
    'description': "Type of entry into camp",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['f_entrydate'] = {
    'label': "Entry Date",
    'description': "Date of entry into camp",
    'type': 'date',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['f_departuretype'] = {
    'label': "Departure Type",
    'description': "Type of departure/leave clearance from camp",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['f_departuredate'] = {
    'label': "Departure Date",
    'description': "Date of departure from camp",
    'type': 'date',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['f_destinationstate'] = {
    'label': "Destination State",
    'description': "Post-camp destination state",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['f_destinationcity'] = {
    'label': "Destination City",
    'description': "Post-camp destination city",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}
FIELD_DEFINITIONS['f_campaddress'] = {
    'label': "Camp Address",
    'description': "Address in camp facility. Typically, block-barrack-apartment.",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Not included in Ancestry or Minidoka datasets.",
}
FIELD_DEFINITIONS['f_farlineid'] = {
    'label': "FAR Line No.",
    'description': "Line number of the record in the original FAR ledger",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': '',
}

FIELD_DEFINITIONS['w_assemblycenter'] = {
    'label': "Assembly Center",
    'description': "Assembly Center. If individual went directly or was born in camp, code \"0\" or \"none\" is used. (Form 26 - Item 3)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': 'Original: Assem Center',
}
FIELD_DEFINITIONS['w_originaladdress'] = {
    'label': 'Home Address',
    'description': "Residence at time of removal. Uses US Census location code list. (Form 26 - Item 4)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Prev Address",
}
FIELD_DEFINITIONS['w_birthcountry'] = {
    'label': "Birth Countries of Parents",
    'description': "Country of birth of each parent. Selected from code list. (Form 26 - Item 5)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original:Birth Country",
}
FIELD_DEFINITIONS['w_fatheroccup'] = {
    'label': "Father's US Occupation",
    'description': "Father's primary occupation in the US. Based on US Employment Service Code list. (Form 26 - Item 5a)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Father Occ US",
}
FIELD_DEFINITIONS['w_fatheroccupcat'] = {
    'label': "Father's Occupation Abroad",
    'description': "Father's primary occupation outside the US, if applicable. Based on US Employment Service Code list. (Form 26 - Item 5a)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original:Father Occ Abr",
}
FIELD_DEFINITIONS['w_yearsschooljapan'] = {
    'label': "Years of School Japan",
    'description': "Total number of years of schooling in Japan (Form 26 - Item 7)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Yrs School Jpn",
}
FIELD_DEFINITIONS['w_gradejapan'] = {
    'label': "Schooling in Japan",
    'description': "Description of school years spent in Japan (Form 26 - Item 7)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Grade In Japan",
}
FIELD_DEFINITIONS['w_schooldegree'] = {
    'label': "Degree Achieved",
    'description': "Highest degree achieved in Japan or US (Form 26 - Item 7a)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: School Degree",
}
FIELD_DEFINITIONS['w_yearofusarrival'] = {
    'label': "Year of US Arrival",
    'description': "Year of first arrival in territorial US for foreign born only (Form 26 - Item 8)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Yr US Arrival",
}
FIELD_DEFINITIONS['w_timejapan'] = {
    'label': "Time in Japan",
    'description': "Total length of time in Japan (Form 26 - Item 8)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Time in Japan",
}
FIELD_DEFINITIONS['w_notimesjapan'] = {
    'label': "Number of times in Japan",
    'description': "Number of times in Japan (Form 26 - Item 8)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: No# Times Jpn",
}
FIELD_DEFINITIONS['w_agejapan'] = {
    'label': "Age in Japan",
    'description': "Age at time in Japan (Form 26 - Item 8)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original:Age In Japan",
}
FIELD_DEFINITIONS['w_militaryservice'] = {
    'label': "Military Service/Public Assistance/Physical Defects",
    'description': "Military/Naval service, public assistance and pensions, and physical defects. Form 26 recorded these four questions into a single code field. (Form 26 - Item 9, 10, 11 and 13)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Military, etc#",
}
FIELD_DEFINITIONS['w_maritalstatus'] = {
    'label': "Marital Status",
    'description': "Marital status (Form 26 - 18)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Sex & Marital",
}
FIELD_DEFINITIONS['w_ethnicity'] = {
    'label': "Ethnicity",
    'description': "Ethnicity of individual and spouse (Form 26 - 17)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Race",
}
FIELD_DEFINITIONS['w_birthplace'] = {
    'label': "Birthplace",
    'description': "Place of birth. Originally recorded with a two digit code based on US Census location list. (Form 26 - 21)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Birthplace",
}
FIELD_DEFINITIONS['w_citizenshipstatus'] = {
    'label': "Citizenship and Japanese Language School",
    'description': "Alien registration number, Social Security number and Japanese language school. Form 26 recorded these three questions into a single code field. (Form 26 - 22, 29a and 31)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Alien #, SS#",
}
FIELD_DEFINITIONS['w_highestgrade'] = {
    'label': "Highest Grade",
    'description': "Highest grade of school completed (Form 26 - Item 7a)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Highest Grade",
}
FIELD_DEFINITIONS['w_language'] = {
    'label': "Languages",
    'description': "Language abilities (Form 26 - Item 25)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Language",
}
FIELD_DEFINITIONS['w_religion'] = {
    'label': "Religion",
    'description': "For children under 12, this field was coded with the religion of the parents, unless they did not share the same religion in which case the field was left blank. Codes were selected from a controlled list. (Form 26 - Item 30)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Religion",
}
FIELD_DEFINITIONS['w_occupqual1'] = {
    'label': "Occupation Primary",
    'description': "Primary occupation. Based on US Employment Service Code list. (Form 26 - Item 27)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Occup Qual 1",
}
FIELD_DEFINITIONS['w_occupqual2'] = {
    'label': "Occupation Secondary",
    'description': "Secondary occupation. Based on US Employment Service Code list. (Form 26 - Item 27)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Occup Qual 2",
}
FIELD_DEFINITIONS['w_occupqual3'] = {
    'label': "Occupation Tertiary",
    'description': "Tertiary occupation. Based on US Employment Service Code list. (Form 26 - Item 27)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Occup Qual 3",
}
FIELD_DEFINITIONS['w_occuppotn1'] = {
    'label': "Potential Occupation Primary",
    'description': "Primary potential occupation. Used by WRA to determine occupational aptitude and placement. Based on US Employment Service Code list. (Form 26 - Item 27)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Occup Potn 1",
}
FIELD_DEFINITIONS['w_occuppotn2'] = {
    'label': "Potential Occupation Secondary",
    'description': "Secondary potential occupation. Used by WRA to determine occupational aptitude and placement. Based on US Employment Service Code list. (Form 26 - Item 27)",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: Occup Potn 2",
}
FIELD_DEFINITIONS['w_filenumber'] = {
    'label': "File Number",
    'description': "WRA file number",
    'type': 'string',
    'required': False,
    'display': True,
    'sample': '',
    'notes': "Original: File Number",
}
FIELD_DEFINITIONS_NAMES = [key for key,item in FIELD_DEFINITIONS.items()]
FIELD_DEFINITIONS_NAMES_STRINGS = [
    key for key,item in FIELD_DEFINITIONS.items()
    if item['type'] == 'string'
]
SEARCH_FIELDS = [
    'm_dataset', 'm_pseudoid', 'm_camp', 'm_lastname', 'm_firstname', 'm_gender',
    'm_birthyear', 'm_originalstate', 'm_familyno', 'm_individualno',
    'fulltext',
]
