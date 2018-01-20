#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Name: CodyCloud Ngrok Server
# Author: Icy(enderman1024@foxmail.com)

import time, socket, threading, os, sys, json




def init():
	global LOGGER, KEY, STOP
	paths = ("./bin","./cache","./configs","./logs")
	for i in paths:
		path_fixer(i)
	try:
		configs = read_config("./configs/codycloud.json")
	except Exception as err:
		print("INITIALIZE FAILED: " + str(err))
		sys.exit(1)
	log_level = "INFO"
	if "log_level" in configs:
		log_level = configs["log_level"]
	LOGGER = logger("./logs/codycloud.log","crlf","%Y-%m-%d %H:%M:%S",log_level)
	LOGGER.INFO("[Main] Initilizing...")
	LOGGER.DEBUG("[Main] Path check: OK")
	os.system("rm cache/*")
	LOGGER.DEBUG("[Main] Cache clear: OK")
	KEY = b"CODYCLOUDORIGINALBASEKEY"
	if "socket_key" in configs:
		KEY = configs["socket_key"].encode("utf-8")
	LOGGER.DEBUG("[Main] Configs load: OK")
	# global tags
	STOP = False
	NGROK_SERVICE = False
	CODYCLOUD_SERVER = False
	LOGGER.DEBUG("[Main] Global tags define: OK")
	LOGGER.INFO("[Main] Initialized")




def path_fixer(path): # path checker
	chk = ""
	for i in path:
		chk += i
		if os.sep == i:
			if not os.path.exists(chk):
				os.mkdir(chk)




class iccode: # Simple Data encoder/decoder
	def __init__(self,key):
		if len(key) < 1:
			assert 0,"Key's length must be greater than 0"
		self.origin_key = key
		self.key = []
		keys = ""
		for i in key:
			keys = keys + str(ord(i))
		temp = ""
		for i in keys:
			temp = temp + i
			if int(temp[0]) < 5:
				if len(temp) == 3:
					self.key.append(int(temp))
					temp = ""
				else:
					pass
			else:
				if len(temp) == 2:
					self.key.append(int(temp))
					temp = ""
				else:
					pass
		if temp != "":
			self.key.append(int(temp))
		self.walk = 0
		self.origin_ickey = self.key
	def encode(self,data):
		res = b""
		for i in data:
			if self.walk >= len(self.key):
				self.walk = 0
				self.flush()
			code = i - self.key[self.walk]
			while code < 0:
				code = 256 + code
			res = res + bytes((code,))
			self.walk += 1
		return res
	def decode(self,data):
		res = b""
		for i in data:
			if self.walk >= len(self.key):
				self.walk = 0
				self.flush()
			code = i + self.key[self.walk]
			while code > 255:
				code = code - 256
			res = res + bytes((code,))
			self.walk += 1
		return res
	def flush(self):
		key = []
		for i in self.key:
			key.append(str(i))
		for i in "".join(key):
			key.append(str(i))
		self.key = []
		for i in range(len(key)):
			cursor = i + int(key[i])
			while cursor > (len(key)-1):
				cursor = cursor - len(key)
			key[i] = (str(int(key[i])+int(key[cursor])+len(key)))[-1:]
		temp = ""
		key = "".join(key)
		for i in key:
			temp = temp + i
			if len(self.key) >= len(self.origin_key):
				break
			if int(temp[0]) < 5:
				if len(temp) == 3:
					self.key.append(int(temp))
					temp = ""
				else:
					pass
			else:
				if len(temp) == 2:
					self.key.append(int(temp))
					temp = ""
				else:
					pass
		if len(temp) > 0 and len(self.key) < len(self.origin_key):
			self.key.append(int(temp))
	def reset(self):
		self.key = self.origin_ickey
		self.walk = 0
	def debug(self):
		print("Original   key: " + str(self.origin_key))
		print("Original ickey: " + str(self.origin_ickey))
		print("Step     ickey: " + str(self.key))
		print("Walk    cursor: " + str(self.walk))
		return (self.origin_key,self.origin_ickey,self.key,self.walk)




