import json
import math
import os

import imagehash
import numpy as np
from sklearn.linear_model import RANSACRegressor

from configs.config import prior_knowledge_path
from core.prolog.prolog import prolog
from PIL import Image


def distance(point1, point2):
    return math.sqrt((point1['bbox'][0] - point2['bbox'][0]) ** 2 + (point1['bbox'][1] - point2['bbox'][1]) ** 2)


def nearest_point(points, reference_point):
    min_distance = float('inf')
    nearest = None

    for point in points:
        if not point['enable']:
            continue
        dist = distance(point, reference_point)
        if dist < min_distance:
            min_distance = dist
            nearest = point

    return nearest


def points_on_opposite_side(points, line_slope, line_intercept):
    side1 = []
    side2 = []

    for point in points:
        if point['bbox'][1] < line_slope * point['bbox'][0] + line_intercept:
            side1.append(point)
        else:
            side2.append(point)

    return side1, side2


def distance_to_line(x, y, slope, intercept):
    a = slope
    b = -1
    c = -intercept
    numerator = abs(a * x + b * y + c)
    denominator = math.sqrt(a ** 2 + b ** 2)
    return numerator / denominator


def total_distance_to_line(points, slope, intercept):
    total_distance = 0
    for point in points:
        total_distance += distance_to_line(point['bbox'][0], point['bbox'][1], slope, intercept)

    return total_distance


def check_overlap(box1, box2, threshold):
    # box1 和 box2 格式: (x, y, width, height)
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    # 计算两个框的交集区域
    x_intersection = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
    y_intersection = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
    intersection = x_intersection * y_intersection

    if intersection > w1 * h1 * threshold or intersection > w2 * h2 * threshold:
        return True
    else:
        return False


# 获取椎骨线
def get_bone_line(bboxList):
    # 提取 x 和 y 值
    x_values = np.array([(bbox['bbox'][0] + bbox['bbox'][2] / 2) for bbox in bboxList]).reshape(-1, 1)
    y_values = np.array([(bbox['bbox'][1] + bbox['bbox'][3] / 2) for bbox in bboxList])

    if len(bboxList) == 1:
        bone_line_slope = 1e10
        bone_line_intercept = y_values[0] - bone_line_slope * x_values[0]
        return bone_line_slope, bone_line_intercept

    # 使用 RANSAC 进行鲁棒线性回归
    ransac = RANSACRegressor()
    ransac.fit(x_values, y_values)

    # 获取拟合直线的斜率和截距
    bone_line_slope = ransac.estimator_.coef_[0]
    bone_line_intercept = ransac.estimator_.intercept_

    # # 绘制原始数据点
    # plt.scatter(x_values, y_values, color='blue', label='Data Points')
    #
    # x_range = [-bone_line_intercept / bone_line_slope, (676 - bone_line_intercept) / bone_line_slope]
    # y_range = [0, 676]
    # plt.plot(x_range, y_range, color='red')

    return bone_line_slope, bone_line_intercept


def get_basic_fact(vertebral_list, pelvis_list, rib_list, artifact_list):
    prolog.asserta(f"is_pelvic(-1)")
    prolog.asserta(f"is_vertebra(-1)")
    prolog.asserta(f"is_rib(-1)")
    prolog.asserta(f"is_artifact(-1)")
    prolog.asserta(f"from_detail(-1, t12)")
    for pelvis in pelvis_list:
        if not pelvis['enable']:
            continue
        prolog.asserta(f"is_pelvic({pelvis['id']})")

    for vertebra in vertebral_list:
        if not vertebra['enable']:
            continue
        prolog.asserta(f"is_vertebra({vertebra['id']})")

    for costa in rib_list:
        if not costa['enable']:
            continue
        prolog.asserta(f"is_rib({costa['id']})")

    for artifact in artifact_list:
        if not artifact['enable']:
            continue
        prolog.asserta(f"is_artifact({artifact['id']})")


def get_near_fact(is_prior, vertebral_list, pelvis_list, rib_list, artifact_list, coco_detail_data):
    prolog.asserta(f"is_adjacent(-1, -1)")
    prolog.asserta(f"is_closest(-1, -1)")
    bone_line_slope, bone_line_intercept = get_bone_line(vertebral_list)
    for i, vertebral in enumerate(vertebral_list):
        if not vertebral['enable']:
            continue
        # 计算垂线斜率和截距
        perpendicular_intercept_val = vertebral['bbox'][1] + vertebral['bbox'][1] / bone_line_slope
        perpendicular_slope_val = -(1 / bone_line_slope)

        # 将点分为两部分
        side1, side2 = points_on_opposite_side(vertebral_list[:i] + vertebral_list[i + 1:], perpendicular_slope_val,
                                               perpendicular_intercept_val)

        # 找到每部分中离选定点最近的点
        nearest_point_side1 = nearest_point(side1, vertebral)
        nearest_point_side2 = nearest_point(side2, vertebral)

        if nearest_point_side1 is not None:
            prolog.asserta(f"is_adjacent({vertebral['id']}, {nearest_point_side1['id']})")

        if nearest_point_side2 is not None:
            prolog.asserta(f"is_adjacent({vertebral['id']}, {nearest_point_side2['id']})")

        print("离选定点最近的点在第一部分:", nearest_point_side1)
        print("离选定点最近的点在第二部分:", nearest_point_side2)

    if is_prior:
        for i, artifact in enumerate(artifact_list):
            if not artifact['enable']:
                continue
            point = nearest_point(vertebral_list, artifact)
            if nearest_point is not None:
                prolog.asserta(f"is_closest({artifact['id']}, {point['id']})")
    else:
        if len(coco_detail_data.l5) != 0 or len(coco_detail_data.l1) != 0 or len(coco_detail_data.t12) != 0:
            for vertebral in vertebral_list:
                if not vertebral['enable']:
                    continue
                for l5 in coco_detail_data.l5:
                    if check_overlap(vertebral['bbox'], l5['bbox'], 0.9):
                        prolog.asserta(f"from_detail({vertebral['id']}, l5)")
                for l1 in coco_detail_data.l1:
                    if check_overlap(vertebral['bbox'], l1['bbox'], 0.9):
                        prolog.asserta(f"from_detail({vertebral['id']}, l1)")
                for t12 in coco_detail_data.t12:
                    if check_overlap(vertebral['bbox'], t12['bbox'], 0.9):
                        prolog.asserta(f"from_detail({vertebral['id']}, t12)")
        else:
            for i, pelvis in enumerate(pelvis_list):
                if not pelvis['enable']:
                    continue
                point = nearest_point(vertebral_list, pelvis)

                if point is not None:
                    prolog.asserta(f"is_closest({pelvis['id']}, {point['id']})")

            for i, rib in enumerate(rib_list):
                if not rib['enable']:
                    continue
                point = nearest_point(vertebral_list, rib)

                if nearest_point is not None:
                    prolog.asserta(f"is_closest({rib['id']}, {point['id']})")


