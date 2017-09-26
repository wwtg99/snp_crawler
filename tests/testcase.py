import unittest
from snp_crawler.item_generators import IdGenerator


class CrawlerTest(unittest.TestCase):

    def test_id_generator(self):
        # string ids
        generator = IdGenerator(ids='aa,bb,cc')
        n = 0
        for res in generator.generate():
            self.assertEqual(['aa', 'bb', 'cc'], res)
            n += 1
        self.assertEqual(1, n)
        # list ids
        generator = IdGenerator(ids=['aa', 'bb', 'cc'])
        n = 0
        for res in generator.generate():
            self.assertEqual(['aa', 'bb', 'cc'], res)
            n += 1
        self.assertEqual(1, n)
        # list ids with batch_num
        generator = IdGenerator(ids=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], batch_num=3)
        n = 0
        arr = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]
        for res in generator.generate():
            self.assertEqual(arr[n], res)
            n += 1
        self.assertEqual(len(arr), n)
        # list ids with large batch_num
        generator = IdGenerator(ids=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], batch_num=20)
        n = 0
        arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for res in generator.generate():
            self.assertEqual(arr, res)
            n += 1
        self.assertEqual(1, n)
        # list ids with invalid batch_num
        generator = IdGenerator(ids=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], batch_num=0)
        n = 0
        arr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        for res in generator.generate():
            self.assertEqual(arr, res)
            n += 1
        self.assertEqual(1, n)

if __name__ == '__main__':
    unittest.main()
