#### BACKGROUND

The purpose of this repo is to make public algorithmic code associated with the research publication:

_Gupta, R.S. and Biercuk, M.J., 2018. Machine learning for predictive estimation of qubit dynamics subject to dephasing. Physical Review Applied, 9(6), p.064042._

This repo is intended to provide visibility of core algorithms in a research publication. The theoretical algorithm design decisions are justified in the research publication. 
It is possible to code all algorithms based on the research publication alone, and parameter regime information has been provided to reproduce all reported data figures. 

In addition to the publication above, we publish Python packages associated with the paper. Each Python package was designed to support evolving research needs, and hence, software not been designed with the objective to efficiently deploy core algorithms by non-authors (third parties.) Many Python objects were developed to support data generation, data management, specific research questions, and error handling. 

For ease of reference, the following Python modules directly link to algorithms reported in the paper:

    LSF : ls.LSF_risk_analysis
    LKFFB : kf.fast_2 (light LKFFB), kf.detailed (full LKFFB)
    AKF : akf.armakf
    QKF : qif.qif
    GPR : Implemented via GPy. See also: gpr.GPRP_risk_analysis.
For questions regarding the publication and supporting code, please contact me at riddhi.sw@gmail.com.

#### SELECTED PYTHON PACKAGES
**akf**: The purpose of akf package is to implement autoregressive Kalman Filtering (AKF) 

**analysis_tools**: The purpose of analysis_tools is to optimise and generate analysis for Livska
Kalman Filter on experimental scenarios indexed by (test_case, variation). 

**data_tools**: The purpose of data_tools is to load data and analyse data generated by any algorithm (LKFFB, AKF, LSF, GPR) for any scenario (test_case, variation) for linear measurement models

**gpr**: The purpose of gpr is to implement Gaussian Process Regression (GPR) using GPy.
At present, the kernel being testing is the Periodic Kernel.

**kf**: The purpose of kf package is to implement Livska Kalman Filtering (KF) for linear measurement records

**ls** The purpose of ls package is to return LSF Predictions using a modified version of Virginia Frey and Sandeep Mavadia's LS Filter (statePredictions.py)

**qif**: The purpose of qif package is to implement Quantised Kalman Filtering (QKF) using AKF dynamics and single shot qubit outcomes.

#### REFERENCES: 

Please see full reference list in the publication above.
