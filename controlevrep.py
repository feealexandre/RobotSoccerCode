# -*- coding: utf-8 -*-

import vrep
import numpy as np
import time
import math
from estrategias import estrategia
import sys

pi = math.pi
    
#estrategia(robot, bola, ser, frame, constX, constY, Gleyson, debug, clientID)

def visaovrep(clientID,ang_corr):
    
    MA = np.zeros([3,3])
    MF = np.zeros([3,3])
    robot = np.zeros([3,3])
    
    
    #PEGA OS IDENTIFICADORES
    
    errorCode,bola_handle = vrep.simxGetObjectHandle(clientID,'Bola',vrep.simx_opmode_blocking)
    
    #VETOR DE IDENTIFICADORES DOS MARCADORES AZUIS
    errorCode,MAroboHandle0 = vrep.simxGetObjectHandle(clientID,'marcadorAzulRobo1',vrep.simx_opmode_blocking)
    errorCode,MAroboHandle1 = vrep.simxGetObjectHandle(clientID,'marcadorAzulRobo2',vrep.simx_opmode_blocking)
    errorCode,MAroboHandle2 = vrep.simxGetObjectHandle(clientID,'marcadorAzulRobo3',vrep.simx_opmode_blocking)
    
    #VETOR DE IDENTIFICADORES DOS MARCADORES DE CADA ROBO
    errorCode,MFHandle0 = vrep.simxGetObjectHandle(clientID,'marcadorVerde',vrep.simx_opmode_blocking)
    errorCode,MFHandle1 = vrep.simxGetObjectHandle(clientID,'marcadorVermelho',vrep.simx_opmode_blocking)
    errorCode,MFHandle2 = vrep.simxGetObjectHandle(clientID,'marcadorRosa',vrep.simx_opmode_blocking)

    errorCode,bola = vrep.simxGetObjectPosition(clientID,bola_handle,-1,vrep.simx_opmode_streaming)
    
    errorCode,MA[0] = vrep.simxGetObjectPosition(clientID,MAroboHandle0,-1,vrep.simx_opmode_streaming)
    errorCode,MA[1] = vrep.simxGetObjectPosition(clientID,MAroboHandle1,-1,vrep.simx_opmode_streaming)
    errorCode,MA[2] = vrep.simxGetObjectPosition(clientID,MAroboHandle2,-1,vrep.simx_opmode_streaming)
    
    errorCode,MF[0] = vrep.simxGetObjectPosition(clientID,MFHandle0,-1,vrep.simx_opmode_streaming)
    errorCode,MF[1] = vrep.simxGetObjectPosition(clientID,MFHandle1,-1,vrep.simx_opmode_streaming)
    errorCode,MF[2] = vrep.simxGetObjectPosition(clientID,MFHandle2,-1,vrep.simx_opmode_streaming)
    
    time.sleep(0.03)

    errorCode,bola = vrep.simxGetObjectPosition(clientID,bola_handle,-1,vrep.simx_opmode_buffer)
    
    errorCode,MA[0] = vrep.simxGetObjectPosition(clientID,MAroboHandle0,-1,vrep.simx_opmode_buffer)
    errorCode,MA[1] = vrep.simxGetObjectPosition(clientID,MAroboHandle1,-1,vrep.simx_opmode_buffer)
    errorCode,MA[2] = vrep.simxGetObjectPosition(clientID,MAroboHandle2,-1,vrep.simx_opmode_buffer)
    
    errorCode,MF[0] = vrep.simxGetObjectPosition(clientID,MFHandle0,-1,vrep.simx_opmode_buffer)
    errorCode,MF[1] = vrep.simxGetObjectPosition(clientID,MFHandle1,-1,vrep.simx_opmode_buffer)
    errorCode,MF[2] = vrep.simxGetObjectPosition(clientID,MFHandle2,-1,vrep.simx_opmode_buffer)
    
    #Conversão da bola de metros por centimetros
    bola[0] = 100*bola[0]
    bola[1] = 100*bola[1]


    for i in range(3):
        
        dx = MA[i,0] - MF[i,0]
        dy = MA[i,1] - MF[i,1]
        
        #Conversão de centimetros para metros (multiplicação por 100); (MA[i,0] + MF[i,0])/2 para o centro em x do robô
        cx = 100*(MA[i,0] + MF[i,0])/2
        cy = 100*(MA[i,1] + MF[i,1])/2

        angulo = np.arctan2(dy,dx) + ang_corr
        
        # CORREÇÃO DA DESCONTINUIDADE DO ANGULO PARA O CONTROLE
        if (angulo >= -pi and angulo <= pi):
            pass
        elif (angulo > pi):
            angulo = angulo - 2*pi
            
        else:
            print("NÂO CUIDADO!!!!!!!!!!!!!!!!!!!!!!!!!")           # Avisa sobre a ocorrência de uma condição não prevista na correção do ângulo
        
        robot[i] = [cx,cy,angulo]
        
    
    return robot, bola
