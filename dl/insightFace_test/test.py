import sys
sys.path.append("..")
import torch
from torchvision import transforms as trans
from dl.insightFace.models import MobileFaceNet
import cv2

test_transform = trans.Compose([
    trans.ToTensor(),
    trans.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
])
input = cv2.imread("res.jpg")
input = cv2.resize(input, (112, 112))
input = test_transform(input)
net = MobileFaceNet(512)
net.load_state_dict(torch.load("../insightFace/cfg/mobilefacenet.pth", map_location='cpu'));
net.eval()
x = net(input.unsqueeze(0))
for i in x:
    i=i.detach().numpy()
    print(i)