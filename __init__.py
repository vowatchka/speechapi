#!/usr/bin/env python

"""
Do it.
"""

# define metadata
__version__     = "1.0.0"
__author__      = "Vladimir Saltykov"
__copyright__   = "Copyright 2019, %s" % __author__
__email__       = "vowatchka@mail.ru"
__license__     = "MIT"
__date__        = "2019-12-12"

__all__ = [
	"SessionApi", "TTSApi", "SPBaseError", "APIRequestError", "APIResponseError", 
	"base64_to_bin"
]

# import modules and packages
from .api import SessionApi, TTSApi, base64_to_bin
from .exceptions import SPBaseError, APIRequestError, APIResponseError