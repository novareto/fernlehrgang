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
      install_requires=[
          'simplejson',
          'uvc.menus',
          'gocept.httpserverlayer',
          'gocept.selenium',
          'grok',
          'grokcore.startup',
          'grokui.admin',
          'kombu',
          'lxml',
          'megrok.traject',
          'megrok.z3ctable',
          'openpyxl',
          'plone.memoize',
          'megrok.nozodb',
          'dolmen.beaker',
          'memory_profiler',
          #'psycopg2',
          'psycopg2-binary',
          'pygal',
          'python-gettext',
          'reportlab',
          'repoze.debug',
          'repoze.profile',
          'requests',
          'rq',
          'setuptools',
          'timeout-decorator',
          'ukh.ibmdbsa',
          'xlwt',
          'waitress',
          'z3c.saconfig',
          'zeam.form.base',
          'zeam.form.ztk',
          'zope.app.testing',
          'zope.pluggableauth',
          'zope.sendmail',
          'simplejson',
          'js.bootstrap',
          'uvc.siguvtheme',
      ],
      extras_require={
          'oracle': ['cx_Oracle',],
          'postgres': ['psycopg2-binary',],
          'odbc': ['pyodbc', 'ibm-db-sa'],
          'ibm': ['ibm_db', 'ibm-db-sa'],
          },
      entry_points={
          'sqlalchemy.dialects': [
               'bghw.pyodbc400=fernlehrgang.config.odbc:AS400Dialect_pyodbc',
          ],
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
