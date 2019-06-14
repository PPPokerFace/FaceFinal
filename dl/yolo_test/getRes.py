import matplotlib.pyplot as plt
import numpy as np

def getRes(filename):
    x = []
    y = []
    for i in range(0, 100):
        thres = i / 100
        TP, TN, FP, FN = 0, 0, 0, 0
        f = open(filename, "r")
        for line in f:
            l = line.split(" ")
            if len(l) != 3:
                continue
            name = l[0][0:-9]
            test = l[1]
            score = float(l[2])
            if score >= thres and name == test:
                TP += 1
            elif score >= thres and name != test:
                FP += 1
            elif score < thres and name == test:
                FN += 1
            elif score < thres and name != test:
                TN += 1
        R1 = TP / (TP + FN)
        R2 = FP / (FP + TN)
        x.append(R2 * 100)
        y.append(R1 * 100)
    return x,y

x = []
y = []
y2 = []
# filename="test_Mobile.txt"
filename = "test_IR50SE.txt"
for i in range(0, 100):
    thres = i / 100
    TP, TN, FP, FN = 0, 0, 0, 0
    f = open(filename, "r")
    for line in f:
        l = line.split(" ")
        if len(l) != 3:
            continue
        name = l[0][0:-9]
        test = l[1]
        score = float(l[2])
        if score >= thres and name == test:
            TP += 1
        elif score >= thres and name != test:
            FP += 1
        elif score < thres and name == test:
            FN += 1
        elif score < thres and name != test:
            TN += 1
    R1 = TP / (TP + FN)
    R2 = FP / (FP + TN)
    x.append(i)
    if TP+FP!=0:
        y.append(TP/(TP+FP)*100)
    else:
        y.append(0)

x2 = []
y2 = []
y3 = []
filename = "test_Mobile.txt"
# filename="test_IR50SE.txt"
for i in range(0, 100):
    thres = i / 100
    TP, TN, FP, FN = 0, 0, 0, 0
    f = open(filename, "r")
    for line in f:
        l = line.split(" ")
        if len(l) != 3:
            continue
        name = l[0][0:-9]
        test = l[1]
        score = float(l[2])
        if score >= thres and name == test:
            TP += 1
        elif score >= thres and name != test:
            FP += 1
        elif score < thres and name == test:
            FN += 1
        elif score < thres and name != test:
            TN += 1
    R1 = TP / (TP + FN)
    R2 = FP / (FP + TN)


    x2.append(i)
    if TP+FP!=0:
        y2.append(TP/(TP+FP)*100)
    else:
        y2.append(0)

figsize = 5,5
figure, ax = plt.subplots(figsize=figsize)

B, = plt.plot(x2, y2, '-', label="MobileFaceNet",linewidth=2.0)
A, = plt.plot(x, y, '-', label="IR50SE",linewidth=2.0)

plt.plot(x, x, 'k--',linewidth=1)
font1 = {'family': 'Times New Roman',
         'weight': 'normal',
         'size': 12,
         }
legend = plt.legend(handles=[A, B], prop=font1)
plt.xlabel("Threshold")
plt.ylabel("Percent of pass")

plt.show()
