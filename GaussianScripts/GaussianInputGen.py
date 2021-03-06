import os
import csv
import numpy as np
import pandas as pd
from GaussianAnalyse import readOutput, readOptimizedGeom, checkOutput

def generateInputNamesFromPDB(rootdir='.', file_prefix='run'):
    """This function generates a list of gaussian input names, titles 
    and names from the original pdb files and their relative paths.
    Rootdir argument is the directory from which the directory tree search starts."""

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


def readPDB(filename):
    """This function reads a single PDB file and extracts all the useful data
    for the gaussian input file"""

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


def writeGaussianInput(filename, title, atom_data, mem, ncores, gpu, method, basis_set, keywords, charge, multiplicity):
    """This function writes a single gaussian input file
    based on the data from the geometry file and
    some additional gaussian-related info."""
    
    with open(filename, 'w') as file:
        file.write(f'%mem={mem}gb \n')
        file.write(f'%cpu={range(int(ncores))[0]}-{range(int(ncores))[-1]} \n')
        if gpu:
            file.write(f'%gpucpu=0=0 \n') # dummy %gpucpu directive for Kebnekaise gpu runs
        file.write(f'%chk={filename.replace("com", "chk")} \n')
        file.write(f'# {method}/{basis_set} {keywords} \n\n')
        file.write(f'Title - {title} \n\n')
        file.write(f'{charge} {multiplicity} \n')
        file.writelines(atom_data)
        file.write('\n')
        
    return


def generateGaussianInputfromPDB(pdb_filenames, gaussian_input_names, gaussian_titles, 
                          mem=12, ncores='6', gpu=False, method='b3pw91', basis_set="6-31g(d')", 
                          keywords='empiricaldispersion=gd3', charge='2', multiplicity='1'):
    """This function generates gaussian input files corresponding
    to every PDB file that is found in the directory tree"""

    if len(pdb_filenames) > 0:
    
        print(f'Writing {len(gaussian_titles)} gaussian input files using {ncores} CPU core(s), \
    {method}/{basis_set} level of theory, {keywords}, charge={charge} and multiplicity={multiplicity}.\n\n')
        for pdbname, inputname, title in zip(pdb_filenames, gaussian_input_names, gaussian_titles):
            atom_data = readPDB(pdbname)
            writeGaussianInput(inputname, title, atom_data, mem=mem, ncores=ncores, gpu=gpu, method=method, 
                            basis_set=basis_set, keywords=keywords, charge=charge, multiplicity=multiplicity)
            
        print('Done! \n')

    else:
        print('No pdb files were found! \n')


def generateGaussianOptFromSP(energy_stats_filename='energy.csv', conformations_to_optimize=1, opt_keywords='opt', file_prefix='run_opt'):
    """Generates N geometry optimization input files with the lowest energy.
    The function uses energy stats csv file from GaussianAnalyse.py.
    It is implied that for every single point energy calculation output file 'run.log'
    there is a 'run.com' input file. The function generates the geometry optimization
    input file with the same geometry but with added keyword 'opt'.
    """

    print(f'Reading {energy_stats_filename}... \n')

    energy_stats = pd.read_csv(energy_stats_filename, delimiter=' ').sort_values('SCF energy, Hartree')
    selected_output_filenames = energy_stats.iloc[:, 0][:conformations_to_optimize].tolist()
    assert selected_output_filenames != [], 'Could not find any confirmations to optimize!'

    print(f'Generating geometry optimization files of {conformations_to_optimize} conformations with the lowest energy... \n')

    for i in range(len(selected_output_filenames)):
        output_filename = selected_output_filenames[i]
        original_input = output_filename.replace('.log', '.com')
        opt_filename = f'{file_prefix}-{i + 1}.com'

        try:
            with open(original_input, 'r') as file_input:
                lines = file_input.readlines()
        except NameError:
            print(f'File {original_input} does not exist')

        with open(opt_filename, 'w') as file_opt:
            for line in lines:
                if '#' in line:
                    file_opt.write(line.replace('\n', '') + opt_keywords + '\n\n')
                elif 'Title' in line:
                    file_opt.write(line.replace('\n', '') + 'Optimization' + '\n\n')
                else:
                    file_opt.write(line)
                 
    print('Done! \n')

    return


def generateGaussianOpt(energy_stats_filename='energy.csv', conformations_to_optimize=1, file_prefix='run_opt', mem=12, ncores='6', gpu=False,
                        method='b3pw91', basis_set="6-31g(d')", keywords='empiricaldispersion=gd3', title='', charge='2', multiplicity='1'):
    """Generates N geometry optimization input files with the lowest energy.
    The function uses energy stats csv file from GaussianAnalyse.py.
    Geometry data is read from previous geometry optimization output file.
    """

    print(f'Reading {energy_stats_filename}... \n')

    energy_stats = pd.read_csv(energy_stats_filename, delimiter=' ').sort_values('SCF energy, Hartree')
    selected_output_filenames = energy_stats.iloc[:, 0][:conformations_to_optimize].tolist()
    assert selected_output_filenames != [], 'Could not find any confirmations to optimize!'

    print(f'Generating geometry optimization files of {conformations_to_optimize} conformations with the lowest energy... \n')

    for i in range(len(selected_output_filenames)):
        output_filename = selected_output_filenames[i]
        opt_filename = f'{file_prefix}-{i + 1}.com'

        optimized_geometry_file = readOutput(output_filename)
        print(f'Reading optimized geometry from {output_filename}')
        optimized_geometry = readOptimizedGeom(optimized_geometry_file)

        title = f'Optimized geometry is taken from {output_filename}'
        writeGaussianInput(opt_filename, title, optimized_geometry, mem, ncores, gpu, method, basis_set, keywords, charge, multiplicity)

    print('Done! \n')

    return


def continueFreq(output_filenames, freq_keywords='geom=allcheck guess=read freq Temperature=4 Pressure=0.000001'):
    """Takes optimization job input files and continues freq job
    using geometry from the chk file."""

    print(f'Checking {len(output_filenames)} output files... \n')

    incomplete_job_indices = []

    for i in range(len(output_filenames)):
        if not checkOutput(output_filenames[i]):
            incomplete_job_indices.append(i)
            print(f'{output_filenames[i].replace("./", "").replace(".log", "")} job has not finished succesfully.')

    filtered_output_filenames = [output_filenames[i] for i in range(len(output_filenames)) if i not in incomplete_job_indices]


    input_filenames = [filtered_output_filenames[i].replace('.log', '.com') for i in range(len(filtered_output_filenames))]
    new_input_filenames = [input_filenames[i].replace('./', '').replace('.com', '_freq.com') for i in range(len(input_filenames))]

    print(f'\nWriting {len(input_filenames)} input files for frequency calculations... \n')

    for input_file_index in range(len(input_filenames)):
        lines = ''
        with open(input_filenames[input_file_index], 'r') as file1:
            lines = file1.readlines()

        with open(new_input_filenames[input_file_index], 'w') as file2:
            for line in lines:
                if '#' not in line:
                    file2.write(line)
                else:
                    file2.write(line.replace('opt', freq_keywords))
                    file2.write('\n')
                    break

    print('Done! \n')

    return

