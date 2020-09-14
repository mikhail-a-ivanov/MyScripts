from GaussianAnalyseFunctions import findGaussianOutput, writePerformanceStats

output_filenames = findGaussianOutput()

writePerformanceStats(output_filenames, csv_name='performance.csv')