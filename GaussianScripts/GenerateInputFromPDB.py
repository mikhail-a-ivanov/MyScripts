from GaussianInputGen import generateInputNamesFromPDB, generateGaussianInputfromPDB

# Generate list of filenames
pdb_filenames, gaussian_input_names, gaussian_titles = generateInputNamesFromPDB(rootdir='.', file_prefix='GRGDS+2')

# Generate gaussian input files
generateGaussianInputfromPDB(pdb_filenames, gaussian_input_names, gaussian_titles, mem=12,
                          ncores='24', gpu=False, method='b3pw91', basis_set="6-31g(d')", 
                          keywords='empiricaldispersion=gd3', charge='2', multiplicity='1')
