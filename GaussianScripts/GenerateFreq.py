from GaussianAnalyse import findGaussianOutput
from GaussianInputGen import continueFreq

output_filenames = findGaussianOutput()

continueFreq(output_filenames, freq_keywords='geom=allcheck guess=read freq Temperature=4 Pressure=0.000001')