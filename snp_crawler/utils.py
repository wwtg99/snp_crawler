
class Configurable:

    def get_api_url(self, query={}):
        """
        Get api url.
        :param query:
        :return:
        """
        q = self.get_spider_conf('query')
        if q is not None:
            query = dict(query, **q)
        if query:
            qls = ['%s=%s' % (k, v) for k, v in query.items()]
            url = self.api_host + '?' + '&'.join(qls)
        else:
            url = self.api_host
        return url

    def get_spider_conf(self, field=None, default=None):
        """
        Get spider configuration.

        :param field:
        :param default: default value if not exists
        :return:
        :rtype: dict
        """
        conf = self.settings['SPIDER_SETTINGS'][self.name] if self.name in self.settings['SPIDER_SETTINGS'] and self.settings['SPIDER_SETTINGS'][self.name] else {}
        if field:
            return conf[field] if field in conf else default
        return conf
