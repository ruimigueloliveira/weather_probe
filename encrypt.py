import random,socket,hashlib
from base64 import b64decode
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Hash import MD5

def main():
	tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	a=random.getrandbits(2,10)
	p=random.getrandbits(64)
	g=random.getrandbits(64)
	value=pow(g,a,p)
	tcp_s.connect( ("xcoa.av.it.pt", 8080) )
	str_data = "CONNECT "+str(value)+","+str(p)+","+str(g)+"\n"
	b_data = str_data.encode("utf-8")
	tcp_s.send(b_data)
	
	b_data = tcp_s.recv(4096).decode("utf-8")
	print(b_data)
	cipher = AES.new(getkey(getb(b_data),a,p))
	tcp_s.send(encrypt("READ "+gettoken(b_data),cipher))
	b_data = tcp_s.recv(4096).decode("utf-8")
	print(b_data)
	
def getkey(bint,a,p):
	x=pow(int(bint),int(a),int(p))
	chave=hashlib.md5(str(x).encode("utf-8")).hexdigest()
	chave=chave[0:16]
	return chave
def gettoken(b_data):	
	partes=b_data.split(",")
	read="READ"
	partesb=partes[0].split(":")
	b=partesb[1]
	partest=partes[1].split(":")

	token=partest[1].split("}")
	sendtoken=read+token[0]
	
	try:
		float(token[0])
	
	except ValueError:
		sys.exit("Token invalido, possivel falha na comunicacao com a sonda")
	
	return token	
def getb(b_data):
	
	partes=b_data.split(",")
	partesb=partes[0].split(":")
	b=partesb[1]
	try:
		bint=float(b)
	except ValueError:
		sys.exit("Chave invalida, possivel falha de comunicacao com sonda")
	
	return bint
def setsize(text):
	while len(text)%16!=0:
		text=str(text)+" "
	return text
def encrypt(text,cipher):
	encripted=cipher.encrypt(setsize(text))
	encripted=b64encode(encripted)+"\n".encode('utf-8')
	return bytes(encripted.decode("utf-8"),'utf,8')
def decrypt(encripted,cipher):
	decripted=cipher.decrypt(b64decode(encripted.decode('utf-8')))
	return decripted

