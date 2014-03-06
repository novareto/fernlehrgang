from setuptools import setup, find_packages

version = '0.0'

setup(name='fernlehrgang.app',
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
      namespace_packages=['fernlehrgang'],
      zip_safe=False,
      install_requires=[
        'celery',
        'cromlech.security',
        'dolmen.authentication',
        'dolmen.beaker',
        'dolmen.content',
        'dolmen.forms.composed',
        'dolmen.forms.crud',
        'dolmen.forms.table',
        'dolmen.menu',
        'dolmen.uploader',
        'fernlehrgang.models',
        'fernlehrgang.tools',
        'js.bootstrap-wysihtml5',
        'js.jquery_tablesorter',
        'lxml',
        'megrok.z3ctable',
        'openpyxl',
        'plac',
        'plone.memoize',
        'profilehooks',
        'profilestats',
        'psycopg2',
        'pygooglechart',
        'python-gettext',
        'repoze.profile',
        'setuptools',
        'sqlalchemy_imageattach',
        'uvc.tb_layout',
        'uvc.widgets',
        'uvclight [auth]',
        'uvclight [sql]',
        'uvclight [traject]',
        'xlwt',
        ],
      entry_points = {
          'paste.app_factory': [
               'main = fernlehrgang.app.wsgi:application_factory',
               ],
          'fanstatic.libraries': [
              'fernlehrgang.app.browser = fernlehrgang.app.browser.resources:library',
              'bs_calendar = fernlehrgang.app.browser.resources:cal_library',
              ],
          'zeam.form.components': [
              'file = fernlehrgang.app.browser.widgets:register',
              ],
          }
      )
