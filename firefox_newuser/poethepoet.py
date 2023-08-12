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
  * Cambiar la versión en pyproject.toml
  * Modificar el Changelog en README
  * poe translate
  * Update *.po files
  * poe translate
  * git commit -a -m 'firefox_newuser-{0}'
  * git push
  * Hacer un nuevo tag en GitHub
  * poetry build
  * poetry publish --username --password  
  * Crea un nuevo ebuild de firefox_newuser Gentoo con la nueva versión
  * Subelo al repositorio del portage

""".format(__version__))
