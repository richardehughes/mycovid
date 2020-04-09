import numpy as np
def running_mean(x, N):
	cumsum = np.cumsum(np.insert(x, 0, 0)) 
	return (cumsum[N:] - cumsum[:-N]) / N

x = [0,1,2,2,2,3,3,3,4,4,4,5,5,5]
print(running_mean(x,3))


