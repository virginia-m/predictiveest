'''
The purpose of this code is to return covariance matrices based on a choice of kernel.
All code has two copies with identical functionality, written in:
    Tensor Flow - for training. 
    Numpy - for predictions. 
Functions for Tensor Flow are suffixed by _tf in the function name.

Kernel: "RQ"
            params[0] = sig_f -- variance multipler of stochastic process
            params[1] = l -- length scale
            params[2] = alpha -- scale mixture parameter
            
        Kernel: "RBF"
            params[0] = sig_f -- variance multipler of stochastic process
            params[1] = l -- length scale
            
        Kernel: "PER"
            params[0] = sig_f -- variance multipler of stochastic process
            params[1] = l -- length scale
            params[2] = p -- fundamental periodicity
            
        Kernel: "MAT" NOT DONE
            params[0] =  sig_f
            params[1] =  l
            params[2] = p -- order, s.t. we model AR(p) process
'''

import numpy as np
from gprtf.kernellist import * 
import tensorflow as tf # run script using pythonsys alias in command line


KER_NAME = {'RQ': rq ,'RBF': rbf, 'PER': periodic, 'MAT': None}
KER_NAME_TF = {'RQ': rq_tf ,'RBF': rbf_tf, 'PER': periodic_tf, 'MAT': None}



#### IN NUMPY ####

def ker_matrix(kernel_name, hyp_params, R, x, length):
    '''
    Returns covariance matrix based on kernel choice,kernel hyper
    parameters, measurment noise and inputs:

    ARGS:
        kernel_name: One of [RQ, RBF, PER, MAT]
        hyp_params: Hyper parameters associated with kernel
        R: Measurement noise covariance strength
        x: Inputs, s.t. v == |x_i - x_j| for some i, j in length(x)
    
    Returns k: k[i,j] == R(v) + R*I, where I == identity
    '''
    k = KER_NAME[kernel_name](x, hyp_params) + R*np.diag(np.ones([length]))
    return k

#### IN TENSORFLOW ####

def ker_matrix_tf(kernel_name, hyp_params, R, x, length):
	# generate kernel matrix by tensor
    k = KER_NAME_TF[kernel_name](x, hyp_params)  + R*tf.diag(tf.ones([length]))
    return k