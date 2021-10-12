import os
import json
import asyncio
import aiohttp
import speechapi
import wave

if __name__ == "__main__":
	async def get_available_packages(session):
		return await speechapi.api._get_api_response(
			"https://cp.speechpro.com/vkasr/rest/v1/packages/available", 
			"get", 
			headers={"x-session-id" : session.session_id}
		)
		
	async def load_package(session, package_id):
		return await speechapi.api._get_api_response(
			"https://cp.speechpro.com/vkasr/rest/v1/packages/%s/load" % package_id, 
			"get", 
			headers={"x-session-id" : session.session_id}
		)
		
	async def unload_package(session, package_id):
		return await speechapi.api._get_api_response(
			"https://cp.speechpro.com/vkasr/rest/v1/packages/%s/unload" % package_id, 
			"get", 
			headers={"x-session-id" : session.session_id}
		)
		
	async def offline_recognize(session, data, audio_mime, package_id):
		return await speechapi.api._get_api_response(
			"https://cp.speechpro.com/vkasr/rest/v1/recognize", 
			"post", 
			{
				"audio": {
					"data": data, 
					"mime": audio_mime, 
				}, 
				"package_id": package_id
			}, 
			headers={"content-type": "application/json", "x-session-id": session.session_id}, 
			json_serialize=json.dumps
		)
		
	async def offline_recognize_words(session, data, audio_mime, package_id):
		return await speechapi.api._get_api_response(
			"https://cp.speechpro.com/vkasr/rest/v1/recognize/words", 
			"post", 
			{
				"audio": {
					"data": data, 
					"mime": audio_mime, 
				}, 
				"package_id": package_id
			}, 
			headers={"content-type": "application/json", "x-session-id": session.session_id}, 
			json_serialize=json.dumps
		)
		
	async def offline_recognize_advanced(session, data, channels, package_id):
		return await speechapi.api._get_api_response(
			"https://cp.speechpro.com/vkasr/rest/v1/recognize/advanced", 
			"post", 
			{
				"channels": channels, 
				"data": data,
				"package_id": package_id
			}, 
			headers={"content-type": "application/json", "x-session-id": session.session_id}, 
			json_serialize=json.dumps
		)
		
	async def recognize_open_stream(session, audio_mime, package_id):
		return await speechapi.api._get_api_response(
			"https://cp.speechpro.com/vkasr/rest/v1/recognize/stream", 
			"post", 
			{
				"mime": audio_mime,
				"package_id": package_id
			}, 
			headers={"content-type": "application/json", "x-session-id": session.session_id}, 
			json_serialize=json.dumps
		)
		
	async def recognize_close_stream(session, ws):
		return await speechapi.api._get_api_response(
			"https://cp.speechpro.com/vkasr/rest/v1/recognize/stream", 
			"delete", 
			headers={"x-session-id": session.session_id, "x-transaction-id": ws.transaction_id}, 
		)
		
	async def stream_recognize(data, wsconfig):
		async def _(data, wsconfig):
			async with aiohttp.ClientSession() as websockets:
				async with websockets.ws_connect(wsconfig.url) as ws:
					# if len(data):
						# while len(data):
							# await ws.send_bytes(data[:500000])
							# data = data[500000:]
					# else:
						# await ws.send_bytes(data)
					
					# loop = asyncio.get_running_loop()
					
					# # There are some problems with ending of read data wrom websocket.
					# # Timer is needed for resolve this problems.
					# handle = loop.call_later(2, lambda : loop.create_task(ws.close()))
					
					# d = await ws.receive()
					# print(d)
					
					# async for msg in ws:
						# # cancel timer if read data successfully
						# handle.cancel()
						# if msg.type == aiohttp.WSMsgType.CLOSING:
							# break
						# else:
							# yield msg.data
							# print(msg.data)
							# # set new timer
							# handle = loop.call_later(2, lambda : loop.create_task(ws.close()))
							
					result = ""
					while len(data):
						await ws.send_bytes(data[:1000])
						
						msg = None
						try: msg = await ws.receive(timeout=2)
						except asyncio.exceptions.TimeoutError: pass
						
						# print(msg)
						
						# while msg != None and msg.type not in [aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING]:
							# print(msg.type)
						# print("msg: %s" % msg.data)
							# yield msg.data
						if msg != None and msg.type not in [aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING]:
							yield msg.data
							# try: msg = await ws.receive(timeout=30)
							# except asyncio.exceptions.TimeoutError: break
							
						data = data[1000:]
							
					# always close web socket connection
					if not ws.closed:
						await ws.close()
						
		# result = ""
		# async for chunck in _(data, wsconfig):
			# result += chunck
		# return result
		async for __ in _(data, wsconfig): continue
		return __
		
	async def stream_synthes(text, wsconfig):
		ttsapi = speechapi.TTSApi()
		bin = b""
		async for chunck in ttsapi.stream_synthes(text, wsconfig):
			bin += chunck
		return bin
		
		
	sesapi = speechapi.SessionApi()
	ttsapi = speechapi.TTSApi()
		
	loop = asyncio.get_event_loop()
	
	
	
	task = loop.create_task(sesapi.session_create(957, "vowatchka@mail.ru", "y77d53caD@"))
	loop.run_until_complete(task)
	session = task.result()
	
	# text = "Всем привет! Меня зовут Вова."
	text = """Для потокового распознавания требуется создать подключение по протоколу Websocket. Для этого направить POST-запрос на URL v1/synthesize/stream, передав в запросе формат синтезированного аудио и информацию о голосе. Результатом выполнения запроса является ссылка для подключения по протоколу Websocket. После установления подключения, можно отправлять текстовые данные на сервер, а в ответ получать PCM в бинарном виде. """ * 10
	# task = loop.create_task(ttsapi.package_synthes(text, session, "Alexander8000"))
	# loop.run_until_complete(task)
	# data = task.result()
	
	
	
	task = loop.create_task(ttsapi.open_synthes_stream(session, "Alexander8000"))
	loop.run_until_complete(task)
	ws_synthes = task.result()
	
	
	bin_data = b""
	print("text len: %d" % len(text))
	task = loop.create_task(stream_synthes(text, ws_synthes))
	loop.run_until_complete(task)
	bin_data = task.result()
	# print(bin_data)
	
	with wave.open(os.path.join(os.path.dirname(__file__), "stream_synthes.wav"), "wb") as f:
		# f.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
		f.setnchannels(1)
		f.setsampwidth(2)
		# f.setframerate(22050)
		f.setframerate(8000)
		f.writeframes(bin_data)
	
	
	
	task = loop.create_task(ttsapi.close_synthes_stream(ws_synthes))
	loop.run_until_complete(task)
	resp = task.result()
	print(resp)
	
	
	
	# task = loop.create_task(get_available_packages(session))
	# loop.run_until_complete(task)
	# packages = task.result()
	# print(packages)
	
	
	
	# task = loop.create_task(load_package(session, "TelecomEsp"))
	# loop.run_until_complete(task)
	# resp = task.result()
	
	
	
	# task = loop.create_task(offline_recognize(session, data, "audio/wav", ""))
	# loop.run_until_complete(task)
	# resp = task.result()
	# print(resp)
	
	
	
	# task = loop.create_task(offline_recognize_words(session, data, "audio/wav", ""))
	# loop.run_until_complete(task)
	# resp = task.result()
	# print(resp)
	
	
	
	# task = loop.create_task(offline_recognize_advanced(session, data, [0], ""))
	# loop.run_until_complete(task)
	# resp = task.result()
	# print(resp)
	
	
	
	task = loop.create_task(recognize_open_stream(session, "audio/pcm16", "IvrRus"))
	loop.run_until_complete(task)
	resp = task.result()
	print(resp)
	ws = speechapi.session._WsConfiguration(json.loads(resp), session)
	
	
	
	# task = loop.create_task(stream_recognize(speechapi.api.base64_to_bin(data), ws))
	task = loop.create_task(stream_recognize(bin_data, ws))
	loop.run_until_complete(task)
	resp = task.result()
	print(resp)
	print("len recognized text: %d" % len(resp))
	with open(os.path.join(os.path.dirname(__file__), "resp.txt"), "w", encoding="utf-8") as f:
		f.write(resp)
	
	
	
	task = loop.create_task(recognize_close_stream(session, ws))
	loop.run_until_complete(task)
	resp = task.result()
	print(resp)
	print("len recognized text from resp: %d" % len(json.loads(resp)["text"]))
	with open(os.path.join(os.path.dirname(__file__), "text.txt"), "w", encoding="utf-8") as f:
		f.write(json.loads(resp)["text"])
	
	
	
	# task = loop.create_task(unload_package(session, "TelecomEsp"))
	# loop.run_until_complete(task)
	# resp = task.result()
	
	
	
	task = loop.create_task(sesapi.session_delete(session))
	loop.run_until_complete(task)
	
	print(session.is_active)
	
	loop.close()
		