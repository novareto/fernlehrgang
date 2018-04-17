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
          'GenericCache',
          'dolmen.app.authentication',
          'dolmen.app.viewselector',
          'dolmen.content',
          'dolmen.forms.crud',
          'dolmen.forms.wizard',
          'dolmen.menu',
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
          'profilehooks',
          'profilestats',
          'psycopg2',
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
          'uvc.layout',
          'uvc.tbskin',
          'uvc.widgets',
          'xlwt',
          'z3c.saconfig',
          'zeam.form.table',
          'zope.app.testing',
          'zope.pluggableauth',
          'zope.sendmail',
      ],
      extras_require={
          'oracle': ['cx_Oracle',],
          'postgres': ['psycopg2',],
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
