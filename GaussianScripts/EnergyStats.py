from GaussianAnalyse import findGaussianOutput, writePerformanceStats, writeEnergyStats

output_filenames = findGaussianOutput()

#writePerformanceStats(output_filenames, csv_name='performance.csv')

writeEnergyStats(output_filenames, csv_name='energy.csv')
