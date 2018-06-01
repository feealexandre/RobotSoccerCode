# -*- coding: utf-8 -*-

'''
Objetivo:      Possui a função estratégia que controla a chamada das funções executadas por cada jogador, a função do posicionamento inicial dos robos e a função de parar os robos
Data:          26/Outubro/2017
Autor:         RED DRAGONS UFSCAR - Divisão de Controle e Estratégia
Membros:        Alexandre Dias Negretti
                Carlos Basali
                George Maneta
                Marcos Augusto Faglioni Junior 
                Natália dos Santos Andrade
                Vinicius Ancheschi Strini
'''

from controle import *
from funcoescontrole import *
from math import pi
import numpy as np
import cv2
import vrep

"""
Função:  estrategia
Objetivo: A função estratégia recebe as coordenadas e os angulos dos robos e em cada linha da matriz inseri outros dados necessários para o controle do robô, como
o Kp de cada robô, a velocidade máxima de cada robô e o número da função de cada robô.

Parametros de entrada:

    # RD - matriz 3x3, sendo:
    [0,X] - Coordenada X do robô; [1,X] - Coordenada Y do robô; [2,X] - angulo do robô
    # bola - vetor de 2 posições, sendo:
    [0] - Coordenada X da bola; [1] - Coordenada Y da bola
    # ser - Porta serial (em caso de não haver comunicador conectado, passar 0)
    # constX e constY - Constantes para transformar pixels em metros
    # Gleyson - Variavel booleana responsável por ativar a escrita na porta serial
    # Strini - Variavel booleana responsável por ativar a simulação
    !!!Strini e Gleyson são variveis exclusivas, assim, somente uma pode ser verdadeira por vez!!!
    # duasFaces - Variavel booleana responsável por ativar as duas frentes do robô
    # trocouCampo - Variavel booleana responsável por informar qual o lado do campo que está o jogo corrente
    # debug - Faz, em tempo de execução, exibir dados relevantes no terminal
    # clientID - Criado na main (caso Strini seja falso, fazer clientID = 0)

Retorno:
    # angulo_d - Valor na forma de float indicando o angulo desejado que o robô deverá atingir
    # flagInverteuTheta - Variável booleana para identificar a mudança da referência do ângulo

"""

def estrategia(RD, bola, ser, constX, constY, Gleyson, Strini, duasFaces, trocouCampo, debug, clientID):

    #Criando a matriz para armazenar os dados extras de Kp, velocidade máxima, função do robo e código do robô
    dadosR = np.zeros([3, 7])

    #Criando o vetor para armazenar os ângulos desejados
    angulo_d = np.zeros([3])
    flagInverteuTheta = np.zeros([3])

    alvo = np.zeros([2])
    adv = False

    #0 posição X; 1 posição Y; 2 angulo; 3 KP; 4 velocidade máxima; 5 função do robo (0-goleiro; 1-zagueiro; 2-atacante); 6 código do robô (0-@; 1-&; 2-!)
    if (Strini):
        dadosR[0] = RD[0,0] * constX, RD[0,1] * constY, RD[0,2], 3, 20, 1, 0
        dadosR[1] = RD[1,0] * constX, RD[1,1] * constY, RD[1,2], 3, 20, 1, 1
        dadosR[2] = RD[2,0] * constX, RD[2,1] * constY, RD[2,2], 3, 20, 2, 2 
    else:
        dadosR[0] = RD[0,0] * constX, RD[0,1] * constY, RD[0,2], 18, 250, 1, 1
        dadosR[1] = RD[1,0] * constX, RD[1,1] * constY, RD[1,2], 18, 220, 1, 0
        dadosR[2] = RD[2,0] * constX, RD[2,1] * constY, RD[2,2], 20, 300, 2, 2 

    if(adv):
        dadosAD = np.zeros([3, 3])
        AD = np.zeros([3, 3])
        dadosAD[0] = AD[0,0] * constX, AD[0,1] * constY, AD[0,2]
        dadosAD[1] = AD[1,0] * constX, AD[1,1] * constY, AD[1,2]
        dadosAD[2] = AD[2,0] * constX, AD[2,1] * constY, AD[2,2]

    bola[0] = bola[0] * constX
    bola[1] = bola[1] * constY

    #angulo_d[1], flagInverteuTheta[1] = zagueiro(dadosR[1], bola, ser, Gleyson, Strini, duasFaces, trocouCampo, debug, clientID)

    #angulo_d[0], flagInverteuTheta[0] = goleiro(dadosR[0], bola, ser, Gleyson, Strini, duasFaces, trocouCampo, debug, clientID)

    angulo_d[2], flagInverteuTheta[2] = atacante(dadosR[2], bola, ser, Gleyson, Strini, duasFaces, trocouCampo, debug, clientID)




    return angulo_d, flagInverteuTheta