def get_all_overlap_to_logic(data_list, threshold):
    prolog.asserta(f"overlap({-1}, {-1})")
    for i, box1 in enumerate(data_list):
        for box2 in data_list[i + 1:]:
            if check_overlap(box1['bbox'], box2['bbox'], threshold):
                prolog.asserta(f"overlap({box1['id']}, {box2['id']})")
                print(f"Box {box1['id']} and Box {box2['id']} overlap")


def get_distant_point(data_list):
    prolog.asserta(f"distant({-1})")
    bone_line_slope, bone_line_intercept = get_bone_line(data_list)

    avgDis = total_distance_to_line(data_list, bone_line_slope, bone_line_intercept) / len(data_list)
    for entry in data_list:
        if not entry['enable']:
            continue
        dis = distance_to_line(entry['bbox'][0], entry['bbox'][1], bone_line_slope, bone_line_intercept)

        if dis > avgDis * 2:
            prolog.asserta(f"distant({entry['id']})")
            print(f"Box {entry['id']} is over avgDis")


def resolve_accept_list(frontal_vertebral_data, accept_list):
    max_p = -1
    max_value = -1
    map_accept_p = -1
    for i, accept_entry in enumerate(accept_list):
        print("now checking ", accept_entry['result'], " img path: ", accept_entry['path'])
        for j, vertebral in enumerate(frontal_vertebral_data):
            image1 = Image.open(vertebral['path'])
            image1 = image1.crop((vertebral['bbox'][0] - 5, vertebral['bbox'][1] - 5,
                                  vertebral['bbox'][0] + accept_entry['bbox'][2] + 10,
                                  vertebral['bbox'][1] + accept_entry['bbox'][3] + 10))
            hash1 = imagehash.dhash(image1)
            image2 = Image.open(accept_entry['path'])
            image2 = image2.crop((accept_entry['bbox'][0] - 5, accept_entry['bbox'][1] - 5,
                                  accept_entry['bbox'][0] + accept_entry['bbox'][2] + 10,
                                  accept_entry['bbox'][1] + accept_entry['bbox'][3] + 10))
            hash2 = imagehash.dhash(image2)

            similarity = 1.0 - (hash1 - hash2) / 64.0
            print(vertebral['id'], " and ", accept_entry['id'], 'dHash: ', similarity)
            if similarity > max_value:
                map_accept_p = i
                max_p = j
                max_value = similarity

    if max_value > 0.8:
        try:
            result = list(prolog.query(f"vertebra({frontal_vertebral_data[max_p]['id']}, Y)"))
            print("Already have label: ", result[0]['Y'])
        except:
            try:
                result = list(prolog.query(f"vertebra_from_top({frontal_vertebral_data[max_p]['id']}, Y)"))
                print("Already have label: ", result[0]['Y'])
            except:
                print("I guess ", frontal_vertebral_data[max_p]['id'], " is ", accept_list[map_accept_p]['result'])
                prolog.asserta(
                    f"dhash_vertebra({frontal_vertebral_data[max_p]['id']}, {accept_list[map_accept_p]['result']})")


def get_loc_logic(frontal_vertebral_data):
    prolog.asserta("higher(-1, -1)")
    prolog.asserta("lower(-2, -2)")
    for vertebral_1 in frontal_vertebral_data:
        for vertebral_2 in frontal_vertebral_data:
            if vertebral_1['id'] == vertebral_2['id'] or not vertebral_1['enable'] or not vertebral_2['enable']:
                continue
            if vertebral_1['bbox'][1] < vertebral_2['bbox'][1]:
                prolog.asserta(f"higher({vertebral_1['id']}, {vertebral_2['id']})")
                prolog.asserta(f"lower({vertebral_2['id']}, {vertebral_1['id']})")


def get_prior_knowledge(image_file, artifact_list):
    with open(prior_knowledge_path, "r") as f:
        prior_knowledge_data = json.load(f)

    for prior_knowledge in prior_knowledge_data['prior_knowledge']:
        if prior_knowledge['image_name'] == os.path.basename(image_file):
            for artifact in artifact_list:
                prolog.asserta(f"close_artifact({artifact['id']}, {prior_knowledge['artifact_closest']})")
                return True

    return False
