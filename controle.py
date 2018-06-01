# -*- coding: utf-8 -*-
"""
@Data:			25/Outubro/2017
@Objetivo:		Função do controle básico do time do futebol de robôs da Universidade Federal de São Carlos - USFCar, e possui como objetivo ir até um alvo específico
@Autor:     	RED DRAGONS UFSCAR - Divisão controle e estratégia
@Membros:		Alexandre Dias Negretti
				Carlos Basali
				George Frisanco Maneta
				Marcos Augusto Faglioni Junior 
				Natália dos Santos Andrade
				Vinicius Ancheschi Strini
"""
import math
from math import pi
import numpy as np
import random
import cv2
import time  
#Caso não exista os arquivos do V-rep, remover a importação do vrep, mas não será possível simular       
import vrep              

"""
Função:  serialEscreverPorta
Objetivo: Caso seja encaminhado um comando para a porta serial, e este possa ser executado, essa função encaminhará o código para a porta serial
    # ser - Configurações da porta serial
    # comando - Dado de formato string que contém o dado a ser enviado
    # Gleyson - Variável bolleana que libera ou não a escrita na porta serial
Retorno:
    # Sem retorno
"""
def serialEscreverPorta(ser, comando, Gleyson):
    if Gleyson:
        if (ser.isOpen()):
            #Realiza a tentativa de envio de dados
            try:
                ser.flushInput()
                ser.flushOutput()

                ser.write(comando)

            #Em caso de exception, exibe o erro
            except Exception, e:
                print ("ERRO: " + str(e))


