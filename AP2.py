import random,socket,hashlib,sys,csv,json,binascii
from base64 import b64decode
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Hash import MD5

def main():
	while 1:## Escolha se quer encriptar as comunicações
		op_0=input("Pretende encriptar os dados? (Y/N) ") 
		if op_0=="Y":
			op=True 
			break
		elif op_0=="N":
			op=False 
			break
		print("(Y/N)")
	if op: 
		key=startencript() ##realizar todas as comunicaçoes encriptadas
	else:
		normal()	##sem encriptaçao
	
	wind=0
	temp=0
	hum=0
	sumw=0
	sumt=0
	sumh=0
	t=0
	fout = open('data.csv', 'w')
	writer = csv.DictWriter(fout, fieldnames=['Wind', 'Temperature','Humidity'], delimiter=';')##escrita de dados em ficheiro csv
	writer.writeheader();
	while 1:
		if op:
			while 1:
				try:
					b_data=rcvencripted(key)##receber dados encriptados
					break
				except binascii.Error:
					continue
		else:
			b_data=rcvnormal()##receber dados nao encriptados 
			
		print(b_data)
		partes=b_data.split(",")
		i=0
		while i<len(partes):## obtençao dos dados de temperatura, vento e humidade
			partes2=partes[i].split(":")
			if i==0:
				try:
					wind=getValue(partes2[1])
				except IndexError:
					print("Possivel falha de comunicacao com a sonda")
			elif i==1:
				try:
					temp=getValue(partes2[1])
				except IndexError:
					print("Possivel falha de comunicacao com a sonda")
			else:
				try:
					partes3=partes2[1].split("}")
					hum=getValue(partes3[0])
				except IndexError:
					print("Possivel falha de comunicacao com a sonda")
			i+=1
		
		writer.writerow({'Wind': wind, 'Temperature' : temp, 'Humidity': hum} )##escrita dos dados em csv
		try:##soma dos dados para calcular medias, caso haja dados corrompidos ignora-os
			sumw=sumw+wind
			sumt=sumt+temp
			sumh=sumh+hum
			t+=1
		except :
			continue
		if t==3:
	
			mwind=media(sumw,t)##calculo de medias
			mtemp=media(sumt,t)
			mhum=media(sumh,t)
			t=0
			if mhum>80:##mecanismos de decisao
				if mtemp<10:
					if mwind>40:
						if mtemp<=0:
							print("Temperaturas negativas! Recomendado usar roupa quente e roupas impermeaveis devido a probabilidade de chuva e ventos fortes\n") 
						elif mtemp<=10:
							print("Recomendado usar um casaco quente, e roupas impermeaveis devido a probabilidade de chuva e ventos fortes\n")
					
						elif mtemp<=20:
							print("Recomendado usar um casaco,e roupas impermeaveis devido a probabilidade de chuva e ventos fortes\n")
						elif mtemp<=30:
							print("Recomendado uma camada de roupa fina,e roupas impermeaveis devido a probabilidade de chuva e ventos fortes\n\n")
						elif mtemp>30:
							("Recomendado usar roupa de verao(calcoes, t-shirt, chapeu, etc),e roupas impermeaveis devido a probabilidade de chuva e ventos fortes\n\n")
				
					else:
						if mtemp<=0:
							print("Temperaturas negativas! Recomendado usar roupa quente e guarda-chuva\n") 
						elif mtemp<=10:
							print("Recomendado usar um casaco quente, e guarda-chuva\n")
					
						elif mtemp<=20:
							print("Recomendado usar um casaco,e guarda-chuva\n")
						elif mtemp<=30:
							print("Recomendado uma camada de roupa fina,e guarda-chuva\n\n")
						elif mtemp>30:
							print("Recomendado usar roupa de verao(calcoes, t-shirt, chapeu, etc),e guarda-chuva\n")
						
			else:
				if mtemp<=0:
					print("Temperaturas negativas! Recomendado usar roupa quente \n") 
				elif mtemp<=10:
					print("Recomendado usar um casaco quente\n")
					
				elif mtemp<=20:
					print("Recomendado usar um casaco\n")
				elif mtemp<=30:
					print("Recomendado uma camada de roupa fina\n")
				else:
					print("Recomendado usar roupa de verao(calcoes, t-shirt, chapeu, etc)\n")
					
			sumw=0
			sumt=0
			sumh=0
	fout.close()	
	tcp_s.close()


