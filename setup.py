from setuptools import setup

setup(name = 'graph_stitcher',
      version = "0.0.1",
      author = 'Thijs Metsch',
      description = ('This tool is a little framework to determine possible'
                     'merges between two graphs based on a set of required'
                     'additional relationships (aka as stitches / edges).'),
      license = "MIT",
      keywords = 'graph stitching algorithms framework',
      packages=['stitcher'],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Topic :: Utilities"
      ])
