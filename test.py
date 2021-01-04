import unittest
from random import randrange

from parameterized import parameterized

from polygon import Polygon, Board, PolygonPiece


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
        [randrange(-192834, 135783)] for _ in range(1, 300)
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
        [randrange(-192834, 135783)] for _ in range(1, 300)
    ])
    def test_rotate_and_rotate_back_returns_to_starting_points(self, rotation):
        polygon = Polygon(self.square_points.copy())
        polygon.rotate(rotation)
        polygon.rotate(-rotation)

        rotated = [[round(p[0]), round(p[1])] for p in polygon.get_points()]

        self.assertEqual(self.square_points, rotated)


def random_polygon_points(count: int):
    return [
        [
            [
                randrange(600, 700), randrange(600, 700)
            ]
            for _ in range(randrange(3, 12))
        ]
        for _ in range(count)
    ]


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

    @parameterized.expand(random_polygon_points(300))
    def test_flip_polygon_point_order_changes(self, *points):
        points = list(points)
        poly = Polygon(points.copy())
        poly.flip()
        flipped = [[round(p[0]), round(p[1])] for p in poly.get_points()]

        self.assertNotEqual(points, flipped)

    @parameterized.expand(random_polygon_points(300))
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

    @parameterized.expand(random_polygon_points(300))
    def test_points_same_as_poly_if_position_zero(self, *points):
        points = list(points)
        polygon = Polygon(points.copy())
        piece = PolygonPiece(polygon, [0, 0])
        self.assertEqual(polygon.get_points().tolist(), piece.get_points_in_plane().tolist())

    @parameterized.expand([
        [randrange(-192834, 135783), randrange(-192834, 135783)] for _ in range(300)
    ])
    def test_points_not_same_as_poly_if_position_not_zero(self, *position):
        position = list(position)
        polygon = Polygon([[0, 0], [0, 10], [10, 0], [10, 10]])
        piece = PolygonPiece(polygon, position)
        self.assertNotEqual(polygon.get_points().tolist(), piece.get_points_in_plane().tolist())

    @parameterized.expand([
        [randrange(1, 135783), randrange(1, 135783)] for _ in range(300)
    ])
    def test_points_dont_decrease_with_positive_position(self, *position):
        position = list(position)
        polygon = Polygon([[0, 0], [0, 10], [10, 0], [10, 10]])
        piece = PolygonPiece(polygon, position)
        self.assertGreaterEqual(piece.get_points_in_plane().sum(), polygon.get_points().sum())

    @parameterized.expand([
        [randrange(-123123, -1), randrange(-123123, -1)] for _ in range(300)
    ])
    def test_points_dont_increase_with_positive_position(self, *position):
        position = list(position)
        polygon = Polygon([[0, 0], [0, 10], [10, 0], [10, 10]])
        piece = PolygonPiece(polygon, position)
        self.assertLessEqual(piece.get_points_in_plane().sum(), polygon.get_points().sum())


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


class TestGameBoard(unittest.TestCase):
    def test_construct(self):
        Board(Polygon([[0, 0], [0, 1000], [1000, 0], [1000, 1000]]), [0, 0])

    def test_get_intersection_area_same_as_piece_if_fully_submerged(self):
        board = Board(Polygon([[0, 0], [0, 1000], [1000, 1000], [1000, 0]]), [0, 0])
        piece = PolygonPiece(Polygon([[0, 0], [100, 100], [100, 0]]), [50, 50])
        self.assertEqual(piece.get_polygon().area(), board.intersection_area(piece))

    def test_get_intersection_zero_if_poly_on_a_different_planet(self):
        board = Board(Polygon([[0, 0], [0, 1000], [1000, 0], [1000, 1000]]), [0, 0])
        piece = PolygonPiece(Polygon([[0, 0], [100, 100], [100, 0]]), [5000, 5000])
        self.assertEqual(0, board.intersection_area(piece))

    def test_get_intersection_area_same_if_poly_same_size(self):
        board = Board(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        piece = PolygonPiece(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        self.assertEqual(piece.get_polygon().area(), board.intersection_area(piece))

    def test_intersection_half_of_square(self):
        board = Board(Polygon([[0, 0], [100, 100], [100, 0]]), [0, 0])
        piece = PolygonPiece(Polygon([[0, 0], [0, 100], [100, 100], [100, 0]]), [0, 0])
        self.assertEqual(piece.get_polygon().area() / 2, board.intersection_area(piece))
