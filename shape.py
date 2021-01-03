import math
from typing import List

import numpy


class Shape:
    def __init__(self, points: List[List[int]]):
        self._points_matrix = numpy.array(points)
        self._move_to_quadrant_one()

    def get_points(self) -> numpy.ndarray:
        return self._points_matrix

    def rotate(self, degrees: int) -> None:
        if self._rotation_result_same_as_current_state(degrees):
            return

        self._points_matrix = self._get_rotated_points(degrees)
        self._move_to_quadrant_one()

    def flip(self) -> None:
        self.rotate(-90)
        self._points_matrix = numpy.flip(self._points_matrix)
        self._points_matrix = self._points_matrix - self._get_centroid_point()
        self._move_to_quadrant_one()

    def _get_point_count(self) -> int:
        return len(self._points_matrix)

    def _get_point_sum(self) -> numpy.ndarray:
        return self._points_matrix.sum(axis=0)

    def _get_centroid_point(self) -> numpy.ndarray:
        return self._get_point_sum() / [self._get_point_count(), self._get_point_count()]

    def _get_point_min(self) -> List[float]:
        return self._points_matrix.min(axis=0, initial=None)

    def _move_to_quadrant_one(self) -> None:
        minimums = self._get_point_min()

        point_adjustment = [
            0 if minimums[0] >= 0 else -minimums[0],
            0 if minimums[1] >= 0 else -minimums[1]
        ]

        self._points_matrix = self._points_matrix + point_adjustment

    @staticmethod
    def _get_clockwise_rotation_matrix_for_degrees(degrees: int) -> numpy.ndarray:
        theta = math.radians(degrees)
        cos_angle = math.cos(theta)
        sin_angle = math.sin(theta)

        return numpy.array([
            [cos_angle, sin_angle],
            [-sin_angle, cos_angle]
        ])

    def _apply_rotation(self, centroid_matrix: numpy.ndarray, rotation_matrix: numpy.ndarray) -> numpy.ndarray:
        centroid_subtracted = self._points_matrix - centroid_matrix
        rotation_applied = centroid_subtracted.dot(rotation_matrix)
        return rotation_applied + centroid_matrix

    def _get_rotated_points(self, degrees: int) -> numpy.ndarray:
        centroid_matrix = numpy.array(self._get_centroid_point())
        rotation_matrix = self._get_clockwise_rotation_matrix_for_degrees(degrees)
        return self._apply_rotation(centroid_matrix, rotation_matrix)

    @staticmethod
    def _rotation_result_same_as_current_state(degrees) -> bool:
        return degrees % 360 == 0
