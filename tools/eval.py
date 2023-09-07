import json

import numpy as np
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

# 加载预测值和真实值的 JSON 文件
from configs.config import base_path

# 加载真实值的数据
true_bbox_data_path = base_path + "/output/truth.json"
with open(true_bbox_data_path, "r") as f:
    true_bbox_data = json.load(f)

# 加载预测值的数据
predicted_bbox_data_path = base_path + "/output/result.json"
with open(predicted_bbox_data_path, "r") as f:
    predicted_bbox_data = json.load(f)

for i, bbox in enumerate(predicted_bbox_data):
    bbox['id'] = i + 1  # 使用索引作为唯一的 id
    bbox['area'] = bbox['bbox'][2] * bbox['bbox'][3]

gen_true_bbox_data = {
    "info": true_bbox_data['info'],
    "images": true_bbox_data['images'],
    'annotations': [],
    "categories": true_bbox_data['categories']
}

for i, bbox in enumerate(true_bbox_data['annotations']):
    for pre_data in predicted_bbox_data:
        if bbox['image_id'] == pre_data['image_id'] and bbox['category_id'] <= 13:
            if bbox['image_id'] == 46:
                print(bbox)
            gen_true_bbox_data['annotations'].append(bbox)
            break

# 创建 COCO 对象并加载数据
coco_gt = COCO()
coco_gt.dataset = gen_true_bbox_data
coco_gt.createIndex()

with open(base_path + "/judge.json", 'w') as json_file:
    json.dump(gen_true_bbox_data, json_file, indent=4)

# 创建 COCO 对象并加载数据
coco_dt = COCO()
coco_dt.dataset["images"] = coco_gt.dataset["images"]
coco_dt.dataset["categories"] = coco_gt.dataset["categories"]
coco_dt.dataset["annotations"] = predicted_bbox_data
coco_dt.createIndex()

# 初始化 COCO 评估器
coco_eval = COCOeval(coco_gt, coco_dt, 'bbox')

# 运行评估
coco_eval.evaluate()
coco_eval.accumulate()
coco_eval.summarize()

# 获取 per-image 的 AP 值
per_image_ap = coco_eval.eval['precision']

# 获取 mAP
mAP = coco_eval.stats[0]
print(f"mAP: {mAP}")
