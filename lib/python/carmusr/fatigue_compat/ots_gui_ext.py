'''
Extensions to the :carmsys_man:`Gui` library.

:date: 07Mar2010
:organization: Jeppesen Systems AB
'''

__docformat__ = 'restructuredtext en'

import Gui


def add_menu_item(parent_menu,
                  title,
                  action=None,
                  icon=None,
                  tooltip=None,
                  mnemonic=None,
                  accelerator=None,
                  potency=Gui.POT_REDO,
                  opacity=Gui.OPA_OPAQUE,
                  identifier=None,
                  sensitive=True,
                  menu_mode=None,
                  python_action=None,
                  ):

    """Adds a menu item (wraps :carmsys_man:`GuiAddMenuButton`)

    This is a simpler-to-use version of :carmsys_man:`GuiAddMenuButton` which adds
    commonly used argument defaults, and also a new optional argument
    'python_action'.

    Examples
    --------

    .. python::
      add_menu_item('PlanningToolsMenu',
                    'Check Data Consistency',
                    python_action = 'menu_command.check_consistency()')

    The python_action will be run using ``PythonEvalExpr``. For this reason
    all double quotes (") will be converted to single ('). If python_action
    is used, the action argument is disregarded.
"""

    if python_action is not None:
        python_action = python_action.replace('"', "'")
        action = 'PythonEvalExpr("%s")' % python_action

    Gui.GuiAddMenuButton(parent_menu,
                         icon,
                         title,
                         tooltip,
                         mnemonic,
                         accelerator,
                         action,
                         potency,
                         opacity,
                         identifier,
                         sensitive,
                         menu_mode)


def add_separator(parent_menu, title, identifier=None):
    # The Gui-call can take title and identifier args to enable referring and dropping
    Gui.GuiAddMenuSeparator(parent_menu, title, identifier)
