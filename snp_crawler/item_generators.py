import os
from scrapy.exceptions import CloseSpider
import glob


class GeneratorFactory(object):
    """
    Generator factory.
    """
    @classmethod
    def get_generator(cls, spider, **kwargs):
        """
        Get generator depends on params.
        :param spider:
        :param kwargs:
        :return:
        """
        if 'id' in kwargs:
            return GeneratorFactory.get_generator_by_name('id', spider, **kwargs)
        elif 'rs' in kwargs:
            return GeneratorFactory.get_generator_by_name('rs', spider, **kwargs)
        elif 'file' in kwargs:
            return GeneratorFactory.get_generator_by_name('file', spider, **kwargs)
        elif 'bed' in kwargs:
            return GeneratorFactory.get_generator_by_name('bed', spider, **kwargs)
        elif 'vcf' in kwargs:
            return GeneratorFactory.get_generator_by_name('vcf', spider, **kwargs)
        else:
            return None

    @classmethod
    def get_generator_by_name(cls, name, spider, **kwargs):
        """
        Get generator by name.
        :param name:
        :param spider:
        :param kwargs:
        :return:
        """
        if name == 'id':
            ids = kwargs['id']
            batch_num = kwargs['batch_num'] if 'batch_num' in kwargs else 0
            return IdGenerator(ids=ids, spider=spider, batch_num=batch_num)
        elif name == 'rs':
            ids = kwargs['rs']
            batch_num = kwargs['batch_num'] if 'batch_num' in kwargs else 0
            return IdGenerator(ids=ids, spider=spider, batch_num=batch_num)
        elif name == 'file':
            fp = kwargs['file']
            batch_num = kwargs['batch_num'] if 'batch_num' in kwargs else 0
            return FileGenerator(filepath=fp, spider=spider, batch_num=batch_num)
        elif name == 'bed':
            fp = kwargs['bed']
            batch_num = kwargs['batch_num'] if 'batch_num' in kwargs else 0
            return BedGenerator(filepath=fp, spider=spider, batch_num=batch_num)
        elif name == 'vcf':
            fp = kwargs['vcf']
            batch_num = kwargs['batch_num'] if 'batch_num' in kwargs else 0
            return VcfGenerator(filepath=fp, spider=spider, batch_num=batch_num)
        else:
            return None


class BaseGenerator(object):
    """
    Base Generator, subclass should override generate function.
    """
    def __init__(self, spider, **kwargs):
        self._spider = spider
        self._conf = kwargs

    def get_batch_num(self):
        """
        Get number of each batch.
        :return: int
        """
        if 'batch_num' in self._conf:
            bnum = int(self._conf['batch_num'])
        else:
            bnum = 0
        return bnum

    def generate(self):
        """
        Generate items.
        :return:
        """
        yield None


class IdGenerator(BaseGenerator):

    def __init__(self, ids, spider, **kwargs):
        super().__init__(spider, **kwargs)
        self._ids = ids

    def generate(self):
        bnum = self.get_batch_num()
        if not isinstance(self._ids, list):
            self._ids = self._ids.split(',')
        if 0 < bnum < len(self._ids):
            split_list = lambda _list, n: [_list[i * n:(i + 1) * n] for i in range(int((len(_list) + n - 1) / n))]
            for l in split_list(self._ids, bnum):
                yield l
        else:
            yield self._ids


class FileGenerator(BaseGenerator):

    def __init__(self, filepath, spider, **kwargs):
        super().__init__(spider, **kwargs)
        self._filepath = filepath

    def generate(self):
        bnum = self.get_batch_num()
        for fpath in glob.iglob(self._filepath):
            self._spider.logger.info('Read from file %s' % os.path.realpath(fpath))
            with open(fpath) as fh:
                i = 0
                ids = []
                for line in fh:
                    line = self.parse_line(line)
                    if line is None:
                        continue
                    ids.append(line)
                    i += 1
                    if i >= bnum:
                        yield ids
                        i = 0
                        ids = []
                if len(ids) > 0:
                    yield ids

    def parse_line(self, line):
        """
        Process each line in file.
        :param line:
        :return:
        """
        line = line.strip()
        if not line:
            return None
        if line.find('\t') > 0:
            cols = line.split('\t')
            line = cols[0]
        elif line.find(',') > 0:
            cols = line.split(',')
            line = cols[0]
        return line


class BedGenerator(FileGenerator):
    def parse_line(self, line):
        line = line.strip()
        cols = line.split('\t')
        if len(cols) < 4:
            return None
        return cols[3]


class VcfGenerator(FileGenerator):
    def parse_line(self, line):
        line = line.strip()
        if line[0] == '#':
            return None
        cols = line.split('\t')
        if len(cols) < 3:
            return None
        return cols[2]
