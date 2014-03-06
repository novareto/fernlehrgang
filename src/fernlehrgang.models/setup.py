from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='fernlehrgang.models',
      version=version,
      description="Shared SQL Models",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      license='ZPL',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      namespace_packages=['fernlehrgang'],
      zip_safe=False,
      install_requires=[
          'setuptools',
          'SQLAlchemy',
          'sqlalchemy_imageattach',
          'dolmen.content',
          'zope.interface',
          'cromlech.file',
          ],
      )
