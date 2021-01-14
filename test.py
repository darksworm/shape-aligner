import math
import random
import unittest
from math import atan2
from random import randrange

import numpy
from parameterized import parameterized

from polygon import Polygon, Board, PolygonPiece, Level, PolygonIntersector

HUNDRED_THOUSAND = 100000
TEST_CHUNK_SIZE = 100


class PolygonGenerator:
    def __init__(self, point_rng: callable):
        self.point_rng = point_rng

    def random_convex_polygon_points(self, vertices_count):
        """
        Port of Valtr algorithm by Sander Verdonschot.

        Reference:
            http://cglab.ca/~sander/misc/ConvexGeneration/ValtrAlgorithm.java
        """
        x_points = sorted([self.point_rng() for _ in range(vertices_count)])
        y_points = sorted([self.point_rng() for _ in range(vertices_count)])

        min_x, *x_points, max_x = x_points
        min_y, *y_points, max_y = y_points

        x_vectors = self._to_vectors_coordinates(x_points, min_x, max_x)
        y_vectors = self._to_vectors_coordinates(y_points, min_y, max_y)

        random.shuffle(y_vectors)

        vectors = sorted(zip(x_vectors, y_vectors), key=lambda vector: atan2(vector[0], vector[1]))

        point_x = point_y = 0
        min_polygon_x = min_polygon_y = 0
        points = []

        for vector_x, vector_y in vectors:
            points.append((point_x, point_y))
            point_x += vector_x
            point_y += vector_y
            min_polygon_x = min(min_polygon_x, point_x)
            min_polygon_y = min(min_polygon_y, point_y)
        shift_x, shift_y = min_x - min_polygon_x, min_y - min_polygon_y

        return [[point_x + shift_x, point_y + shift_y]
                for point_x, point_y in points]

    def _to_vectors_coordinates(self, coordinates, min_coordinate, max_coordinate):
        last_min = last_max = min_coordinate
        result = []
        for coordinate in coordinates:
            if random.getrandbits(1):
                result.append(coordinate - last_min)
                last_min = coordinate
            else:
                result.append(last_max - coordinate)
                last_max = coordinate
        result.extend((max_coordinate - last_min,
                       last_max - max_coordinate))
        return result


def random_polygon_points(count: int):
    generator = PolygonGenerator(lambda: random.randint(1, 500))
    return [
        generator.random_convex_polygon_points(random.randint(3, 12))
        for _ in range(count)
    ]


def random_position():
    return [
        randrange(-HUNDRED_THOUSAND, HUNDRED_THOUSAND),
        randrange(-HUNDRED_THOUSAND, HUNDRED_THOUSAND),
    ]


class TestPolygonGenerator(unittest.TestCase):
    @parameterized.expand(random_polygon_points(1000))
    def test_convex_generator_outputs_polygons_with_180_deg_or_less_internal_angles(self, *points):
        points = list(points)
        for i in range(-1, len(points) - 1):
            first_point = points[i]
            second_point = points[i + 1]
            dot_product = numpy.array(first_point).dot(second_point)

            def square(p):
                return math.pow(p, 2)

            magnitude = math.sqrt(sum(map(square, first_point))) * math.sqrt(sum(map(square, second_point)))
            angle = dot_product / magnitude

            if angle > 1:
                self.assertAlmostEqual(1, angle)
                angle = 1

            degrees = math.degrees(math.acos(angle))
            self.assertLessEqual(degrees, 180)


class TestPolygon(unittest.TestCase):
    def setUp(self) -> None:
        self.square_points = [
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1]
        ]

    def test_polygon_created_with_points_list(self):
        Polygon(self.square_points)

    def test_polygon_returns_points(self):
        polygon = Polygon(self.square_points.copy())
        self.assertEqual(polygon.get_points().tolist(), self.square_points)


