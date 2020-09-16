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