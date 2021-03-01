import os
import csv
import numpy as np
import pandas as pd

def findGaussianOutput(rootdir='.'):
    """This function finds all the gaussian output files in the directory tree"""

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


def readOutput(filename):
    """This function reads the file and makes sure that the
    run has ended normally. It returns contents of the output
    file for further analysis"""

    lines = ''
    with open(filename, 'r') as file:
        lines = file.readlines()
    assert 'Normal termination' in lines[-1], f'Error termination in {filename}. \n'

    return(lines)

def checkOutput(filename):
    """This function checks whether the job has been
    finished successfully."""

    lines = ''
    with open(filename, 'r') as file:
        lines = file.readlines()

    if 'Normal termination' in lines[-1]:
        return True
    
    else:
        return False


def performanceStats(file):
    """Collects performance statistics from one output file"""

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


def writePerformanceStats(output_filenames, csv_name='performance.csv'):
    """Collects performance statistics for all output files and write a csv table"""

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


def energyStats(file):
    """Collects information about energy from one output file"""
    try:
        file
    except NameError:
        print(f'Could not read energy stats. \n')

    for line in file:
        if 'SCF Done' in line:
            scf_energy = line.split()[4]
            assert scf_energy.replace('.', '', 1).replace('-', '', 1).isnumeric(), 'It is not possible to read the SCF energy. Check the format of the output. \n'

    return(scf_energy)


def writeEnergyStats(output_filenames, csv_name='energy.csv'):
    """Collects energy information for all output files and write a csv table"""

    print(f'Collecting energy information and writing them to {csv_name} \n')

    with open(csv_name, 'w', newline='') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=' ')

        file_writer.writerow(['# Output filename', 'SCF energy, Hartree'])

        for filename in output_filenames:
            output = readOutput(filename)
            scf_energy = energyStats(output)

            file_writer.writerow([filename, scf_energy])

    print('Done! \n')
    
    return


def readOptimizedGeom(file):
    """This function reads the optimized geometry from an output file"""

    try:
        file
    except NameError:
        print(f'Could not read optimized geometry. \n')

    lines = file
     
    header_rows = 4
    geometry_columns = 6
    optimization_completed_index = 0
    optimized_geometry_starting_index = 0

    count_atoms = True
    optimization_completed = False

    optimized_geometry = []
            
    for count, line in enumerate(lines, start=1):
        if "NAtoms" in line and count_atoms == True:
            try:
                NAtoms = int(line.split()[1])
            except ValueError:
                print(f'Could not convert {NAtoms} to integer!')
            count_atoms = False
            print(f'Number of atoms = {NAtoms}')
        if "Optimization completed." in line:
            optimization_completed_index = count
            print(f'Optimization completed (line {optimization_completed_index}).')
            optimization_completed = True

    if optimization_completed:
        for count, line in enumerate(lines[optimization_completed_index:], start=1):
            if "Standard orientation" in line:
                optimized_geometry_starting_index = count + optimization_completed_index
                print(f'Found optimized geometry starting at line {optimized_geometry_starting_index}.')

        start_read_optimized_geometry = optimized_geometry_starting_index + header_rows
        end_read_optimized_geometry = start_read_optimized_geometry + NAtoms

        for line in lines[start_read_optimized_geometry:end_read_optimized_geometry]:
            line = line.split()
            assert len(line) == geometry_columns, 'Unexpected geometry format!'
            for index, element in enumerate(line[0:3]):
                try:
                    line[index] = int(element)
                except ValueError:
                    print(f'Could not convert {element} to an integer!')
                    
            for index, element in enumerate(line[3:6], start=3):
                try:
                    line[index] = float(element)
                except ValueError:
                    print(f'Could not convert {element} to a float!')

            # Format the geometry lines:
            del(line[0])
            del(line[1])

            # Element index
            line[0] = '{:<4d}'.format(line[0])
            # Cartesian coordinates
            line[1] = '{:.8f}'.format(line[1])
            line[2] = '{:.8f}'.format(line[2])
            line[3] = '{:.8f}'.format(line[3])
                    
            optimized_geometry.append(f' {line[0]} {line[1]} {line[2]} {line[3]} \n')

        assert len(optimized_geometry) == NAtoms, 'Read wrong number of atoms'
        print('Optimized geometry saved.\n')

    else:
        print('Optimization is incomplete.')

    return(optimized_geometry)
            