"""
Convenience functions for adding common command options.
"""

import argparse


class PostProcessor(object):
    def __init__(self, dest, processor):
        self.dest      = dest
        self.processor = processor

    @classmethod
    def path_processor(cls, dest="path"):
        def process(args):
            raw_path = args.__dict__[dest]
            if hasattr(args, "product"):
                return raw_path.format(args.product)
            else:
                return raw_path
        return cls(dest, process)


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ArgumentParser, self).__init__(*args, **kwargs)
        self._post_processors = []

    def add_product(self, metavar="PRODUCT", help="e.g. BTC-USD", **kwargs):
        self.add_argument("product", metavar=metavar, help=help, **kwargs)

    def add_path(self, name='--path', dest="path",
                 help="path (can be parameterized by product), e.g. /path/to/{}.txt",
                 **kwargs):
        self.add_argument(name, help=help, **kwargs)
        self._post_processors.append(PostProcessor.path_processor(dest=dest))

    def parse_args(self, *args, **kwargs):
        args = super(ArgumentParser, self).parse_args(*args, **kwargs)
        for post_processor in self._post_processors:
            setattr(
                args,
                post_processor.dest,
                post_processor.processor(args)
            )
        return args
