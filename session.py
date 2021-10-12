#!/usr/bin/env python

"""
Do it.
"""

# import modules and packages
import speechapi
from urllib.parse import urlparse
from speechapi.exceptions import *

class _Session(object):
	"""
	SpeechPro session.
	"""	
	
	def __init__(self, api_json):
		"""
		Initialize SpeechPro session.
		
		:param dict api_json:
		    API JSON response.
			
		:except APIResponseError:
		    If session id is missing.
		"""
		try:
			self._session_id = api_json["session_id"]
		except KeyError:
			raise APIResponseError("session id is missing", key="session_id")
		
		self._is_active = self.session_id != ""
	
	def __str__(self):
		"""
		Return str(self).
		"""
		return '<%s session_id="%s" is_active=%r>' % (self.__class__.__name__, self.session_id, self.is_active)
		
	def __repr__(self):
		"""
		Return repr(self).
		"""
		return "%s(%r)" % (self.__class__.__name__, {"session_id": self.session_id})
		
	async def __aenter__(self):
		"""
		Return self.
		"""
		return self
		
	async def __aexit__(self, ex_type, ex_val, ex_traceback):
		"""
		Close self.
		"""
		sesapi = speechapi.SessionApi()
		await sesapi.session_delete(self)
	
	async def update_status(self):
		sesapi = speechapi.SessionApi()
		self._is_active = await sesapi.session_status(self)
	
	session_id = property()
	is_active = property()
	
	@session_id.getter
	def session_id(self):
		"""
		Return session id.
		
		:return str:
		"""
		return self._session_id
		
	@is_active.getter
	def is_active(self):
		"""
		Return True if session is still active and False in other case.
		
		:return bool:
		"""
		return self._is_active
		
class _WsConfiguration(object):
	"""
	Configuration of web socket connection for synthes.
	"""
	
	def __init__(self, api_json, session):
		"""
		Initialize web socket configuration.
		
		:param dict api_json:
		    API JSON response..
			
		:param _Session sesion:
		    SpeechPro session that was be used for open stream synthes.
			
		:except APIResponseError:
		    If web socket url is missing.
			
		:except APIResponseError:
		    If transaction id is missing or invalid.
		"""
		try:
			self._url = api_json["url"]
		except KeyError:
			raise APIResponseError("web socket url is missing", key="url")
		
		try:
			self._transaction_id = urlparse(self.url).path.split("/")[-1]
		except:
			raise APIResponseError("transaction id is missing or invalid", key="url")
		self._session = session
	
	async def __aenter__(self):
		"""
		Return self.
		"""
		return self
		
	async def __aexit__(self, ex_type, ex_val, ex_traceback):
		"""
		Close self.
		"""
		ttsapi = speechapi.TTSApi()
		await ttsapi.close_synthes_stream(self)
	
	url = property()
	transaction_id = property()
	session = property()
	
	@url.getter
	def url(self):
		"""
		Return web socket url.
		"""
		return self._url
		
	@transaction_id.getter
	def transaction_id(self):
		"""
		Return transaction id.
		"""
		return self._transaction_id
		
	@session.getter
	def session(self):
		"""
		Return session.
		"""
		return self._session
	
