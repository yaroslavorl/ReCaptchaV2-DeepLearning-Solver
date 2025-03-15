import cv2
import numpy as np
from ultralytics import YOLO

from .detector_settings import CaptchaCell, CAPTCHA_CELL, OBJECT_NOT_FOUND, CELL_NOT_FOUND


class CaptchaDetector:

    def __init__(self, model_weight: str = 'yolo_weights/yolov9e-seg.pt'):
        self.__model = YOLO(model_weight).cuda()

        self._captcha_cell_dict: dict[str, CaptchaCell] = CAPTCHA_CELL

    @property
    def get_all_detected_classes(self):
        return self.__model.names

    @property
    def captcha_cell_dict(self):
        return self._captcha_cell_dict

    def predict_click_coord(
            self,
            captcha: bytes | np.ndarray,
            required_class_idx: int,
            captcha_type: str,
            is_img_blur: bool = True,
            ksize_blur: tuple[int, int] = (11, 11),
            sigma_blur: float = 1,
            binary_cell_thresh: float = 254,
            area_cell_thresh: float = 5e3,
            error_similar_area: float = 250,
            detect_confidence: float = 0.05,
            mask_cell_overlap_px: int = 5,
    ) -> list[tuple[float, float]] | None:
        img_captcha = self._decoding_bytes_to_img(captcha) if isinstance(captcha, bytes) else captcha
        captcha_size = img_captcha.shape

        processed_img = cv2.GaussianBlur(img_captcha, ksize_blur, sigma_blur) if is_img_blur else img_captcha
        predict_result = self.__model.predict(processed_img, conf=detect_confidence)

        if predict_result[0].masks is None:
            return
        all_masks = predict_result[0].masks.data.cpu().numpy()

        all_classes = predict_result[0].boxes.cls.cpu().int().numpy()
        required_masks = all_masks[all_classes == required_class_idx]

        if not required_masks.size:
            print(f'{self.__class__.__name__}: {OBJECT_NOT_FOUND}')
            return

        if not self._captcha_cell_dict[captcha_type].cell_coord:
            bbx_cell_coord = self.find_captcha_cell_contours(img_captcha,
                                                             cell_num=self._captcha_cell_dict[captcha_type].cell_num,
                                                             binary_thresh=binary_cell_thresh,
                                                             area_thresh=area_cell_thresh,
                                                             error_similar_area=error_similar_area)
            if not bbx_cell_coord:
                print(f'{self.__class__.__name__}: {CELL_NOT_FOUND}')
                return
            self._captcha_cell_dict[captcha_type].cell_coord = bbx_cell_coord
        else:
            bbx_cell_coord = self._captcha_cell_dict[captcha_type].cell_coord

        intersecting_bbx = self._get_intersecting_boxes(bbx_cell_coord,
                                                        required_masks,
                                                        captcha_size=captcha_size,
                                                        thresh=mask_cell_overlap_px)
        coord_click = self._get_center_bbx(intersecting_bbx)

        return coord_click

    def find_captcha_cell_contours(
            self,
            img_captcha: np.ndarray,
            cell_num: int,
            binary_thresh: float,
            area_thresh: float,
            error_similar_area: float
    ):
        gray = cv2.cvtColor(img_captcha, cv2.COLOR_BGR2GRAY)
        threshold = cv2.threshold(gray, binary_thresh, 255, cv2.THRESH_BINARY)[1]
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        area_list = [cv2.contourArea(contour) for contour in contours]
        group_area = self._group_similar_area(area_list, threshold=error_similar_area)
        len_group_area = np.array([group for group in group_area if len(group) == cell_num])

        if len_group_area.size > 0:
            len_group_area = len_group_area[0]
            required_contours = []
            for contour in contours:
                area_contour = cv2.contourArea(contour)
                if area_contour in len_group_area and area_contour > area_thresh:
                    required_contours.append(cv2.boundingRect(contour))
            return required_contours

    @staticmethod
    def _get_intersecting_boxes(boxes, masks, captcha_size: tuple[int, ...], thresh: int):
        intersecting_boxes = []
        for box in boxes:
            x, y, w, h = box
            for mask in masks:
                mask = cv2.resize(mask, dsize=(captcha_size[1], captcha_size[0]))
                if cv2.countNonZero(mask[y:y + h, x:x + w]) > thresh:
                    intersecting_boxes.append(box)
                    break

        return intersecting_boxes

    @staticmethod
    def _group_similar_area(array: list, threshold: float):
        array_sorted = np.sort(array)
        groups, group = [], [array_sorted[0]]
        for area in array_sorted[1:]:
            if area - group[-1] <= threshold:
                group.append(area)
            else:
                groups.append(group)
                group = [area]
        groups.append(group)
        return groups

    @staticmethod
    def _get_center_bbx(boxes):
        bbx_center_coord = []
        for box in boxes:
            x, y, w, h = box
            bbx_center_coord.append((x + w / 2, y + h / 2))
        return bbx_center_coord

    @staticmethod
    def _decoding_bytes_to_img(img_bytes: bytes) -> np.array:
        array_data = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(array_data, cv2.IMREAD_COLOR)
        return img

    @staticmethod
    def convert_local_to_global_coord_img(
            img_full_page: np.ndarray,
            img_captcha: np.ndarray,
            local_coord_cell_center: list[tuple[float, float], ...]
    ):
        result = cv2.matchTemplate(img_full_page, img_captcha, cv2.TM_CCOEFF_NORMED)
        _, _, _, max_loc = cv2.minMaxLoc(result)
        transform_matrix = np.array([[1, 0, max_loc[0]], [0, 1, max_loc[1]]], dtype=np.float32)

        global_captcha_coord = []
        for loc_coord in local_coord_cell_center:
            x, y = loc_coord
            point_local = np.array([x, y], dtype=np.float32).reshape(1, 1, -1)
            point_global = cv2.transform(point_local, transform_matrix)
            global_captcha_coord.append((point_global[0, 0, 0], point_global[0, 0, 1]))
        return global_captcha_coord