"""
Função:  parada
Objetivo: A função parada tem objetivo de enviar aos robôs a velocidade zero para todas as rodas, parando o robô.

Parametros de entrada:

    # RD -  matriz 3x3, sendo:
    [0,X] - Coordenada X do robô; [1,X] - Coordenada Y do robô; [2,X] - angulo do robô
    # bola - vetor de 2 posições, sendo:
    [0] - Coordenada X da bola; [1] - Coordenada Y da bola
    # ser -  Porta serial (em caso de não haver comunicador conectado, passar 0)
    # constX e constY - Constantes para transformar pixels em metros
    # Gleyson - Variavel booleana responsável por ativar a escrita na porta serial
    # Strini - Variavel booleana responsável por ativar a simulação
    !!!Strini e Gleyson são variveis exclusivas, assim, somente uma pode ser verdadeira por vez!!!
    # duasFaces - Variavel booleana responsável por ativar as duas frentes do robô
    # trocouCampo - Variavel booleana responsável por informar qual o lado do campo que está o jogo corrente
    # debug - Faz, em tempo de execução, exibir dados relevantes no terminal
    # clientID - Criado na main (caso Strini seja falso, fazer clientID = 0)

Retorno:
    Sem retorno
"""

def parada(RD, bola, ser, constX, constY, Gleyson, Strini, duasFaces, trocouCampo, debug, clientID):
    #dadosR - 0 posição X do robô; 1 posição Y do robô; 2 angulo do robô; 3 KP; 4 velocidade máxima; 5 função do robo (0-goleiro; 1-zagueiro; 2-atacante); 6 código do robô (0-@; 1-&; 2-!)
    dadosR = np.zeros([3, 7])
     #0 posição X; 1 posição Y; 2 angulo; 3 KP; 4 velocidade máxima; 5 função do robo (0-goleiro; 1-zagueiro; 2-atacante); 6 código do robô (0-@; 1-&; 2-!)
    if (Strini):
        dadosR[0] = RD[0,0] * constX, RD[0,1] * constY, RD[0,2], 2.5, 10, 1, 0
        dadosR[1] = RD[1,0] * constX, RD[1,1] * constY, RD[1,2], 2.5, 10, 1, 1
        dadosR[2] = RD[2,0] * constX, RD[2,1] * constY, RD[2,2], 2.5, 10, 2, 2 
    else:
        dadosR[0] = RD[0,0] * constX, RD[0,1] * constY, RD[0,2], 18, 300, 1, 1
        dadosR[1] = RD[1,0] * constX, RD[1,1] * constY, RD[1,2], 18, 300, 1, 0
        dadosR[2] = RD[2,0] * constX, RD[2,1] * constY, RD[2,2], 18, 300, 2, 2 

    controle2(dadosR[0], ser, 0, 0, 0, 0, Gleyson, Strini, clientID, debug)
    controle2(dadosR[1], ser, 0, 0, 0, 0, Gleyson, Strini, clientID, debug)
    controle2(dadosR[2], ser, 0, 0, 0, 0, Gleyson, Strini, clientID, debug)


