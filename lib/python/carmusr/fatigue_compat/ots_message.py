"""
This module gives access to some functions in csl
that are nice for displaying information to the user.
"""
#
__docformat__ = 'restructuredtext en'

import tempfile

import Csl
csl = Csl.Csl()


def show_file(title, filepath):
    """
    Displays a file in a nice Studio pop-up window.

    :param title: Text to show in the window frame
    :type  title: str
    :param filepath: Text to display in the window.
    :type  filepath: str
    """
    csl.evalExpr('csl_show_file("%s","%s")' % (title, filepath))


def show_text(title, text):
    """
    Displays a text in a nice Studio pop-up window.

    :param title: Text to show in the window frame
    :type  title: str
    :param text: Text to display in the window.
    :type  text: str
    """
    with tempfile.NamedTemporaryFile() as f:
        f.write(text)
        f.flush()
        show_file(title, f.name)

if __name__ == "__main__":
    """ Self testing code """
    show_text("Hello World 1", "Hello World 2")
    show_file("CONFIG_extension", "$CARMUSR/CONFIG_extension")
