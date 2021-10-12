#!/usr/bin/env python

"""
Do it.
"""

# import modules and packages
from collections import OrderedDict
from speechapi.exceptions import *

class _TTSEntity(object):
	"""
	Base class for TTS entity such as language or voice.
	
	All TTS entities must have id and name. 
	"""
	
	def __init__(self, api_json):
		"""
		Initialize TTS entity.
		
		:param dict api_json:
		    API JSON response.
			
		:except APIResponseError:
		    If id is missing.
			
		:except APIResponseError:
		    If name is missing.
		"""
		try:
			self._id = api_json["id"]
		except KeyError:
			raise APIResponseError("id is missing", key="id")
			
		try:
			self._name = api_json["name"]
		except KeyError:
			raise APIResponseError("name is missing", key="name")
		
	id = property()
	name = property()
	
	@id.getter
	def id(self):
		"""
		Return entity id.
		
		:return str:
		"""
		return self._id
		
	@name.getter
	def name(self):
		"""
		Return entity name.
		
		:return str:
		"""
		return self._name

class _Language(_TTSEntity):
	"""
	SpeachPro language.
	"""
	
	def __init__(self, api_json):
		"""
		Initialize SpeachPro language.
		
		:param dict api_json:
		    API JSON response.
		"""
		try:
			super().__init__(api_json)
		except APIResponseError as ex:
			raise APIResponseError("language %s" % ex, key=ex.key)
	
	def __str__(self):
		"""
		Return str(self).
		"""
		return str({"id": self.id, "name": self.name})
		
	def __repr__(self):
		"""
		Return repr(self).
		"""
		return "%s(%r)" % (self.__class__.__name__, {"id": self.id, "name": self.name})
		
	
class _Voice(_TTSEntity):
	"""
	SpeachPro voice.
	"""
	
	def __init__(self, api_json):
		"""
		Initialize SpeachPro voice.
		
		:param dict api_json:
		    API JSON response.
		
		:except APIResponseError:
		    If gender is missing.
		"""
		try:
			super().__init__(api_json)
		except APIResponseError as ex:
			raise APIResponseError("voice %s" % ex, key=ex.key)
		
		try:
			self._gender = api_json["gender"]
		except KeyError:
			raise APIResponseError("voice gender is missing", key="gender")
	
	gender = property()
	
	def __str__(self):
		"""
		Return str(self).
		"""
		return str({"id": self.id, "name": self.name, "gender": self.gender})
		
	def __repr__(self):
		"""
		Return repr(self).
		"""
		return "%s(%r)" % (self.__class__.__name__, {"id": self.id, "name": self.name, "gender": self.gender})
		
	@gender.getter
	def gender(self):
		"""
		Return voice gender.
		
		:return str:
		"""
		return self._gender
		

class _TTSEntitiesSet(object):
	"""
	Base class for set of SpeachPro entities such as language or voice.
	"""	
	def __init__(self):
		"""
		Initialize set of SpeachPro entities.
		"""
		self._entities = OrderedDict()
		
	def __str__(self):
		"""
		Return str(self).
		"""
		return "[%s]" % ", ".join([str(entity) for entity in self])
		
	def __len__(self):
		"""
		Return len(self).
		"""
		return len(self._entities)
	
	def __contains__(self, value):
		"""
		Return true if value in self.
		"""
		return isinstance(value, _TTSEntity) and value.id in self._entities.keys()
	
	def __getitem__(self, idx):
		"""
		Return item by index.
		"""
		return self._entities[idx]
	
	def __iter__(self):
		"""
		Return self.
		"""
		self._index = -1
		return self
		
	def __next__(self):
		"""
		Return next item.
		"""
		if self._index < len(self) - 1:
			self._index += 1
			return list(self._entities.values())[self._index]
		else:
			raise StopIteration
	
	def _add(self, entity):
		"""
		Add TTS entity to set.
		
		:param _TTSEntity entity:
		    TTS entity:
			
		:return None:
		
		:except KeyError:
		    If entity already exists in set.
		"""
		if not entity in self:
			self._entities[entity.id] = entity
		else:
			raise KeyError("Entity with id '%s' already exists" % entity.id)
			
	def remove(self, entity):
		"""
		Remove TTS entity and return it.
		
		:param _TTSEntity entity:
		    TTS entity.
			
		:return _TTSEntity or None:
		"""
		self._entities.pop(entity.id, None)
		
	def get_by_id(self, id):
		"""
		Return TTS entity by id.
		
		:param str id:
		    TTS entity id.
			
		:return _TTSEntity:
		
		:except KeyError:
		    If entity with specified id dosn't exists in set.
		"""
		for idx,entity in enumerate(self):
			if entity.id == id:
				return entity
		raise KeyError("Entity with id '%s' dosn't exists" % id)
		
	def get_by_name(self, name):
		"""
		Return TTS entity by name.
		
		:param str name:
		    TTS entity name.
			
		:return _TTSEntity:
		
		:except KeyError:
		    If entity with specified name dosn't exists in set.
		"""
		for idx,entity in enumerate(self):
			if entity.name == name:
				return entity
		raise KeyError("Entity with name '%s' dosn't exists" % name)
		
class _LanguagesSet(_TTSEntitiesSet):
	"""
	Set of SpeachPro languages.
	"""
	
	def __repr__(self):
		"""
		Return repr(self).
		"""
		return "%s()" % self.__class__.__name__
	
	def _add(self, lang):
		"""
		Add SpeachPro language to set.
		
		:param _Language lang:
		    SpeachPro language:
			
		:return None:
		
		:except TypeError:
		    If lang not is instance of _Language.
		
		:except KeyError:
		    If language already exists.
		"""
		if not isinstance(lang, _Language):
			raise TypeError("expected SpeechPro language, not %s" % lang.__class__.__name__)
		super()._add(lang)
		
class _VoicesSet(_TTSEntitiesSet):
	"""
	Set of SpeachPro voices.
	"""

	def __repr__(self):
		"""
		Return repr(self).
		"""
		return "%s()" % self.__class__.__name__
	
	def _add(self, voice):
		"""
		Add SpeachPro voices to set.
		
		:param _Voice voice:
		    SpeachPro voices:
			
		:return None:
		
		:except TypeError:
		    If voice not is instance of _Voice.
		
		:except KeyError:
		    If voice already exists.
		"""
		if not isinstance(voice, _Voice):
			raise TypeError("expected SpeechPro voice, not %s" % voice.__class__.__name__)
		super()._add(voice)
		