class TestPolygonRotations(unittest.TestCase):
    def setUp(self) -> None:
        self.square_points = [
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1]
        ]

        self.vertical_rectangle_points = [
            [0, 0],
            [1, 0],
            [1, 3],
            [0, 3]
        ]

    @parameterized.expand([
        [0], [360], [-360], [720], [-5760]
    ])
    def test_rotate_360_doesnt_change_points(self, rotation):
        polygon = Polygon(self.vertical_rectangle_points.copy())
        polygon.rotate(rotation)
        rotated = [[round(p[0]), round(p[1])] for p in polygon.get_points()]
        self.assertEqual(self.vertical_rectangle_points, rotated)

    @parameterized.expand([
        [randrange(-HUNDRED_THOUSAND, HUNDRED_THOUSAND)] for _ in range(1, TEST_CHUNK_SIZE)
    ])
    def test_polygon_rotate_doesnt_result_in_negative_coords(self, rotation):
        polygon = Polygon(self.vertical_rectangle_points.copy())
        polygon.rotate(rotation)

        for point in polygon.get_points():
            self.assertGreaterEqual(point[0], 0)
            self.assertGreaterEqual(point[1], 0)

    @parameterized.expand([
        [90], [-90], [180], [360], [-180], [-360], [720], [-720]
    ])
    def test_rotate_square_has_same_points(self, rotation):
        polygon = Polygon(self.square_points.copy())
        polygon.rotate(rotation)
        rotated = [[round(p[0]), round(p[1])] for p in polygon.get_points()]

        for point in self.square_points:
            self.assertIn(point, rotated)

    @parameterized.expand([
        [randrange(-HUNDRED_THOUSAND, HUNDRED_THOUSAND)] for _ in range(1, TEST_CHUNK_SIZE)
    ])
    def test_rotate_and_rotate_back_returns_to_starting_points(self, rotation):
        polygon = Polygon(self.square_points.copy())
        polygon.rotate(rotation)
        polygon.rotate(-rotation)

        rotated = [[round(p[0]), round(p[1])] for p in polygon.get_points()]

        self.assertEqual(self.square_points, rotated)


class TestPolygonFlip(unittest.TestCase):
    def setUp(self) -> None:
        self.square_points = [
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1]
        ]

        self.vertical_rectangle_points = [
            [0, 0],
            [1, 0],
            [1, 3],
            [0, 3]
        ]

    def test_flip_square_has_same_points(self):
        polygon = Polygon(self.square_points.copy())
        polygon.flip()
        rotated = [[round(p[0]), round(p[1])] for p in polygon.get_points()]

        for point in self.square_points:
            self.assertIn(point, rotated)

    @parameterized.expand(random_polygon_points(1))
    def test_flip_polygon_point_count_doesnt_change(self, *points):
        points = list(points)
        poly = Polygon(points.copy())
        poly.flip()

        self.assertEqual(len(points), len(poly.get_points()))

    @parameterized.expand(random_polygon_points(TEST_CHUNK_SIZE))
    def test_flip_polygon_point_order_changes(self, *points):
        points = list(points)
        poly = Polygon(points.copy())
        poly.flip()
        flipped = [[round(p[0]), round(p[1])] for p in poly.get_points()]

        self.assertNotEqual(points, flipped)

    @parameterized.expand(random_polygon_points(TEST_CHUNK_SIZE))
    def test_flip_twice_doesnt_change_surface_area(self, *points):
        points = list(points)
        poly = Polygon(points.copy())
        poly.flip()
        poly.flip()

        self.assertEqual(poly.area(), poly.area())

    def test_polygon_flip_doesnt_result_in_negative_coords(self):
        polygon = Polygon(self.vertical_rectangle_points.copy())
        polygon.flip()

        for point in polygon.get_points():
            self.assertGreaterEqual(point[0], 0)
            self.assertGreaterEqual(point[1], 0)


