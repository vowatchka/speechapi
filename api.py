#!/usr/bin/env python

"""
Do it.
"""

# import modules and packages
import json
import asyncio
import aiohttp
import speechapi.session
import speechapi.tts

from binascii import a2b_base64
from threading import Timer
from speechapi.exceptions import *

async def _get_api_response(url, http_method, req=None, headers=None, json_serialize=None, ok_statuses=None):
	"""
	Return response from url.
	
	:param str url:
	    Url.
		
	:param str http_method:
	    HTTP method.
		
	:keyword object req:
	    Request data. If it is None that means no request data.
		
	:keyword dict headers:
	    Request headers. If it is None that means no request headers.
		
	:keyword function json_serialize:
	    Function that serialize json for requests with this data.
	    If it is None that means no serialize.
		
	:keyword list or tuple ok_statuses:
	    List of response statuses that must be detected as ok.
		If it is None then status 200 used as default.
		
	:return str:
	
	:except TypeError:
	    If has some problems with request.
	"""
	async with aiohttp.ClientSession(json_serialize=json_serialize) as requests:
		async with getattr(requests, http_method.lower())(url, json=req, headers=headers) as resp:
			if not isinstance(ok_statuses, (list, tuple)): ok_statuses = [200]
			
			if resp.status in ok_statuses:
				return await resp.text()
			else:
				await _raise_for_api(resp)

async def _raise_for_api(resp):
	"""
	Raise exception for SpeechPro API.
	
	:param aiohttp.ClientResponse resp:
		API response.
	
	:return None:
	
	:except APIRequestError:
		If some problems with request to api.
	"""
	reason = message = ""
	try:
		json_resp = await resp.json()
		reason, message = json_resp["reason"], json_resp["message"]
	except Exception as ex:
		pass
	finally:
		raise APIRequestError(
			"Some problems with request to api. Server status: %d %s. Error description: %s (reason code: %s)" % (resp.status, resp.reason, message, reason), 
			status=resp.status, 
			status_text=resp.reason, 
			api_reason=reason, 
			api_reason_desc=message
		)

def base64_to_bin(data):
	"""
	Most simple wrapper of binascii.a2b_base64.
	
	:param str data:
	    String data in base64.
		
	:return bytes:
	"""
	return a2b_base64(data)
		
class SessionApi(object):
	"""
	SpeechPro session API.
	
	API session prefix: <https://cp.speechpro.com/vksession/rest/>
	"""
	
	_api_prefix = "https://cp.speechpro.com/vksession/rest"
	
	def __new__(cls):
		if not hasattr(cls, "_instance"):
			cls._instance = super(SessionApi, cls).__new__(cls)
		return cls._instance
		
	def __init__(self):
		"""
		Initialize SpeechPro session API.
		"""
		pass
		
	def __str__(self):
		"""
		Return str(self).
		"""
		return '<%s api="%s">' % (self.__class__.__name__, self._api_prefix)
		
	def __repr__(self):
		"""
		Return repr(self).
		"""
		return "%s()" % self.__class__.__name__
		
	async def session_create(self, domain_id, login, password):
		"""
		Create SpeechPro session.
		
		:param int domain_id:
		    Domain ID. Get it in you account.
			
		:param str login:
		    Login. Get it in you account.
			
		:param str password:
		    Password. Get it in you account.
			
		:return _Session:
		
		:except TypeError:
		    If some problems with request to api.
		"""
		resp = await _get_api_response(
			self._api_prefix + "/session", 
			"POST", 
			req={
				"domain_id": domain_id, 
				"username": login, 
				"password": password, 
			}, 
			headers={"content-type": "application/json"}, 
			json_serialize=json.dumps, 
		)
		
		session = speechapi.session._Session(json.loads(resp))
		session._is_active = await self.session_status(session)
		return session
			
	async def session_delete(self, session):
		"""
		Delete SpeechPro session.
		
		:param _Session session:
		    SpeechPro session.
			
		:return None:
		
		:except TypeError:
		    If some problems with request to api.
		"""
		resp = await _get_api_response(
			self._api_prefix + "/session", 
			"DELETE", 
			headers={"x-session-id": session.session_id}, 
			ok_statuses=[200, 204]
		)
		session._is_active = await self.session_status(session)
		
	async def session_status(self, session):
		"""
		Check SpeechPro session status.
		
		:param _Session session:
		    SpeechPro session.
			
		:return bool:
		
		:except APIRequestError:
		    If some problems with request to api.
			
		:except APIResponseError:
		    If key ``is_active`` is missing in api response.
		"""
		resp = await _get_api_response(
			self._api_prefix + "/session", 
			"GET", 
			headers={"x-session-id": session.session_id}, 
		)
		
		json_resp = json.loads(resp)
		if "is_active" in json_resp:
			session._is_active = json_resp["is_active"]
			return session.is_active
		else:
			raise APIResponseError("Data about session active is missing in api response", key="is_active")
			

