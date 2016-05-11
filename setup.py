import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name="portrayal_server",
      version="0.0.1",
      author="wtwang",
      author_email="wenting.wang@baifendian.com",
      description=("For distributed in ProtrayalServer"),
      license="GPL",
      packages=find_packages(),
      long_description=read('README'),
      package_data={'': ['*.cfg','*.so']},
      data_files=[('/etc/portrayal_server', ['etc/portrayal_server/portrayal_server.conf']),
                  ('/etc/init', ['etc/init/portrayal_server.conf']),],

      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: python2.7",
        "Framework :: Thrift",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: Unix"],
      scripts=['portrayal_server/cmd/portrayal_server',])
