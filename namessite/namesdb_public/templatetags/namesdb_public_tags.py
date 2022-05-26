from django import template
from django.conf import settings


register = template.Library()
	
def record( record ):
    if record.get('model'):
        t = template.loader.get_template(
            f'namesdb_public/list-object-{record["model"]}.html'
        )
    else:
        t = template.loader.get_template('namesdb_public/list-object.html')
    return t.render({'record':record})
	
def names_paginate( paginator ):
    t = template.loader.get_template('namesdb_public/names-paginate.html')
    return t.render({'paginator':paginator})

register.simple_tag(record)
register.simple_tag(names_paginate)
