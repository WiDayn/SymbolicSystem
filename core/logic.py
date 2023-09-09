from .prolog.prolog import prolog
from .scan import get_all_overlap_to_logic, get_distant_point, get_basic_fact, get_near_fact, resolve_accept_list, \
    get_loc_logic, get_prior_knowledge


def resolve_overlap(data_list):
    for bbox in data_list:
        if not bbox['enable']:
            continue
        overlapQuery = prolog.query(f"overlap({bbox['id']}, Y)")

        for result in list(overlapQuery):
            for item in data_list:
                if item['id'] == result['Y']:
                    item['enable'] = False


def resolve_distant_point(data_list):
    for entry in data_list:
        if not entry['enable']:
            continue
        distantQuery = list(prolog.query(f"distant({entry['id']})"))

        if len(distantQuery):
            entry['enable'] = False


class logic:
    coco_data = []
    is_prior = False

    def __init__(self, coco_data):
        self.coco_data = coco_data

    def resolve_all_logic(self, accept_list, image_file, coco_detail_data):
        get_basic_fact(self.coco_data.frontal_vertebral_data, self.coco_data.pelvis_data, self.coco_data.rib_data,
                       self.coco_data.artifact_data)
        self.is_prior = get_prior_knowledge(image_file, self.coco_data.artifact_data)
        if len(self.coco_data.frontal_vertebral_data) != 0:
            self.resolve_front_logic(accept_list, coco_detail_data)

    def resolve_front_logic(self, accept_list, coco_detail_data):
        get_all_overlap_to_logic(self.coco_data.frontal_vertebral_data, 0.5)
        get_all_overlap_to_logic(self.coco_data.rib_data, 0.5)
        get_all_overlap_to_logic(self.coco_data.pelvis_data, 0.5)
        get_all_overlap_to_logic(self.coco_data.artifact_data, 0.5)
        resolve_overlap(self.coco_data.frontal_vertebral_data)
        resolve_overlap(self.coco_data.rib_data)
        resolve_overlap(self.coco_data.pelvis_data)
        resolve_overlap(self.coco_data.artifact_data)
        get_distant_point(self.coco_data.frontal_vertebral_data)
        resolve_distant_point(self.coco_data.frontal_vertebral_data)
        get_near_fact(self.is_prior, self.coco_data.frontal_vertebral_data, self.coco_data.pelvis_data,
                      self.coco_data.rib_data, self.coco_data.artifact_data, coco_detail_data)
        get_loc_logic(self.coco_data.frontal_vertebral_data)
        resolve_accept_list(self.coco_data.frontal_vertebral_data, accept_list)

    def get_result(self):
        all_accept = True
        prolog.asserta("dhash_vertebra(-1, -1)")
        # result = list(prolog.query(f"lower(A, B)"))
        for entry in self.coco_data.frontal_vertebral_data:
            if not entry['enable']:
                continue
            try:
                result = list(prolog.query(f"vertebra({entry['id']}, Y)"))
                entry['result'] = result[0]['Y']
            except:
                try:
                    result = list(prolog.query(f"vertebra_from_top({entry['id']}, Y)"))
                    entry['result'] = result[0]['Y']
                except:
                    all_accept = False
                    print(entry['id'])

        return all_accept

    def add_result_to_accept_list(self, accept_list):
        for entry in self.coco_data.frontal_vertebral_data:
            if not entry['enable']:
                continue
            if 'result' in entry:
                accept_list.append(entry)