"""
Função:	 Controle
Objetivo: Calcular a velocidade e sentido das rodas afim de guiaŕ o robô até o alvo dado; está função invoca o controle2 para já enviar os dados para o robô, seja no simulador ou em ambiente real
Parametros de entrada:
    # RD - vetor com 6 posições, sendo:
    [0] - Coordenada X do robô; [1] - Coordenada Y do robô; [2] - angulo do robô; [3] - KP (constante de controle);
    [4] - velocidade máxima;    [5] - Função do robo (0-goleiro; 1-zagueiro; 2-atacante); [6] - Código do robô (0 -> @; 1 -> &; 2 -> $)
	# alvo - Vetor de duas posição com as coordenadas (x,y) do alvo
	# ser - Configurações da porta serial
	# Gleyson - Variavel booleana responsável por ativar a escrita na porta serial 
    # Strini - Variavel booleana responsável por ativar a simulação
    !!!Strini e Gleyson são variveis exclusivas, assim, somente uma pode ser verdadeira por vez!!!
	# duasFaces - Variavel bolleana responsável por ativar as duas frentes do robô
    # debug - Faz, em tempo de execução, exibir dados relevantes no terminal
    # clientID - criado na main (caso Strini seja falso, fazer clientID = 0)

Retorno:
    # angulo_d - Variavel do tipo float, contendo o ângulo desejado

"""
def controle(RD, alvo, ser, Gleyson, Strini, duasFaces, debug, clientID):

    #Decompondo o vetor RD em angulo_r, que é o ângulo do robô; pos_x_r e pos_y_r, que é respectivamente a posição x e y do robô ;  
    angulo_r = RD[2]
    pos_x_r = RD[0]
    pos_y_r = RD[1]
    distanciaRodas = 4

    #Auxiliares para armazenar as velocidades em cada uma das rodas
    rodaR = 0
    rodaL = 0

    #informações do alvo
    pos_x_a = alvo[0]
    pos_y_a = alvo[1]

    #calculo do angulo desejado
    delta_x = pos_x_a - pos_x_r
    delta_y = pos_y_a - pos_y_r
    angulo_d = np.arctan2(delta_y,delta_x)    

    #calculo do erro do angulo
    angulo_e = angulo_d - angulo_r

    #normalizar angulo
    if (angulo_e > pi):
        angulo_e = angulo_e - 2*pi;
    elif (angulo_e < -pi):
        angulo_e = angulo_e + 2*pi;

    #flag responsável por determinar se o ângulo foi invertido
    flagInverteuTheta = False

    #Verifica a possibilidade do robo andar de ré, caso seja mais facil atingir o angulo desejado dessa forma
    if(duasFaces):
        if(angulo_e > pi/2):
            flagInverteuTheta = True
            angulo_e = angulo_e - pi 

        elif(angulo_e < -pi/2):
            flagInverteuTheta = True
            angulo_e = angulo_e + pi 

    #calculo da distancia absoluta do robo para o alvo
    distRA = math.sqrt((pos_x_r - pos_x_a)**2 + (pos_y_r - pos_y_a)**2)
    
    #caso a distância menor que X, o robo para
    if(distRA <= 3.5):
        rodaL = 0
        rodaR = 0
        sentidoL = 0
        sentidoR = 0
    #caso a distância seja maior que X, executa a lógica de encaminhar os dados
    else: 
        if(distRA > 20):
            Vlinear = RD[4]
        elif(distRA <= 20 and distRA >10):
            Vlinear = RD[4] * 0.8
        else:
            Vlinear = RD[4] * 0.7

        # lógica de 2 faces
        if (flagInverteuTheta):
            Vlinear = -Vlinear;
        
    	#distribuição das velocidades em cada uma das rodas 
        VL = Vlinear - distanciaRodas * RD[3] * angulo_e
        VR = Vlinear + distanciaRodas * RD[3] * angulo_e

        #Definindo o sentido das rodas, enquanto a velocidade for positiva, sentido sera igual a 1, caso a velocidade seja negativa, sentido recebe 0
        if(VL < 0):
            VL = -VL
            sentidoL = 0
        else:
            sentidoL = 1

        if(VR < 0):
            VR = -VR
            sentidoR = 0
        else:
            sentidoR = 1

        #verificação de qual a velocidade máxima entre as duas
        maxV = max(VL, VR)

        #se o maxV for maior que a velocidade permitida pela eletrônica do robô, é realizado uma proporcional para converter as velocidades correntes em velocidades possíveis de serem enviadas para o robô
        if (maxV > RD[4]):
            constSat = RD[4]/maxV
            VL = VL * constSat
            VR = VR * constSat

        #Caso a velocidade das rodas estejam fora do range possível, mesmo após a conversão, o sistema mandará 0 para a roda, afim de evitar possíveis danos
        if(VL >= -RD[4] and VL <= RD[4]):
            rodaL = round(VL)
        else:
            rodaL = 0
            if (debug):
                print ("Roda L fora do range permitido")
        if(VR >= -RD[4] and VR <= RD[4]):
            rodaR = round(VR)
        else:
            rodaR = 0
            if (debug):
                print ("Roda R fora do range permitido")

    #chamada a função que envia o comando para o robô tanto na simulação como em ambiente real
    controle2(RD, ser, rodaL, rodaR, sentidoL, sentidoR, Gleyson, Strini, clientID, debug)

    #Dados que serão exibidos na tela em caso de debug
    if debug:
        print ("================== DEBUG ==================")
        print ("Posicao X: %f" % pos_x_r)
        print ("Posicao Y: %f" % pos_y_r)
        print ("Posicao do alvo X: %f" % pos_x_a)
        print ("Posicao do alvo Y: %f" % pos_y_a)
        print ('Distancia entre robô e alvo: %f' % distRA)
        print ("Velocidade roda esquerda: %d" % rodaL)
        print ("Velocidade roda direita : %d" % rodaR)
        print ("Sentido roda esquerda: %d" % sentidoL)
        print ("Sentido roda direita : %d" % sentidoR)
        anguloaux = RD[2]*180/pi
        print ("Angulo: %.2f rad" % RD[2])
        print ("Angulo: %.2fº" % anguloaux)
        anguloaux = angulo_e*180/pi
        print ("Angulo e: %.2f rad" % angulo_e)
        print ("Angulo e: %.2fº" % anguloaux)
        anguloaux = angulo_d*180/pi
        print ("Angulo d: %.2f rad" % angulo_d)
        print ("Angulo d: %.2fº" % anguloaux)
        print ("============== END DEBUG ==================")
    
    #Retorno do ângulo desejado para a visão poder exibir uma animação
    return angulo_d, flagInverteuTheta

