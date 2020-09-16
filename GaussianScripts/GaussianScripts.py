import os
import csv

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
        

def generateGaussianOpt()


    return

    

# This function finds all the gaussian output files in the
# directory tree

def findGaussianOutput(rootdir='.'):

    output_filenames = []
    
    dir_counter = -1 # do not include the root dir

    file_counter = 0

    # Loop through all directories and files in the root directory
    for subdir, dirs, files in os.walk(rootdir):
        dir_counter += 1
        # Loop over all files
        for file in files:
            if '.log' in file:
                file_counter += 1
                output_file = os.path.join(subdir, file)
                output_filenames.append(output_file)
                
    print(f'Found {file_counter} gaussian output files in {dir_counter} directories...\n')
    
    return(output_filenames)


# This function reads the file and makes sure that the 
# run has ended normally. It returns contents of the output
# file for further analysis

def readOutput(filename):
    lines = ''
    with open(filename, 'r') as file:
        lines = file.readlines()
    assert 'Normal termination' in lines[-1], f'Error termination in {filename}. \n'

    return(lines)


# Collects performance statistics from one output file

def performanceStats(file):
    try:
        file
    except NameError:
        print(f'Could not read performance stats. \n')

    for line in file:
        if 'processors via shared memory' in line:
            ncores = line.split()[4]
            assert ncores.isnumeric(), 'It is not possible to read the number of processors. Check the format of the output. \n'
        
        if 'Elapsed time' in line:
            days = line.split()[2]
            hours = line.split()[4]
            minutes = line.split()[6]
            seconds = line.split()[8]
            assert days.replace('.', '', 1).isnumeric(), 'It is not possible to read the number of days. Check the format of the output. \n'
            assert hours.replace('.', '', 1).isnumeric(), 'It is not possible to read the number of hours. Check the format of the output. \n'
            assert minutes.replace('.', '', 1).isnumeric(), 'It is not possible to read the number of minutes. Check the format of the output. \n'
            assert seconds.replace('.', '', 1).isnumeric(), 'It is not possible to read the number of seconds. Check the format of the output. \n'

            elapsed_time = float(days) * 12 + float(hours) + float(minutes) / 60 + float(seconds) / 3600 # total time in hours
            
    
    return(ncores, elapsed_time)


# Collects performance statistics for all output files and write a csv table

def writePerformanceStats(output_filenames, csv_name='performance.csv'):

    print(f'Collecting performance stats and writing them to {csv_name} \n')

    with open(csv_name, 'w', newline='') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=' ')

        file_writer.writerow(['Output filename', 'Number of CPU cores', 'Elapsed time (hours)', 'Core-h'])

        for filename in output_filenames:
            output = readOutput(filename)
            ncores, elapsed_time = performanceStats(output)

            file_writer.writerow([filename, ncores, round(elapsed_time, 4), round(int(ncores) * elapsed_time, 4)])

    print('Done! \n')
    
    return


# Collects information about energy from one output file

def energyStats(file):
    try:
        file
    except NameError:
        print(f'Could not read energy stats. \n')

    for line in file:
        if 'SCF Done' in line:
            scf_energy = line.split()[4]
            assert scf_energy.replace('.', '', 1).replace('-', '', 1).isnumeric(), 'It is not possible to read the SCF energy. Check the format of the output. \n'

    return(scf_energy)


# Collects energy information for all output files and write a csv table

def writeEnergyStats(output_filenames, csv_name='energy.csv'):

    print(f'Collecting energy information and writing them to {csv_name} \n')

    with open(csv_name, 'w', newline='') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=' ')

        file_writer.writerow(['# Total number of output files = ', len(output_filenames)])
        file_writer.writerow(['# Output filename', 'SCF energy, Hartree'])

        for filename in output_filenames:
            output = readOutput(filename)
            scf_energy = energyStats(output)

            file_writer.writerow([filename, scf_energy])

    print('Done! \n')
    
    return







    
