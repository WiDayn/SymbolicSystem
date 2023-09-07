import json
import os

from configs.config import retrain_path, retrain_tpl_path, output_path
from PIL import Image


class cocoData:
    bboxes_data = []
    pelvis_data = []
    rib_data = []
    artifact_data = []
    frontal_vertebral_data = []

    def init(self, json_path, image_file, now_id, is_detail):
        self.bboxes_data = []
        self.pelvis_data = []
        self.rib_data = []
        self.frontal_vertebral_data = []
        self.artifact_data = []
        self.l5 = []
        self.l1 = []
        self.t12 = []
        with open(json_path, 'r') as f:
            self.bboxes_data = json.load(f)

        for i, bbox in enumerate(self.bboxes_data):
            bbox['id'] = now_id
            bbox['enable'] = True
            bbox['path'] = image_file
            bbox['file_name'] = os.path.basename(image_file)
            now_id += 1

        if is_detail:
            self.get_all_l5()
            self.get_all_l1()
            self.get_all_t12()
        else:
            self.get_all_pelvis()
            self.get_all_frontal_vertebral()
            self.get_all_rib()
            self.get_all_artifact()

        return now_id

    def get_all_l5(self):
        for entry in self.bboxes_data:
            if entry['score'] > 0.5 and entry['category_id'] == 13:
                self.l5.append(entry)

    def get_all_l1(self):
        for entry in self.bboxes_data:
            if entry['score'] > 0.5 and entry['category_id'] == 9:
                self.l1.append(entry)

    def get_all_t12(self):
        for entry in self.bboxes_data:
            if entry['score'] > 0.5 and entry['category_id'] == 8:
                self.t12.append(entry)

    # 获取盆骨边界框
    def get_all_pelvis(self):
        for entry in self.bboxes_data:
            if entry['score'] > 0.5 and entry['category_id'] == 14:
                self.pelvis_data.append(entry)

        # x_values = np.array([(bbox['bbox'][0] + bbox['bbox'][2] / 2) for bbox in self.pelvis_data]).reshape(-1, 1)
        # y_values = np.array([(bbox['bbox'][1] + bbox['bbox'][3] / 2) for bbox in self.pelvis_data])
        #
        # # 绘制原始数据点
        # plt.scatter(x_values, y_values, color='blue', label='Data Points')
        # plt.plot(x_values, y_values, color='red')

    # 获取椎体边界框
    def get_all_frontal_vertebral(self):
        for entry in self.bboxes_data:
            if entry['score'] > 0.35 and entry['category_id'] == 3:
                self.frontal_vertebral_data.append(entry)

    # 获取肋骨边界框
    def get_all_rib(self):
        for entry in self.bboxes_data:
            if entry['score'] > 0.2 and entry['category_id'] == 15:
                self.rib_data.append(entry)

    # 获取人造物边界框
    def get_all_artifact(self):
        for entry in self.bboxes_data:
            if entry['score'] > 0.5 and entry['category_id'] == 16:
                self.artifact_data.append(entry)

    def save_coco_result(self, img_path):
        with open(retrain_tpl_path, 'r') as json_file:
            data = json.load(json_file)

        image = Image.open(img_path)

        width, height = image.size

        data['images'].append(
            {
                "id": 1,
                "path": img_path,
                "width": width,
                "height": height,
                "file_name": os.path.basename(img_path),
            }
        )

        for i, vertebral in enumerate(self.frontal_vertebral_data):
            if not vertebral['enable'] or 'result' not in vertebral:
                continue

            for category in data['categories']:
                if vertebral['result'] == category['name']:
                    data['annotations'].append(
                        {
                            "id": i,
                            "image_id": 1,
                            "category_id": category['id'],
                            "area": vertebral['bbox'][2] * vertebral['bbox'][3],
                            "bbox": vertebral['bbox'],
                            "iscrowd": False,
                            "isbbox": True,
                            "color": "#17b212",
                            "metadata": {}
                        }
                    )

        with open(retrain_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def save_bbox_result(self, img_path):
        print("writing results to: ", output_path + "/" + os.path.basename(img_path) + ".json")
        data = []

        with open(retrain_tpl_path, 'r') as json_file:
            coco_tpl = json.load(json_file)

        for vertebral in self.frontal_vertebral_data:
            if not vertebral['enable'] or 'result' not in vertebral:
                continue

            for category in coco_tpl['categories']:
                if vertebral['result'] == category['name']:
                    data.append(
                        {
                            "image_id": 0,
                            "category_id": category['id'],
                            "bbox": vertebral['bbox'],
                            "score": vertebral['score']
                        }
                    )

        with open(output_path + "/" + os.path.basename(img_path) + ".json", 'w') as json_file:
            json.dump(data, json_file, indent=4)
