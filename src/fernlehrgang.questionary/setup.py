from setuptools import setup, find_packages

version = '0.0'

setup(name='fernlehrgang.questionary',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[],
      keywords="",
      author="",
      author_email="",
      url="",
      license="",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['fernlehrgang'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'dolmen.app.container',
          'dolmen.forms.base',
          'dolmen.forms.crud',
          'uvc.composedview',
          'dolmen.security.policies',
          'grok',
          'grokcore.startup',
          'grokui.admin',
          'setuptools',
          'z3c.testsetup',
      ],
      entry_points = {
          }
      )