class logger: # Logger
	def __init__(self,filename,line_end,date_format,level):
		self.level = 1
		if level == "DEBUG":
			self.level = 0
		elif level == "INFO":
			self.level = 1
		elif level == "WARNING":
			self.level = 2
		elif level == "ERROR":
			self.level = 3
		elif level == "CRITICAL":
			self.level = 4
		else:
			assert 0,"logger level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
		try:
			log_file = open(filename,"w")
			log_file.close()
		except Exception as err:
			assert 0,"Can't open file: \"" + filename + "\", result: " + str(err)
		self.filename = filename
		try:
			temp = time.strftime(date_format)
			del temp
		except Exception as err:
			assert 0,"Failed to set date formant, result: " + str(err)
		self.date_format = date_format
		if line_end == "lf":
			self.line_end = "\n"
		elif line_end == "crlf":
			self.line_end = "\r\n"
		else:
			assert 0,"Unknow line end character(s): \"" + line_end + "\""
	def DEBUG(self,msg):
		if self.level > 0:
			return
		infos = "["+ time.strftime(self.date_format) +"] [DBUG] " + msg + self.line_end
		log_file = open(self.filename,"a")
		log_file.write(infos)
		log_file.close()
	def INFO(self,msg):
		if self.level > 1:
			return
		infos = "["+ time.strftime(self.date_format) +"] [INFO] " + msg + self.line_end
		log_file = open(self.filename,"a")
		log_file.write(infos)
		log_file.close()
	def WARNING(self,msg):
		if self.level > 2:
			return
		infos = "["+ time.strftime(self.date_format) +"] [WARN] " + msg + self.line_end
		log_file = open(self.filename,"a")
		log_file.write(infos)
		log_file.close()
	def ERROR(self,msg):
		if self.level > 3:
			return
		infos = "["+ time.strftime(self.date_format) +"] [EROR] " + msg + self.line_end
		log_file = open(self.filename,"a")
		log_file.write(infos)
		log_file.close()
	def CRITICAL(self,msg):
		infos = "["+ time.strftime(self.date_format) +"] [CRIT] " + msg + self.line_end
		log_file = open(self.filename,"a")
		log_file.write(infos)
		log_file.close()




class isock: #tcp socket server
	def __init__(self):
		self.isock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server = False
	def build_server(self,addr,maxcon):
		if self.server == False:
			try:
				self.isock.bind(addr)
				self.isock.listen(maxcon)
			except Exception as err:
				return (False,str(err))
			self.server = True
			return (True,"")
		else:
			return (False,"socket server has already been built")
	def connect(self,addr):
		if self.server:
			return (False,"Already became a server")
		else:
			try:
				self.isock.connect(addr)
			except Exception as err:
				return (False,str(err))
			return (True,"")
	def settimeout(self,to):
		self.isock.settimeout(to)
	def accept(self):
		if self.server:
			try:
				clt,con = self.isock.accept()
			except Exception as err:
				return (False,str(err))
			return (True,(clt,con))
		else:
			return (False,"server has not been built yet")
	def send(self,data):
		try:
			self.isock.send(data)
		except Exception as err:
			return (False,str(err))
		return (True,len(data))
	def recv(self,length):
		try:
			data = self.isock.recv(length)
		except Exception as err:
			return (False,str(err))
		return(True,data)
	def close(self):
		try:
			self.isock.close()
		except Exception as err:
			return(False,str(err))
		return(True,'')




def keygen(code,mt): # Live key generator
	code = code.decode()
	dt = int((time.time()+(300*mt))/300)
	key = ""
	timekey = str(dt*int(dt/3600)+dt*len(code))+str(dt*dt+dt**len(code))
	while len(timekey) < len(code):
		timekey += timekey
	for i in range(0,len(code)):
		a = ord(code[i]) + int(timekey[i])
		key = key + chr(a)
	key = key.encode()
	return key




def keymatch(key): # Live key matcher
	global KEY
	lock_1 = keygen(KEY,-1)
	lock_2 = keygen(KEY,0)
	lock_3 = keygen(KEY,1)
	lock = [lock_1,lock_2,lock_3]
	if key in lock:
		return True
	else:
		return False




def get_args(): # read command shell's argument(s)
	opts = sys.argv[1:]
	argv = ""
	res = {}
	for i in opts:
		if len(argv) > 0 and "-" != i[0]:
			res.update({argv:i})
			argv = ""
		if "-" == i[0]:
			argv = i
			res.update({argv:""})
	return res




def read_config(file): # Json Config Reader
	config_file = open(file,"r")
	data = json.load(config_file)
	return data




def run_ngrokd(path,config): # run ngrok server file (sub thread)
	cmd = "./bin/" + path
	for i in config:
		if i == "domain":
			cmd += " -domain=\"" + config["domain"] + "\""
		elif i == "http_port":
			cmd += " -httpAddr=\":" + config["http_port"] + "\""
		elif i == "tunnel_addr":
			cmd += " -tunnelAddr=\":" + config["tunnel_addr"] + "\""
		elif i == "log_path":
			cmd += " -log \"" + config["log_path"] + "\""
		elif i == "log_level":
			cmd += " -log-level " + config["log_level"]
	LOGGER.DEBUG("[NgrokThread] Command generated: " + cmd)
	try:
		os.system(cmd)
	except Exception as err:
		LOGGER.WARNING("[NgrokThread] NGROK server(\"" + path + "\")stopped, result: " + str(err))




