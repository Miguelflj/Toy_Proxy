from socket import *
import os.path
import signal
import threading

address = ('localhost',12345) #endereco socket (fica escutando atras da porta)

#conexao com meu browser
browser = socket(AF_INET,SOCK_STREAM) #IPv4 e TCP

browser.setsockopt(SOL_SOCKET, SO_REUSEADDR,1) # reutilizacao de porta

browser.bind(address) #associa socket a endereco
browser.listen(10)





def load_blacklist():
	bk = []
	with open("blacklist.txt",'r') as arc_bk:
		for line in arc_bk:
	 		print(line)
	 		bk.append(line)

	return bk

def check_request(webserver,bk):
	flag = 1
	for i in range(len(bk)):
		if( webserver.find(bk[i]) ):
			flag = 0

	return flag


def reply_request(webserver,port,connection,request):
	#estabelece conexao com o servidor web desejado
	server = socket(AF_INET, SOCK_STREAM) 
	server.settimeout(20)
	print(webserver)
	server.connect((webserver, port))
	server.sendall(request.encode())
	

	while 1:
		try:
			#Le os dados enviados pelo servidor web
			data = server.recv(2048)
			if (len(data) > 0):
				print("Send...")

				connection.send(data) # envia os dados para o browser
			else:
				print("Ok!")
				break
		except Exception:
			print("Sent!")
			break
	server.close()

def reply_blocked(connection,arq_name):
	connection.send("HTTP/1.1 200 OK\r\ncontent-type: text/html\r\n\r\n".encode())
	with open(arq_name, "rb") as f:
			data = f.read(2048)
			while data:
				connection.send(data)
				data = f.read(2048)
	connection.close()



bk = load_blacklist()

while True:

	connection, addres_remote = browser.accept()
	request = connection.recv(2048).decode()
	#print(request)
	line_1 = request.split('\n')[0]

	
	#print(line_1)
	url = line_1.split(' ')[1]
	url = url.replace("http://","")
	port_pos = url.find(":") # procura a posicao da porta caso a requisicao tenha enviado
	webserver_pos = url.find("/")
	
	if webserver_pos == -1:
		webserver_pos = len(url)

	
	webserver = url[:webserver_pos]
	arq_name = url[webserver_pos:]

	test = webserver.find(":")

	if( arq_name == "/"):
		arq_name = "indice.html"
	if( arq_name.startswith("/") ):
		arq_name = arq_name.strip("/")




	if( test == -1):
		port = 80
	else:
		port = webserver[test+1:]
		webserver = webserver.replace(":" + port,"")
		port = int(port)

	print(webserver)	
	
	#verifica se a requisição está na blacklist
	blackList = check_request(webserver,bk)

	if(blackList == 1):
		
		t = threading.Thread(target=reply_request,args=(webserver,port,connection,request))	
		t.setDaemon(True)
		t.start()
	else:
		verification = arq_name.find("success")
		if(verification == -1):
			reply_blocked(connection,arq_name)