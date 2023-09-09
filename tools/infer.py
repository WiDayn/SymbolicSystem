import json
import os.path

import matplotlib.pyplot as plt

import core
from configs.config import json_path, base_path, retrain_tpl_path
from core.paddle import get_dataset_file, infer_img, infer_detail_img

if __name__ == "__main__":
    image_files = get_dataset_file()

    accept_list = []
    accept_img = []
    now_id = 0
    new_logic = True

    while new_logic:
        new_logic = False
        for image_file in image_files:
            if image_file in accept_img:
                continue
            plt.title(os.path.basename(image_file))
            # 先用具体的模型检测
            infer_detail_img(image_file)
            coco_detail_data = core.coco.cocoData()
            now_id = coco_detail_data.init(json_path, image_file, now_id, True)
            infer_img(image_file)
            coco_data = core.coco.cocoData()
            now_id = coco_data.init(json_path, image_file, now_id, False)
            logic = core.logic.logic(coco_data)
            logic.resolve_all_logic(accept_list, image_file, coco_detail_data)
            all_accept = logic.get_result()
            logic.add_result_to_accept_list(accept_list)
            logic.coco_data.save_coco_result(image_file)
            vis = core.vis.vis(image_file)
            vis.draw(logic.coco_data.frontal_vertebral_data, logic.coco_data.pelvis_data, logic.coco_data.rib_data,
                     logic.coco_data.artifact_data, image_file)
            if all_accept:
                new_logic = True
                accept_img.append(image_file)
                logic.coco_data.save_bbox_result(image_file)
            print("Complete: ", image_file)

    with open(base_path + "/evalset/bbox_train.json", 'r') as json_file:
        train_truth = json.load(json_file)

    with open(base_path + "/evalset/bbox_val.json", 'r') as json_file:
        eval_truth = json.load(json_file)

    truth_img = train_truth['images'] + eval_truth['images']
    truth_cat = train_truth['categories']
    truth_ann = train_truth['annotations'] + eval_truth['annotations']

    with open(retrain_tpl_path, 'r') as json_file:
        coco_tpl = json.load(json_file)

    data = []
    truth_data = []

    for bbox in accept_list:
        for t_img in truth_img:
            if bbox['file_name'] == t_img['file_name']:
                for category in coco_tpl['categories']:
                    if bbox['result'] == category['name']:
                        data.append(
                            {
                                "image_id": t_img['id'],
                                "category_id": category['id'],
                                "bbox": bbox['bbox'],
                                "score":bbox['score']
                            }
                        )

    with open(base_path + "/output/result.json", 'w') as json_file:
        json.dump(data, json_file, indent=4)
