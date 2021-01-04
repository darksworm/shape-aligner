import math
from typing import List

import numpy

PolygonPointsList = List[List[int]]


class Polygon:
    def __init__(self, points: PolygonPointsList):
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
        return self._points_matrix.min(axis=0, initial=None).tolist()

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

    def area(self) -> float:
        x, y = zip(*self._points_matrix)
        result = 0.5 * (numpy.dot(x, numpy.roll(y, 1)) - numpy.dot(y, numpy.roll(x, 1)))
        return abs(result)


class PolygonPiece:
    def __init__(self, polygon: Polygon, position: List[int]):
        self._polygon = polygon
        self._position = position

    def get_position(self):
        return self._position

    def get_polygon(self):
        return self._polygon

    def get_points_in_plane(self) -> numpy.ndarray:
        return self._polygon.get_points() + self._position


class Board(PolygonPiece):
    def intersection_area(self, piece: PolygonPiece) -> float:
        polygons_points = self._get_intersection_polygons_points(piece)
        polygons = [Polygon(points) for points in polygons_points]
        polygon_areas = [polygon.area() for polygon in polygons]
        return sum(polygon_areas)

    def _get_intersection_polygons_points(self, clip: PolygonPiece) -> List[PolygonPointsList]:
        # don't import this globally to avoid use of it outside of this method
        import pyclipper

        clipper = pyclipper.Pyclipper()
        clipper.AddPath(self.get_points_in_plane(), pyclipper.PT_SUBJECT, True)
        clipper.AddPath(clip.get_points_in_plane(), pyclipper.PT_CLIP, True)

        return clipper.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)
