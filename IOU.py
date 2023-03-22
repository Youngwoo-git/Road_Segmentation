from glob import glob
import cv2
import json
import os
from PIL import Image
import numpy as np
import hydra


@hydra.main(config_path="conf", config_name="iou")
def get_IOU(cfg):
    iou_sum = 0
    ori_dir = cfg.ori_dir
    pred_dir = cfg.pred_dir
    
    pred_img_list = glob(os.path.join(pred_dir, "*.png"))
    
    for img_path in pred_img_list:
#         load predicted seg result
        pred_img = cv2.imread(img_path)

#         load gt seg info
        json_path = os.path.join(ori_dir, os.path.basename(img_path)).replace(".png", ".json")
        with open(json_path, "r") as f:
            anno = json.load(f)
            
        lbl_list = anno["shapes"]
        
#         draw gt seg
        blank_img = np.zeros(list(pred_img.shape), dtype = np.uint8)

        for lbl in lbl_list:
            points = lbl["points"]
            pts = np.array(points, np.int32)
            pts = pts.reshape((-1,1,2))
            cv2.fillPoly(blank_img,[pts],(255,255,255))

#         In case you need to compare the results visually
#         display(Image.fromarray(cv2.hconcat([blank_img, pred_img])))


#         IOU calculation
        intersection = np.logical_and(pred_img, blank_img)
        union = np.logical_or(pred_img, blank_img)
        iou_score = np.sum(intersection) / np.sum(union)
        iou_sum += iou_score


    mIOU = iou_sum/len(pred_img_list)
    print(mIOU)
#         display(Image.fromarray(blank_img))

if __name__ == "__main__":
    result = get_IOU()