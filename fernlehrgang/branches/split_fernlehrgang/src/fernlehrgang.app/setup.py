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
        'dolmen.app.authentication',
        'dolmen.app.viewselector',
        'dolmen.content',
        'dolmen.forms.crud',
        'dolmen.forms.wizard',
        'dolmen.menu',
        'dolmen.uploader',
        'fernlehrgang.models',
        'grok',
        'grokcore.startup',
        'grokui.admin',
        'js.bootstrap-wysihtml5',
        'js.jquery_tablesorter',
        'lxml',
        'megrok.traject',
        'megrok.z3ctable',
        'openpyxl',
        'plac',
        'plone.memoize',
        'profilehooks',
        'profilestats',
        'pygooglechart',
        'python-gettext',
        'repoze.profile',
        'setuptools',
        'sqlalchemy_imageattach',
        'uvc.layout',
        'uvc.tbskin',
        'uvc.widgets',
        'xlwt',
        'z3c.saconfig',
        'z3c.testsetup',
        'zeam.form.table',
        'zope.pluggableauth',
        ],
      entry_points = {
          'paste.app_factory': [
               'main = grokcore.startup:application_factory',
               'debug = grokcore.startup:debug_application_factory',
               ],
          'fanstatic.libraries': [
              'fernlehrgang.app.browser = fernlehrgang.app.browser.resources:library',
              ],
          'zeam.form.components': [
              'file = fernlehrgang.app.browser.widgets:register',
              ],
          'paste.filter_app_factory': [
               'image = fernlehrgang.app:image_middleware',
               ],
          }
      )
