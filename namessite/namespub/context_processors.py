import logging
logger = logging.getLogger(__name__)

from django.conf import settings


def sitewide(request):
    """Variables that need to be inserted into all templates.
    """
    return {
        'hide_header_search': True,
    }
