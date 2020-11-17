import os
import csv
import numpy as np
import pandas as pd
from GaussianAnalyse import readOutput, readOptimizedGeom

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


def writeGaussianInput(filename, title, atom_data, ncores, method, basis_set, keywords, charge, multiplicity):
    """This function writes a single gaussian input file
    based on the data from the PDB file and
    some additional gaussian-related info."""
    
    with open(filename, 'w') as file:
        file.write(f'%nprocshared={ncores} \n')
        file.write(f'%chk={filename.replace("com", "chk")} \n')
        file.write(f'# {method}/{basis_set} {keywords} \n\n')
        file.write(f'Title - {title} \n\n')
        file.write(f'{charge} {multiplicity} \n')
        file.writelines(atom_data)
        file.write('\n')
        
    return


def generateGaussianInput(pdb_filenames, gaussian_input_names, gaussian_titles, 
                          ncores='6', method='b3pw91', basis_set="6-31g(d')", 
                          keywords='empiricaldispersion=gd3', charge='2', multiplicity='1'):
    """This function generates gaussian input files corresponding
    to every PDB file that is found in the directory tree"""

    if len(pdb_filenames) > 0:
    
        print(f'Writing {len(gaussian_titles)} gaussian input files using {ncores} CPU core(s), \
    {method}/{basis_set} level of theory, {keywords}, charge={charge} and multiplicity={multiplicity}.\n\n')
        for pdbname, inputname, title in zip(pdb_filenames, gaussian_input_names, gaussian_titles):
            atom_data = readPDB(pdbname)
            writeGaussianInput(inputname, title, atom_data, ncores=ncores, method=method, 
                            basis_set=basis_set, keywords=keywords, charge=charge, multiplicity=multiplicity)
            
        print('Done! \n')

    else:
        print('No pdb files were found! \n')


def generateGaussianOpt(energy_stats_filename='energy.csv', conformations_to_optimize=1, opt_keywords='opt', file_prefix='run_opt', title_addition='', keep_geometry=True):
    """Generates N geometry optimization input files with the lowest energy.
    The function uses energy stats csv file from GaussianAnalyse.py.
    It is implied that for every single point energy calculation output file 'run.log'
    there is a 'run.com' input file. The function generates the geometry optimization
    input file with the same geometry but with added keyword 'opt'.
    
    keep_geometry=True: keep the same geometry as in the original input file

    keep_geometry=False: read optimized geometry from the output file, write
    it into the new input file
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
                # Read charge and multiplicity data:
                for line in lines:
                    numbers = 0
                    for element in line.split():
                        if element.replace('-', '').isnumeric():
                            numbers += 1
                            if numbers == 2:
                                charge_multiplicity_data = line

        except NameError:
            print(f'File {original_input} does not exist')

        if keep_geometry:
            with open(opt_filename, 'w') as file_opt:
                for line in lines:
                    if '#' in line:
                        file_opt.write(line.replace('\n', '') + opt_keywords + '\n')
                    elif 'Title' in line:
                        file_opt.write(line.replace('\n', '') + title_addition + '\n')
                    else:
                        file_opt.write(line)
        
        if not keep_geometry:
            optimized_geometry_file = readOutput(output_filename)
            optimized_geometry = readOptimizedGeom(optimized_geometry_file)

            percent_section_written = False
            hashtag_section_written = False
            title_section_written = False
            charge_multiplicity_section_written = False

            with open(opt_filename, 'w') as file_opt:
                for line in lines:
                    if '%' in line:
                        file_opt.write(line)
                        percent_section_written = True
                    elif '#' in line:
                        file_opt.write(line.replace('\n', '') + opt_keywords + '\n')
                        hashtag_section_written = True
                    elif 'Title' in line:
                        file_opt.write(line.replace('\n', '') + title_addition + '\n')
                        title_section_written = True

                if (percent_section_written and hashtag_section_written and title_section_written and not charge_multiplicity_section_written):
                    file_opt.write(charge_multiplicity_data)
                    file_opt.write('\n')
                    charge_multiplicity_section_written = True
                
                elif (percent_section_written and hashtag_section_written and title_section_written and charge_multiplicity_section_written):
                    for geometry_line in optimized_geometry:
                        for element in geometry_line:
                            file_opt.write(str(element))
                            file_opt.write(' ')
                        file_opt.write('\n')
                    
    print('Done! \n')

    
    return

    

