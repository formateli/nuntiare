# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from importlib import import_module
from ... import CONFIG


def get_data_provider(provider_name):
    '''
    Returns an API 2.0 module for the dataprovider name
    especified in ../../nuntiare.cfg
    '''

    if not CONFIG.has_option('data_providers', provider_name):
        return None
    module = CONFIG.get('data_providers', provider_name)
    provider = import_module(module)

    return provider
