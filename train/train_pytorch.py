import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import freeze_support
import torch.optim as optim
from torch.utils.tensorboard import SummaryWriter
from sklearn.metrics import recall_score, precision_score, f1_score
from tqdm import tqdm
import torch.nn.functional as F



class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()

        self.cnn_layers = nn.Sequential(
            # Defining a 2D convolution layer
            nn.Conv2d(3, 16, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            # Defining another 2D convolution layer
            nn.Conv2d(16, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        self.linear_layers = nn.Sequential(
            nn.Linear(25088, 3)
        )

    # Defining the forward pass
    def forward(self, x):
        x = self.cnn_layers(x)
        x = x.view(x.size(0), -1)
        x = self.linear_layers(x)
        return x


preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ColorJitter(brightness=0.25, contrast=0.25),
    transforms.RandomAffine(degrees=15, fillcolor=(0, 0, 0), translate=(0.1, 0.1), shear=10, scale=(.5, 2)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def imshow(img):
    img = img / 2 + 0.5  # unnormalize
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()


if __name__ == '__main__':
    device = torch.device("cuda")
    writter = SummaryWriter()
    ds = torchvision.datasets.ImageFolder(root="../data", transform=preprocess)
    dl = torch.utils.data.DataLoader(ds, batch_size=64, shuffle=True, num_workers=0)

    # get some random training images
    dataiter = iter(dl)
    images, labels = dataiter.next()

    # show images
    grid = torchvision.utils.make_grid(images)
    writter.add_image("example batch", grid, 0)

    model = torch.hub.load('pytorch/vision', 'mobilenet_v2', pretrained=True)
    model.classifier[1] = nn.Linear(1280, 3)

    # model = Net()

    model.to(device)

    for param in [x for x in model.parameters()][:-10]:
        param.requires_grad = False

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

    for epoch in range(500):  # loop over the dataset multiple times

        running_loss = 0.0
        for i, data in tqdm(enumerate(dl, 0), total=len(dl), desc="epoch %i: " % epoch):
            # get the inputs; data is a list of [inputs, labels]
            inputs, labels = data
            inputs = inputs.to(device)
            labels = labels.to(device)

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            outputs = model(inputs)

            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            labels = labels.cpu()
            outputs = np.argmax(outputs.cpu().detach(), axis=1)

            writter.add_scalar("f1", f1_score(labels, outputs, average="micro"), i + epoch * len(dl))
            writter.add_scalar("recall", recall_score(labels, outputs, average="micro"), i + epoch * len(dl))
            writter.add_scalar("precision", precision_score(labels, outputs, average="micro"), i + epoch * len(dl))
            writter.add_scalar("loss", loss.item(), i + epoch * len(dl))

    torch.save(model, "model_final.pt")
    print('Finished Training')
