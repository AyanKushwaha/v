"""
To keep track of checkin changes 

This is used to be able to handle information to crew the right way.
"""

import os
from AbsTime import AbsTime

class ModifiedCheckin:
    
    changed_checkin ={}
        
    def add(self, crew, udor, flight, adep, checkin):
        self.changed_checkin[(crew, udor, flight, adep)] = checkin
    
    def get(self, crew, udor, flight, adep):
        try: 
            returnValue = self.changed_checkin[crew, udor, flight, adep]
            return returnValue
        except:
            return None
    
    def remove(self, crew, udor, flight, adep):
        del self.changed_checkin[crew, udor, flight, adep]
    
    def clear(self):
        self.changed_checkin.clear()
            

# additionally_modified_crew ============================================={{{1
# Instance of the wrapper object.
modified_checkin = ModifiedCheckin()

# get ===================================================================={{{1
def get(crew, udor, flight, adep):
    """Return unsorted list of crew that has been modifed, either known by
    Studio, or, by using the add() function below."""
    return modified_checkin.get(crew, udor, flight, adep)


# add ===================================================================={{{1
def add(crewid, udor, flight, adep, checkin):
    """Add one additional crew member to be marked as modified."""
    modified_checkin.add(crewid, udor, flight, adep, checkin)

def remove(crew, udor, flight, adep):
    modified_checkin.remove(crew, udor, flight, adep)
    
def clear():
    modified_checkin.clear()
    

# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
