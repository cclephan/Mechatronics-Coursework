import numpy as np
X = np.ones((9,1))
ADC_vals = np.array([[-71.2,-40.2],[-71.2,-1.5],[-71.2,36],[2.1,36],[2.1,-1.5],[2.1,-40.2],[79.8,-40.2],[79.8,-1.5],[79.8,36]])
X = np.append(ADC_vals,X,axis=1)
X_act = np.array([[-88,-50],[-88,0],[-88, 50],[0,50],[0,0],[0,-50],[88,-50],[88,0],[88,50]])
Y = np.matmul(np.transpose(X),X_act)
B = np.matmul(np.linalg.inv(np.matmul(np.transpose(X),X)),Y)
print(B)
