#####################################################

#
# Module for building AC-rotations according to opus, turn, fifo or lifo.
#

import Cui, Gui, Variable, Errlog, os

def buildAcRotations(ac_params):
  try:
    rotation_ruleset = 0
    lp_name = Variable.Variable('')
    Cui.CuiGetLocalPlanName(Cui.gpc_info, lp_name)
    #Check that we have a local plan loaded, exit if not
    if lp_name.value == "":
      Errlog.set_user_message("Please load a local plan first")
      return
    #Get the current ruleset name, and check if a ruleset is loaded
    ruleset_name = Variable.Variable('')
    try:
      Cui.CuiCrcGetRulesetName(ruleset_name)
    except: pass
       
    if ruleset_name.value != "":
      #If a ruleset was loaded, store the parameters
      Cui.CuiCrcSaveParameterSet(Cui.gpc_info, "", "$CARMTMP/parameters/tmp_$USER")
    if ac_params != "studio_param":
      Cui.CuiCrcLoadRuleset(Cui.gpc_info, "BuildAcRotations") == -1
      Cui.CuiCrcLoadParameterSet(Cui.gpc_info, ac_params)
    rotation_ruleset = 1
    Cui.CuiBuildAcRotations(Cui.gpc_info, 0)
    #Errlog.set_user_message("AC-rotations successfully created")
    if ruleset_name.value != "":
      #If a ruleset was loaded, reload the original one
      Cui.CuiCrcLoadRuleset(Cui.gpc_info, ruleset_name.value)
      Cui.CuiCrcLoadParameterSet(Cui.gpc_info, "$CARMTMP/parameters/tmp_$USER")
    try:
      os.unlink("$CARMTMP/parameters/tmp_$USER")
    except: pass
      
  except exception, err:
    if err == "Function CuiCrcSaveParameterSet returned -1":
      Errlog.set_user_message("Could not store current ruleset parameters.\nNo new rotations built")
    if err == "Function CuiCrcLoadRuleset returned -1" and rotation_ruleset == 0:
      Errlog.set_user_message("Could not load rule set BuildAcRotations.\nNo new rotations built")
    if err == "Function CuiDissolveAcRotations returned -1":
      Errlog.set_user_message("Old rotations not dissolved.\nOld rotations will be connected to new rotations")
    if err == "Function CuiBuildAcRotations returned -1":
      Errlog.set_user_message("Could not build rotations\nNo new rotations built")
    if err == "Function CuiCrcLoadRuleSet returned -1" and rotation_ruleset == 1:
      Errlog.set_user_message("Could not reload the original ruleset.")
    if err == "Function CuiCrcLoadParameterSet returned -1":
      Errlog.set_user_message("Could not reload original ruleset parameters.")


def buildOpusAcRotations():
  if Gui.GuiYesNo("AcRot-Verify", "Build OPUS AC-rotations?"):
    buildAcRotations("ac_rot/opus")

def buildTurnAcRotations():
  if Gui.GuiYesNo("AcRot-Verify", "Build TURN AC-rotations?"):
    buildAcRotations("ac_rot/turn")

def buildFifoAcRotations():
  if Gui.GuiYesNo("AcRot-Verify", "Build FIFO AC-rotations?"):
    buildAcRotations("ac_rot/fifo")

def buildLifoAcRotations():
  if Gui.GuiYesNo("AcRot-Verify", "Build LIFO AC-rotations?"):
    buildAcRotations("ac_rot/lifo")

def buildRotationsFromStudioParameters():
 if Gui.GuiYesNo("AcRot-Verify", "Build rotations according to parameters set in Studio?"):
    buildAcRotations("studio_param")
