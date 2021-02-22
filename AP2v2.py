import socket
import json
import csv
import sys
import random

def main():
	
	tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	tcp_s.connect( ("xcoa.av.it.pt", 8080) )
	str_data = "CONNECT\n"
	b_data = str_data.encode("utf-8")
	tcp_s.send(b_data)
	
	b_data = tcp_s.recv(4096).decode("utf-8")
	
	read="READ"
	partes=b_data.split(":")
	partes2=partes[1].split('}')
	try:
		float(partes2[0])
	except ValueError:
		sys.exit("Token invalido, possivel falha na comunicacao com a sonda")
	token=read+ partes2[0]+"\n"	
	tcp_s.send(bytes(token,'utf-8'))
	b_data=tcp_s.recv(4096).decode("utf-8")	
	wind=0
	temp=0
	hum=0
	sumw=0
	sumt=0
	sumh=0
	t=0
	fout = open('data.csv', 'w')
	writer = csv.DictWriter(fout, fieldnames=['Wind', 'Temperature','Humidity'], delimiter=';')
	writer.writeheader();
	while 1:
		
		b_data=tcp_s.recv(4096).decode("utf-8")	
		print(b_data)
		partes=b_data.split(",")
		i=0
		while i<len(partes):
			partes2=partes[i].split(":")
			if i==0:
				try:
					wind=getValue(partes2[1])
				except IndexError:
					print("Possivel falha de comunicacao com a sonda")
			elif i==1:
				try:
					hum=getValue(partes2[1])
				except IndexError:
					print("Possivel falha de comunicacao com a sonda")
			else:
				try:
					partes3=partes2[1].split("}")
					temp=getValue(partes3[0])
				except IndexError:
					print("Possivel falha de comunicacao com a sonda")
			i+=1
		
		writer.writerow({'Wind': wind, 'Temperature' : temp, 'Humidity': hum} )
		try:
			sumw=sumw+wind
			sumt=sumt+temp
			sumh=sumh+hum
			t+=1
		except :
			continue
		if t==3:
	
			mwind=media(sumw,t)
			mtemp=media(sumt,t)
			mhum=media(sumh,t)
			
			t=0
			if mhum>80:
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
					print("Recomendado usar roupa de vera0(calcoes, t-shirt, chapeu, etc)\n")
					
			sumw=0
			sumt=0
			sumh=0
	fout.close()	
	tcp_s.close()


def getValue(string):
	try:
		float(string)
		return float(string)
	except ValueError:
		print("Valor invalido,possivel falha na comunicacao com a sonda")
	
def media(soma,t):
	return soma/t;	

main()