class TTSApi(object):
	"""
	SpeechPro TTS API.
	
	API TTS prefix: <https://cp.speechpro.com/vktts/rest/>
	"""
	
	_api_prefix = "https://cp.speechpro.com/vktts/rest"
	
	def __new__(cls):
		if not hasattr(cls, "_instance"):
			cls._instance = super(TTSApi, cls).__new__(cls)
		return cls._instance
		
	def __init__(self):
		"""
		Initialize SpeechPro TTS API.
		"""
		pass
		
	def __str__(self):
		"""
		Return str(self).
		"""
		return '<%s api="%s">' % (self.__class__.__name__, self._api_prefix)
		
	def __repr__(self):
		"""
		Return repr(self).
		"""
		return "%s()" % self.__class__.__name__
	
	@staticmethod
	def _getdata(text_response, bin=False):
		"""
		Return data from api response by key ``data``.
		
		:param str text_response:
		    API text response.
			
		:keyword bool bin:
		    If it is True, result of synthes will be returns as binary data.
		    Default is False.
			
		:return string or bytes:	
		
		:except APIResponseError:
		    If key ``data`` is missing in api response.
		"""
		json_resp = json.loads(text_response)
		if "data" in json_resp:
			return json_resp["data"] if not bin else base64_to_bin(json_resp["data"])
		else:
			raise APIResponseError("Data is missing in api response", key="data")
	
	async def get_languages(self, session, skip_invalid_langs=False):
		"""
		Return SpeechPro available languages.
		
		:param _Session session:
		    SpeechPro session.
			
		:keyword bool skip_invalid_langs:
		    If it is True, invalid languages will be skipped.
			
		:return _Languages:
		
		:except TypeError:
		    If some problems with request to api.
		"""
		resp = await _get_api_response(
			self._api_prefix + "/v1/languages", 
			"GET", 
			headers={"x-session-id": session.session_id}
		)
		
		langs = json.loads(resp)
		speechpro_langs = speechapi.tts._LanguagesSet()
		
		for idx,lang in enumerate(langs):
				try:
					speechpro_langs._add(speechapi.tts._Language(lang))
				except Exception as ex:
					if skip_invalid_langs: print(ex)
					else: raise ex
		return speechpro_langs
			
	async def get_voices(self, session, lang, skip_invalid_voices=False):
		"""
		Return SpeechPro available voices for language.
		
		:param _Session session:
		    SpeechPro session.
			
		:param str or _Language lang:
		    SpeechPro language.
			
		:keyword bool skip_invalid_voices:
		    If it is True, invalid voices will be skipped.
			
		:return _Voices:
		
		:except TypeError:
		    If some problems with request to api.
		"""
		resp = await _get_api_response(
			self._api_prefix + ("/v1/languages/%s/voices" % (lang.name if isinstance(lang, speechapi.tts._Language) else str(lang))), 
			"GET", 
			headers={"x-session-id": session.session_id}
		)
		
		voices = json.loads(resp)
		speechpro_voices = speechapi.tts._VoicesSet()
		
		for idx,voice in enumerate(voices):
			try:
				speechpro_voices._add(speechapi.tts._Voice(voice))
			except Exception as ex:
					if skip_invalid_voices: print(ex)
					else: raise ex
		return speechpro_voices
			
	async def package_synthes(self, text, session, voice, bin=False):
		"""
		Package text-to-speech synthes.
		
		:param str text:
		    Synthesized text.
			
		:param _Session session:
		    SpeechPro session.
			
		:param str or _Voice voice:
		    SpeechPro voice.
			
		:keyword bool bin:
		    If it is True, result of synthes will be returns as binary data.
		    Default is False.
			
		:return str or bytes:
		
		:except TypeError:
		    If some problems with request to api.
			
		:except ValueError:
		    If key ``data`` is missing in api response.
		"""
		resp = await _get_api_response(
			self._api_prefix + "/v1/synthesize", 
			"POST", 
			req={
				"voice_name": voice.name if isinstance(voice, speechapi.tts._Voice) else str(voice),
				"text": {
					"mime": "text/plain",
					"value": text, 
				},
				"audio": "audio/wav", 
			}, 
			json_serialize=json.dumps, 
			headers={"content-type": "application/json", "x-session-id": session.session_id}
		)
		return self._getdata(resp, bin=bin)
	
	async def open_synthes_stream(self, session, voice):
		"""
		Open text-to-speech stream.
		
		:param _Session session:
		    SpeechPro session.
			
		:param str or _Voice voice:
		    SpeechPro voice.
			
		:return _WsConfiguration:
			
		:except TypeError:
		    If some problems with request to api.
		"""
		resp = await _get_api_response(
			self._api_prefix + "/v1/synthesize/stream", 
			"POST", 
			req={
				"voice_name": voice.name if isinstance(voice, speechapi.tts._Voice) else str(voice), 
				"text": {
					"mime": "text/plain"
				}, 
				"audio": "audio/wav"
			}, 
			headers={"content-type": "application/json", "x-session-id": session.session_id}, 
			json_serialize=json.dumps
		)
		return speechapi.session._WsConfiguration(json.loads(resp), session)
		
	async def close_synthes_stream(self, wsconfig):
		"""
		Close text-to-speech stream.
			
		:param _WsConfiguration wsconfig:
		    SpeechPro web socket configuration.
			
		:return int or None:
			
		:except TypeError:
		    If some problems with request to api.
		"""
		resp = await _get_api_response(
			self._api_prefix + "/v1/synthesize/stream", 
			"DELETE", 
			headers={"x-session-id": wsconfig.session.session_id, "x-transaction-id": wsconfig.transaction_id}
		)
		json_resp = json.loads(resp)
		if "synthesize_text_size" in json_resp:
			return json_resp["synthesize_text_size"]
		else:
			return None
	
	async def stream_synthes(self, text, wsconfig):
		"""
		Stream text-to-speech synthes.
		
		:param str text:
		    Synthesized text.
			
		:param _WsConfiguration wsconfig:
		    SpeechPro web socket configuration.
			
		:return generator:
		
		:except TypeError:
		    If some problems with request to api.
		"""		
		async with aiohttp.ClientSession() as websockets:
			async with websockets.ws_connect(wsconfig.url) as ws:
				# if len(text):
					# while len(text):
						# await ws.send_str(text[:3000])
						# text = text[3000:]
				# else:
					# await ws.send_str(text)
				
				# loop = asyncio.get_running_loop()
				
				# # There are some problems with ending of read data wrom websocket.
				# # Timer is needed for resolve this problems.
				# handle = loop.call_later(2, lambda : loop.create_task(ws.close()))
				
				# async for msg in ws:
					# # cancel timer if read data successfully
					# handle.cancel()
					# if msg.type == aiohttp.WSMsgType.CLOSING:
						# break
					# else:
						# yield msg.data
						# # set new timer
						# handle = loop.call_later(2, lambda : loop.create_task(ws.close()))
						
				while len(text):
					await ws.send_str(text[:500])
					
					msg = None
					try: msg = await ws.receive(timeout=2)
					except asyncio.exceptions.TimeoutError: pass
					
					while msg != None and msg.type not in [aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING]:
						yield msg.data
						try: msg = await ws.receive(timeout=2)
						except asyncio.exceptions.TimeoutError: break
					
					text = text[500:]
					
				# while len(text):
					# await ws.send_str(text[:500])
					# text = text[500:]
					
				# msg = None
				# try: msg = await ws.receive(timeout=2)
				# except asyncio.exceptions.TimeoutError: pass
				
				# while msg != None and msg.type not in [aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING]:
					# yield msg.data
					# try: msg = await ws.receive(timeout=2)
					# except asyncio.exceptions.TimeoutError: break
				
				# always close web socket connection
				if not ws.closed:
					await ws.close()

