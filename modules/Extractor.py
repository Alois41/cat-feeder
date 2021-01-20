import torch
import torch.nn as nn
from torchvision import transforms
import ast

extractor = torch.hub.load('pytorch/vision', 'mobilenet_v2', pretrained=True)
custom_classifier = torch.load("./modules/model_final.pt", map_location=torch.device('cpu'))
extractor.eval()
custom_classifier.eval()

classifier_coarse = extractor.classifier

new_classifier = nn.Sequential(*list(extractor.classifier.children())[:-1])
extractor.classifier = new_classifier

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

file = open("../classes", "r")
contents = file. read()
classes = ast.literal_eval(contents)
