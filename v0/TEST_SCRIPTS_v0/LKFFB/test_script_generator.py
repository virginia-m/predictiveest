import sys
import os

test_case = int(sys.argv[1])
variation = int(sys.argv[2])
var_f0_ = float(sys.argv[3])
var_J_ = int(sys.argv[4])
var_multiplier_ = float(sys.argv[5])
var_n_train_ = int(sys.argv[6])
var_n_predict_ = int(sys.argv[7])
var_alpha_ = float(sys.argv[8])
var_msmt_noise_level_ = float(sys.argv[9])
filepath = sys.argv[10]

######################################
# Need to var r, f0, J, msmt_noise_level and alpha depending on parameter regimes
# Too tedious to do via command line
# Need a way to look up parameters based on test case and variation
########################################
var_p_ = -1
########################################

import numpy as np
from analysis_tools.riskanalysis import Create_KF_Experiment
from analysis_tools.plot_BR import Plot_BR_Results
from analysis_tools.plot_KF import Plot_KF_Results
import kf.fast_2 as skf
import kf.detailed as dkf


########################
# File Data
########################
filename0_ = 'test_case_'+str(test_case)+'_var_'+str(variation)
savetopath_ = filepath

########################
# Bayes Risk Parameters
########################
max_it_BR_ = 50
num_randparams_ = 75
space_size_ = np.arange(-8,3)
truncation_ = 20
bayes_params_ = [max_it_BR_, num_randparams_, space_size_,truncation_]

########################
# Experiment Parameters
########################
n_train_ = var_n_train_
n_predict_ = var_n_predict_
n_testbefore_ = 50
multiplier_ = var_multiplier_
bandwidth_ = 50.0

exp_params_ = [n_train_, n_predict_, n_testbefore_, multiplier_, bandwidth_]

########################
# Truth Parameters
########################
apriori_f_mean_ = 0.0 
alpha_ = var_alpha_
f0_ = var_f0_
p_ = var_p_ #1 #-2 #-1 #0.0
J_ = var_J_
jstart_ = 1 # (not zero)
pdf_type_u_ = 'Uniform'
      
true_noise_params_ = [apriori_f_mean_, pdf_type_u_, alpha_, f0_, p_, J_, jstart_]

########################
# Measurement Noise 
########################
msmt_noise_mean_ = 0.0 
msmt_noise_level_ = var_msmt_noise_level_

msmt_noise_params_ = [msmt_noise_mean_, msmt_noise_level_]

########################
# Kalman Parameters
########################
p0_ = 10000.0 
x0_ = 1.0
optimal_sigma_ = 0.1
optimal_R_ = 0.1
b_delta_ = 0.5 

max_it_ = 100

kalman_params_ = [optimal_sigma_, optimal_R_, x0_, p0_, b_delta_]

########################
# Skip Msmts
########################
skip =1

########################
# Max Forecast Step for Bayes Risk
########################

max_forecast_step = n_predict_

################
# Calculations
################

Test_Object = Create_KF_Experiment(bayes_params_, filename0_, savetopath_, max_it_, exp_params_, kalman_params_, msmt_noise_params_, true_noise_params_, user_defined_variance=None)

Test_Object.naive_implementation()

filename_and_path_BR = os.path.join(savetopath_, str(Test_Object.filename_BR)+'.npz')
plotter_BR = Plot_BR_Results(filename_and_path_BR)
plotter_BR.load_data()
Test_Object.get_tuned_params(int(max_forecast_step))
Test_Object.set_tuned_params()

truth, data = Test_Object.generate_data_from_truth(None)
np.savez(os.path.join(savetopath_, str(Test_Object.filename_KF)+'_skip_msmts_Truth'), truth=truth, noisydata=data)

for skip in [1, 2, 3, 4, 5, 10, 16]:
    filename_skippy = os.path.join(savetopath_, str(Test_Object.filename_KF)+'_skipmsmts_'+str(skip))
    Test_Object.ensemble_avg_predictions(skip)
    pred_skf = skf.kf_2017(data, n_train_, n_testbefore_, n_predict_, Test_Object.Delta_T_Sampling, x0_, p0_, Test_Object.optimal_sigma, Test_Object.optimal_R, Test_Object.basisA, phase_correction=0 ,prediction_method="PropForward", skip_msmts=skip, descriptor=filename_skippy+'SKF') 
    pred_dkf, amps_dkf = dkf.detailed_kf(filename_skippy+'DKF', data, n_train_, n_testbefore_, n_predict_, Test_Object.Delta_T_Sampling, x0_,p0_, Test_Object.optimal_sigma, Test_Object.optimal_R, Test_Object.basisA, 0.0, skip_msmts=skip)
    