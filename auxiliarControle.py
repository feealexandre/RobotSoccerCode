# -*- coding: utf-8 -*-
"""
@Data:          26/Outubro/2017
@Objetivo:      Funções de cada jogador do time, goleiro, zagueiro e atacante, além de funções de estratégia de jogo, como penalti, e um verificador para atigiu o alvo
@Autor:         RED DRAGONS UFSCAR - Divisão controle e estratégia
@Membros:       Alexandre Dias Negretti
                Carlos Basali
                George Maneta
                Marcos Augusto Faglioni Junior 
                Natália dos Santos Andrade
                Vinicius Ancheschi Strini
"""
from math import *
import numpy as np
from controle import *
import math


"""
Função:  atingiuAlvo
Objetivo: Verificar se o robô esta dentro de uma circunferência de raio erro com o centro no alvo

Parametros de entrada:
    # RD - Vetor de 6 posições, sendo:
    [0] - Coordenada X do robô; [1] - Coordenada Y do robô; [2] - angulo do robô; [3] - KP (constante de controle);
    [4] - velocidade máxima;    [5] - Função do robo (0-goleiro; 1-zagueiro; 2-atacante); [6] - Código do robô (0 -> @; 1 -> &; 2 -> $)
    # alvo - vetor de 2 posições, sendo:
    [0] - Coordenada X do alvo; [1] - Coordenada Y do alvo
    # erro - Valor em centimetros que representa o raio da circunferência com centro em alvo

Retorno:
    "True" ou "False"
    Variável booleana indicando se o robô está em um raio de erro centimetros do ponto desejado (verdadeiro se estiver no raio e falso caso contrário)

"""
def atingiuAlvo(RD, alvo, erro):
    temp = math.sqrt((alvo[0] - RD[0]) ** 2 + (alvo[1] - RD[1]) ** 2)
    return temp < erro

"""
Função:  atingiuAlvoY
Objetivo: Verificar se o robô esta dentro de uma circunferência de raio erro com o centro no alvo

Parametros de entrada:
    # RD - Vetor de 6 posições, sendo:
    [0] - Coordenada X do robô; [1] - Coordenada Y do robô; [2] - angulo do robô; [3] - KP (constante de controle);
    [4] - velocidade máxima;    [5] - Função do robo (0-goleiro; 1-zagueiro; 2-atacante); [6] - Código do robô (0 -> @; 1 -> &; 2 -> $)
    # alvo - vetor de 2 posições, sendo:
    [0] - Coordenada X do alvo; [1] - Coordenada Y do alvo
    # erro - Valor em centimetros que representa o raio da circunferência com centro em alvo

Retorno:
    "True" ou "False"
    Variável booleana indicando se o robô está em um raio de erro centimetros do ponto desejado (verdadeiro se estiver no raio e falso caso contrário)

"""
def atingiuAlvoY(RD, alvo, erro):
    temp = math.sqrt((alvo[1] - RD[1]) ** 2)
    return temp < erro

"""
Função:  atingiuAngulo
Objetivo: Verificar se o robô atingiu o angulo desejado, a menos de um erro

Parametros de entrada:
    # RD - Vetor de 6 posições, sendo:
    [0] - Coordenada X do robô; [1] - Coordenada Y do robô; [2] - angulo do robô; [3] - KP (constante de controle);
    [4] - velocidade máxima;    [5] - Função do robo (0-goleiro; 1-zagueiro; 2-atacante); [6] - Código do robô (0 -> @; 1 -> &; 2 -> $)
    # anguloDesejado - Ângulo desejado em radianos
    # erro - Valor em radianos que representa o erro máximo para ser considerado

Retorno:
    "True" ou "False"
    Variável booleana indicando se o robô está a menos de erro do ângulo desejado
"""
def atingiuAngulo(RD, anguloDesejado, erro):
    temp = math.sqrt((RD[2] - anguloDesejado) ** 2)
    return temp < erro

def calculaAngulo(origem, destino):
    #calculo do angulo desejado
    delta_x = origem[0] - destino[0]
    delta_y = origem[1] - destino[1]
    angulo = np.arctan2(delta_y,delta_x)

    return angulo

def distancia(pontoa, pontob):
    dist = math.sqrt((pontoa[0]-pontob[0])**2 + (pontoa[1]-pontob[1])**2)
    return dist

"""
Funções: estaNaBorda (Inferior, Superior, InferiorGolEsq, InferiorGolDir, SuperiorGolDir, SuperiorGolEsq)
Objetivo: Verificar se o robô esta na area em questão, considerando a distância perpendicular da borda analisada.

Parametros de entrada:
    # RD - Vetor de 6 posições, sendo:
    [0] - Coordenada X do robô; [1] - Coordenada Y do robô; [2] - angulo do robô; [3] - KP (constante de controle);
    [4] - velocidade máxima;    [5] - Função do robo (0-goleiro; 1-zagueiro; 2-atacante); [6] - Código do robô (0 -> @; 1 -> &; 2 -> $)
    # tamanhoBorda - Distância em centimetros que pode ser considerada para o robô "estar" na borda

Retorno:
    "True" ou "False"
    Variável booleana indicando se o robô está ou não na borda
"""

def estaNaBordaInferior(RD, tamanhoBorda):
    if(RD[1] > 130 - tamanhoBorda):
        return True
    else:
        return False

def estaNaBordaSuperior(RD, tamanhoBorda):
    if(RD[1] < tamanhoBorda):
        return True
    else:
        return False

def estaNaBordaInferiorGolEsq(RD, tamanhoBorda):
    if(RD[0] < tamanhoBorda and RD[1] > 85 and RD[1] < 130 - tamanhoBorda):
        return True
    else:
        return False

def estaNaBordaInferiorGolDir(RD, tamanhoBorda):
    if(RD[0] > 170 - tamanhoBorda and RD[1] > 85 and RD[1] < 130 - tamanhoBorda):
        return True
    else:
        return False

def estaNaBordaSuperiorGolEsq(RD, tamanhoBorda):
    if(RD[0] < tamanhoBorda and RD[1] < 45 and RD[1] > tamanhoBorda):
        return True
    else:
        return False

def estaNaBordaSuperiorGolDir(RD, tamanhoBorda):
    if(RD[0] > 170 - tamanhoBorda and RD[1] < 45 and RD[1] > tamanhoBorda):
        return True
    else:
        return False

def estaNaArea(ponto, trocouCampo):
    if trocouCampo:
        if(ponto[1] > 45 and ponto[1] < 85 and ponto[0] < 28):
            return True
        else:
            return False
    else:
        if(ponto[1] > 45 and ponto[1] < 85 and ponto[0] > 145):
            return True
        else:
            return False