from GaussianInputGenFunctions import generateInputNames, generateGaussianInput

# Generate list of filenames
pdb_filenames, gaussian_input_names = generateInputNames(rootdir='.')

# Generate gaussian input files
generateGaussianInput(pdb_filenames, gaussian_input_names, 
                          ncores='6', method='b3pw91', basis_set="6-31g(d')", 
                          keywords='empiricaldispersion=gd3', charge='2', multiplicity='1')