def ngrokd_server(): # ngrok control server loop (thread)
	global NGROK_SERVICE
	NGROK_SERVICE = True
	LOGGER.DEBUG("[NgrokService] Loading configs")
	try:
		configs = read_config("./configs/codycloud.json")
	except Exception as err:
		LOGGER.CRITICAL("[NgrokService] Can't open(or missing) \"codycloud.json\" config file")
		global STOP
		STOP = True
		sys.exit(1)
	ngrok_configs = configs["ngrok_servers"]
	threads = []
	for i in ngrok_configs:
		temp = ngrok_configs[i]
		if "log_path" in temp:
			LOGGER.DEBUG("[NgrokService] Checking " + i + " log path")
			path_fixer(temp["log_path"])
		ngrokd_thread = threading.Thread(target=run_ngrokd,args=(i,temp))
		ngrokd_thread.start()
		LOGGER.INFO("[NgrokService] MGROK server \"" + i + "\" thread has been started")
		if not "tunnel_addr" in temp:
			threads.append((i,4443))
		else:
			threads.append((i,int(temp["tunnel_addr"])))
	LOGGER.DEBUG("[NgrokService] Server detecting loop starting")
	temp = 0
	while True:
		time.sleep(1)
		temp += 1
		if STOP:
			LOGGER.INFO("[NgrokService] Stopping Ngrok Service")
			for i in threads:
				LOGGER.DEBUG("[NgrokService] Sending kill signal to \"" + i[0] + "\"")
				os.system("killall \"" + i[0] + "\"")
			LOGGER.INFO("[NgrokService] Ngrok Service stopped")
			NGROK_SERVICE = False
			return
		if temp >= 120:
			test = isock()
			test.settimeout(5)
			LOGGER.DEBUG("[NgrokService] Testing ngrok server connections")
			for i in threads:
				temp = test.connect(("localhost",i[1]))
				if temp[0]:
					LOGGER.DEBUG("[NgrokService] Ngrok server \"" + i[0] + "\" : OK")
					test.close()
				else:
					LOGGER.WARNING("[NgrokService] Ngrok server \"" + i[0] + "\" : No response")
					LOGGER.INFO("[NgrokService] Restarting " + i[0])
					temp = ngrok_configs[i[0]]
					ngrokd_thread = threading.Thread(target=run_ngrokd,args=(i[0],temp))
					ngrokd_thread.start()
			temp = 0




def bin2str(data): # transform bin data to string
	try:
		res = data.decode()
	except:
		res = str(data)
	return res




def codycloud_clientHandler(host): # CodyCloud Client Handler (sub thread)
	clt = host[0]
	con = host[1]
	clt.settimeout(15)
	LOGGER.INFO("[CCClientHandler] Connection " + str(con[0]) + "?" + str(con[1]) + " handled")
	LOGGER.DEBUG("[CCClientHandler] Waitting to match coming key")
	try:
		data = clt.recv(1024)
	except Exception as err:
		LOGGER.ERROR("[CCClientHandler] Error while waitting for respons: " + str(err))
	coder = iccode(KEY)
	key = coder.decode(data)
	coder.reset()
	res = keymatch(key)
	if res:
		LOGGER.DEBUG("[CCClientHandler] Live key matched, sending feedback")
	else:
		LOGGER.WARNING("[CCClientHandler] Live key match failed, data received: " + bin2str(data) + ". Closing connection.")
		clt.close()
		return
	try:
		clt.send(coder.encode(b"OK"))
	except Exception as err:
		LOGGER.ERROR("[CCClientHandler] Failed to send feedbaxk, result: " + str(err) + ". Closing connection")
		clt.close()
		return
	LOGGER.DEBUG("[CCClientHandler] Waitting for respons")
	try:
		data = clt.recv(1024)
	except Exception as err:
		LOGGER.ERROR("[CCClientHandler] Failed to receive message, result: " + str(err) + ". Closing connection")
		clt.close()
		return
	coder.reset()
	data = coder.decode(data)
	data = int(data)
	if not data in range(65536):
		LOGGER.WARNING("[CCClientHandler] Unexpected data: " + bin2str(data) + ". Closing connection")
		clt.close()
		return
	else:
		LOGGER.INFO("[CCClientHandler] Request received: port " + str(data))
	socket = isock()
	socket.settimeout(5)
	LOGGET.DEBUG("[CCClientHandler] Testing port " + str(data))
	res = socket.connect(("localhost",data))
	if res:
		LOGGER.DEBUG("[CCClientHandler] Port " + str(data) + " is OPEN, sending feedback")
		socket.close()
		coder.reset()
		try:
			clt.send(coder.encode(b"OP"))
		except Exception as err:
			LOGGER.ERROR("[CCClientHandler] Failed to send feedback, result: " + str(err) + ". Closing connection")
			clt.close()
			return
	else:
		LOGGER.DEBUG("[CCClientHandler] Port " + str(data) + " is CLOSE, sending feedback")
		coder.reset()
		try:
			clt.send(coder.encode(b"CL"))
		except Exception as err:
			LOGGER.ERROR("[CCClientHandler] Failed to send feedback, result: " + str(err) + ". Closing connection")
			clt.close()
			return
	clt.close()
	LOGGER.DEBUG("[CCClientHandler] Connection closed, handler thread end")
	return




