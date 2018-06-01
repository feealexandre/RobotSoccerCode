#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 20:50:41 2017

@author: geo
"""

import numpy as np

def loop_time(tempo):
    soma_tempo = np.sum(tempo)
    n_tempo = float(len(tempo))
    media = soma_tempo/n_tempo
    var = np.sum((media - tempo)**2)/(n_tempo)
    desv_pad = var**(1.0/2)
    return desv_pad,media


def detect_ball(frame_counter,frame_max,bola,bola_sumiu,percent,s):
    if np.sum(bola) == 0:
        bola_sumiu += 1
        
    if frame_counter == frame_max-s-1:
        percent = 100*(frame_max-s-1 - bola_sumiu) / (frame_max-s-1)
    
    return bola_sumiu,percent