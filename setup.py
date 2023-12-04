from setuptools import setup, find_packages

version = '1.1.dev0'

test_extras = [
    'gocept.httpserverlayer',
    'zope.app.testing',
    'z3c.unconfigure',
    'zope.testbrowser'
]

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
          "dolmen.beaker",
          'grok',
          'grokcore.startup',
          'kombu',
          'megrok.nozodb',
          'megrok.traject',
          'megrok.z3ctable',
          'openpyxl',
          'psycopg2-binary',
          'reportlab',
          'requests',
          'rq',
          'setuptools',
          'simplejson',
          'uvc.menus',
          'uvc.siguvtheme',
          'xlwt',
          'z3c.saconfig',
          'zeam.form.base',
          'zeam.form.composed',
          'zeam.form.table',
          'zeam.form.ztk[fanstatic]',
          'zeam.form.layout',
          'zope.pluggableauth',
          'zope.sendmail',
      ],
      extras_require={
          'oracle': ['cx_Oracle',],
          'postgres': ['psycopg2-binary',],
          'odbc': ['pyodbc', 'ibm-db-sa'],
          'ibm': ['ibm_db', 'ibm-db-sa', 'ukh.ibmdbsa'],
          'test': test_extras,
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
