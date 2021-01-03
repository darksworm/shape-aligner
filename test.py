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

        self.vertical_rectangle_points = [
            [0, 0],
            [1, 0],
            [1, 3],
            [0, 3]
        ]

    def test_shape_created_with_points_list(self):
        Shape(self.square_points)

    def test_shape_returns_points(self):
        shape = Shape(self.square_points.copy())
        self.assertEqual(shape.get_points().tolist(), self.square_points)

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
