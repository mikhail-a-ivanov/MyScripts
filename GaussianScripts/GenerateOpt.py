from GaussianInputGen import generateGaussianOpt

generateGaussianOpt(energy_stats_filename='energy.csv', conformations_to_optimize=1, file_prefix='run_opt', ncores='6', 
                        method='b3pw91', basis_set="6-31g(d')", keywords='empiricaldispersion=gd3', title='', charge='2', multiplicity='1')