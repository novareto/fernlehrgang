from setuptools import setup, find_packages

version = '0.0'

setup(name='fernlehrgang',
      version=version,
      description="",
      long_description="""\
""",
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords="",
      author="",
      author_email="",
      url="",
      license="",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'grokui.admin',
                        'z3c.testsetup',
                        'grokcore.startup',
                        'megrok.traject',
                        'cx_Oracle',
                        'z3c.saconfig',
                        'uvc.layout',
                        'uvc.widgets',
                        'uvc.tbskin',
                        'python-gettext',
                        'dolmen.menu',
                        'profilehooks',
                        'dolmen.app.viewselector',
                        'dolmen.forms.crud',
                        'dolmen.forms.wizard',
                        'dolmen.app.authentication',
                        'dolmen.content',
                        'repoze.profile',
                        'profilestats',
                        'plone.memoize',
                        'megrok.z3ctable',
                        'zope.pluggableauth',
                        'zeam.form.table',
                        'xlwt',
                        'openpyxl',
                        'celery',
                        'lxml',
                        'nva.asynctask',
                        # Add extra requirements here
                        ],
      entry_points = {
          'paste.app_factory': [
               'main = grokcore.startup:application_factory',
               'debug = grokcore.startup:debug_application_factory'
               ],
          'fanstatic.libraries': [
              'fernlehrgang = fernlehrgang.resources:library',
              ],
          'console_scripts': [
              'export = fernlehrgang.scripts.export:main_export',
              ],
          }
      )
