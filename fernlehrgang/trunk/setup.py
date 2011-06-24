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
                        'cx-Oracle',
                        'grokcore.startup',
                        'megrok.traject',
                        'z3c.saconfig',
                        'uvc.layout',
                        'uvc.widgets',
                        'uvc.skin',
                        'dolmen.menu',
                        'profilehooks',
                        'dolmen.app.viewselector',
                        'dolmen.forms.crud',
                        'dolmen.app.authentication',
                        'dolmen.content',
                        'repoze.profile',
                        'profilestats',
                        'pygooglechart',
                        'megrok.navigation',
                        'megrok.z3ctable',
                        'zope.pluggableauth',
                        'hurry.jquerytools',
                        'xlwt',
                        # Add extra requirements here
                        ],
      entry_points = """
      [paste.app_factory]
      main = grokcore.startup:application_factory
      debug = grokcore.startup:debug_application_factory
      """,
      )