"""
Função:  Controle2
Objetivo: Enviar dados via serial (se Gleyson for verdadeiro) ou para o simulador V-rep (se Strini for verdadeiro) de informações diretas, que não necessitam de tratamento algum
Parametros de entrada:
    # RD - vetor com 6 posições, sendo:
    [0] - Coordenada X do robô; [1] - Coordenada Y do robô; [2] - angulo do robô; [3] - KP (constante de controle);
    [4] - velocidade máxima;    [5] - Função do robo (0-goleiro; 1-zagueiro; 2-atacante); [6] - Código do robô (0 -> @; 1 -> &; 2 -> $)
    # ser - Configurações da porta serial
    # rodaL - Velocidade da roda esquerda
    # rodaR - Velocidade da roda direita
    # sentidoL - Sentido da roda esquerda (1 para frente e 0 para trás)
    # sentidoR - Sentido da roda direita (1 para frente e 0 para trás)
    # Gleyson - Variavel booleana responsável por ativar a escrita na porta serial (Strini e Gleyson são variveis exclusivas, assim, somente uma pode ser verdadeira por vez)
    # Strini - Variavel booleana responsável por ativar a simulação (Strini e Gleyson são variveis exclusivas, assim, somente uma pode ser verdadeira por vez)
    # clientID - parâmetro necessário para o funcionamento do v-rep, criado na main (caso Strini seja falso, fazer clientID = 0)
    # debug - Faz, em tempo de execução, exibir dados relevantes no terminal
    
Retorno:
    Sem retorno
"""
def controle2(RD, ser, rodaL, rodaR, sentidoL, sentidoR, Gleyson, Strini, clientID, debug):

    #Caso o Xbee esteja conectado, o comando será construido e encaminhado para a porta serial    
    if Gleyson:
        #Construção do comando no formato em que a eletrônica aceita (formato código_do_robô)
        comandorobo1 = "%d,%.4d,%d,%.4d" % (sentidoL, rodaL, sentidoR, rodaR)
        
        #Determina qual robô receberá o comando
        if (RD[6] == 0):
            serialEscreverPorta(ser, '@' + comandorobo1 + '#', Gleyson)
            #if debug:
                #print ("Robo @")
        if (RD[6] == 1):
            serialEscreverPorta(ser, '&' + comandorobo1 + '#', Gleyson)
            #if debug:
                #print ("Robo &")
        if (RD[6] == 2):
            serialEscreverPorta(ser, '!' + comandorobo1 + '#', Gleyson)
            #if debug:
                #print ("Robo !")

    #Caso o Xbee não esteja conectado e se deseja utilizar o V-rep para simular
    if Strini:
        #Definição dos parâmetros necessários para o envio da informação para o V-rep
        if (RD[6] == 0):
            errorCode,left_motor_handle = vrep.simxGetObjectHandle(clientID,'MotorEsquerdoRobo1',vrep.simx_opmode_blocking)
            if debug:
                if errorCode == 0:
                    print ("Sem erro")
                else:
                    print ("Erro na criação do parametro para o MotorEsquerdoRobo1: %d" % errorCode)

            errorCode,right_motor_handle = vrep.simxGetObjectHandle(clientID,'MotorDireitoRobo1',vrep.simx_opmode_blocking)
            if debug:
                if errorCode == 0:
                    print ("Sem erro")
                else:
                    print ("Erro na criação do parametro para o MotorDireitoRobo1: %d" % errorCode)

        if (RD[6] == 1):
            errorCode,left_motor_handle = vrep.simxGetObjectHandle(clientID,'MotorEsquerdoRobo2',vrep.simx_opmode_blocking)
            if debug:
                if errorCode == 0:
                    print ("Sem erro")
                else:
                    print ("Erro na criação do parametro para o MotorEsquerdoRobo2: %d" % errorCode)

            errorCode,right_motor_handle = vrep.simxGetObjectHandle(clientID,'MotorDireitoRobo2',vrep.simx_opmode_blocking)
            if debug:
                if errorCode == 0:
                    print ("Sem erro")
                else:
                    print ("Erro na criação do parametro para o MotorDireitoRobo2: %d" % errorCode)

        if (RD[6] == 2):
            errorCode,left_motor_handle = vrep.simxGetObjectHandle(clientID,'MotorEsquerdoRobo3',vrep.simx_opmode_blocking)
            if debug:
                if errorCode == 0:
                    print ("Sem erro")
                else:
                    print ("Erro na criação do parametro para o MotorEsquerdoRobo3: %d" % errorCode)

            errorCode,right_motor_handle = vrep.simxGetObjectHandle(clientID,'MotorDireitoRobo3',vrep.simx_opmode_blocking)
            if debug:
                if errorCode == 0:
                    print ("Sem erro")
                else:
                    print ("Erro na criação do parametro para o MotorDireitoRobo3: %d" % errorCode)

        #O V-rep aceita valores negativos para as rodas, portanto, retorna-se o sentido como sendo o sinal da velocidade
        if sentidoL == 0:
            rodaL = -rodaL
        
        if sentidoR == 0:
            rodaR = -rodaR

        #Envio do código para o V-rep
        errorCode = vrep.simxSetJointTargetVelocity(clientID,left_motor_handle,rodaL,vrep.simx_opmode_streaming)
        if debug:
            if errorCode == 0:
                print ("Sem erro")
            else:
                print ("Erro ao enviar comando para o motor esquerdo: %d" % errorCode)
            
        errorCode = vrep.simxSetJointTargetVelocity(clientID,right_motor_handle,rodaR,vrep.simx_opmode_streaming)
        if debug:
            if errorCode == 0:
                print ("Sem erro")
            else:
                print ("Erro ao enviar comando para o motor direito: %d" % errorCode)

    return 0,0