"""
Função:  posicaoInicial
Objetivo: Tem a função de posicionar os robôs até as respectivas posições iniciais do jogo

Parametros de entrada:
    # RD - matriz 3x3, sendo:
    [0,X] - Coordenada X do robô; [1,X] - Coordenada Y do robô; [2,X] - angulo do robô
    # bola - vetor de 2 posições, sendo:
    [0] - Coordenada X da bola; [1] - Coordenada Y da bola
    # ser - Porta serial (em caso de não haver comunicador conectado, passar 0)
    # constX e constY - Constantes para transformar pixels em metros
    # Gleyson - Variavel booleana responsável por ativar a escrita na porta serial
    # Strini - Variavel booleana responsável por ativar a simulação
    !!!Strini e Gleyson são variveis exclusivas, assim, somente uma pode ser verdadeira por vez!!!
    # duasFaces - Variavel booleana responsável por ativar as duas frentes do robô
    # trocouCampo - Variavel booleana responsável por informar qual o lado do campo que está o jogo corrente
    # debug - Faz, em tempo de execução, exibir dados relevantes no terminal
    # clientID - Criado na main (caso Strini seja falso, fazer clientID = 0)

Retorno:
    Sem retorno
"""

def posicaoInicial(RD, bola, ser, constX, constY, Gleyson, Strini, duasFaces, trocouCampo, bolaNossa, debug, clientID):
    #dadosR - 0 posição X do robô; 1 posição Y do robô; 2 angulo do robô; 3 KP; 4 velocidade máxima; 5 função do robo (0-goleiro; 1-zagueiro; 2-atacante); 6 código do robô (0-@; 1-&; 2-!)
    dadosR = np.zeros([3, 7])
    alvoR1 = np.zeros([3])
    alvoR2 = np.zeros([3])
    alvoR3 = np.zeros([3])


     #0 posição X; 1 posição Y; 2 angulo; 3 KP; 4 velocidade máxima; 5 função do robo (0-goleiro; 1-zagueiro; 2-atacante); 6 código do robô (0-@; 1-&; 2-!)
    if (Strini):
        dadosR[0] = RD[0,0] * constX, RD[0,1] * constY, RD[0,2], 2.5, 10, 1, 0
        dadosR[1] = RD[1,0] * constX, RD[1,1] * constY, RD[1,2], 2.5, 10, 1, 1
        dadosR[2] = RD[2,0] * constX, RD[2,1] * constY, RD[2,2], 2.5, 10, 2, 2 
    else:
        dadosR[0] = RD[0,0] * constX, RD[0,1] * constY, RD[0,2], 18, 200, 1, 1
        dadosR[1] = RD[1,0] * constX, RD[1,1] * constY, RD[1,2], 18, 200, 1, 0
        dadosR[2] = RD[2,0] * constX, RD[2,1] * constY, RD[2,2], 18, 200, 2, 2


        
    if trocouCampo and (bolaNossa == 1):
        print ("aki1")
        alvoR1 = [150,65]
        alvoR2 = [115,75]
        alvoR3 = [95,55]

    elif ((not trocouCampo) and (bolaNossa == 1)):
        print ("aki2")
        alvoR1 = [15,65]
        alvoR2 = [60,75]
        alvoR3 = [75,55]
    
    elif (trocouCampo and (bolaNossa == 0)):
        print ("aki3")
        alvoR1 = [150,65]
        alvoR2 = [115,75]
        alvoR3 = [115,55]

    elif ((not trocouCampo) and (bolaNossa == 0)):
        print ("aki4")
        alvoR1 = [15,65]
        alvoR2 = [60,75]
        alvoR3 = [60,55]
    

    controle(dadosR[0], alvoR1, ser, Gleyson, Strini, duasFaces, debug, clientID)
    controle(dadosR[1], alvoR2, ser, Gleyson, Strini, duasFaces, debug, clientID)
    controle(dadosR[2], alvoR3, ser, Gleyson, Strini, duasFaces, debug, clientID)
