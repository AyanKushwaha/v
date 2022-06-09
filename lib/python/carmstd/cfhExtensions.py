"""
A module using Cfh for implementing:
* a message popup box 
* a verify popup box
* an input box for strings

The behaviour is similar to the csl functions "csl_message", "csl_confirm"
and "csl_input".

HINT: 
If you specify the formName when you call the functions
it becomes possible to bypass the dialogue later on.
"""
from application import application

if application=="Matador":
    import carmstd.matador.cfhExtensions as cfhExtensions
else:
    import carmstd.studio.cfhExtensions as cfhExtensions 

def show(message, form_name = "MESSAGE_BOX", title = "Message"):
    """
    Shows a box containing the specified message and with the specified title. 
    Stops the execution of the calling python program until the user 
    presses the Ok button.
    """
    cfhExtensions.show(message, form_name, title)
    

def showFile(fileName, title = ""):
    """
    Dipsplays a file to in a studio popup
    """
    cfhExtensions.showFile(fileName,title)

def confirm(message, form_name = "CONFIRM_BOX", title = "Choice"):
    """
    Shows a box containing the specified message and with the specified title.
    Stops the execution of the calling python program until the user
    presses one of the buttons (Yes or No). Returns 1 (Yes) or 0 (No).
    """
    return cfhExtensions.confirm(message, form_name, title)

def choices(message, form_name = "CHOICES_BOX", title = "Choice", choices=["Choice 1","Choice 2"],default=None,style=16):
    """
    Shows a box containing the specified message and with the specified set of 
    choices as a list of radio buttons (default, or a Cfh.CfhSChouceXXX option).
    The return value is the string of the selected chocie.
    """
    return cfhExtensions.choices(message, form_name, title, choices, default, style)

def ask(message, form_name = "ASK_BOX", title = "Question", buttons=[("CANCEL","_Cancel"), ("OK","_OK")], default_button="OK"):
    """
    Shows a box containing the specified message and with the specified title and
    a given set of choice buttons.
    Returns the name(key) of the chosen button.
    """
    return cfhExtensions.ask(message, form_name, title, buttons, default_button)

def inputString(label, size, default = "", form_name = "INPUT_BOX", title = "Enter"):
    """
    Shows a box containing a label with an input field, optionally using a
    specified title. The input field with be at most be 60 characters long.
    If the input string is longer, the field will be scrolled.
    Returns the input string or None if the form is cancelled.
    """
    return cfhExtensions.inputString(label, size, default, form_name, title)
    
