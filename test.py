import unittest
from random import randrange

from parameterized import parameterized

from shape import Shape


class TestShape(unittest.TestCase):
    def setUp(self) -> None:
        self.square_points = [
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1]
        ]

    def test_shape_created_with_points_list(self):
        Shape(self.square_points)

    def test_shape_returns_points(self):
        shape = Shape(self.square_points.copy())
        self.assertEqual(shape.get_points().tolist(), self.square_points)


class TestShapeRotations(unittest.TestCase):
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
        shape = Shape(self.vertical_rectangle_points.copy())
        shape.rotate(rotation)
        rotated = [[round(p[0]), round(p[1])] for p in shape.get_points()]
        self.assertEqual(self.vertical_rectangle_points, rotated)

    @parameterized.expand([
        [randrange(-192834, 135783)] for _ in range(1, 300)
    ])
    def test_shape_rotate_doesnt_result_in_negative_coords(self, rotation):
        shape = Shape(self.vertical_rectangle_points.copy())
        shape.rotate(rotation)

        for point in shape.get_points():
            self.assertGreaterEqual(point[0], 0)
            self.assertGreaterEqual(point[1], 0)

    @parameterized.expand([
        [90], [-90], [180], [360], [-180], [-360], [720], [-720]
    ])
    def test_rotate_square_has_same_points(self, rotation):
        shape = Shape(self.square_points.copy())
        shape.rotate(rotation)
        rotated = [[round(p[0]), round(p[1])] for p in shape.get_points()]

        for point in self.square_points:
            self.assertIn(point, rotated)

    @parameterized.expand([
        [randrange(-192834, 135783)] for _ in range(1, 300)
    ])
    def test_rotate_and_rotate_back_returns_to_starting_points(self, rotation):
        shape = Shape(self.square_points.copy())
        shape.rotate(rotation)
        shape.rotate(-rotation)

        rotated = [[round(p[0]), round(p[1])] for p in shape.get_points()]

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


class TestShapeFlip(unittest.TestCase):
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
        shape = Shape(self.square_points.copy())
        shape.flip()
        rotated = [[round(p[0]), round(p[1])] for p in shape.get_points()]

        for point in self.square_points:
            self.assertIn(point, rotated)

    @parameterized.expand(random_polygon_points(1))
    def test_flip_polygon_point_count_doesnt_change(self, *points):
        points = list(points)
        poly = Shape(points.copy())
        poly.flip()

        self.assertEqual(len(points), len(poly.get_points()))

    @parameterized.expand(random_polygon_points(300))
    def test_flip_polygon_point_order_changes(self, *points):
        points = list(points)
        poly = Shape(points.copy())
        poly.flip()
        flipped = [[round(p[0]), round(p[1])] for p in poly.get_points()]

        self.assertNotEqual(points, flipped)

    @parameterized.expand(random_polygon_points(300))
    def test_flip_twice_doesnt_change_surface_area(self, *points):
        def poly_area(corners):
            point_count = len(corners)
            area = 0.0
            for i in range(point_count):
                j = (i + 1) % point_count
                area += corners[i][0] * corners[j][1]
                area -= corners[j][0] * corners[i][1]
            area = abs(area) / 2.0
            return area

        points = list(points)
        poly = Shape(points.copy())
        poly.flip()
        poly.flip()
        flipped = [[int(round(p[0])), int(round(p[1]))] for p in poly.get_points()]

        self.assertEqual(poly_area(points), poly_area(flipped))

    def test_shape_flip_doesnt_result_in_negative_coords(self):
        shape = Shape(self.vertical_rectangle_points.copy())
        shape.flip()

        for point in shape.get_points():
            self.assertGreaterEqual(point[0], 0)
            self.assertGreaterEqual(point[1], 0)
