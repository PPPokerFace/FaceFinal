import numpy as np

import torch


a=np.array([[1,2,3],[3,4,5],[5,6,7]])

a=torch.from_numpy(a)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

b=a.to(device).to(device).to(device).to(device).to(device).to(device).to(device)

print(b.shape[0])