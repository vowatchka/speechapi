import os
import asyncio

from speechapi import *
import wave

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	
	async def main_session():
		sesapi = SessionApi()
		
		session = await sesapi.session_create(957, "vowatchka@mail.ru", "y77d53caD@")
		print("open session with id %s" % session.session_id)
		session_status = await sesapi.session_status(session)
		print("incapsulated session status: %r" % session.is_active)
		print("requested session status: %r" % session_status)
		
		await sesapi.session_delete(session)
		print("delete session with id %s" % session.session_id)
		
		session_status = await sesapi.session_status(session)
		print("incapsulated session status: %r" % session.is_active)
		print("requested session status: %r" % session_status)
			
	async def main_package_synthes():
		sesapi = SessionApi()
		ttsapi = TTSApi()
		
		from speechapi.tts import _Voice
		
		session = await sesapi.session_create(957, "vowatchka@mail.ru", "y77d53caD@")
		print("open session with id %s" % session.session_id)
		
		# bin data
		# async with session:
			# bin_data = await ttsapi.package_synthes("Здорова!", session, "Alexander", bin=True)
			
		# base64 data
		async with session:
			data = await ttsapi.package_synthes("Здорова!", session, "Alexander", bin=False)
			
		with open(r"c:\users\vsaltykov\desktop\base64.txt", "w", encoding="utf-8") as f:
			f.write(data)
			
		print("auto delete session with id %s" % session.session_id)
		session_status = await sesapi.session_status(session)
		print("incapsulated session status: %r" % session.is_active)
		print("requested session status: %r" % session_status)
		
		# with open(os.path.join(os.path.dirname(__file__), "package_synthes.wav"), "wb") as f:
			# f.write(bin_data)
			
	async def main_stream_synthes():
		sesapi = SessionApi()
		ttsapi = TTSApi()
		
		from speechapi.tts import _Voice
		
		session = await sesapi.session_create(957, "vowatchka@mail.ru", "y77d53caD@")
		print("open session with id %s" % session.session_id)
		
		async with session:
			wsconfig = await ttsapi.open_synthes_stream(session, "Alexander")
			
			fulldata = b""
			async with wsconfig:
				async for bin_data in ttsapi.stream_synthes("""Для потокового распознавания требуется создать подключение по протоколу Websocket. Для этого направить POST-запрос на URL v1/synthesize/stream, передав в запросе формат синтезированного аудио и информацию о голосе. Результатом выполнения запроса является ссылка для подключения по протоколу Websocket. После установления подключения, можно отправлять текстовые данные на сервер, а в ответ получать PCM в бинарном виде.""", wsconfig):
					fulldata += bin_data
					
			with wave.open(os.path.join(os.path.dirname(__file__), "stream_synthes.wav"), "wb") as f:
				# f.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
				f.setnchannels(1)
				f.setsampwidth(2)
				f.setframerate(22050)
				f.writeframes(fulldata)
					
		print("auto delete session with id %s" % session.session_id)
		session_status = await sesapi.session_status(session)
		print("incapsulated session status: %r" % session.is_active)
		print("requested session status: %r" % session_status)
		
	async def main_languages():
		sesapi = SessionApi()
		ttsapi = TTSApi()
		
		from speechapi.tts import _Voice
		
		session = await sesapi.session_create(957, "vowatchka@mail.ru", "y77d53caD@")
		print("open session with id %s" % session.session_id)
		
		async with session:
			langs = await ttsapi.get_languages(session)
			print(langs)
					
		print("auto delete session with id %s" % session.session_id)
		session_status = await sesapi.session_status(session)
		print("incapsulated session status: %r" % session.is_active)
		print("requested session status: %r" % session_status)
		
	async def main_voices():
		sesapi = SessionApi()
		ttsapi = TTSApi()
		
		from speechapi.tts import _Voice
		
		session = await sesapi.session_create(957, "vowatchka@mail.ru", "y77d53caD@")
		print("open session with id %s" % session.session_id)
		
		async with session:
			langs = await ttsapi.get_languages(session)
			for lang in langs:
				print("\nvoices for lang %r" % lang.name)
				voices = await ttsapi.get_voices(session, lang)
				print(voices)
					
		print("auto delete session with id %s" % session.session_id)
		session_status = await sesapi.session_status(session)
		print("incapsulated session status: %r" % session.is_active)
		print("requested session status: %r" % session_status)
		
	async def print_voices(session, lang):
		ttsapi = TTSApi()
		voices = await ttsapi.get_voices(session, lang)
		print("\nvoices for lang %r" % lang.name)
		print(voices)
		
	async def main():
		sesapi = SessionApi()
		ttsapi = TTSApi()
		
		from speechapi.tts import _Voice
		
		session = await sesapi.session_create(957, "vowatchka@mail.ru", "y77d53caD@")
		print("open session with id %s" % session.session_id)
		
		async with session:
			langs = await ttsapi.get_languages(session)
			await asyncio.wait([asyncio.ensure_future(print_voices(session, lang), loop=asyncio.get_running_loop()) for lang in langs])
					
		print("auto delete session with id %s" % session.session_id)
		session_status = await sesapi.session_status(session)
		print("incapsulated session status: %r" % session.is_active)
		print("requested session status: %r" % session_status)
		
	# task = loop.create_task(main_session())
	# task = loop.create_task(main_package_synthes())
	task = loop.create_task(main_stream_synthes())
	# task = loop.create_task(main_languages())
	# task = loop.create_task(main_voices())
	# task = loop.create_task(main())
	loop.run_until_complete(task)
	loop.close()