class TestPolygonPiece(unittest.TestCase):
    def test_construct(self):
        PolygonPiece(Polygon([[0, 0], [0, 10], [10, 0], [10, 10]]), [0, 0])

    def test_get_position_returns_value_passed_in_construct(self):
        position = [12, 543]
        piece = PolygonPiece(Polygon([[0, 0], [0, 10], [10, 0], [10, 10]]), position.copy())
        self.assertEqual(position, piece.get_position())

    def test_polygon_used(self):
        polygon = Polygon([[0, 0], [0, 10], [10, 0], [10, 10]])
        piece = PolygonPiece(polygon, [1, 2])
        self.assertEqual(polygon, piece.get_polygon())

    @parameterized.expand(random_polygon_points(TEST_CHUNK_SIZE))
    def test_points_same_as_poly_if_position_zero(self, *points):
        points = list(points)
        polygon = Polygon(points.copy())
        piece = PolygonPiece(polygon, [0, 0])
        self.assertEqual(polygon.get_points().tolist(), piece.get_points_in_plane().tolist())

    @parameterized.expand([
        [randrange(-HUNDRED_THOUSAND, HUNDRED_THOUSAND), randrange(-HUNDRED_THOUSAND, HUNDRED_THOUSAND)] for _ in
        range(TEST_CHUNK_SIZE)
    ])
    def test_points_not_same_as_poly_if_position_not_zero(self, *position):
        position = list(position)
        polygon = Polygon([[0, 0], [0, 10], [10, 0], [10, 10]])
        piece = PolygonPiece(polygon, position)
        self.assertNotEqual(polygon.get_points().tolist(), piece.get_points_in_plane().tolist())

    @parameterized.expand([
        [randrange(1, HUNDRED_THOUSAND), randrange(1, HUNDRED_THOUSAND)] for _ in range(TEST_CHUNK_SIZE)
    ])
    def test_points_dont_decrease_with_positive_position(self, *position):
        position = list(position)
        polygon = Polygon([[0, 0], [0, 10], [10, 0], [10, 10]])
        piece = PolygonPiece(polygon, position)
        self.assertGreaterEqual(piece.get_points_in_plane().sum(), polygon.get_points().sum())

    @parameterized.expand([
        [randrange(-HUNDRED_THOUSAND, -1), randrange(-HUNDRED_THOUSAND, -1)] for _ in range(TEST_CHUNK_SIZE)
    ])
    def test_points_dont_increase_with_positive_position(self, *position):
        position = list(position)
        polygon = Polygon([[0, 0], [0, 10], [10, 0], [10, 10]])
        piece = PolygonPiece(polygon, position)
        self.assertLessEqual(piece.get_points_in_plane().sum(), polygon.get_points().sum())

    @parameterized.expand([
        [randrange(0, HUNDRED_THOUSAND), randrange(0, HUNDRED_THOUSAND)] for _ in range(TEST_CHUNK_SIZE)
    ])
    def test_move_nonnegative_amount_doesnt_decrease_position(self, x, y):
        starting_position = [125, 123]
        piece = PolygonPiece(Polygon([[0, 0], [3, 3], [0, 3]]), starting_position.copy())
        piece.move(x, y)
        self.assertGreaterEqual(piece.get_position(), starting_position)

    @parameterized.expand([
        [randrange(-HUNDRED_THOUSAND, -1), randrange(-HUNDRED_THOUSAND, -1)] for _ in range(TEST_CHUNK_SIZE)
    ])
    def test_move_negative_amount_doesnt_increase_position(self, x, y):
        starting_position = [125, 123]
        piece = PolygonPiece(Polygon([[0, 0], [3, 3], [0, 3]]), starting_position.copy())
        piece.move(x, y)
        self.assertLessEqual(piece.get_position(), starting_position)

    def test_move_zeroes_doesnt_change_position(self):
        starting_position = [125, 123]
        piece = PolygonPiece(Polygon([[0, 0], [3, 3], [0, 3]]), starting_position.copy())
        piece.move(0, 0)
        self.assertEqual(starting_position, piece.get_position())

    def test_get_center_distance_from_returns_array_with_two_numbers(self):
        piece = PolygonPiece(Polygon([[0, 0], [3, 3], [0, 3]]), [125, 30])
        distance = piece.get_center_distance_from(250, 300)
        self.assertEqual(2, len(distance))

    def test_get_center_distance_from_returns_0_if_centroid_in_same_point(self):
        polygon = Polygon([[0, 0], [3, 3], [0, 3]])
        polygon.get_centroid_point = lambda: [1337, 1337]

        piece = PolygonPiece(polygon, [0, 0])
        distance = piece.get_center_distance_from(1337, 1337)

        self.assertEqual(0, distance[0])
        self.assertEqual(0, distance[1])

    def test_get_center_distance_from_doesnt_return_0_if_centroid_in_different_point(self):
        polygon = Polygon([[0, 0], [3, 3], [0, 3]])
        polygon.get_centroid_point = lambda: [51, 33]

        piece = PolygonPiece(polygon, [0, 0])
        distance = piece.get_center_distance_from(1337, 1337)

        self.assertNotEqual(0, distance[0])
        self.assertNotEqual(0, distance[1])

    def test_get_center_distance_from_is_affected_by_polygon_piece_position(self):
        polygon = Polygon([[0, 0], [3, 3], [0, 3]])

        piece1 = PolygonPiece(polygon, [0, 0])
        piece2 = PolygonPiece(polygon, [15, 66])

        p1pts = piece1.get_center_distance_from(0, 0)
        p2pts = piece2.get_center_distance_from(0, 0)

        self.assertFalse(all(a == b for a, b in zip(p1pts, p2pts)))

    def test_get_distance_from_returns_positive_vals(self):
        polygon = Polygon([[0, 0], [3, 3], [0, 3]])
        piece1 = PolygonPiece(polygon, [1233, 12312])
        self.assertTrue(all(a > 0 for a in piece1.get_center_distance_from(0, 0)))
        piece2 = PolygonPiece(polygon, [-1233, -12312])
        self.assertTrue(all(a > 0 for a in piece2.get_center_distance_from(0, 0)))


