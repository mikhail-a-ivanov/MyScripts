from GaussianInputGen import generateInputNamesFromPDB, generateGaussianInput

# Generate list of filenames
pdb_filenames, gaussian_input_names, gaussian_titles = generateInputNamesFromPDB(rootdir='.', file_prefix='GRGDS+2')

# Generate gaussian input files
generateGaussianInput(pdb_filenames, gaussian_input_names, gaussian_titles, 
                          ncores='24', method='b3pw91', basis_set="6-31g(d')", 
                          keywords='empiricaldispersion=gd3', charge='2', multiplicity='1')
