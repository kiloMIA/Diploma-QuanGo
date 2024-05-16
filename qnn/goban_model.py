import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor

def create_model(num_classes, weights='DEFAULT'):
    weights_enum = None
    if weights == 'DEFAULT':
        weights_enum = torchvision.models.detection.FasterRCNN_ResNet50_FPN_Weights.DEFAULT
    else:
        weights_enum = torchvision.models.detection.FasterRCNN_ResNet50_FPN_Weights.COCO_V1

    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights=weights_enum)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    return model