class TestPolygonArea(unittest.TestCase):
    def test_square_area_correct(self):
        points = [[0, 0], [0, 1], [1, 1], [1, 0]]
        expected_area = 1
        poly = Polygon(points)
        self.assertEqual(expected_area, poly.area())

    def test_rectangle_area_correct(self):
        points = [[0, 0], [0, 3], [1, 3], [1, 0]]
        expected_area = 3
        poly = Polygon(points)
        self.assertEqual(expected_area, poly.area())

    def test_right_angle_triangle_area_correct(self):
        points = [[1, 1], [3, 3], [3, 1]]
        expected_area = 2
        poly = Polygon(points)
        self.assertEqual(expected_area, poly.area())


class TestIntersector(unittest.TestCase):
    def test_construct(self):
        Board(Polygon([[0, 0], [0, 1000], [1000, 0], [1000, 1000]]), [0, 0])
        PolygonIntersector()

    def test_get_intersection_area_same_as_piece_if_fully_submerged(self):
        board = Board(Polygon([[0, 0], [0, 1000], [1000, 1000], [1000, 0]]), [0, 0])
        piece = PolygonPiece(Polygon([[0, 0], [100, 100], [100, 0]]), [50, 50])
        actual_area = PolygonIntersector().intersection_area(board.get_points_in_plane(), piece.get_points_in_plane())
        self.assertEqual(piece.get_polygon().area(), actual_area)

    def test_get_intersection_zero_if_poly_on_a_different_planet(self):
        board = Board(Polygon([[0, 0], [0, 1000], [1000, 0], [1000, 1000]]), [0, 0])
        piece = PolygonPiece(Polygon([[0, 0], [100, 100], [100, 0]]), [5000, 5000])
        actual_area = PolygonIntersector().intersection_area(board.get_points_in_plane(), piece.get_points_in_plane())
        self.assertEqual(0, actual_area)

    def test_get_intersection_area_same_if_poly_same_size(self):
        board = Board(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        piece = PolygonPiece(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        actual_area = PolygonIntersector().intersection_area(board.get_points_in_plane(), piece.get_points_in_plane())
        self.assertEqual(piece.get_polygon().area(), actual_area)

    def test_intersection_half_of_square(self):
        board = Board(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        piece = PolygonPiece(Polygon([[0, 0], [0, 100], [100, 100], [100, 0]]), [0, 0])
        actual_area = PolygonIntersector().intersection_area(board.get_points_in_plane(), piece.get_points_in_plane())
        self.assertEqual(piece.get_polygon().area() / 2, actual_area)


class TestLevel(unittest.TestCase):
    def test_board_coverage_with_piece_same_size_as_board_is_100_percent(self):
        board = Board(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        piece = PolygonPiece(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        level = Level(board, [piece], PolygonIntersector())
        self.assertEqual(100, level.get_completion_percentage())

    @parameterized.expand(random_polygon_points(TEST_CHUNK_SIZE))
    def test_board_coverage_not_negative(self, *points):
        piece = PolygonPiece(Polygon(list(points)), random_position())
        board = Board(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        level = Level(board, [piece], PolygonIntersector())
        actual_coverage = level.get_completion_percentage()
        self.assertGreaterEqual(0, actual_coverage)

    def test_board_with_no_pieces_has_zero_coverage(self):
        board = Board(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        level = Level(board, [], PolygonIntersector())
        self.assertEqual(0, level.get_completion_percentage())

    @parameterized.expand(random_polygon_points(TEST_CHUNK_SIZE))
    def test_two_fully_overlapping_pieces_serve_same_board_coverage(self, *points):
        piece = PolygonPiece(Polygon(list(points)), [0, 0])
        board = Board(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        level = Level(board, [piece], PolygonIntersector())
        coverage_with_one_piece = level.get_completion_percentage()
        level = Level(board, [piece, piece], PolygonIntersector())
        coverage_with_two_pieces = level.get_completion_percentage()
        self.assertAlmostEqual(coverage_with_one_piece, coverage_with_two_pieces, delta=1)

    @parameterized.expand(random_polygon_points(TEST_CHUNK_SIZE))
    def test_adding_a_piece_does_not_decrease_coverage(self, *points):
        piece = PolygonPiece(Polygon(list(points)), [0, 0])
        piece1 = PolygonPiece(Polygon(random_polygon_points(1)[0]), [0, 0])
        board = Board(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        intersector = PolygonIntersector()
        level = Level(board, [piece], intersector)
        coverage_with_one_piece = level.get_completion_percentage()
        level = Level(board, [piece, piece1], intersector)
        coverage_with_two_pieces = level.get_completion_percentage()
        if len(intersector.intersection_polygons(piece.get_points_in_plane(), piece1.get_points_in_plane())) == 0:
            self.assertGreaterEqual(coverage_with_two_pieces, coverage_with_one_piece)
        else:
            coverage_almost_equal = abs(coverage_with_two_pieces - coverage_with_one_piece) <= 1
            two_piece_coverage_greater_equal = coverage_with_two_pieces >= coverage_with_one_piece
            self.assertTrue(two_piece_coverage_greater_equal or coverage_almost_equal)

    def test_get_board_returns_board(self):
        board = Board(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        intersector = PolygonIntersector()
        level = Level(board, [], intersector)
        self.assertEqual(board, level.get_board())

    def test_get_pieces_returns_pieces(self):
        board = Board(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        pieces = [
            PolygonPiece(Polygon(random_polygon_points(1)[0]), [0, 0]),
            PolygonPiece(Polygon(random_polygon_points(1)[0]), [0, 0]),
            PolygonPiece(Polygon(random_polygon_points(1)[0]), [0, 0])
        ]
        intersector = PolygonIntersector()
        level = Level(board, pieces, intersector)
        self.assertEqual(pieces, level.get_pieces())
