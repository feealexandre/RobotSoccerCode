# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 19:42:28 2017

@author: geo
"""

import numpy as np
import time
import math

from estrategias import estrategia

# Importações do Vrep
import sys
import vrep
from controlevrep import *
pi = math.pi


# =========================[  Variaveis do controle]===========================
ser = 0
Gleyson = False
Strini = not Gleyson
duasFaces = True
trocouCampo = False
debug = True

# =========================[ VARIÁVEIS DE AJUSTE]==============================
ang_corr = pi/4 

#======[Distancia entre as cruzetas]======
constX = 1     # Campo novo
constY = 1     # Campo novo

#=====[Definições da visao do vrep]=========
angulo_d = np.zeros([3])
robot = np.zeros([3,3])     # Alocação de espaço para matriz robot: [ ] 
bola = np.zeros([3])         # Alocação de espaço para o vetor bola: [ ]

MAroboHandle = np.zeros([3])
MFHandle = np.zeros([3])



vrep.simxFinish(-1) # just in case, close all opened connections
clientID=vrep.simxStart('127.0.0.1',19999,True,True,5000,5) # Connect to V-REP

if clientID!=-1:
    print ('Connected to remote API server')
    
else:   
    print('Connection not successful')
    sys.exit('Could not connect')



#=======[LOOP PRINCIPAL]=========

while (1):
    

    startv = time.time()        # Começa a contar o tempo para o desempenho da visão    
    
    robot, bola = visaovrep(clientID, ang_corr)

    angulo_d = estrategia(robot, bola, ser, constX, constY, Gleyson, Strini, duasFaces, trocouCampo, debug, clientID)
    
    endv = time.time()      #Encerra contagem de tempo do loop da visão
    
    ## ANÁLISE DE DESEMPENHO =============================================
    total_time = 1000*(endv-startv)
    #print(total_time)
