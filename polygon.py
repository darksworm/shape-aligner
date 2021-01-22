import math
from typing import List

import numpy

PolygonPointsList = List[List[float]]


class Polygon:
    def __init__(self, points: PolygonPointsList):
        self._points_matrix = numpy.array(points)

    def get_points(self) -> numpy.ndarray:
        return self._points_matrix

    def rotate(self, degrees: float) -> None:
        if self._rotation_result_same_as_current_state(degrees):
            return

        self._points_matrix = self._get_rotated_points(degrees)
        self.move_to_quadrant_one()

    def flip(self) -> None:
        self.rotate(-90)
        self._points_matrix = numpy.flip(self._points_matrix)
        self._points_matrix = self._points_matrix - self.get_centroid_point()
        self.move_to_quadrant_one()

    def _get_point_count(self) -> int:
        return len(self._points_matrix)

    def _get_point_sum(self) -> numpy.ndarray:
        return self._points_matrix.sum(axis=0)

    def get_centroid_point(self) -> numpy.ndarray:
        return self._get_point_sum() / [self._get_point_count(), self._get_point_count()]

    def _get_point_min(self) -> List[float]:
        return self._points_matrix.min(axis=0, initial=None).tolist()

    def move_to_quadrant_one(self) -> None:
        minimums = self._get_point_min()

        point_adjustment = [
            0 if minimums[0] >= 0 else -minimums[0],
            0 if minimums[1] >= 0 else -minimums[1]
        ]

        self._points_matrix = self._points_matrix + point_adjustment

    @staticmethod
    def _get_clockwise_rotation_matrix_for_degrees(degrees: float) -> numpy.ndarray:
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

    def _get_rotated_points(self, degrees: float) -> numpy.ndarray:
        centroid_matrix = numpy.array(self.get_centroid_point())
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

    def get_center_in_plane(self) -> List:
        centroid_position = self._polygon.get_centroid_point()
        centroid_in_plane = numpy.array(self.get_position()) + centroid_position
        return centroid_in_plane

    def move(self, x: int, y: int):
        self._position = [
            self._position[0] + x,
            self._position[1] + y,
        ]

    def get_center_distance_from(self, x, y):
        centroid_in_plane = self.get_center_in_plane()
        distance = numpy.subtract([x, y], centroid_in_plane)
        return numpy.abs(distance)


class PolygonIntersector:
    def intersection_area(self, subject: iter, clip: iter) -> float:
        polygons = self.intersection_polygons(subject, clip)
        return sum([polygon.area() for polygon in polygons])

    def intersection_polygons(self, subject: iter, clip: iter) -> List[Polygon]:
        polygons_points = self._get_intersections(subject, clip)
        return [Polygon(points) for points in polygons_points]

    @staticmethod
    def _get_intersections(subject: iter, clip: iter) -> List[PolygonPointsList]:
        # don't import this globally to avoid use of it outside of this method
        import pyclipper

        clipper = pyclipper.Pyclipper()

        try:
            clipper.AddPath(subject, pyclipper.PT_SUBJECT, True)
        except pyclipper.ClipperException:
            return []

        try:
            clipper.AddPath(clip, pyclipper.PT_CLIP, True)
        except pyclipper.ClipperException:
            return []

        return clipper.Execute(pyclipper.CT_INTERSECTION, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD)


class Board(PolygonPiece):
    pass


class Level:
    def __init__(self, board: Board, pieces: List[PolygonPiece], intersector: PolygonIntersector):
        self._board = board
        self._pieces = pieces
        self._intersector = intersector

    def _get_pieces_skipping_these_indexes(self, skip_indexes: List[int]):
        pieces = []
        for piece_index, piece in enumerate(self._pieces):
            if piece_index not in skip_indexes:
                pieces.append(piece)
        return pieces

    @staticmethod
    def _sum_piece_areas(pieces: List[PolygonPiece]):
        return sum([p.get_polygon().area() for p in pieces])

    def _get_intersections_one_to_one(self, subject: PolygonPiece, clip: PolygonPiece):
        intersections = self._intersector.intersection_polygons(
            subject.get_points_in_plane(),
            clip.get_points_in_plane()
        )
        return [PolygonPiece(i, [0, 0]) for i in intersections]

    def _get_intersections_one_to_many(self, subject: PolygonPiece, clips: List[PolygonPiece]):
        intersections = []
        for clip in clips:
            intersections += self._get_intersections_one_to_one(subject, clip)

        return intersections

    def _get_intersections_many_to_many(self, subjects: List[PolygonPiece], clips: List[PolygonPiece]):
        intersections = []
        for subject in subjects:
            intersections += self._get_intersections_one_to_many(subject, clips)

        return intersections

    def get_completion_percentage(self):
        covered_area = 0
        checked_piece_indexes = []

        for piece_index, piece in enumerate(self._pieces):
            board_intersections = self._get_intersections_one_to_one(self._board, piece)
            checked_piece_indexes.append(piece_index)

            covered_area += self._sum_piece_areas(board_intersections)
            other_pieces = self._get_pieces_skipping_these_indexes(checked_piece_indexes)

            # this will break in cases where multiple polygons share an intersection
            other_piece_intersections = self._get_intersections_many_to_many(board_intersections, other_pieces)
            covered_area -= self._sum_piece_areas(other_piece_intersections)

        board_area = self._board.get_polygon().area()
        return covered_area / board_area * 100 if covered_area > 0 else 0

    def get_board(self) -> Board:
        return self._board

    def get_pieces(self):
        return self._pieces
