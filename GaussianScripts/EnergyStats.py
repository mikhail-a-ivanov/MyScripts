from GaussianAnalyse import findGaussianOutput, writePerformanceStats, writeEnergyStats

output_filenames = findGaussianOutput()

writeEnergyStats(output_filenames, csv_name='energy.csv')
