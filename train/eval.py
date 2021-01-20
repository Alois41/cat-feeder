import torch
import torchvision
import torchvision.transforms as transforms
import cv2
import numpy as np
from PIL import Image

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

if __name__ == '__main__':
    model = torch.load("model_final.pt")
    model.eval()
    device = torch.device("cpu")
    with torch.no_grad():
        model = model.to(device)
        image = cv2.imread("last.jpg")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        tensor = preprocess(Image.fromarray(image)).unsqueeze(0).to(device)
        output = torch.nn.Softmax(dim=0)(model(tensor).squeeze())
        print(output)
