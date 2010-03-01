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
                        'z3c.saconfig',
                        'uvc.skin',
                        'uvc.layout',
                        'z3c.menu.simple',
                        'megrok.z3cform.base',
                        'megrok.z3cform.ui',
                        'megrok.z3cform.tabular',
                        'dolmen.menu',
                        'megrok.pagetemplate',
                        'collective.z3cform.datetimewidget',
                        'elementtree',
                        'dolmen.app.layout',
                        'dolmen.app.viewselector',
                        # Add extra requirements here
                        ],
      entry_points = """
      [console_scripts]
      fernlehrgang-debug = grokcore.startup:interactive_debug_prompt
      fernlehrgang-ctl = grokcore.startup:zdaemon_controller
      [paste.app_factory]
      main = grokcore.startup:application_factory
      debug = grokcore.startup:debug_application_factory
      """,
      )
