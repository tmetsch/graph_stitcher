from setuptools import setup

setup(name = 'graph_sticher',
      version = "0.0.1",
      author = 'Thijs Metsch',
      description = ('This tool is a little framework to determine possible'
                     'merges between two graphs based on a set of additional'
                     'required relationships (aka stiches/edges). Based on a '
                     'set of possible resulting candidate graphs we validate '
                     'which of the candidate graphs is the "best".'),
      license = "MIT",
      keywords = 'graphs algorithms framework',
      packages=['sticher'],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Topic :: Utilities"
      ])
