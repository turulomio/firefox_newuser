from setuptools import setup, Command
from os import system, chdir
from platform import system as platform_system
from site import getsitepackages

class Reusing(Command):
    description = "Fetch remote modules"
    user_options = [
      # The format is (long option, short option, description).
      ( 'local', None, 'Update files without internet'),
  ]

    def initialize_options(self):
        self.local=False

    def finalize_options(self):
        pass

    def run(self):
        from sys import path
        path.append("firefox_newuser/reusing")
#        print(self.local)
#        if self.local is False:
#            from github import download_from_github
#            download_from_github('turulomio','reusingcode','python/github.py', 'firefox_newuser/reusing/')
#            download_from_github('turulomio','reusingcode','python/casts.py', 'firefox_newuser/reusing/')
#            download_from_github('turulomio','reusingcode','python/datetime_functions.py', 'firefox_newuser/reusing/')
#            download_from_github('turulomio','reusingcode','python/listdict_functions.py', 'firefox_newuser/reusing/')
#            download_from_github('turulomio','reusingcode','python/file_functions.py', 'firefox_newuser/reusing/')
#            download_from_github('turulomio','reusingcode','python/decorators.py', 'firefox_newuser/reusing/')
#            download_from_github('turulomio','reusingcode','python/libmanagers.py', 'firefox_newuser/reusing/')
#            download_from_github('turulomio','reusingcode','python/percentage.py', 'firefox_newuser/reusing/')
#            download_from_github('turulomio','reusingcode','python/currency.py', 'firefox_newuser/reusing/')
#        
#        from file_functions import replace_in_file
#        replace_in_file("firefox_newuser/reusing/casts.py","from currency","from firefox_newuser.reusing.currency")
#        replace_in_file("firefox_newuser/reusing/casts.py","from percentage","from firefox_newuser.reusing.percentage")
#        replace_in_file("firefox_newuser/reusing/listdict_functions.py","from casts","from firefox_newuser.reusing.casts")


## Class to define doc command
class Translate(Command):
    description = "Update translations"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        #es
        system("xgettext -L Python --no-wrap --no-location --from-code='UTF-8' -o locale/firefox_newuser.pot *.py firefox_newuser/*.py setup.py")
        system("msgmerge -N --no-wrap -U locale/es.po locale/firefox_newuser.pot")
        system("msgfmt -cv -o firefox_newuser/locale/es/LC_MESSAGES/firefox_newuser.mo locale/es.po")
        system("msgfmt -cv -o firefox_newuser/locale/en/LC_MESSAGES/firefox_newuser.mo locale/en.po")

class Procedure(Command):
    description = "Show release procedure"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("""Nueva versión:
  * Cambiar la versión y la fecha en __init__.py
  * Modificar el Changelog en README
  * python setup.py translate
  * linguist
  * python setup.py translate
  * python setup.py uninstall; python setup.py install
  * git commit -a -m 'firefox_newuser-{0}'
  * git push
  * Hacer un nuevo tag en GitHub
  * python setup.py sdist
  * twine upload dist/firefox_newuser-{0}.tar.gz 
  * python setup.py uninstall
  * Crea un nuevo ebuild de firefox_newuser Gentoo con la nueva versión
  * Subelo al repositorio del portage

""".format(__version__))

## Class to define doxygen command
class Doxygen(Command):
    description = "Create/update doxygen documentation in doc/html"

    user_options = [
      # The format is (long option, short option, description).
      ( 'user=', None, 'Remote ssh user'),
      ( 'directory=', None, 'Remote ssh path'),
      ( 'port=', None, 'Remote ssh port'),
      ( 'server=', None, 'Remote ssh server'),
  ]

    def initialize_options(self):
        self.user="root"
        self.directory="/var/www/html/doxygen/firefox_newuser/"
        self.port=22
        self.server="127.0.0.1"

    def finalize_options(self):
        pass

    def run(self):
        print("Creating Doxygen Documentation")
        system("""sed -i -e "41d" doc/Doxyfile""")#Delete line 41
        system("""sed -i -e "41iPROJECT_NUMBER         = {}" doc/Doxyfile""".format(__version__))#Insert line 41
        system("rm -Rf build")
        chdir("doc")
        system("doxygen Doxyfile")      
        command=f"""rsync -avzP -e 'ssh -l {self.user} -p {self.port} ' html/ {self.server}:{self.directory} --delete-after"""
        print(command)
        system(command)
        chdir("..")
  
## Class to define uninstall command
class Uninstall(Command):
    description = "Uninstall installed files with install"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if platform_system()=="Linux":
            system("rm -Rf {}/firefox_newuser*".format(getsitepackages()[0]))
            system("rm /usr/bin/firefox_newuser*")
        else:
            system("pip uninstall firefox_newuser")

########################################################################

## Version of firefox_newuser captured from commons to avoid problems with package dependencies
__version__= None
with open('firefox_newuser/__init__.py', encoding='utf-8') as f:
    for line in f.readlines():
        if line.find("__version__=")!=-1:
            __version__=line.split("'")[1]


setup(name='firefox_newuser',
     version=__version__,
     description='Python script to launch firefox in Linux as a new user',
     long_description='Project web page is in https://github.com/turulomio/firefox_newuser',
     long_description_content_type='text/markdown',
     classifiers=['Development Status :: 4 - Beta',
                  'Intended Audience :: Developers',
                  'Topic :: Software Development :: Build Tools',
                  'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                  'Programming Language :: Python :: 3',
                 ], 
     keywords='firefox new user',
     url='https://github.com/turulomio/firefox_newuser',
     author='Turulomio',
     author_email='turulomio@yahoo.es',
     license='GPL-3',
     packages=['firefox_newuser', 'firefox_newuser.locale.es.LC_MESSAGES', 'firefox_newuser.locale.en.LC_MESSAGES'],
     install_requires=["colorama", "psutil", "tqdm"],
     entry_points = {'console_scripts': [
                            'firefox_newuser=firefox_newuser.core:main',
                        ],
                    },
     cmdclass={'doxygen': Doxygen,
               'uninstall':Uninstall, 
               'translate': Translate,
               'procedure': Procedure,
               'reusing': Reusing,
              },
     zip_safe=False,
     include_package_data=True
)
