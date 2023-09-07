import os
import subprocess

import yaml

from configs.config import dataset_path, rtdetr_path, detail_path, class_path


def get_dataset_file():
    image_extensions = [".jpg", ".jpeg", ".png", ".bmp"]
    image_files = []

    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(root + "/" + file))

    return image_files


def set_coco_train(image_dir, anno_path, dataset_dir):
    with open(rtdetr_path + '/configs/datasets/coco_detection.yml', 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)
    data['TrainDataset']['image_dir'] = image_dir
    data['TrainDataset']['anno_path'] = anno_path
    data['TrainDataset']['dataset_dir'] = dataset_dir

    with open(rtdetr_path + '/configs/datasets/coco_detection.yml', 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)


def set_coco_eval(image_dir, anno_path, dataset_dir):
    with open(rtdetr_path + '/configs/datasets/coco_detection.yml', 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)
    data['EvalDataset']['image_dir'] = image_dir
    data['EvalDataset']['anno_path'] = anno_path
    data['EvalDataset']['dataset_dir'] = dataset_dir

    with open(rtdetr_path + '/configs/datasets/coco_detection.yml', 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)


def set_model_weights(weights):
    with open(rtdetr_path + '/configs/rtdetr/rtdetr_r50vd_6x_coco.yml', 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)
    data['weights'] = weights
    with open(rtdetr_path + '/configs/rtdetr/rtdetr_r50vd_6x_coco.yml', 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)


def set_detail_model_weights(weights):
    with open(rtdetr_path + '/configs/rtdetr/rtdetr_r50vd_detail_6x_coco.yml', 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)
    data['weights'] = weights
    with open(rtdetr_path + '/configs/rtdetr/rtdetr_r50vd_detail_6x_coco.yml', 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)


def set_pretrain_model(pretrain_weights):
    with open(rtdetr_path + '/configs/rtdetr/_base_/rtdetr_r50vd.yml', 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)
    data['pretrain_weights'] = pretrain_weights
    with open(rtdetr_path + '/configs/rtdetr/_base_/rtdetr_r50vd.yml', 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)


def start_train():
    result = subprocess.run(["python", rtdetr_path + "/tools/train.py",
                             "-c", rtdetr_path + "/configs/rtdetr/rtdetr_r50vd_6x_coco.yml"],
                            capture_output=True, text=True)

    print("output:", result.stdout)
    print("error:", result.stderr)


def infer_detail_img(image_path):
    os.chdir(rtdetr_path)
    set_detail_model_weights(detail_path)
    result = subprocess.run(["python", rtdetr_path + "/tools/infer.py",
                             "-c", rtdetr_path + "/configs/rtdetr/rtdetr_r50vd_detail_6x_coco.yml",
                             "--infer_img", image_path,
                             "--save_results", "true"],
                            capture_output=True, text=True)

    print("output:", result.stdout)
    print("error:", result.stderr)

def infer_img(image_path):
    set_model_weights(class_path)
    result = subprocess.run(["python", rtdetr_path + "/tools/infer.py",
                             "-c", rtdetr_path + "/configs/rtdetr/rtdetr_r50vd_6x_coco.yml",
                             "--infer_img", image_path,
                             "--save_results", "true"],
                            capture_output=True, text=True)

    print("output:", result.stdout)
    print("error:", result.stderr)


def retrain(pretrain_model, image_dir, anno_path, dataset_dir):
    set_pretrain_model(pretrain_model)
    set_coco_train(image_dir, anno_path, dataset_dir)
    start_train()
