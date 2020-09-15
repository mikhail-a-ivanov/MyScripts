import os

# This function generates a list of gaussian input names and titles as well as extracts
# the names of original pdb files and their relative paths.
# Rootdir argument is the directory from which the directory tree search starts

def generateInputNames(rootdir='.', file_prefix='run'):

    rootdir_length = len(rootdir) + 1 # length of the root directory plus '/' sign

    gaussian_titles = []
    gaussian_input_names = []
    pdb_filenames = []
    
    dir_counter = -1 # do not include the root dir
    file_counter = 0

    # Loop through all directories and files in the root directory
    for subdir, dirs, files in os.walk(rootdir):
        dir_counter += 1
        # Loop over all files
        for file in files:
            if '.pdb' in file:
                file_counter += 1
                pdb_file = os.path.join(subdir, file)
                pdb_filenames.append(pdb_file)

                title = os.path.join(subdir, file)[rootdir_length:].replace('/', '_').replace('.pdb','')
                gaussian_titles.append(f'{title}-{file_prefix}-{file_counter}')
                gaussian_input_names.append(f'{file_prefix}-{file_counter}.com')
                
    print(f'Found {file_counter} pdb files in {dir_counter} directories...\n')
    
    return(pdb_filenames, gaussian_input_names, gaussian_titles)

# This function reads a single PDB file and extracts all the useful data
# for the gaussian input file

def readPDB(filename):

    atom_data = []

    with open(filename, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if 'ATOM' in line:
                atomname = line.split()[-1]
                pdbname = line.split()[2]
                resname = line.split()[3]
                resnum = line.split()[4]
                X = '{:.8f}'.format(float(line.split()[5]))
                Y = '{:.8f}'.format(float(line.split()[6]))
                Z = '{:.8f}'.format(float(line.split()[7]))

                atom_data.append(f' {atomname:}(PDBName={pdbname},ResName={resname},ResNum={resnum}) {X:>20} {Y:>20} {Z:>20} \n')
    
    return(atom_data)

# This function writes a single gaussian input file
# based on the data from the PDB file and
# some additional gaussian-related info

def writeGaussianInput(filename, title, atom_data, ncores, method, basis_set, keywords, charge, multiplicity):
    
    with open(filename, 'w') as file:
        file.write(f'%nprocshared={ncores} \n')
        file.write(f'%chk={filename.replace("com", "chk")} \n')
        file.write(f'# {method}/{basis_set} {keywords} \n\n')
        file.write(f'{title} \n\n')
        file.write(f'{charge} {multiplicity} \n')
        file.writelines(atom_data)
        file.write('\n')
        
    return

# This function generates gaussian input files corresponding
# to every PDB file that is found in the directory tree

def generateGaussianInput(pdb_filenames, gaussian_input_names, gaussian_titles, 
                          ncores='6', method='b3pw91', basis_set="6-31g(d')", 
                          keywords='empiricaldispersion=gd3', charge='2', multiplicity='1'):
    
    print(f'Writing {len(gaussian_titles)} gaussian input files using {ncores} CPU core(s), \
{method}/{basis_set} level of theory, {keywords}, charge={charge} and multiplicity={multiplicity}.\n\n')
    for pdbname, inputname, title in zip(pdb_filenames, gaussian_input_names, gaussian_titles):
        atom_data = readPDB(pdbname)
        writeGaussianInput(inputname, title, atom_data, ncores=ncores, method=method, 
                           basis_set=basis_set, keywords=keywords, charge=charge, multiplicity=multiplicity)
        
    print('Done! \n')
        
        
    return