import torch
from .models import MobileFaceNet, Backbone
from torchvision import transforms as trans
import os

import cv2
import numpy as np


class InsightFace:

    def __init__(self, use_mobilefacenet=True):
        self.input_size = (112, 112)

        self.embedding_size = 512

        self.use_mobilefacenet = use_mobilefacenet

        self.net_depth = 50

        self.drop_ratio = 0.6

        self.net_mode = 'ir_se'

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        self.prepare_transform = trans.Compose([
            trans.ToTensor(),
            trans.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])

        self.model = MobileFaceNet(self.embedding_size).to(self.device) \
            if self.use_mobilefacenet else Backbone(self.net_depth, self.drop_ratio, self.net_mode).to(self.device)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.model.load_state_dict(
            torch.load(os.path.join(BASE_DIR, "cfg", "mobilefacenet.pth"),map_location=self.device)
            if self.use_mobilefacenet else torch.load(os.path.join(BASE_DIR, "cfg", "model_ir_se50.pth"),map_location=self.device))

        self.model.eval()

    def predict(self,frame):
        if isinstance(frame,np.ndarray):
            frame=cv2.resize(frame,(112,112))
            frame=self.prepare_transform(frame)
        frame=frame.to(self.device)
        return self.model(frame)