def codycloud_socketServer(): # codycloud server (thread)
	global CODYCLOUD_SERVER
	CODYCLOUD_SERVER = True
	LOGGER.DEBUG("[CodyCloudServer] Loading configs")
	try:
		configs = read_config("./configs/codycloud.json")
	except Exception as err:
		LOGGER.CRITICAL("[CodyCloudServer] Can't open(or missing) \"codycloud.json\" config file")
		global STOP
		STOP = True
		sys.exit(1)
	max_con = 10
	port = 2220
	if "max_con" in configs:
		max_con = configs["max_con"]
	if "codycloud_server_port" in configs:
		port = configs["codycloud_server_port"]
	srv = isock()
	temp = srv.build_server(("0.0.0.0",port),max_con)
	if not temp[0]:
		LOGGER.ERROR("[CodyCloudServer] Error while starting codycloud server, result: " + str(err))
	else:
		LOGGER.INFO("[CodyCloudServer] CodyCloud is now listening on 0.0.0.0:" + str(port) + " with max connection number of " + str(max_con))
	error = 0
	while True:
		host = srv.accept()
		if not host[0]:
			if error >= 10:
				LOGGER.CRITICAL("[CodyCloudServer] Too many errors, exitting")
				global STOP
				STOP = True
				return
			LOGGER.ERROR("[CodyCloudServer] Socket server error: " + host[1])
			error += 1
			continue
		error = 0
		host = host[1]
		if STOP:
			LOGGER.INFO("[CodyCloudServer] Stopping codycloud server")
			host[0].close()
			LOGGER.DEBUG("[CodyCloudServer] Connection closed")
			temp = srv.close()
			if not temp[0]:
				LOGGER.WARNING("[CodyCloudServer] Failed to close socket server, result: " + temp[1])
			else:
				LOGGER.DEBUG("[CodyCloudServer] Socket server closed")
			LOGGER.INFO("[CodyCloudServer] CodyCloud server stopped")
			CODYCLOUD_SERVER = False
			return
		handler_thread = threading.Thread(target=codycloud_clientHandler,args=(host))
		try:
			handler_thread.start()
		except Exception as err:
			LOGGER.ERROR("[CodyCloudServer] Failed to start a handler thread, result: " + str(err))
			host[0].close()




def stop_service(): # stopping service (main)
	global STOP
	LOGGER.INFO("[StopService] Stopping Service is now listening for stopping signal")
	try:
		configs = read_config()
	except:
		configs = {}
	while True:
		time.sleep(2)
		signal = os.path.exists("cache/CMD_STOP")
		if signal or STOP:
			STOP = True
			LOGGER.INFO("[StopService] Stopping signal detected, stopping CodyCloud")
			socket = isock()
			port = 2220
			if "codycloud_server_port" in configs:
				port = configs["codycloud_server_port"]
			socket.settimeout(5)
			socket.connect(("localhost",port))
			socket.close()
			temp = 0
			while True:
				time.sleep(1)
				temp += 1
				if temp >= 120:
					if NGROK_SERVICE:
						LOGGER.WARNING("[StopService] Ngrok Service thread has no response, stopping failed")
					if CODYCLOUD_SERVER:
						LOGGER.WARNING("[StopService] CodyCloud Server thread has no response, stopping failed")
				else:
					if NGROK_SERVICE == False and CODYCLOUD_SERVER == False:
						LOGGER.INFO("[StopService] All main threads stopped")
						break
			LOGGER.DEBUG("[StopService] Releasing Stopped signal file")
			file = open("cache/FB_STOPPED","w")
			file.write("stopped")
			file.close()
			LOGGER.INFO("[StopService] CodyCloud stopped")
			return




def main():
	init()
	LOGGER.DEBUG("[Main] Starting Ngrok Service")
	ngrok_service_thread = threading.Thread(target=ngrokd_server,args=())
	ngrok_service_thread.start()
	LOGGER.DEBUG("[Main] Starting CodyCloud SocketServer")
	codycloud_thread = threading.Thread(target=codycloud_socketServer,args=())
	codycloud_thread.start()
	LOGGER.DEBUG("[Main] Starting main thread control service")
	stop_service()
	sys.exit(0)




if __name__ == "__main__":
	main()