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

import Cfh
import Csl
import Localization
import Variable

def show(message, form_name = "MESSAGE_BOX", title = "Message"):
    """
    Shows a box containing the specified message and with the specified title. 
    Stops the execution of the calling python program until the user 
    presses the Ok button.
    """
    
    print 'cfhExtensions.show("%s")' % message

    box = Cfh.Box(form_name, title)

    p = Cfh.Label(box,"PICTURE","xm_information.pm")
    p.setLoc(Cfh.CfhLoc(1,1))

    l = Cfh.Label(box,"MESSAGE",message)
    l.setLoc(Cfh.CfhLoc(1,4))

    ok = Cfh.Done(box,"OK")
    ok.setText(Localization.MSGR("Ok"))
    ok.setMnemonic(Localization.MSGR("_Ok"))

    box.build()
    box.show(1)
    box.loop()

def showFile(fileName, title = ""):
    cslExpr = "csl_show_file(\"" + title + "\", \"" + fileName + "\")"
    Csl.Csl().evalExpr(cslExpr)

def confirm(message, form_name = "CONFIRM_BOX", title = "Choice"):
    """
    Shows a box containing the specified message and with the specified title.
    Stops the execution of the calling python program until the user
    presses one of the buttons (Yes or No). Returns 1 (Yes) or 0 (No).
    """
  
    box = Cfh.Box(form_name, title)

    p = Cfh.Label(box,"ICON","xm_question.pm")
    p.setLoc(Cfh.CfhLoc(1,0))

    l = Cfh.Label(box,"MESSAGE",message)
    l.setLoc(Cfh.CfhLoc(1,4))

    y = Cfh.Done(box,"YES")
    y.setText(Localization.MSGR("Yes"))
    y.setMnemonic(Localization.MSGR("_Yes"))
  
    n = Cfh.Cancel(box,"NO")
    n.setText(Localization.MSGR("No"))
    n.setMnemonic(Localization.MSGR("_No"))
  
    box.build()
    box.show(1)
    ret = box.loop() == Cfh.CfhOk    
    print 'cfhExtensions.confirm("%s") = %r' % (message, ret)
    return ret

def choices(message, form_name = "CHOICES_BOX", title = "Choice", choices=["Choice 1","Choice 2"],default=None,style=Cfh.CfhSChoiceRadioCol):
    """
    """
    
    box = Cfh.Box(form_name, title)
    #box.setDim(Cfh.CfhDim(40, 3))
    p = Cfh.Label(box,"ICON","xm_question.pm")
    p.setLoc(Cfh.CfhLoc(1,0))

    l = Cfh.Label(box,"MESSAGE",message)
    l.setLoc(Cfh.CfhLoc(1,4))
            
    maxlen = max(len(x) for x in choices)
    if maxlen < 6: maxlen = 6
    if not default: default = choices[0]
    selector = Cfh.String(box,"MESSAGE",maxlen,default)#Cfh.String(box,"CHOICE",maxlen,"xxx")
    selector.setLoc(Cfh.CfhLoc(3,1))
    sz = 1+len(choices)
    if sz > 10: sz = 10
    selector.setDim(Cfh.CfhDim(40,sz))
    selector.setMenu([''] + choices)
    selector.setStyle(style)

    ok = Cfh.Done(box, "OK")
    ok.setText("OK")
    box.build()
    box.show(1)
    box.loop()
    ret = selector.getValue()
    print 'cfhExtensions.choices("%s", choices=%r) = %r' % (message, choices, ret)
    return ret
    
def ask(message, form_name = "ASK_BOX", title = "Question", buttons=[("CANCEL","_Cancel"), ("OK","_OK")], default_button="OK"):
    """
    Shows a box containing the specified message and with the specified title and
    a given set of choice buttons.
    Returns the name(key) of the chosen button.
    """
  
    box = Cfh.Box(form_name, title)
    #box.setDim(Cfh.CfhDim(40, 3))
    p = Cfh.Label(box,"ICON","xm_question.pm")
    p.setLoc(Cfh.CfhLoc(1,0))

    l = Cfh.Label(box,"MESSAGE",message)
    l.setLoc(Cfh.CfhLoc(1,4))
    
    class UserDefinedButton(Cfh.Function):
        """Button with return code."""
        def __init__(self, box, name, text, retval):
            Cfh.Function.__init__(self, box, name, None)
            self.retval = retval
            self.setText(text)

        def action(self):
            self.finishForm(0, self.retval)
    
    i = 0
    retvals = {}
    if not default_button in [name for name,_ in buttons]:
        default_button = buttons[-1][0]
        
    btns = []
    for db in (True,False):
        for name,mnemonic in buttons:
            label = mnemonic.replace('_', '')
            print (name,mnemonic,label)
            if name == default_button:
                if not db: continue
                btn = Cfh.Done(box, name)
                retvals[0] = name
            elif name == 'CANCEL':
                if db: continue
                btn = Cfh.Cancel(box, name)
                retvals[1] = name
            else:
                if db: continue
                btn = UserDefinedButton(box, name, label, i+100)
                retvals[i+100] = name
            btn.setMnemonic(Localization.MSGR(mnemonic))
            btn.setText(Localization.MSGR(label))
            btns.append(btn) # Cheat Python's GC
        
            #btn.setLoc(Cfh.CfhLoc(2,i))
            i += 1
    #print "  ## retvals:", retvals
    box.build()
    box.show(1)
    rv = box.loop()
    #print "  ## rv:", rv
    ret = retvals[rv]
    print 'cfhExtensions.ask("%s") = %r' % (message, ret)
    return ret

def inputString(label, size, default = "", form_name = "INPUT_BOX", title = "Enter"):
    """
    Shows a box containing a label with an input field, optionally using a
    specified title. The input field with be at most be 60 characters long.
    If the input string is longer, the field will be scrolled.
    Returns the input string or None if the form is cancelled.
    """
  
    box = Cfh.Box(form_name, title)

    l = Cfh.Label(box,"LABEL",label)
    l.setLoc(Cfh.CfhLoc(1,0))

    if size > 60:
        sizeShown = 60
    else:
        sizeShown = size
    i = Cfh.String(box,"INPUT",Cfh.CfhArea(2, 0, sizeShown,1),size,default)

    y = Cfh.Done(box,"OK")
    y.setText(Localization.MSGR("Ok"))
    y.setMnemonic(Localization.MSGR("_OK"))
  
    n = Cfh.Cancel(box,"CANCEL")
    n.setText(Localization.MSGR("Cancel"))
    n.setMnemonic(Localization.MSGR("_Cancel"))
  
    box.build()
    box.show(1)
    if box.loop() == Cfh.CfhOk:
        return i.valof()
    else:
        return None

if __name__ == "__main__":
    if confirm("Is this Ok?"):
        r = inputString("Type 'Yes' to confim", 20, title = "Are you really sure?")
        if r == 'Yes':
            show("Good. Let's continue!")
            show( __doc__ )
        else:
            show("Why not sure?")
    else:
        show("Why not?")
