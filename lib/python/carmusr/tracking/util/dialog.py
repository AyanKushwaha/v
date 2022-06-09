
from Cfh import Box, Done, Cancel, Area, Loc, Label

DEFAULT_BUTTON_AREA = Area(Loc(-1, -1))
DO = "DO"
CANCEL = "CANCEL"


def show_message_dialog(title, message, button_label="OK"):
    """This dialog should always return "OK" """

    box = Box("box", title)
    m = Label(box,  "message",  Area(Loc(0, 0)), message)
    d = Done(box, "done", DEFAULT_BUTTON_AREA, button_label, None)

    box.build()
    box.show(1)
    if box.loop():
        raise "box.loop() canceled somehow"
    return "OK"


def show_do_cancel_dialog(title, message, do_button_label="Do", cancel_button_label="Cancel"):
    """This dialog should always return DO or CANCEL """

    box = Box("box", title)
    m = Label(box,  "message",  Area(Loc(0, 0)), message)
    d = Done(box, "done", DEFAULT_BUTTON_AREA, do_button_label, None)
    c = Cancel(box, "cancel", DEFAULT_BUTTON_AREA, cancel_button_label, None)

    box.build()
    box.show(1)

    if box.loop():
        return CANCEL
    return DO

