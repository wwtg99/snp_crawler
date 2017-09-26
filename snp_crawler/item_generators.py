import os


class GeneratorFactory(object):

    @classmethod
    def get_generator(cls, **kwargs):
        """
        Get generator depends on params.
        :param kwargs:
        :return:
        """
        if 'id' in kwargs:
            ids = kwargs['id']
            batch_num = kwargs['batch_num'] if 'batch_num' in kwargs else 0
            return IdGenerator(ids=ids, batch_num=batch_num)
        elif 'rs' in kwargs:
            ids = kwargs['rs']
            batch_num = kwargs['batch_num'] if 'batch_num' in kwargs else 0
            return IdGenerator(ids=ids, batch_num=batch_num)
        elif 'file' in kwargs:
            fp = kwargs['file']
            batch_num = kwargs['batch_num'] if 'batch_num' in kwargs else 0
            return FileGenerator(fp, batch_num=batch_num)
        else:
            return None

    @classmethod
    def get_generator_by_name(cls, name, **kwargs):
        """
        Get generator by name.
        :param name:
        :param kwargs:
        :return:
        """
        if name == 'id':
            ids = kwargs['id']
            batch_num = kwargs['batch_num'] if 'batch_num' in kwargs else 0
            return IdGenerator(ids=ids, batch_num=batch_num)
        elif name == 'rs':
            ids = kwargs['rs']
            batch_num = kwargs['batch_num'] if 'batch_num' in kwargs else 0
            return IdGenerator(ids=ids, batch_num=batch_num)
        elif name == 'file':
            fp = kwargs['file']
            batch_num = kwargs['batch_num'] if 'batch_num' in kwargs else 0
            return FileGenerator(fp, batch_num=batch_num)
        else:
            return None


class BaseGenerator(object):

    def __init__(self, **kwargs):
        self._conf = kwargs

    def generate(self):
        """
        Generate items.
        :return:
        """
        yield None


class IdGenerator(BaseGenerator):

    def __init__(self, ids, **kwargs):
        super().__init__(**kwargs)
        self._ids = ids

    def generate(self):
        if 'batch_num' in self._conf:
            bnum = self._conf['batch_num']
        else:
            bnum = 0
        if not isinstance(self._ids, list):
            self._ids = self._ids.split(',')
        if 0 < bnum < len(self._ids):
            split_list = lambda _list, n: [_list[i * n:(i + 1) * n] for i in range(int((len(_list) + n - 1) / n))]
            for l in split_list(self._ids, bnum):
                yield l
        else:
            yield self._ids


class FileGenerator(BaseGenerator):

    def __init__(self, filepath, **kwargs):
        super().__init__(**kwargs)
        self._filepath = filepath

    def generate(self):
        if 'batch_num' in self._conf:
            bnum = self._conf['batch_num']
        else:
            bnum = 0
        if not os.path.exists(self._filepath):
            raise Exception('File %s not exists!' % self._filepath)
        with open(self._filepath) as fh:
            i = 0
            ids = []
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                if line.find('\t') > 0:
                    cols = line.split('\t')
                    line = cols[0]
                elif line.find(',') > 0:
                    cols = line.split(',')
                    line = cols[0]
                ids.append(line)
                i += 1
                if i >= bnum:
                    yield ids
                    i = 0
                    ids = []
            if len(ids) > 0:
                yield ids

