from portrayal_server.common import utils

A = utils.import_class("test_args.Module")
a = A.create()


a()
