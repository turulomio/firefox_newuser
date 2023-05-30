from os import system
from firefox_newuser import __version__

def translate():
        #es
        system("xgettext -L Python --no-wrap --no-location --from-code='UTF-8' -o firefox_newuser/locale/firefox_newuser.pot firefox_newuser/*.py")
        system("msgmerge -N --no-wrap -U firefox_newuser/locale/es.po firefox_newuser/locale/firefox_newuser.pot")
        system("msgfmt -cv -o firefox_newuser/locale/es/LC_MESSAGES/firefox_newuser.mo firefox_newuser/locale/es.po")
        system("msgfmt -cv -o firefox_newuser/locale/en/LC_MESSAGES/firefox_newuser.mo firefox_newuser/locale/en.po")

def release():
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
