import os

from matplotlib import patches, pyplot as plt
from PIL import Image

from configs.config import save_file_path, result_save_method


class vis:
    image = []
    ax = []

    def __init__(self, image_path):
        self.image = Image.open(image_path)
        plt.imshow(self.image)
        self.ax = plt.gca()
        # 禁用坐标轴的自动缩放
        self.ax.autoscale(False)

    def draw(self, vertebral_list, pelvis_list, rib_list, artifact_list, image_file):
        for entry in vertebral_list:
            if not entry['enable']:
                continue
            bbox = entry['bbox']
            rect = patches.Rectangle(
                (bbox[0], bbox[1]), bbox[2], bbox[3],
                linewidth=1, edgecolor='r', facecolor='none'
            )
            self.ax.add_patch(rect)
            if 'result' in entry:
                plt.text(
                    bbox[0], bbox[1],
                    f"{entry['result']}  {round(entry['score'], 2)}",
                    color='r', fontsize=8, backgroundcolor='w'
                )

        for entry in pelvis_list:
            if not entry['enable']:
                continue
            bbox = entry['bbox']
            rect = patches.Rectangle(
                (bbox[0], bbox[1]), bbox[2], bbox[3],
                linewidth=1, edgecolor='r', facecolor='none'
            )
            self.ax.add_patch(rect)
            plt.text(
                bbox[0], bbox[1],
                f"pelvis {round(entry['score'], 2)}",
                color='r', fontsize=8, backgroundcolor='w'
            )

        for entry in rib_list:
            if not entry['enable']:
                continue
            bbox = entry['bbox']
            rect = patches.Rectangle(
                (bbox[0], bbox[1]), bbox[2], bbox[3],
                linewidth=1, edgecolor='r', facecolor='none'
            )
            self.ax.add_patch(rect)
            plt.text(
                bbox[0], bbox[1],
                f"rib {round(entry['score'], 2)}",
                color='r', fontsize=8, backgroundcolor='w'
            )

        for entry in artifact_list:
            if not entry['enable']:
                continue
            bbox = entry['bbox']
            rect = patches.Rectangle(
                (bbox[0], bbox[1]), bbox[2], bbox[3],
                linewidth=1, edgecolor='r', facecolor='none'
            )
            self.ax.add_patch(rect)
            plt.text(
                bbox[0], bbox[1],
                f"artifact {round(entry['score'], 2)}",
                color='r', fontsize=8, backgroundcolor='w'
            )

        if result_save_method == "file":
            plt.savefig(f'{save_file_path}/'
                    f'{os.path.basename(image_file).split(".")[0]}.result.png', dpi=300)
        elif result_save_method == "show":
            plt.show()

        plt.close()