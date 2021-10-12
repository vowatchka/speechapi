#!/usr/bin/env python

"""
Do it.
"""

# define metadata
__all__ = ["SPBaseError", "APIRequestError", "APIResponseError"]

# import modules and packages
# import here

class SPBaseError(Exception):
	pass
	
class APIRequestError(SPBaseError):
	def __init__(self, *args, status=None, status_text=None, api_reason=None, api_reason_desc=None, **kwargs):
		super().__init__(*args, **kwargs)
		self.status          = status
		self.status_text     = status_text
		self.api_reason      = api_reason
		self.api_reason_desc = api_reason_desc
		
class APIResponseError(SPBaseError):
	def __init__(self, *args, key=None, **kwargs):
		super().__init__(*args, **kwargs)
		self.key = key
		
