from matplotlib import pyplot as plt
from modules.Extractor import extractor, preprocess
import os
import torch
from PIL import Image
import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import pandas as pd
import seaborn as sns
import itertools
import hashlib
import cv2
from joblib import dump, load
import tqdm

folder = "./data"
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")


def grouper(iterable, n):
    iterable = iter(iterable)
    while True:
        tup = tuple(itertools.islice(iterable, 0, n))
        if tup:
            yield tup
        else:
            break


batch_size = 64

if __name__ == '__main__':
    features = {}
    extractor.to(device)

    with open("../hash_images", 'r+') as f:
        old_hash = f.read()

    chain = ""
    for _, _, files in os.walk(folder):
        for file in files:
            chain += file
    new_hash = hashlib.md5(chain.encode("utf-8"))
    print(new_hash.hexdigest())
    print(old_hash)

    if new_hash.hexdigest() != old_hash:
        print("md5 error, redo dataframe")

        for subdir, dirs, files in tqdm.tqdm(os.walk(folder)):
            for file_batch in tqdm.tqdm(grouper(files, batch_size)):
                name = subdir.split("\\")[-1]

                tensor_batch = torch.stack(
                    [preprocess(Image.open(os.path.join(subdir, file)).convert('RGB')) for file in file_batch])
                with torch.no_grad():
                    tensor_batch = tensor_batch.to(device)
                    feature_batch = extractor(tensor_batch)
                    if name not in features:
                        features[name] = []
                    features[name].append(list(feature_batch.cpu().numpy()))

        all_features = []
        size = []
        names = []
        for name in features.keys():
            features[name] = np.concatenate(features[name])
            all_features.append(features[name])
            names.append(name)
            size.append(len(features[name]))

        y = np.concatenate(np.array([[names[i]] * v for i, v in enumerate(size)]))

        all_features = np.concatenate(all_features)

        # reducer = IncrementalPCA(n_components=4, batch_size=10)
        # all_features = reducer.fit_transform(X=all_features)

        reducer = LinearDiscriminantAnalysis(n_components=2)
        all_features = reducer.fit_transform(X=all_features, y=y)

        dump(reducer, "../LDA")

        df = pd.DataFrame(data=all_features)
        df["labels"] = y
        print(df)
        df.to_csv("data.csv")

        with open("../hash_images", 'w') as f:
            f.write(new_hash.hexdigest())

    else:
        print("using saved dataframe")
        reducer = load("../LDA")
        df = pd.DataFrame.from_csv("../data.csv")

    g = sns.pairplot(df, hue="labels", )
    plt.show()

    cam = cv2.VideoCapture(0)

    plt.ion()
    fig, ax = plt.subplots()

    cat = list(np.unique(df["labels"]))
    z = [cat.index(label) for label in list(df["labels"])]

    for i, c in enumerate(cat):
        sub_df = df.loc[df["labels"] == c]
        x, y = list(sub_df["0"]), list(sub_df["1"])
        sc = ax.scatter(x, y, marker="o", alpha=.5, label=c)
    plt.legend()

    plt.draw()
    while cam.isOpened():
        ret, frame = cam.read()
        if ret:
            with torch.no_grad():
                tensor = preprocess(Image.fromarray(frame)).to(device)
                tensor_out = extractor(tensor.unsqueeze(0)).cpu().numpy()
                res = reducer.predict(tensor_out)

                feature_res = reducer.transform(tensor_out).squeeze()
                plt.scatter(feature_res[0], feature_res[1], label=res, marker="d")

                fig.canvas.draw_idle()
                plt.pause(0.5)
                # cv2.imshow("", frame)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break

                print(res)

    cam.release()
    cv2.destroyAllWindows()

    # plt.figure()
    # for name in features.keys():
    #     X = reducer.transform(features[name])
    #     plt.scatter(X[:, 0], X[:, 1], label=name, edgecolors=None, alpha=.5)
    # plt.legend()
    # plt.show()
