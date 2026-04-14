# custom_loss.py
import torch
from ultralytics.nn.tasks import v8DetectionLoss

class CustomDetectionLoss(v8DetectionLoss):
    def __init__(self, model):
        super().__init__(model)
        self.nc = getattr(model, 'nc', 10)  # 10为默认类别数
        # 假设类别0和1（可乐、百事可乐）容易混淆
        self.similarity_matrix = torch.eye(self.nc)
        self.similarity_matrix[0, 1] = self.similarity_matrix[1, 0] = 0.5  # 可乐和百事可乐相似度高

    def classification_loss(self, pred, target):
        # 继承原有的Focal Loss
        loss = super().classification_loss(pred, target)
        # 针对易混类别加权
        with torch.no_grad():
            target_classes = target.argmax(dim=-1)
        for i in range(pred.shape[0]):
            for j in range(pred.shape[1]):
                cls = target_classes[i, j]
                if cls in [0, 1]:  # 可乐、百事可乐
                    loss[i, j] *= 1.2  # 对这两类的分类损失加权
        return loss

    def bbox_loss(self, pred, target):
        # 继承原有的CIoU Loss
        return super().bbox_loss(pred, target)