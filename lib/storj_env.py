import json
from datetime import datetime
from ext import python_libstorj as pystorj

class StorjEnv():
    def __init__(self,
                 bridge_options,
                 encrypt_options,
                 http_options,
                 log_options):

        options_list = (
            (bridge_options, pystorj.BridgeOptions()),
            (encrypt_options, pystorj.EncryptOptions()),
            (http_options, pystorj.HttpOptions()),
            (log_options, pystorj.LogOptions())
        )

        for option_pair in options_list:
            (options, option_struct) = option_pair
            for key, value in options.viewitems():
                if key == 'pass':
                    # NB: `pass` is a reserved attribute name
                    key = '_pass'
                setattr(option_struct, key, value)

        options = zip(*options_list)[1]
        self.env = pystorj.init_env(*options)
        self.env.loop = pystorj.set_loop(self.env)

    def get_info(self, handle):
        def _handle(error, result):
            result_object = json.loads(result)
            handle(error, result_object)
        pystorj.get_info(self.env, _handle)
        pystorj.run(self.env.loop)

    def list_buckets(self, handle):
        def _handle(error, buckets):
            for i, bucket in enumerate(buckets):
                iso8601_format = '%Y-%m-%dT%H:%M:%S.%fZ'
                created_date = datetime.strptime(bucket['created'], iso8601_format)
                buckets[i]['created'] = created_date
            handle(error, buckets)
        pystorj.list_buckets(self.env, _handle)
        pystorj.run(self.env.loop)

    def create_bucket(self, name, handle):
        pystorj.create_bucket(self.env, name, handle)
        pystorj.run(self.env.loop)