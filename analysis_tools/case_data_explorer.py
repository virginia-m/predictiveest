# The purpose of this script is to replace plot_KF and plot_BR in analysis_tools
# Then one can commence plotting with less hassle. 
# All parameter uploads will be done atuomatically with reference to 
# test_case and variation numbers alone.


from __future__ import division, print_function, absolute_import
import numpy as np
from analysis_tools.common import get_tuned_params_, truncate_losses_, analyse_loss
from analysis_tools.experiment import Experiment
from analysis_tools.truth import Truth
import sys
import os
import kf.fast_2 as Kalman
from kf.common import calc_inst_params

from kf.armakf import autokf as akf 

sys.path.append("../") # look in the parent directory containing both kf and analysis_tools packages

basis_list = ['A', 'B', 'C'] 
prediction_method_list =["ZeroGain", "PropForward"]
count_steps_DICT = {'A': 0, 'B': 2, 'C': 4}
FUDGE = 0.5
HILBERT_TRANSFORM = 2.0

class CaseExplorer(Experiment,Truth):

    def __init__(self, test_case, variation, skip,
                 max_forecast_loss, path_to_directory,
                 Hard_load='No', SKF_load='No', 
                 AKF_load='Yes', LS_load = 'Yes'):

        self.test_case = test_case
        self.variation = variation
        self.AKF_load = AKF_load
        self.LS_load = LS_load

        self.path_to_directory = path_to_directory

        self.savetopath = self.path_to_directory +'/test_case_'+str(self.test_case)+'/'
        self.filename0 = 'test_case_'+str(self.test_case)+'_var_'+str(self.variation)
        self.filename_BR = self.filename0+str('BR_Map')
        self.filename_and_path_BR = os.path.join(self.savetopath, str(self.filename_BR)+'.npz')
        self.filename_kf= self.filename0+'_kfresults'
        self.filename_skippy = os.path.join(self.savetopath, str(self.filename_kf)+'_skipmsmts_'+str(skip))
        self.filename_SKF = self.filename_skippy+str('SKF.npz')
        self.filename_Truth = os.path.join(self.savetopath, self.filename_kf+'_skip_msmts_Truth.npz')

        data = np.load(self.filename_and_path_BR)

        self.msmt_noise_variance = data['msmt_noise_variance']
        self.msmt_noise_params = data['msmt_noise_params'] # Duplicated in KF Results
        self.true_noise_params_= [0.0] + [x for x in data['true_noise_params']] # this confusing but now unavoidable
        self.expt_params_ = data['expt_params'] # Duplicated in KF Results
        self.macro_prediction_errors = data['macro_prediction_errors']
        self.macro_forecastng_errors = data['macro_forecastng_errors']
        self.num_randparams = data['num_randparams']
        self.random_hyperparams_list = data['random_hyperparams_list']
        self.kalman_params = data['kalman_params'] # Duplicated in KF Results
        self.macro_truth = data['macro_truth'] 
        self.max_it_BR = data['max_it_BR']

        self.truncation = 20
        self.max_forecast_loss = max_forecast_loss
        self.lowest_pred_BR_pair = None
        self.lowest_fore_BR_pair = None
        self.means_list_ = None

        Experiment.__init__(self, self.expt_params_)
        Truth.__init__(self, self.true_noise_params_) # this confusing but now unavoidable

        data = np.load(self.filename_skippy+'.npz' )
        self.KF_Predictions_Matrix = data['KF_Predictions_Matrix']
        self.Predict_Zero_Means = data['Predict_Zero_Means']
        self.KF_Error_Means = data['KF_Error_Means']
        self.Normalised_Means = data['Normalised_Means']
        self.skip_msmts = data['skip_msmts']

        data = np.load(self.filename_SKF)
        self.freq_basis_array = data['freq_basis_array']
        self.instantA= data['instantA']
        self.predictions = data['predictions']

        data = np.load(self.filename_Truth)
        self.msmts = data['noisydata']
        self.truth =  data['truth']
        
        if AKF_load != 'No':

            data = np.load(self.path_to_directory +'LS_Ensemble_Folder/'+self.filename0+'_BR_AKF_MAP.npz' )
            self.akf_lowest_pred_BR_pair = None
            self.akf_lowest_fore_BR_pair = None
            self.akf_means_lists_ = None
            self.akf_macro_prediction_errors = data['akf_macro_prediction_errors']
            self.akf_macro_forecastng_errors = data['akf_macro_forecastng_errors']
            self.akf_weights = data['weights']
            
            pass

        
        if LS_load != 'No':

            data = np.load(self.path_to_directory +'LS_Ensemble_Folder/'+self.filename0+'_LS_Ensemble.npz' )
            self.ls_macro_weights = data['macro_weights']
            self.n_start_at = data['n_start_at']
            
            pass
        


        if Hard_load !='No':
            
            data = np.load(self.filename_and_path_BR)
            self.user_defined_variance = data['user_defined_variance'] # Duplicated in KF Results       
            self.spacesize = data['spacesize']
            self.max_it = data['max_it']
            self.skip_msmts = data['skip_msmts']
            self.true_signal_params = data['true_signal_params'] # Duplicated in KF Results
                 

            data = np.load(self.filename_skippy+'.npz' )
            self.max_it = data['max_it']
            self.chosen_params = data['chosen_params']
            self.optimal_R = data['optimal_R']
            self.optimal_sigma = data['optimal_sigma']
            self.truth_datasets = data['truth_datasets']
            self.max_run = self.truth_datasets.shape[1]    

        
        if SKF_load != 'No':

            data = np.load(self.filename_SKF)
            self.phase_correction = data['phase_correction']
            self.P_hat = data['P_hat']
            self.instantP = data['instantP']
            self.x_hat = data['x_hat']
            # self.n_predict = data['n_predict']
            # self.rk = data['rk']
            # self.y_signal = data['y_signal']
            # self.skip_msmts = data['skip_msmts']
            # self.n_train = data['n_train']
            # self.Q = data['Q']
            # self.S = data['S']
            # self.W = data['W']
            # self.a = data['a']
            # self.n_testbefore = data['n_testbefore']
            # self.h = data['h']
            # self.oe = data['oe']
            # self.descriptor = data['descriptor']
            # self.e_z = data['e_z']
            # self.z = data['z' ]
            # self.store_S_Outer_W = data['store_S_Outer_W']
            # self.Propagate_Foward = data['Propagate_Foward']
            
        pass


    def generate_ordered_losses(self, truncation=20):
        """ Generates a list of (sigma, R) pairs from lowest to highest mean prediction 
        and forecasting losses, as well as optimal (sigma, R) for each type of loss"""


        self.means_lists_, self.lowest_pred_BR_pair, self.lowest_fore_BR_pair = get_tuned_params_(self.max_forecast_loss,
                                                                                                np.array(self.num_randparams), 
                                                                                                np.array(self.macro_prediction_errors), 
                                                                                                np.array(self.macro_forecastng_errors),
                                                                                                np.array(self.random_hyperparams_list),
                                                                                                truncation)

        if self.AKF_load != 'No':
            self.akf_means_lists_, self.akf_lowest_pred_BR_pair, self.akf_lowest_fore_BR_pair = get_tuned_params_(self.max_forecast_loss,
                                                                                                np.array(self.num_randparams), 
                                                                                                np.array(self.akf_macro_prediction_errors), 
                                                                                                np.array(self.akf_macro_forecastng_errors),
                                                                                                np.array(self.random_hyperparams_list),
                                                                                                truncation)            
        pass


    def return_low_loss_hyperparams_list(self, truncation_=20):
        '''Returns optimisation data for KF and AKF
        '''

        self.generate_ordered_losses(truncation=truncation_)

        if self.AKF_load == 'No':
            return analyse_loss(self.means_lists_, self.random_hyperparams_list)

        elif self.AKF_load != 'No':
            kf_loss_analysis = analyse_loss(self.means_lists_, self.random_hyperparams_list)
            akf_loss_analysis = analyse_loss(self.akf_means_lists_, self.random_hyperparams_list)
            
            return kf_loss_analysis, akf_loss_analysis



    def count_steps(self, Basis='A'):
        """Returns the maximal number of steps forward for which KF is better
        than predicting the noise mean."""

        counter =0
        basis_index = count_steps_DICT[Basis]
        for x in self.Normalised_Means[basis_index, self.n_testbefore:]:
            if x > 1:
                break
            counter +=1
        return counter


    def return_fourier_amps(self, freq_basis_array=None, instantA=None):
        """ Returns Kalman estimates of amplitudes in one run and theoretical PSD"""

        self.beta_z_truePSD()

        if (freq_basis_array == None) and (instantA == None):
            freq_basis_array = self.freq_basis_array 
            instantA = self.instantA

        x_data = [2.0*np.pi*freq_basis_array, self.true_w_axis[self.J -1:]]

        kalman_amps = (instantA**2)*(2*np.pi)*FUDGE
        theory_PSD = HILBERT_TRANSFORM*self.true_S_twosided[self.J -1:]

        norm_kalman_amps = kalman_amps*(1.0/ self.true_S_norm)
        norm_theory_PSD = theory_PSD*(1.0/ self.true_S_norm)

        y_data = [norm_kalman_amps, norm_theory_PSD]

        return x_data, y_data, self.true_S_norm


    def return_SKF_skip_msmts(self, y_signal, newSKFfile, method): # delete newSKFfile

        oe = self.lowest_pred_BR_pair[0] # Optimally tuned
        rk = self.lowest_pred_BR_pair[1] # Optimally tuned
        x0 = self.kalman_params[2]
        p0 = self.kalman_params[3]
        bdelta = self.kalman_params[4]

        freq_basis_array = np.arange(0.0, self.bandwidth, bdelta)

        predictions, x_hat = Kalman.kf_2017(y_signal, self.n_train, self.n_testbefore, self.n_predict, 
                             self.Delta_T_Sampling, x0, p0, oe, rk, freq_basis_array, 
                             phase_correction=0 ,prediction_method=method, 
                             skip_msmts=1, switch_off_save='Yes')

        x_hat_slice = x_hat[:,:, self.n_train]
        instantA, instantP = calc_inst_params(x_hat_slice)

        x_data, y_data, self.true_S_norm = self.return_fourier_amps(freq_basis_array=freq_basis_array, 
                                                                    instantA=instantA)
        return x_data, y_data, self.true_S_norm, predictions # this has theory and KF data


    def return_AKF(self, y_signal):

        from analysis_tools.common import calc_AR_PSD 

        oe = self.akf_lowest_pred_BR_pair[0] # Optimally tuned
        rk = self.akf_lowest_pred_BR_pair[1] # Optimally tuned
        weights = self.akf_weights
        order = weights.shape[0]

        akf_pred = akf('AKF', y_signal, weights, oe, rk, n_train=self.n_train, n_testbefore=self.n_testbefore, 
           n_predict=self.n_predict, p0=self.kalman_params[3], skip_msmts=1,  switch_off_save='Yes')
        
        akf_x, akf_y = calc_AR_PSD(weights, oe, self.Delta_S_Sampling, self.Delta_T_Sampling)
        akf_y_norm = akf_y*1.0/self.true_S_norm

        print('Total coeff', np.sum(akf_y), np.sum(akf_y_norm))

        return akf_x, akf_y, akf_y_norm, akf_pred 

    
    def return_LS(self, y_signal):

        from analysis_tools.common import calc_AR_PSD
        import sys
        sys.path.append(self.path_to_directory+'LS_Ensemble_Folder/')
        import statePredictions as sp

        weights = np.mean(self.ls_macro_weights[:,:,:,0],  axis=0) # Dims: ensemble x stpsfwd x pastmsmts x 1
        n_predict = weights.shape[0]
        order = weights.shape[1]

        predictions = np.zeros(n_predict)

        for idx_steps in range(0, n_predict, 1):

            validation_data = sp.build_training_dataset(y_signal, 
                                                    past_msmts=order,
                                                    steps_forward=idx_steps, # testing data for n-step ahead
                                                    steps_between_msmts=1)
            
            past_measurements = validation_data[:,1:]
            actual_values = validation_data[:,0]
            predictions[idx_steps] = sp.get_predictions(weights[idx_steps,:], past_measurements)[self.n_start_at] # prediction post n_train at idx_steps ahead

        return predictions