# This file is part of Nuntiare project.
# The COPYRIGHT file at the top level of this repository
# contains the full copyright notices and license terms.

from importlib import import_module
from ... import CONFIG, LOGGER


def get_data_provider(provider_name):
    '''
    Returns an API 2.0 module for the dataprovider name
    especified in ../../nuntiare.cfg
    '''

    if not CONFIG.has_option('data_providers', provider_name):
        return
    module = CONFIG.get('data_providers', provider_name)
    try:
        provider = import_module(module)
    except Exception as e:
        err = "Error importing '{0}' for Data Provider '{1}': {2}".format(
                module, provider_name, e.args)
        LOGGER.error(err, True)
    return provider