def getValue(string):
	try:##recebe strings dos dados e devolve valores 
		i=float(string)
		return i
	except ValueError:
		print("Valor invalido,possivel falha na comunicacao com a sonda")
	
def media(soma,t):##calculo de medias
	return soma/t;	
def normal():##comunicaçao com servidor sem encriptação
	global tcp_s
	tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	tcp_s.connect( ("xcoa.av.it.pt", 8080) )
	str_data = "CONNECT\n"
	b_data = str_data.encode("utf-8")
	tcp_s.send(b_data)
	print("Connected")
	b_data = rcvnormal();

	token=gettokenN(b_data).encode('utf-8')
	tcp_s.send(token)
	b_data=rcvnormal();	
	print("A receber dados:")
def startencript():##comunicaçao com encritaçao
	global tcp_s
	tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	a=random.getrandbits(5)
	p=random.getrandbits(64)
	g=random.getrandbits(64)
	value=pow(g,a,p)
	tcp_s.connect( ("xcoa.av.it.pt", 8080) )
	str_data = "CONNECT "+str(value)+","+str(p)+","+str(g)+"\n"
	print("Connected")
	b_data = str_data.encode("utf-8")
	tcp_s.send(b_data)
	
	b_data = tcp_s.recv(4096).decode("utf-8")

	key=getkey(getb(b_data),a,p)
	
	token=gettokenEn(b_data)
	msg=encrypt(token,key).encode('utf-8')
	tcp_s.send(msg)	
	print("Encrypted communications")
	rcvencripted(key)
	print("A receber dados:")
	return key
def getkey(bint,a,p):##calculo da chave para a cifra AES
	h=MD5.new()
	valX=pow(int(bint),int(a),int(p))
	h.update(str(valX).encode("utf-8"))
	key=h.hexdigest()
	key=key[0:16]
	return key
def rcvnormal():##receçao de dados s/ encriptaçao
	b_data=tcp_s.recv(4096).decode("utf-8")	
	return b_data
def rcvencripted(key):##receçao de dados com encriptaçao
	b_data=tcp_s.recv(4096).decode("utf-8")	
	b_data=decrypt(b_data,key)
	x=0
	s=b_data[x]
	while s!="}":
		x+=1
		s=b_data[x]
	x+=1
	b_data=b_data[0:x]
	return b_data;
def gettokenN(b_data):##token para comunicaçao s/ encriptaçao
	read="READ"
	try:
		partes=b_data.split(":")
		partes2=partes[1].split('}')
	
		token=int(partes2[0])
	except (ValueError,IndexError):
		sys.exit("Token invalido, possivel falha na comunicacao com a sonda")
	token=read+ partes2[0]+"\n"	

	return token
def gettokenEn(b_data):##token para comunicaçao com encriptaçao
	partes=b_data.split(",")
	read="READ"
	partesb=partes[0].split(":")
	b=partesb[1]
	partest=partes[1].split(":")

	token=partest[1].split("}")
	try:
		float(token[0])
	
	except ValueError:
		sys.exit("Token invalido, possivel falha na comunicacao com a sonda")
	token=read+token[0]
	return token	
def getb(b_data):## obtençao do valor B
	
	partes=b_data.split(",")
	partesb=partes[0].split(":")
	b=partesb[1]
	try:
		b=int(b)
	except ValueError:
		sys.exit("Chave invalida, possivel falha de comunicacao com sonda")
	return b
def setsize(text):##acertar tamanho do texto para encriptaçao
	while len(text)%16!=0:
		text=str(text)+" "
	return text
def encrypt(text,key):##encriptaçao
	cipher=AES.new(key)
	encripted=cipher.encrypt(setsize(text))
	encripted=b64encode(encripted)+"\n".encode('utf-8')
	return encripted.decode("utf-8")
	
def decrypt(encripted,key):##desencriptação

	cipher=AES.new(key)
	decripted=b64decode(encripted.encode("utf-8"))
	decripted=cipher.decrypt(decripted).decode("utf-8")
	return decripted
main()


