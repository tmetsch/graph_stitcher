from setuptools import setup

setup(name = 'graph_sticher',
      version = "0.0.1",
      author = 'Thijs Metsch',
      description = ('This tool is a little framework to determine possible'
                     'merges between two graphs based on a set of required'
                     'additional relationships (aka as stiches / edges).'),
      license = "MIT",
      keywords = 'graph stiching algorithms framework',
      packages=['sticher'],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Topic :: Utilities"
      ])
