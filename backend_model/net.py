import numpy as np
import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision import transforms
from PIL import Image
import cv2
from sklearn.cluster import KMeans
import backend_model
import os

class Letter:
    
    def __init__(self, boxesn, classn, scoren):
        self.boxesn = boxesn
        self.classn = classn
        self.scoren = scoren
        
class Model:
    # 构建并加载模型参数
    CLASS_NAMES = ['__background__', 'A', 'B', 'C', 'D', 'X']
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn()
    num_classes = 6
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    model.to(device)
    model_path = os.path.join(os.path.dirname(backend_model.__file__), 'model-use.pth')
    model.load_state_dict(torch.load(model_path))
    model.eval()

    # 预测
    def prediction(self, img, threshold):
        # img = Image.open(img)
        img = cv2.imread(img) # 读取图片，并将图片转为黑底白字
        img[img > 180] = 255
        img = 255 - img
        img[img > 100] = 255
        img = Image.fromarray(img.astype('uint8')).convert('RGB')
        transform = transforms.Compose([transforms.ToTensor()])
        img = transform(img)
        img = img.to(self.device)
        pred = self.model([img]) # Pass the image to the model
        pred_class = [self.CLASS_NAMES[i] for i in list(pred[0]['labels'].to("cpu").numpy())]
        pred_boxes = [[int(i[0]), int(i[1]), int(i[2]), int(i[3])] for i in list(pred[0]['boxes'].to("cpu").detach().numpy())]
        pred_score = list(pred[0]['scores'].to("cpu").detach().numpy())
        pred_t = [pred_score.index(x) for x in pred_score if x >= threshold][-1] # 筛选在阈值之上的目标
        pred_boxes = pred_boxes[:pred_t+1]
        pred_class = pred_class[:pred_t+1]
        pred_score = pred_score[:pred_t+1]
        for i in range(len(pred_score)):
            pred_score[i] = int(pred_score[i] * 100) # 置信率转为整数
        return pred_boxes, pred_class, pred_score

    # 将预测目标进行排序，返回排序后的结果
    def getAns(self, img, threshold, letterNum):

        pred_boxes, pred_class, pred_score =  self.prediction(img, threshold)
        letters = []
        for i in range(len(pred_boxes)):
            if pred_class[i] != 'X':
                letter = Letter(pred_boxes[i], pred_class[i], pred_score[i])
                letters.append(letter)
                
        letters.sort(key=lambda x: x.boxesn[0] + 2000 * x.boxesn[1]) # 按照纵坐标粗排
        letters_y = np.array([(x.boxesn[1] + x.boxesn[3]) / 2 for x in letters]).reshape(-1, 1)

        clf = KMeans(n_clusters=(letterNum // 5))  # kemns聚类模型
        clf.fit(letters_y) # 将所有目标的纵坐标使用聚类，细分出每行的目标，然后行内按照横坐标排序
        row_labels = clf.predict(letters_y)
        last_row_label = -1
        begin = 0
        sorted_letters = [] # 存储排序后的目标字母
        row_labels = np.append(row_labels, 99)
        for i, row_label in enumerate(row_labels):
            if row_label != last_row_label: # 新的一行
                temp = letters[begin:i]
                temp.sort(key=lambda x: x.boxesn[0])
                sorted_letters = sorted_letters + temp
                begin = i
            last_row_label = row_label 
        return sorted_letters
        

        