#!/usr/local/bin/python
# -*- coding: utf-8 -*-
#

#
# Python script for managing SoftLocks
#
# Created 2004-01-14 /Henrik Enström
#

from Tkinter import *
from SoftLocksBasics import *
from SoftLocksValidate import *
import sys, os, re, copy, string, subprocess
import tkMessageBox, tkFileDialog

############################## --------------------- ##############################
##############################  global declarations  ##############################
############################## --------------------- ##############################

gListSLEtabColsShort = ['EType', 'SCarrier1', 'IFlightNr1', 'SDepArr1', 'SActiveOrDH1',
                   'STrafficDay', 'ADateFrom', 'ADateTo', 'SCarrier2',
                   'IFlightNr2', 'SDepArr2', 'SActiveOrDH2', 'RLimitMin',
                   'RLimitMax', 'SBase', 'SACType', 'BACChange', 'IPenalty',
                   'BActive', 'CComment']
gListSLEtabCols = ['EType "Type" [ "REQ_BASE" ; "NOT_BASE" ; "REQ_TRIPSTART" ; "REQ_TRIPEND" ; "NOT_TRIPSTART" ; "NOT_TRIPEND" ; "REQ_DUTYSTART" ; "REQ_DUTYEND" ; "NOT_DUTYSTART" ; "NOT_DUTYEND" ; "REQ_CXN_AFT" ; "NOT_CXN_AFT" ; "REQ_CXN_BEF" ; "NOT_CXN_BEF" ; "REQ_REST_AFT" ; "REQ_REST_BEF" ; "CXN_BUFFER" ] 30 / 20',
                   'SCarrier1 "1st carrier" [ "AA" % "BA" % "ZZ" ] 2 / 13',
                   'IFlightNr1 "1st flight number" [ 0 % 0 % 9999999 ] 7 / 10',
                   'SDepArr1 "1st DEP-ARR" 7 / 13',
                   'SActiveOrDH1 "1st Active/DH" [ "A" % "*" % "Z" ] 1 / 14',
                   'STrafficDay "1st Traf. day (D, 1-7)" [ "A" % "D" % "Z" ] 7 / 16',
                   'ADateFrom "1st From (flight dep)" [ 01JAN2000 % 01JAN2000 % 01JAN2030 ] 15 / 17',
                   'ADateTo "1st To (flight dep)" [ 01JAN2000 % 01JAN2030 % 01JAN2030 ] 15 / 15',
                   'SCarrier2 "2nd carrier" [ "AA" % "BA" % "ZZ" ] 2 / 13',
                   'IFlightNr2 "2nd flight number" [ 0 % 0 % 9999999 ] 7 / 10',
                   'SDepArr2 "2nd DEP-ARR" 7 / 13',
                   'SActiveOrDH2 "2nd Active/DH" [ "A" % "*" % "Z" ] 1 / 14',
                   'RLimitMin "Min time limit" [ -999:00 % 0:00 % 999:00 ] 7 / 15',
                   'RLimitMax "Max time limit" [ -999:00 % 0:00 % 999:00 ] 7 / 15',
                   'SBase "Base" 7 / 7',
                   'SACType "AC type" 7 / 7',
                   'BACChange "If AC-chg" [ false % false % true ] 5 / 10',
                   'IPenalty "Penalty (1-9=Std, 0=Rule)" [ 0 % 0 % 9999999 ] 7 / 22',
                   'BActive "Active" [ false % true % true ] 5 / 10',
                   'CComment "Comment" 50 / 15']
gListMainSLTypes = [('CXN_AFT', 'Connection after'),
                    ('CXN_BEF', 'Connection before'),
                    ('BASE', 'Base'),
                    ('TRIPSTART', 'Trip start'),
                    ('TRIPEND', 'Trip end'),
                    ('DUTYSTART', 'Duty start'),
                    ('DUTYEND', 'Duty end'),
                    ('REST_AFT', 'Rest after'),
                    ('REST_BEF', 'Rest before'),
                    ('CXN_BUFFER', 'Connection buffer')]
gMapMonth = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
gListDayNames = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
gReAbstime = re.compile(r'(?P<day>\d{1,2})(?P<month>\w{3})(?P<year>\d{4})(| (?P<relTime>.*))')
gReReltime = re.compile(r'^(?P<hour>\d+):(?P<minute>\d{2})$')
gReDateOrTime = re.compile(r'(?P<hour>\d+)h(?P<minute>\d{0,2})|(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})', re.IGNORECASE)
gReNonNegNumber = re.compile(r'^(?P<number>[0-9]+)$')
gReNumber = re.compile(r'^(?P<number>[+\-]?[0-9]+)$')
gReDepArr = re.compile(r'^(?P<dep>\w{3})-(?P<arr>\w{3})$')
gReLineSep = re.compile(os.linesep)
# Yellow coloring
#gStrBGColorMain = '#eeeed4'
#gStrBGColorDark = '#d0d0b3'
#gStrActiveColor = '#dddd99'
# Nordic light
gStrBGColorMain = '#e2e2e2'
gStrBGColorDark = '#cccccc'
gStrActiveColor = '#ffffcc'
gStrBGColorButton = '#ededed'
gTypeSaveAs = 0
gTypeOpen = 1
gTypeNew = 2
# Max Page width
gMaxPageWidth = 68
gMaxArrowPos = 50
gLabelCancelButton = 'Cancel'
gLabelOkButton = 'Ok'

############################## --------------------- ##############################
##############################      functions        ##############################
############################## --------------------- ##############################

def printUsage():
    print """Usage: %s [-etab etabFilename] [-report reportFilename]""" %(sys.argv[0])

# Creates empty frames to use as "space fillers"
def getEmptyFrame(parent, width=1):
    retFrame = Frame(parent)
    labelEmpty = Label(retFrame, text=' '*width, font=("Helvetica", min(15, width)), bg=gStrBGColorMain)
    labelEmpty.grid()
    return retFrame
def breakLine(line, maxLen, indent=0):
    posBreak = line.rfind(' ', 0, maxLen + 1)
    if len(line) <= maxLen or posBreak == -1:
        return ' ' * indent + line + '\n'
    return ' ' * indent + line[:posBreak] + '\n' + breakLine(line[posBreak + 1:], maxLen, indent)

############################## --------------------- ##############################
##############################       classes         ##############################
############################## --------------------- ##############################

class AppSoftLockList(Frame):
    def __init__(self, root, parent, slEtab=None):
        Frame.__init__(self, parent, bg=gStrBGColorMain)
        self.root = root
        self.parent = parent

        # ------ constants for controlling layout of buttons ------
        self.buttonWidth = 8
        self.buttonWidthSmall = 3
        self.buttonBGColor = gStrBGColorButton
        # -------------- end constants ----------------

        self.pack(padx=5, pady=5)

        getEmptyFrame(self).grid(row=3, column=1)
        getEmptyFrame(self, 7).grid(row=1, column=3)
        self.frameButtons = Frame(self, bg=gStrBGColorMain)
        self.frameButtons.grid(row=2, rowspan = 4, column=2, columnspan=1, sticky=N)
        getEmptyFrame(self).grid(row=2, column=3)
        self.frameSLOne = Frame(self, bg=gStrBGColorMain)
        self.frameSLOne.grid(row=2, column=4, columnspan=2)
        getEmptyFrame(self).grid(row=3, column=3)
        self.frameSLGroup = Frame(self, bg=gStrBGColorMain)
        self.frameSLGroup.grid(row=4, column=4, columnspan=2)
                        
        ########################
        #   General buttons    #
        ########################

        self.labelTitleButtons = Label(self.frameButtons, text='SL etab', font=('Helvetica',16), bd=2, bg=gStrBGColorMain)
        self.labelTitleButtons.grid(row=1, column=2)
        self.btnNew = Button(self.frameButtons, text='New', fg='black', bg=self.buttonBGColor, bd=2, command=self.doNew,
                              activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnNew.grid(row=2, column=2)
        self.btnOpen = Button(self.frameButtons, text='Open', fg='black', bg=self.buttonBGColor, bd=2, command=self.doOpen,
                              activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnOpen.grid(row=4, column=2)
        getEmptyFrame(self.frameButtons).grid(row=5, column=2)
        self.enableSave()
        self.btnSaveAs = Button(self.frameButtons, text='Save as', fg='black', bg=self.buttonBGColor, bd=2, command=self.doSaveAs,
                                activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnSaveAs.grid(row=8, column=2)
        getEmptyFrame(self.frameButtons).grid(row=9, column=2)

        self.btnPrint = Button(self.frameButtons, text='Print', fg='black', bg=self.buttonBGColor, bd=2, command=self.doPrint,
                                activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnPrint.grid(row=10, column=2)
        getEmptyFrame(self.frameButtons).grid(row=11, column=2)
        
        # The "Close all" button is not necessary
        #self.btnCloseAll = Button(self.frameButtons, text='Close all', fg='black', bg=self.buttonBGColor, bd=2,
        #                          command=self.doCloseAll, activebackground=gStrActiveColor,
        #                          width=self.buttonWidth)
        #self.btnCloseAll.grid(row=12, column=2)
        
        self.btnExit = Button(self.frameButtons, text='Exit', fg='black', bg=self.buttonBGColor, bd=2, command=self.doExit,
                              activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnExit.grid(row=13, column=2)
        getEmptyFrame(self.frameButtons).grid(row=14, column=2)
        self.BoolValidate = BooleanVar()
        self.BoolValidate.set(bool(slEtab.getStrReportFile()))
        self.cbValidate = Checkbutton(self.frameButtons, text="Validate",
                                      variable=self.BoolValidate, bg=gStrBGColorMain,
                                      activebackground=gStrActiveColor, state=[DISABLED, NORMAL][bool(slEtab.getStrReportFile())])
        self.cbValidate.grid(row=15, column=2)

        ########################
        #   SoftLock groups    #
        ########################

        self.labelTitleGroup = Label(self.frameSLGroup, text='SoftLock groups', font=('Helvetica',16), bd=2, bg=gStrBGColorMain)
        self.labelTitleGroup.grid(row=2, column=2, columnspan=18)
        self.scrollGroupY = Scrollbar(self.frameSLGroup, orient=VERTICAL, bg=gStrBGColorMain)
        self.scrollGroupX = Scrollbar(self.frameSLGroup, orient=HORIZONTAL, bg=gStrBGColorMain)
        self.lbSLGroup = Listbox(self.frameSLGroup, yscrollcommand=self.scrollGroupY.set, xscrollcommand=self.scrollGroupX.set, width=71, height=12, font=('Courier',11,'bold'), bg=gStrBGColorMain, selectbackground=gStrActiveColor)
        self.lbSLGroup.bind("<Double-Button-1>", self.doEditGroup)
        self.scrollGroupY.config(command=self.lbSLGroup.yview)
        self.scrollGroupY.grid(row=4, column=18, columnspan=2, sticky=W+N+S)
        self.scrollGroupX.config(command=self.lbSLGroup.xview)
        self.scrollGroupX.grid(row=5, column=2, columnspan=16, sticky=NSEW)
        self.lbSLGroup.grid(row=4, column=2, columnspan=16, sticky=NSEW)
        getEmptyFrame(self.frameSLGroup).grid(row=6, column=2)
        self.btnNewGroup = Button(self.frameSLGroup, text='New', fg='black', bg=self.buttonBGColor, bd=2, command=self.doNewGroup,
                                  activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnNewGroup.grid(row=7, column=2, sticky=W)
        self.btnCopyGroup = Button(self.frameSLGroup, text='Copy', fg='black', bg=self.buttonBGColor, bd=2, command=self.doCopyGroup,
                                  activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnCopyGroup.grid(row=7, column=3, sticky=W)
        self.btnEditGroup = Button(self.frameSLGroup, text='Edit', fg='black', bg=self.buttonBGColor, bd=2, command=self.doEditGroup,
                                   activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnEditGroup.grid(row=7, column=4, sticky=W)
        getEmptyFrame(self.frameSLGroup).grid(row=7, column=5)
        self.btnDeleteGroup = Button(self.frameSLGroup, text='Delete', fg='black', bg=self.buttonBGColor, bd=2, command=self.doDeleteGroup,
                                     activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnDeleteGroup.grid(row=7, column=6, sticky=W)
        self.btnMoveUpGroup = Button(self.frameSLGroup, text='Up', fg='black', bg=self.buttonBGColor, bd=2, command=self.doMoveUpGroup,
                                     activebackground=gStrActiveColor, width=self.buttonWidthSmall)
        getEmptyFrame(self.frameSLGroup).grid(row=7, column=5)
        self.btnMoveUpGroup.grid(row=7, column=8, sticky=W)
        self.btnMoveDownGroup = Button(self.frameSLGroup, text='Down', fg='black', bg=self.buttonBGColor, bd=2, command=self.doMoveDownGroup,
                                     activebackground=gStrActiveColor, width=self.buttonWidthSmall)
        self.btnMoveDownGroup.grid(row=7, column=9, sticky=W)
        self.mapAppGroup = {}

        ########################
        # SoftLocks one by one #
        ########################

        self.labelTitleOne = Label(self.frameSLOne, text='SoftLocks', font=('Helvetica',16), bd=2, bg=gStrBGColorMain)
        self.labelTitleOne.grid(row=2, column=2, columnspan=18)
        self.scrollOneY = Scrollbar(self.frameSLOne, orient=VERTICAL, bg=gStrBGColorMain)
        self.scrollOneX = Scrollbar(self.frameSLOne, orient=HORIZONTAL, bg=gStrBGColorMain)
        self.lbSLOne = Listbox(self.frameSLOne, yscrollcommand=self.scrollOneY.set, xscrollcommand=self.scrollOneX.set, width=71, height=12, font=('Courier',11,'bold'), bg=gStrBGColorMain, selectbackground=gStrActiveColor)
        self.lbSLOne.bind("<Double-Button-1>", self.doEditOne)
        self.scrollOneY.config(command=self.lbSLOne.yview)
        self.scrollOneY.grid(row=4, column=18, columnspan=2, sticky=W+N+S)
        self.scrollOneX.config(command=self.lbSLOne.xview)
        self.scrollOneX.grid(row=5, column=2, columnspan=16, sticky=NSEW)
        self.lbSLOne.grid(row=4, column=2, columnspan=16, sticky=NSEW)
        getEmptyFrame(self.frameSLOne).grid(row=6, column=2)
        self.btnNewOne = Button(self.frameSLOne, text='New', fg='black', bg=self.buttonBGColor, bd=2, command=self.doNewOne,
                                activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnNewOne.grid(row=7, column=2, sticky=W)
        self.btnCopyOne = Button(self.frameSLOne, text='Copy', fg='black', bg=self.buttonBGColor, bd=2, command=self.doCopyOne,
                                activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnCopyOne.grid(row=7, column=3, sticky=W)
        self.btnEditOne = Button(self.frameSLOne, text='Edit', fg='black', bg=self.buttonBGColor, bd=2, command=self.doEditOne,
                                 activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnEditOne.grid(row=7, column=4, sticky=W)
        getEmptyFrame(self.frameSLOne).grid(row=7, column=5)
        self.btnDeleteOne = Button(self.frameSLOne, text='Delete', fg='black', bg=self.buttonBGColor, bd=2, command=self.doDeleteOne,
                                     activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnDeleteOne.grid(row=7, column=6, sticky=W)
        getEmptyFrame(self.frameSLOne).grid(row=7, column=7)
        self.btnMoveUpOne = Button(self.frameSLOne, text='Up', fg='black', bg=self.buttonBGColor, bd=2, command=self.doMoveUpOne,
                                     activebackground=gStrActiveColor, width=self.buttonWidthSmall)
        self.btnMoveUpOne.grid(row=7, column=8, sticky=W)
        self.btnMoveDownOne = Button(self.frameSLOne, text='Down', fg='black', bg=self.buttonBGColor, bd=2, command=self.doMoveDownOne,
                                     activebackground=gStrActiveColor, width=self.buttonWidthSmall)
        self.btnMoveDownOne.grid(row=7, column=9, sticky=W)
        getEmptyFrame(self.frameSLOne).grid(row=7, column=10)
        self.btnOnOff = Button(self.frameSLOne, text='On/Off', fg='black', bg=self.buttonBGColor, bd=2, command=self.doOnOff,
                                     activebackground=gStrActiveColor, width=self.buttonWidthSmall)
        self.btnOnOff.grid(row=7, column=11, sticky=W)
        self.mapAppOne = {}
        self.slEtab = None
        self.initEtab(slEtab)
    def updateTitle(self):
        if self.slEtab.getHasChanged():
            strHasChanged = ' *'
        else:
            strHasChanged = ''
        strFilename = self.slEtab.getStrFilename()
        if strFilename:
            self.root.title('SoftLocks (%s%s)' %(os.path.basename(strFilename), strHasChanged))
        else:
            self.root.title('SoftLocks (New)')
    def initEtab(self, slEtab):
        self.doCloseAll()
        if self.slEtab and self.slEtab.getStrDefaultDir():
            slEtab.setStrDefaultDir(self.slEtab.getStrDefaultDir())
        self.slEtab = slEtab
        mapSL = self.slEtab.getMapSoftLocks()
        self.updateListOne()
        mapSLGroup = self.slEtab.getMapSoftLockGroups()
        self.mapSLGroups = {}
        for slgId in mapSLGroup.keys():
            self.addSoftLockGroup(mapSLGroup[slgId])
        self.updateListGroup()
        self.updateTitle()
        if not self.slEtab.getStrFilename():
            self.disableSave()
    def updateListOne(self, intIdSelected=None):
        if not intIdSelected and self.lbSLOne.curselection():
            softLock = self.slEtab.getSoftLockInRow(int(self.lbSLOne.curselection()[0]) + 1)
            if softLock:
                intIdSelected = softLock.getIntUniqueId()
        self.lbSLOne.delete(0, self.lbSLOne.size() - 1)
        mapSLReprFixedWidth = self.slEtab.getMapSLReprFixedWidth()
        listSLRow = self.slEtab.getListSLRow()
        for ixSL in range(len(listSLRow)):
            self.lbSLOne.insert(END, mapSLReprFixedWidth[listSLRow[ixSL]]['strRepr'])
            if intIdSelected == listSLRow[ixSL]:
                self.lbSLOne.select_set(ixSL)
                self.lbSLOne.see(ixSL)
    def updateListGroup(self, intSLGId=None):
        if not intSLGId and self.lbSLGroup.curselection() and self.listRowSLGroup[int(self.lbSLGroup.curselection()[0])]:
            intSLGRow = self.listRowSLGroup[int(self.lbSLGroup.curselection()[0])]
            slGroup = self.slEtab.getSoftLockGroupInRow(intSLGRow)
            if slGroup:
                intSLGId = slGroup.getIntUniqueId()
        self.lbSLGroup.delete(0, self.lbSLGroup.size() - 1)
        mapSLGRepr = self.slEtab.getMapSLGroupListReprFixedWidth()
        self.listRowSLGroup = []
        intRow = 1
        listSLGroupRow = self.slEtab.getListSLGroupRow()
        for slgKey in listSLGroupRow:
            if intRow > 1:
                self.lbSLGroup.insert(END, '')
                self.listRowSLGroup.append(None)
            for strRepr in mapSLGRepr[slgKey]:
                self.lbSLGroup.insert(END, strRepr)
                self.listRowSLGroup.append(intRow)
            if intSLGId == slgKey:
                intListRow = self.lbSLGroup.size() - len(mapSLGRepr[slgKey])
                self.lbSLGroup.select_set(intListRow)
                self.lbSLGroup.see(intListRow)
            intRow += 1
    def addSoftLockGroup(self, slGroup):
        self.mapSLGroups[slGroup.getIntUniqueId()] = slGroup
    def deleteSoftLockGroup(self, slGroup):
        if slGroup.getIntUniqueId() in self.mapSLGroups.keys():
            del self.mapSLGroups[slGroup.getIntUniqueId()]
            self.slEtab.deleteSoftLockGroup(slGroup)
        else:
            raise Exception('Cannot delete SoftLock group "%s" (does not exist)' %(slGroup))
    def deleteSoftLock(self, softLock):
        self.slEtab.deleteSoftLock(softLock)
    def getBoolValidate(self):
        return self.BoolValidate.get()
    def disableSave(self):
        self.btnSave = Button(self.frameButtons, text='Save', fg='black', bg=gStrBGColorButton, bd=2, command=self.doSave,
                              activebackground=gStrActiveColor, width=self.buttonWidth, state=DISABLED)
        self.btnSave.grid(row=6, column=2)
    def enableSave(self):
        self.btnSave = Button(self.frameButtons, text='Save', fg='black', bg=gStrBGColorButton, bd=2, command=self.doSave,
                              activebackground=gStrActiveColor, width=self.buttonWidth)
        self.btnSave.grid(row=6, column=2)
    def doNew(self):
        if self.slEtab.getHasChanged():
            boolContinue = tkMessageBox.askyesno('Notice', 'SoftLock etab is modified.\nCreate a new one anyway?')
            if not boolContinue:
                return
        slEtabNew = SoftLockEtab(self.slEtab.getStrDefaultDir(), self.slEtab.getStrReportFile())
        self.initEtab(slEtabNew)
        self.disableSave()
    def doOpen(self):
        if self.slEtab.getHasChanged():
            boolContinue = tkMessageBox.askyesno('Notice', 'SoftLock etab is modified.\nOpen a new one anyway?')
            if not boolContinue:
                return
        if self.slEtab.getStrFilename():
            strInFile = self.slEtab.getStrFilename()
        else:
            strInFile = self.slEtab.getStrDefaultDir()
        strFilename = getFilenameDialog(gTypeOpen, self.root, strInFile)
        if strFilename:
            slEtabNew = SoftLockEtab(strFilename, self.slEtab.getStrReportFile())
            if not slEtabNew.getStrFilename():
                tkMessageBox.showwarning('Error', 'Not a SoftLock etab!')
                return
            self.initEtab(slEtabNew)
            self.enableSave()
            try:
                pass
            except:
                print 'Problem when opening SoftLocks etab "%s"' %(strFilename)
                print '%s: %s' %(sys.exc_type, sys.exc_value)
                sys.stdout.flush()
    def doSave(self):
        self.slEtab.writeSoftLocksToFile()
        self.updateTitle()
    def doSaveAs(self):
        if self.slEtab.getStrFilename():
            strInFile = self.slEtab.getStrFilename()
        else:
            strInFile = self.slEtab.getStrDefaultDir()
        strFilename = getFilenameDialog(gTypeSaveAs, self.root, strInFile)
        if strFilename:
            self.slEtab.setStrFilename(strFilename)
            self.slEtab.writeSoftLocksToFile()
            self.enableSave()
        self.updateTitle()
    def doPrint(self):
        # Get SoftLocks
        mapSLReprFixedWidth = self.slEtab.getMapSLReprFixedWidth(gMaxPageWidth, gMaxArrowPos)
        listSLRow = self.slEtab.getListSLRow()
        # Get SoftLock groups
        mapSLGRepr = self.slEtab.getMapSLGroupListReprFixedWidth()
        listSLGroupRow = self.slEtab.getListSLGroupRow()
        # Start printing
        p = subprocess.Popen(os.path.join(gStrCARMSYS, 'bin', 'print_file'), shell="False", stdin=subprocess.PIPE).stdin
        strFilename = self.slEtab.getStrFilename()
        if strFilename:
            strFilename = os.path.basename(strFilename)
        else:
            strFilename = '(New)'
        p.write('SoftLock file: %s\n\n\nSoftLocks:\n\n' %strFilename)
        for ixSL in range(len(listSLRow)):
            p.write('  %s\n' %mapSLReprFixedWidth[listSLRow[ixSL]]['strRepr'])
        p.write('\n\nSoftLock groups:\n')
        for slgKey in listSLGroupRow:
            p.write('\n')
            for strRepr in mapSLGRepr[slgKey]:
                p.write(breakLine(strRepr, gMaxPageWidth, indent=2))
        p.close()
    def _handlerAppGroupClosed(self, event, slGroup):
        intSLGId = slGroup.getIntUniqueId()
        if intSLGId in self.mapAppGroup.keys():
            doUpdate = self.mapAppGroup[intSLGId].getButtonPressed() == gLabelOkButton
            del self.mapAppGroup[intSLGId]
            if doUpdate:
                self.updateListGroup(intSLGId)
    def doNewGroup(self):
        slGroupNew = self.slEtab.createNewSoftLockGroup()
        newAppGroupSoftLock = AppGroupSoftLock(self, self.slEtab, slGroupNew, 1)
        self.addSoftLockGroup(slGroupNew)
        self.mapAppGroup[slGroupNew.getIntUniqueId()] = newAppGroupSoftLock
        def handlerThisAppGroupClosed(event, self=self):
            return self._handlerAppGroupClosed(event, slGroupNew)
        newAppGroupSoftLock.bind('<Destroy>', handlerThisAppGroupClosed)
        newAppGroupSoftLock.mainloop()
    def doCopyGroup(self):
        if not self.lbSLGroup.curselection() or not self.listRowSLGroup[int(self.lbSLGroup.curselection()[0])]:
            return
        intSLGRow = self.listRowSLGroup[int(self.lbSLGroup.curselection()[0])]
        slGroupToCopy = self.slEtab.getSoftLockGroupInRow(intSLGRow)
        slGroupCopy = slGroupToCopy.getCopy()
        self.slEtab.addSoftLockGroup(slGroupCopy)
        self.addSoftLockGroup(slGroupCopy)
        copyAppGroupSoftLock = AppGroupSoftLock(self, self.slEtab, slGroupCopy, 1)
        self.mapAppGroup[slGroupCopy.getIntUniqueId()] = copyAppGroupSoftLock
        def handlerThisAppGroupClosed(event, self=self):
            return self._handlerAppGroupClosed(event, slGroupCopy)
        copyAppGroupSoftLock.bind('<Destroy>', handlerThisAppGroupClosed)
        copyAppGroupSoftLock.mainloop()
    def doEditGroup(self, dummy=None):
        if not self.lbSLGroup.curselection() or not self.listRowSLGroup[int(self.lbSLGroup.curselection()[0])]:
            return
        intSLGRow = self.listRowSLGroup[int(self.lbSLGroup.curselection()[0])]
        slGroupToEdit = self.slEtab.getSoftLockGroupInRow(intSLGRow)
        if slGroupToEdit.getIntUniqueId() in self.mapAppGroup.keys():
            self.mapAppGroup[slGroupToEdit.getIntUniqueId()].lift()
            self.mapAppGroup[slGroupToEdit.getIntUniqueId()].focus_set()
        else:
            newAppGroupSoftLock = AppGroupSoftLock(self, self.slEtab, slGroupToEdit)
            self.mapAppGroup[slGroupToEdit.getIntUniqueId()] = newAppGroupSoftLock
            def handlerThisAppGroupClosed(event, self=self):
                return self._handlerAppGroupClosed(event, slGroupToEdit)
            newAppGroupSoftLock.bind('<Destroy>', handlerThisAppGroupClosed)
            newAppGroupSoftLock.mainloop()
    def doDeleteGroup(self):
        if not self.lbSLGroup.curselection() or not self.listRowSLGroup[int(self.lbSLGroup.curselection()[0])]:
            return
        intSLGRow = self.listRowSLGroup[int(self.lbSLGroup.curselection()[0])]
        slGroupToDelete = self.slEtab.getSoftLockGroupInRow(intSLGRow)
        if slGroupToDelete.getIntUniqueId() in self.mapAppGroup.keys():
            self.mapAppGroup[slGroupToDelete.getIntUniqueId()].destroy()
        self.deleteSoftLockGroup(slGroupToDelete)
        self.slEtab.setHasChanged(1)
        self.updateTitle()
        self.updateListGroup()
    def doMoveUpGroup(self):
        if not self.lbSLGroup.curselection() or not self.listRowSLGroup[int(self.lbSLGroup.curselection()[0])]:
            return
        intSLGRow = self.listRowSLGroup[int(self.lbSLGroup.curselection()[0])]
        slGroupIdToMove = self.slEtab.getSoftLockGroupInRow(intSLGRow).getIntUniqueId()
        self.slEtab.moveSoftLockGroupUp(slGroupIdToMove)
        self.slEtab.setHasChanged(1)
        self.updateTitle()
        self.updateListGroup(slGroupIdToMove)
    def doMoveDownGroup(self):
        if not self.lbSLGroup.curselection() or not self.listRowSLGroup[int(self.lbSLGroup.curselection()[0])]:
            return
        intSLGRow = self.listRowSLGroup[int(self.lbSLGroup.curselection()[0])]
        slGroupIdToMove = self.slEtab.getSoftLockGroupInRow(intSLGRow).getIntUniqueId()
        self.slEtab.moveSoftLockGroupDown(slGroupIdToMove)
        self.slEtab.setHasChanged(1)
        self.updateTitle()
        self.updateListGroup(slGroupIdToMove)        
    def _handlerAppOneClosed(self, event, softLock):
        intSLId = softLock.getIntUniqueId()
        if intSLId in self.mapAppOne.keys():
            doUpdate = self.mapAppOne[intSLId].getButtonPressed() == gLabelOkButton            
            del self.mapAppOne[intSLId]
            if doUpdate:
                self.updateListOne(intSLId)
    def doNewOne(self):
        softLockNew = self.slEtab.createNewSoftLock()
        newAppOneSoftLock = AppOneSoftLock(self, self.slEtab, softLockNew, 1)
        self.mapAppOne[softLockNew.getIntUniqueId()] = newAppOneSoftLock
        def handlerThisAppOneClosed(event, self=self):
            return self._handlerAppOneClosed(event, softLockNew)
        newAppOneSoftLock.bind('<Destroy>', handlerThisAppOneClosed)
        newAppOneSoftLock.mainloop()
    def doCopyOne(self):
        if not self.lbSLOne.curselection():
            return
        slToCopy = self.slEtab.getSoftLockInRow(int(self.lbSLOne.curselection()[0]) + 1)
        softLockCopy = slToCopy.getCopy()
        self.slEtab.addSoftLock(softLockCopy)
        copyAppOneSoftLock = AppOneSoftLock(self, self.slEtab, softLockCopy, 1)
        self.mapAppOne[softLockCopy.getIntUniqueId()] = copyAppOneSoftLock
        def handlerThisAppOneClosed(event, self=self):
            return self._handlerAppOneClosed(event, softLockCopy)
        copyAppOneSoftLock.bind('<Destroy>', handlerThisAppOneClosed)
        copyAppOneSoftLock.mainloop()
    def doEditOne(self, dummy=None):
        if not self.lbSLOne.curselection():
            # tkMessageBox.showwarning('Warning', 'No SoftLock selected!')
            return
        slToEdit = self.slEtab.getSoftLockInRow(int(self.lbSLOne.curselection()[0]) + 1)
        if slToEdit.getIntUniqueId() in self.mapAppOne.keys():
            self.mapAppOne[slToEdit.getIntUniqueId()].lift()
            self.mapAppOne[slToEdit.getIntUniqueId()].focus_set()
        else:
            newAppOneSoftLock = AppOneSoftLock(self, self.slEtab, slToEdit)
            self.mapAppOne[slToEdit.getIntUniqueId()] = newAppOneSoftLock
            def handlerThisAppOneClosed(event, self=self):
                return self._handlerAppOneClosed(event, slToEdit)
            newAppOneSoftLock.bind('<Destroy>', handlerThisAppOneClosed)
            newAppOneSoftLock.mainloop()
    def doDeleteOne(self):
        if not self.lbSLOne.curselection():
            return
        slToDelete = self.slEtab.getSoftLockInRow(int(self.lbSLOne.curselection()[0]) + 1)
        if slToDelete.getIntUniqueId() in self.mapAppOne.keys():
            self.mapAppOne[slToDelete.getIntUniqueId()].destroy()
        self.deleteSoftLock(slToDelete)
        self.slEtab.setHasChanged(1)
        self.updateTitle()
        self.updateListOne()
    def doMoveUpOne(self):
        if not self.lbSLOne.curselection():
            return
        slToMoveId = self.slEtab.getSoftLockInRow(int(self.lbSLOne.curselection()[0]) + 1).getIntUniqueId()
        self.slEtab.moveSoftLockUp(slToMoveId)
        self.slEtab.setHasChanged(1)
        self.updateTitle()
        self.updateListOne(slToMoveId)
    def doMoveDownOne(self):
        if not self.lbSLOne.curselection():
            return
        slToMoveId = self.slEtab.getSoftLockInRow(int(self.lbSLOne.curselection()[0]) + 1).getIntUniqueId()
        self.slEtab.moveSoftLockDown(slToMoveId)
        self.slEtab.setHasChanged(1)
        self.updateTitle()
        self.updateListOne(slToMoveId)
    def doOnOff(self):
        if not self.lbSLOne.curselection():
            return
        slOnOffId = self.slEtab.getSoftLockInRow(int(self.lbSLOne.curselection()[0]) + 1).getIntUniqueId()
        self.slEtab.toggleSLOnOff(slOnOffId)
        self.slEtab.setHasChanged(1)
        self.updateTitle()
        self.updateListOne(slOnOffId)
    def doCloseAll(self):
        for intSLId in self.mapAppOne.keys():
            self.mapAppOne[intSLId].destroy()
        for intSLGId in self.mapAppGroup.keys():
            self.mapAppGroup[intSLGId].destroy()
    def doExit(self):
        if self.slEtab.getHasChanged():
            boolContinue = tkMessageBox.askyesno('Notice', 'SoftLock etab is modified.\nExit anyway?')
            if not boolContinue:
                return
        self.doCloseAll()
        self.root.destroy()

## defaultextension   string
##  extension to add to the filename, if not explicitly given by the user. The string should include the leading dot (ignored by the open dialog).

## filetypes   list
## Sequence of (label, pattern) tuples. The same label may occur with several patterns. Use "*" as the pattern to indicate all files.

## initialdir   string
## Initial directory.

## initialfile   string
## Initial file (ignored by the open dialog)

## parent   widget
## Which window to place the message box on top of. When the dialog is closed, the focus is returned to the parent window.

## title   string
## Message box title.

def getFilenameDialog(intType, parent, strInFile=None):
    if intType == gTypeSaveAs:
        strTitle = 'Save As'
        funcDialog = tkFileDialog.asksaveasfilename
    elif intType == gTypeOpen:
        strTitle = 'Open'
        funcDialog = tkFileDialog.askopenfilename
    else:
        return None
    parent.deiconify()
    #parent.wait_visibility() # wait for window to be displayed
    #parent.focus_force() # force it to be in focus (in front of all other windows)
    if strInFile:
        strInitialDir = os.path.dirname(strInFile)
        strInitialFile = os.path.basename(strInFile)
    else:
        strInitialDir = os.path.join(gStrCARMUSR, 'crc', 'etable')
        strInitialFile = ''
    strFilename = funcDialog(filetypes=[('SoftLock etabs', '.etab')], defaultextension='.etab',
                             title=strTitle, initialdir=strInitialDir, parent=parent,
                             initialfile=strInitialFile)
    if not strFilename:
        return None
    if len(strFilename) < 6 or strFilename[-5:] != '.etab':
        strFilename = strFilename + '.etab'
    return strFilename

class AppGroupSoftLock(Toplevel):
    """Application used to edit a SoftLockGroup, or create a new one"""
    def __init__(self, parent, slEtab, softLockGroup, boolIsNew=0):
        Toplevel.__init__(self, parent)
        self.softLockGroup = softLockGroup
        self.parent = parent
        self.slEtab = slEtab
        self.listValidateFuncs = []
        # self.mapCxn is:
        # {intRow : [[StrFlightNr, StrDepArr], ...]}
        self.mapCxn = {}
        self.mapCxnItems = {}
        self.transient(self.parent)
        self.validateAtEndOnly = 0
        self.isAtEnd = 0
        self.buttonPressed = None
        self.body = Frame(self, bg=gStrBGColorMain)
        if boolIsNew:
            self.isNewDialog = 1
            self.title('New SoftLock group')
        else:
            self.isNewDialog = 0
            self.title('Edit SoftLock group')
        self.resizable(width=NO, height=NO)
        self.initial_focus = self._body(self.body)
        self.body.pack()
        # Makes the dialog modal
        # self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.doCancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.setFrameNormal()
        self.initial_focus.focus_set()
        # Stops execution in calling program
        # self.wait_window(self)

    def _body(self, master):
        
        #################
        #    Frames     #
        #################

        strBGColorCxn = gStrBGColorMain
        strFGColorCxn = 'black'
        strFGColorCxnLabels = 'black'
        strBGColorPenalty = gStrBGColorMain
        strFGColorPenalty = 'black'
        strBGColorConstraints = gStrBGColorDark
        strFGColorConstraints = 'black'
        strBGColorComment = gStrBGColorMain
        strFGColorComment = 'black'
        
        # frame with the main title
        self.frameUpper = Frame(master, bg=gStrBGColorMain)
        # frame with the leg connections
        self.frameCxn = Frame(master, bg=strBGColorCxn)
        # Frame with the "normal" content of the App
        self.frameDefaultSL = Frame(master, bg=gStrBGColorMain)

        self.framePenalty = Frame(self.frameDefaultSL, bg=strBGColorPenalty)
        self.frameConstraints = Frame(self.frameDefaultSL, bg=strBGColorConstraints)
        self.frameEmptyDark = Frame(self.frameDefaultSL, bg=gStrBGColorDark)
        self.frameComment = Frame(self.frameDefaultSL, bg=strBGColorComment)
        self.frameLower = Frame(self.frameDefaultSL, bg=gStrBGColorMain)

        self.frameConRow1 = Frame(self.frameConstraints, bg=strBGColorConstraints)
        self.frameConRow2 = Frame(self.frameConstraints, bg=strBGColorConstraints)
        self.frameConRow3 = Frame(self.frameConstraints, bg=strBGColorConstraints)

        #################
        #     Title     #
        #################
        self.labelTitle=Label(self.frameUpper, text='Edit SoftLock group', font=('Helvetica',15,'bold'),
                              bd=2, bg=gStrBGColorMain)

        #################
        #   Leg cxns    #
        #################
        
        self.labelCxn = Label(self.frameCxn, text='Connections', font=('Helvetica',11), bd=2,
                              bg=strBGColorCxn, fg=strFGColorCxn)
        listCxnIds = self.softLockGroup.getListCxnIds()
        self.listLabelTripStart = []
        self.listLabelTripEnd = []
        self.listLabelFlightNr = [[], []]
        self.listLabelDepArr = [[], []]
        self.listLabelDutyStop = [[], []]
        for ixRow in range(2):
            self.listLabelTripStart.append(Label(self.frameCxn, text='Trip start', font=('Helvetica',7), bd=2,
                                                 bg=strBGColorCxn, fg=strFGColorCxnLabels))
            self.listLabelTripEnd.append(Label(self.frameCxn, text='Trip end', font=('Helvetica',7), bd=2,
                                               bg=strBGColorCxn, fg=strFGColorCxnLabels))
            for ixLeg in range(gNumSLGroupLegs):
                self.listLabelFlightNr[ixRow].append(Label(self.frameCxn, text='Fl.no.', font=('Helvetica',7), bd=2,
                                                           bg=strBGColorCxn, fg=strFGColorCxnLabels))
                self.listLabelDepArr[ixRow].append(Label(self.frameCxn, text='DEP-ARR', font=('Helvetica',7), bd=2,
                                                         bg=strBGColorCxn, fg=strFGColorCxnLabels))
                self.listLabelDutyStop[ixRow].append(Label(self.frameCxn, text='D-stop', font=('Helvetica',7), bd=2,
                                                           bg=strBGColorCxn, fg=strFGColorCxnLabels))
        self.listFlightNr = []
        self.listDepArr = []
        self.listDutyStop = []
        for ixRow in range(gNumSLGroupCxns):
            self.listFlightNr.append([])
            self.listDepArr.append([])
            self.listDutyStop.append([])
            if ixRow < len(listCxnIds):
                intCxnId = listCxnIds[ixRow]
            else:
                intCxnId = None
            BoolTripStart = BooleanVar()
            if intCxnId != None and self.softLockGroup.getBoolTripStart(intCxnId):
                BoolTripStart.set(1)
            cbTripStart = Checkbutton(self.frameCxn, variable=BoolTripStart, bg=strBGColorCxn,
                                      fg=strFGColorCxn, activebackground=gStrActiveColor,
                                      indicatoron=1)
            BoolTripEnd = BooleanVar()
            if intCxnId != None and self.softLockGroup.getBoolTripEnd(intCxnId):
                BoolTripEnd.set(1)
            cbTripEnd = Checkbutton(self.frameCxn, variable=BoolTripEnd, bg=strBGColorCxn,
                                    fg=strFGColorCxn, activebackground=gStrActiveColor,
                                    indicatoron=1)
            # Cxn variables
            self.mapCxn[ixRow] = [BoolTripStart, [], BoolTripEnd]
            # Cxn items, such as entries and checkbuttons
            self.mapCxnItems[ixRow] = [cbTripStart, [], cbTripEnd]
            if intCxnId != None:
                listCxnLegs = self.softLockGroup.getListCxnLegs(intCxnId)
            else:
                listCxnLegs = []
            for ixLeg in range(gNumSLGroupLegs):
                # Flight number
                self.listFlightNr[ixRow].append([StringVar(), None])
                self.listFlightNr[ixRow][ixLeg][1] = Entry(self.frameCxn, textvariable=self.listFlightNr[ixRow][ixLeg][0],
                                                      bg=strBGColorCxn, fg=strFGColorCxn, width=4)
                if ixLeg < len(listCxnLegs) and gReNumber.match(listCxnLegs[ixLeg][0]) and int(listCxnLegs[ixLeg][0]) > 0:
                    self.listFlightNr[ixRow][ixLeg][0].set(listCxnLegs[ixLeg][0])
                # Dep-arr
                self.listDepArr[ixRow].append([StringVar(), None])
                self.listDepArr[ixRow][ixLeg][1] = Entry(self.frameCxn, textvariable=self.listDepArr[ixRow][ixLeg][0],
                                                         font=('Helvetica',7), bg=strBGColorCxn, fg=strFGColorCxn, width=9)
                if ixLeg < len(listCxnLegs):
                    self.listDepArr[ixRow][ixLeg][0].set(listCxnLegs[ixLeg][1])
                # Duty stop
                self.listDutyStop[ixRow].append([BooleanVar(), None])
                self.listDutyStop[ixRow][ixLeg][1] = Checkbutton(self.frameCxn,
                                                                 variable=self.listDutyStop[ixRow][ixLeg][0],
                                                                 bg=strBGColorCxn,
                                                                 fg=strFGColorCxn,
                                                                 activebackground=gStrActiveColor,
                                                                 indicatoron=1)
                # Cxn variables
                self.mapCxn[ixRow][1].append([self.listFlightNr[ixRow][ixLeg][0], self.listDepArr[ixRow][ixLeg][0], self.listDutyStop[ixRow][ixLeg][0]])
                # Cxn items, such as entries and checkbuttons
                #self.mapCxnItems[ixRow][1].append([labelFlightNr, self.listFlightNr[ixRow][ixLeg][1], labelDepArr, self.listDepArr[ixRow][ixLeg][1], labelDutyStop, self.listDutyStop[ixRow][ixLeg][1]])
                self.mapCxnItems[ixRow][1].append([self.listFlightNr[ixRow][ixLeg][1], self.listDepArr[ixRow][ixLeg][1], self.listDutyStop[ixRow][ixLeg][1]])
                if ixLeg < len(listCxnLegs):
                    self.listDutyStop[ixRow][ixLeg][0].set(listCxnLegs[ixLeg][2])

        # 6x5 binds for checking the flight number fields
        self.registerHandler('Flight no. row 1, leg 1', self.mapCxnItems[0][1][0][0], self.mapCxn[0][1][0][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 1, leg 2', self.mapCxnItems[0][1][1][0], self.mapCxn[0][1][1][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 1, leg 3', self.mapCxnItems[0][1][2][0], self.mapCxn[0][1][2][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 1, leg 4', self.mapCxnItems[0][1][3][0], self.mapCxn[0][1][3][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 1, leg 5', self.mapCxnItems[0][1][4][0], self.mapCxn[0][1][4][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 2, leg 1', self.mapCxnItems[1][1][0][0], self.mapCxn[1][1][0][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 2, leg 2', self.mapCxnItems[1][1][1][0], self.mapCxn[1][1][1][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 2, leg 3', self.mapCxnItems[1][1][2][0], self.mapCxn[1][1][2][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 2, leg 4', self.mapCxnItems[1][1][3][0], self.mapCxn[1][1][3][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 2, leg 5', self.mapCxnItems[1][1][4][0], self.mapCxn[1][1][4][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 3, leg 1', self.mapCxnItems[2][1][0][0], self.mapCxn[2][1][0][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 3, leg 2', self.mapCxnItems[2][1][1][0], self.mapCxn[2][1][1][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 3, leg 3', self.mapCxnItems[2][1][2][0], self.mapCxn[2][1][2][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 3, leg 4', self.mapCxnItems[2][1][3][0], self.mapCxn[2][1][3][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 3, leg 5', self.mapCxnItems[2][1][4][0], self.mapCxn[2][1][4][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 4, leg 1', self.mapCxnItems[3][1][0][0], self.mapCxn[3][1][0][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 4, leg 2', self.mapCxnItems[3][1][1][0], self.mapCxn[3][1][1][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 4, leg 3', self.mapCxnItems[3][1][2][0], self.mapCxn[3][1][2][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 4, leg 4', self.mapCxnItems[3][1][3][0], self.mapCxn[3][1][3][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 4, leg 5', self.mapCxnItems[3][1][4][0], self.mapCxn[3][1][4][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 5, leg 1', self.mapCxnItems[4][1][0][0], self.mapCxn[4][1][0][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 5, leg 2', self.mapCxnItems[4][1][1][0], self.mapCxn[4][1][1][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 5, leg 3', self.mapCxnItems[4][1][2][0], self.mapCxn[4][1][2][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 5, leg 4', self.mapCxnItems[4][1][3][0], self.mapCxn[4][1][3][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 5, leg 5', self.mapCxnItems[4][1][4][0], self.mapCxn[4][1][4][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 6, leg 1', self.mapCxnItems[5][1][0][0], self.mapCxn[5][1][0][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 6, leg 2', self.mapCxnItems[5][1][1][0], self.mapCxn[5][1][1][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 6, leg 3', self.mapCxnItems[5][1][2][0], self.mapCxn[5][1][2][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 6, leg 4', self.mapCxnItems[5][1][3][0], self.mapCxn[5][1][3][0], SoftLock.checkIntFlightNr)
        self.registerHandler('Flight no. row 6, leg 5', self.mapCxnItems[5][1][4][0], self.mapCxn[5][1][4][0], SoftLock.checkIntFlightNr)

        # 6x5 binds for checking the flight number fields
        self.registerHandler('Dep-arr, row 1, leg 1', self.mapCxnItems[0][1][0][1], self.mapCxn[0][1][0][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 1, leg 2', self.mapCxnItems[0][1][1][1], self.mapCxn[0][1][1][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 1, leg 3', self.mapCxnItems[0][1][2][1], self.mapCxn[0][1][2][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 1, leg 4', self.mapCxnItems[0][1][3][1], self.mapCxn[0][1][3][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 1, leg 5', self.mapCxnItems[0][1][4][1], self.mapCxn[0][1][4][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 2, leg 1', self.mapCxnItems[1][1][0][1], self.mapCxn[1][1][0][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 2, leg 2', self.mapCxnItems[1][1][1][1], self.mapCxn[1][1][1][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 2, leg 3', self.mapCxnItems[1][1][2][1], self.mapCxn[1][1][2][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 2, leg 4', self.mapCxnItems[1][1][3][1], self.mapCxn[1][1][3][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 2, leg 5', self.mapCxnItems[1][1][4][1], self.mapCxn[1][1][4][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 3, leg 1', self.mapCxnItems[2][1][0][1], self.mapCxn[2][1][0][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 3, leg 2', self.mapCxnItems[2][1][1][1], self.mapCxn[2][1][1][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 3, leg 3', self.mapCxnItems[2][1][2][1], self.mapCxn[2][1][2][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 3, leg 4', self.mapCxnItems[2][1][3][1], self.mapCxn[2][1][3][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 3, leg 5', self.mapCxnItems[2][1][4][1], self.mapCxn[2][1][4][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 4, leg 1', self.mapCxnItems[3][1][0][1], self.mapCxn[3][1][0][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 4, leg 2', self.mapCxnItems[3][1][1][1], self.mapCxn[3][1][1][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 4, leg 3', self.mapCxnItems[3][1][2][1], self.mapCxn[3][1][2][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 4, leg 4', self.mapCxnItems[3][1][3][1], self.mapCxn[3][1][3][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 4, leg 5', self.mapCxnItems[3][1][4][1], self.mapCxn[3][1][4][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 5, leg 1', self.mapCxnItems[4][1][0][1], self.mapCxn[4][1][0][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 5, leg 2', self.mapCxnItems[4][1][1][1], self.mapCxn[4][1][1][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 5, leg 3', self.mapCxnItems[4][1][2][1], self.mapCxn[4][1][2][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 5, leg 4', self.mapCxnItems[4][1][3][1], self.mapCxn[4][1][3][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 5, leg 5', self.mapCxnItems[4][1][4][1], self.mapCxn[4][1][4][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 6, leg 1', self.mapCxnItems[5][1][0][1], self.mapCxn[5][1][0][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 6, leg 2', self.mapCxnItems[5][1][1][1], self.mapCxn[5][1][1][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 6, leg 3', self.mapCxnItems[5][1][2][1], self.mapCxn[5][1][2][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 6, leg 4', self.mapCxnItems[5][1][3][1], self.mapCxn[5][1][3][1], SoftLock.checkStrDepArr)
        self.registerHandler('Dep-arr, row 6, leg 5', self.mapCxnItems[5][1][4][1], self.mapCxn[5][1][4][1], SoftLock.checkStrDepArr)

        #################
        #    Penalty    #
        #################

        self.labelPenalty = Label(self.framePenalty, text='Penalty', font=('Helvetica',11), bd=2,
                                  bg=strBGColorPenalty, fg=strFGColorPenalty)
        self.StrPenalty = StringVar()
        self.StrPenalty.set(str(self.softLockGroup.getIntPenalty()))
        self.entryPenalty = Entry(self.framePenalty, textvariable=self.StrPenalty,
                                  bg=strBGColorPenalty, fg=strFGColorPenalty, width=10)
        self.registerHandler('Penalty', self.entryPenalty, self.StrPenalty, SoftLock.checkIntNonNeg, 0)

        #################
        #     Leg 1     #
        #################

        self.labelCarrier = Label(self.frameConRow1, text='Carrier', font=('Helvetica',9), bd=2,
                                  bg=strBGColorConstraints, fg=strFGColorConstraints)
        self.StrCarrier = StringVar()
        self.StrCarrier.set(self.softLockGroup.getStrCarrier())
        self.entryCarrier = Entry(self.frameConRow1, textvariable=self.StrCarrier, bg=strBGColorConstraints,
                                  fg=strFGColorConstraints, width=4)
        self.registerHandler('Carrier', self.entryCarrier, self.StrCarrier, SoftLock.checkStrCarrier, 0)

        self.labelACType = Label(self.frameConRow1, text='AC type', font=('Helvetica',9), bd=2,
                                 bg=strBGColorConstraints, fg=strFGColorConstraints)
        self.StrACType = StringVar()
        self.StrACType.set(self.softLockGroup.getStrACType())
        self.entryACType = Entry(self.frameConRow1, textvariable=self.StrACType, bg=strBGColorConstraints,
                                 fg=strFGColorConstraints, width=5)

        self.StrActOrDH= StringVar()
        self.rbActOrDH = []
        self.rbActOrDH.append(Radiobutton(self.frameConRow2, text="Active", variable=self.StrActOrDH,
                                           value='A', bg=strBGColorConstraints, fg=strFGColorConstraints,
                                           activebackground=gStrActiveColor))
        self.rbActOrDH.append(Radiobutton(self.frameConRow2, text="Any", variable=self.StrActOrDH,
                                           value='*', bg=strBGColorConstraints, fg=strFGColorConstraints,
                                           activebackground=gStrActiveColor))
        if self.softLockGroup.getStrActiveOrDH() == 'A':
            self.rbActOrDH[0].select()
        else:
            self.rbActOrDH[1].select()

        self.labelDateFrom = Label(self.frameConRow2, text='From', font=('Helvetica',9), bd=2,
                                   bg=strBGColorConstraints, fg=strFGColorConstraints)
        self.StrDateFrom = StringVar()
        self.StrDateFrom.set(self.softLockGroup.getStrDateFrom())
        self.entryDateFrom = Entry(self.frameConRow2, textvariable=self.StrDateFrom,
                                   bg=strBGColorConstraints, fg=strFGColorConstraints, width=10)
        self.registerHandler('Date from', self.entryDateFrom, self.StrDateFrom, SoftLock.checkStrDate, 0)

        self.labelDateTo = Label(self.frameConRow2, text='To', font=('Helvetica',9), bd=2,
                                  bg=strBGColorConstraints, fg=strFGColorConstraints)
        self.StrDateTo = StringVar()
        self.StrDateTo.set(self.softLockGroup.getStrDateTo())
        self.entryDateTo = Entry(self.frameConRow2, textvariable=self.StrDateTo, bg=strBGColorConstraints,
                                  fg=strFGColorConstraints, width=10)
        self.registerHandler('Date to', self.entryDateTo, self.StrDateTo, SoftLock.checkStrDate, 0)

        #################
        #  Constraints  #
        #################

        self.labelConstraints = Label(self.frameConstraints, text='Constraints',
                                      font=('Helvetica',11), bd=2, bg=strBGColorConstraints,
                                      fg=strFGColorConstraints)
        self.labelLimitMin = Label(self.frameConRow3, text='Limit Min', font=('Helvetica',9),
                                   bd=2, bg=strBGColorConstraints, fg=strFGColorConstraints)
        self.StrLimitMin = StringVar()
        self.StrLimitMin.set(self.softLockGroup.getStrLimitMin())
        self.entryLimitMin = Entry(self.frameConRow3, textvariable=self.StrLimitMin,
                                   bg=strBGColorConstraints, fg=strFGColorConstraints, width=7)
        self.registerHandler('Limit min', self.entryLimitMin, self.StrLimitMin, SoftLock.checkStrLimit, 0)

        self.labelLimitMax = Label(self.frameConRow3, text='Limit Max', font=('Helvetica',9),
                                   bd=2, bg=strBGColorConstraints, fg=strFGColorConstraints)
        self.StrLimitMax = StringVar()
        self.StrLimitMax.set(self.softLockGroup.getStrLimitMax())
        self.entryLimitMax = Entry(self.frameConRow3, textvariable=self.StrLimitMax,
                                   bg=strBGColorConstraints, fg=strFGColorConstraints, width=7)
        self.registerHandler('Limit max', self.entryLimitMax, self.StrLimitMax, SoftLock.checkStrLimit, 0)

        self.labelBase = Label(self.frameConRow1, text='Base', font=('Helvetica',9), bd=2,
                               bg=strBGColorConstraints, fg=strFGColorConstraints)
        self.StrBase = StringVar()
        self.StrBase.set(self.softLockGroup.getStrBase())
        self.entryBase = Entry(self.frameConRow1, textvariable=self.StrBase,
                               bg=strBGColorConstraints, fg=strFGColorConstraints, width=5)
        self.registerHandler('Base', self.entryBase, self.StrBase, SoftLock.checkStrBase)

        #################
        #     Empty     #
        #################

        self.labelEmptyDark = Label(self.frameEmptyDark, text='   ', bg=gStrBGColorDark)

        #################
        #    Comment    #
        #################

        self.labelComment = Label(self.frameComment, text='Comment', font=('Helvetica',11), bd=2,
                                  bg=strBGColorComment, fg=strFGColorComment)
        self.StrComment = StringVar()
        self.StrComment.set(self.softLockGroup.getStrComment())
        self.entryComment = Entry(self.frameComment, textvariable=self.StrComment,
                                  bg=strBGColorComment, fg=strFGColorComment, width=24)
        self.registerHandler('Comment', self.entryComment, self.StrComment, SoftLock.checkStrComment, 1, 0)

        #################
        #    Buttons    #
        #################

        self.btnSave=Button(self.frameLower, text=gLabelOkButton, fg='black', bg=gStrBGColorButton, bd=2, command=self.doOk,
                            activebackground=gStrActiveColor)
        self.btnCancel=Button(self.frameLower, text=gLabelCancelButton, fg='black', bg=gStrBGColorButton, bd=2,
                              command=self.doCancel, activebackground=gStrActiveColor)
        self.setAllGrids()
        return self.entryPenalty
    def _validateAtEnd(self):
        self.isAtEnd = 1
        for funcValidate in self.listValidateFuncs:
            if funcValidate():
                self.isAtEnd = 0
                return 1
        self.isAtEnd = 0
        return 0
    def getButtonPressed(self):
        return self.buttonPressed
    def registerHandler(self, strName, entry, variable, funcCheck, emptyOk=1, toUpper=1):
        def handler(event=None, self=self):
            return self._validateEntry(event, strName, funcCheck, variable, emptyOk, toUpper)
        entry.bind('<FocusOut>', handler)
        self.listValidateFuncs.append(handler)
    def _validateEntry(self, event, strName, funcValidate, StrVar=None, emptyOk=1, toUpper=1):
        if StrVar.get() == '' and emptyOk or self.validateAtEndOnly and not self.isAtEnd:
            return ''
        if StrVar.get() == '' and not emptyOk:
            strWarningMessage = '%s may not be empty' %(strName)
        else:
            if toUpper and StrVar and StrVar.get() != StrVar.get().upper():
                StrVar.set(StrVar.get().upper())
            strWarningMessage = funcValidate(StrVar.get(), strName)
        if strWarningMessage and (not self.validateAtEndOnly or self.isAtEnd):
            tkMessageBox.showwarning('Warning', strWarningMessage)
            if event:
                event.widget.focus_set() # put focus back
        return strWarningMessage    
    def _updateSoftLockGroup(self):
        self.softLockGroup.setStrCarrier(self.StrCarrier.get())
        self.softLockGroup.setStrActiveOrDH(self.StrActOrDH.get())
        self.softLockGroup.setStrDateFrom(self.StrDateFrom.get())
        self.softLockGroup.setStrDateTo(self.StrDateTo.get())
        self.softLockGroup.setStrLimitMin(self.StrLimitMin.get())
        self.softLockGroup.setStrLimitMax(self.StrLimitMax.get())
        self.softLockGroup.setStrBase(self.StrBase.get())
        self.softLockGroup.setStrACType(self.StrACType.get())
        self.softLockGroup.setIntPenalty(int(self.StrPenalty.get()))
        self.softLockGroup.setStrComment(self.StrComment.get())
        self.softLockGroup.emptyCxnLegs()
        for ixRow in range(gNumSLGroupCxns):
            listCxnLegs = []
            for ixLeg in range(gNumSLGroupLegs):
                strFlightNr = self.mapCxn[ixRow][1][ixLeg][0].get()
                strDepArr = self.mapCxn[ixRow][1][ixLeg][1].get()
                boolDutyStop = self.mapCxn[ixRow][1][ixLeg][2].get()
                if strDepArr or strFlightNr:
                    listCxnLegs.append([strFlightNr, strDepArr, boolDutyStop])
            if len(listCxnLegs) > 1:
                self.softLockGroup.setListCxnLegs(ixRow, listCxnLegs)
                self.softLockGroup.setBoolTripStart(ixRow, self.mapCxn[ixRow][0].get())
                self.softLockGroup.setBoolTripEnd(ixRow, self.mapCxn[ixRow][2].get())
    def getSoftLockGroup(self):
        return self.softLockGroup
    def doOk(self):
        if self._validateAtEnd():
            return
        self._updateSoftLockGroup()
        listSoftLocks = self.softLockGroup.getListSoftLocks()
        if not listSoftLocks:
            self.parent.deleteSoftLockGroup(self.softLockGroup)
        else:
            listProblems = self.softLockGroup.getDefaultSoftLock().correctByType()
            for listSL in listSoftLocks:
                for softLock in listSL:
                    listProblems += softLock.correctByType()
            if listProblems:
                strMessage = '\n'.join(['Problems with SoftLock group'] + listProblems + ['Please correct this'])
                tkMessageBox.showinfo('Problems', strMessage)
                return
            if self.parent.getBoolValidate():
                strReportFile = self.slEtab.getStrReportFile()
                if strReportFile:
                    listNotice = []
                    for listSL in listSoftLocks:
                        for softLock in listSL:
                            listNotice += validateSoftLockFromReport(softLock, strReportFile)
                    if listNotice:
                        strMessage = '\n'.join(['Problems with SoftLock group'] + listNotice + ['Continue anyway?'])
                        boolContinue = tkMessageBox.askyesno('Notice', strMessage)
                        if not boolContinue:
                            return
        try:
            pass
        except:
            boolContinue = tkMessageBox.askyesno('Notice', 'Exception when updating SoftLock. Continue?')
            if not boolContinue:
                return
        self.buttonPressed = gLabelOkButton
        self.slEtab.setHasChanged(1)
        self.parent.updateTitle()
        self.withdraw()
        self.update_idletasks()
        # Put focus back to the parent window
        self.parent.focus_set()
        self.destroy()
    def doCancel(self):
        if self.isNewDialog:
            self.slEtab.deleteSoftLockGroup(self.softLockGroup)
        self.buttonPressed = gLabelCancelButton
        # Put focus back to the parent window
        self.parent.focus_set()
        self.destroy()
    def setFrameNormal(self):
        self.setAllGrids()
    def setAllGrids(self):
        # Top frames
        self.frameUpper.grid(row=2, rowspan=2, column=2, columnspan=4, sticky=EW)
        self.frameCxn.grid(row=4, rowspan=2, column=2, columnspan=2, sticky=N+S)
        self.frameDefaultSL.grid(row=4, rowspan=2, column=4, columnspan=2, sticky=NSEW)

        #######################
        # Items within frameCxn
        self.labelCxn.grid(row=0, column=0, columnspan=15, sticky=EW)
        # Column headers
        for ixRow in range(2):
            self.listLabelTripStart[ixRow].grid(row=1+3*gNumSLGroupCxns*ixRow, column=0, sticky=EW)
            self.listLabelTripEnd[ixRow].grid(row=1+3*gNumSLGroupCxns*ixRow, column=3*gNumSLGroupLegs, sticky=EW)
            for ixLeg in range(gNumSLGroupLegs):
                self.listLabelFlightNr[ixRow][ixLeg].grid(row=1+3*gNumSLGroupCxns*ixRow, column=3*ixLeg+1, sticky=EW)
                self.listLabelDepArr[ixRow][ixLeg].grid(row=1+3*gNumSLGroupCxns*ixRow, column=3*ixLeg+2, sticky=EW)
                if ixLeg + 1 < gNumSLGroupLegs:
                    self.listLabelDutyStop[ixRow][ixLeg].grid(row=1+3*gNumSLGroupCxns*ixRow, column=3*ixLeg+3, sticky=EW)
        for ixRow in range(gNumSLGroupCxns):
            [cbTripStart, listTupLeg, cbTripEnd] = self.mapCxnItems[ixRow]
            cbTripStart.grid(row=3*ixRow+2, column=0, sticky=EW)
            cbTripEnd.grid(row=3*ixRow+2, column=3*gNumSLGroupLegs, sticky=EW)
            for ixLeg in range(gNumSLGroupLegs):
                [entryFlightNr, entryDepArr, entryDutyStop] = listTupLeg[ixLeg]
                entryFlightNr.grid(row=3*ixRow+2, column=3*ixLeg+1, sticky=EW)
                entryDepArr.grid(row=3*ixRow+2, column=3*ixLeg+2, sticky=EW)
                if ixLeg + 1 < gNumSLGroupLegs:
                    entryDutyStop.grid(row=3*ixRow+2, column=3*ixLeg+3, sticky=EW)

        # Frames within frameDefaultSL
        self.framePenalty.grid(row=2, column=2, sticky=W)
        self.frameConstraints.grid(row=4, column=2, sticky=W)
        self.frameComment.grid(row=6, column=2, sticky=W)
        self.frameLower.grid(row=8, column=2, sticky=EW)

        # Items within frameUpper
        self.labelTitle.grid(row=2, column=2)

        # Items within framePenalty
        self.labelPenalty.grid(row=2, column=2)
        self.entryPenalty.grid(row=4, rowspan=2, column=2, columnspan=2, sticky=W)

        # Frames within frameConstraints
        self.labelConstraints.grid(row=0, column=2, sticky=SW)
        self.frameConRow1.grid(row=1, column=2, sticky=SW)
        self.frameConRow2.grid(row=2, column=2, sticky=SW)
        self.frameConRow3.grid(row=3, column=2, sticky=SW)
        
        # Items within frameConRow1
        self.labelCarrier.grid(row=3, column=2, sticky=SW)
        self.entryCarrier.grid(row=4, column=2, sticky=NW)
        self.labelBase.grid(row=3, column=4, sticky=SW)
        self.entryBase.grid(row=4, column=4, sticky=NW)
        self.labelACType.grid(row=3, column=6, sticky=SW)
        self.entryACType.grid(row=4, column=6, sticky=NW)

        # Items within frameConRow2
        self.labelDateFrom.grid(row=5, column=2)
        self.entryDateFrom.grid(row=5, column=3, columnspan=3, sticky=W)
        self.labelDateTo.grid(row=6, column=2)
        self.entryDateTo.grid(row=6, column=3, columnspan=3, sticky=W)
        self.rbActOrDH[0].grid(row=5, column=6, sticky=W)
        self.rbActOrDH[1].grid(row=6, column=6, sticky=W)

        # Items within frameConRow3
        self.labelLimitMin.grid(row=7, column=2, sticky=SW)
        self.entryLimitMin.grid(row=8, column=2, sticky=NW)
        self.labelLimitMax.grid(row=7, column=6, sticky=SW)
        self.entryLimitMax.grid(row=8, column=6, sticky=NW)
        
        # Items within frameEmptyDark
        self.labelEmptyDark.grid(row=2, sticky=NSEW)

        # Items within frameComment
        self.labelComment.grid(row=2, column=2, sticky=W)
        self.entryComment.grid(row=4, rowspan=2, column=2, columnspan=2, sticky=NW)

        # Items within frameLower
        self.btnSave.grid(row=2, column=6)
        self.btnCancel.grid(row=2, column=10)

class AppOneSoftLock(Toplevel):
    """Application used to edit one SoftLock, or create a new one"""
    def __init__(self, parent, slEtab, softLock, boolIsNew=0):
        Toplevel.__init__(self, parent)
        self.softLock = softLock
        self.parent = parent
        self.slEtab = slEtab
        self.listValidateFuncs = []
        self.transient(self.parent)
        self.validateAtEndOnly = 0
        self.isAtEnd = 0
        self.buttonPressed = None
        self.body = Frame(self, bg=gStrBGColorMain)
        if boolIsNew:
            self.isNewDialog = 1
            self.title('New SoftLock')
        else:
            self.isNewDialog = 0
            self.title('Edit SoftLock')
        self.resizable(width=NO, height=NO)
        self.initial_focus = self._body(self.body)
        self.body.pack()
        # Makes the dialog modal
        # self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.doCancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.showByType()
        self.initial_focus.focus_set()
        # Stops execution in calling program
        # self.wait_window(self)
    def _body(self, master):
        
        #################
        #    Frames     #
        #################

        strBGColorSLType = gStrBGColorMain
        strFGColorSLType = 'black'
        strBGColorPenalty = gStrBGColorMain
        strFGColorPenalty = 'black'
        strBGColorLeg1 = gStrBGColorDark
        strFGColorLeg1 = 'black'
        strBGColorLeg2 = gStrBGColorMain
        strFGColorLeg2 = 'black'
        strBGColorConstraints = gStrBGColorDark
        strFGColorConstraints = 'black'
        strBGColorComment = gStrBGColorMain
        strFGColorComment = 'black'
        
        self.frameUpper = Frame(master, bg=gStrBGColorMain)
        self.frameSLType = Frame(master, bg=strBGColorSLType)
        self.framePenalty = Frame(master, bg=strBGColorPenalty)
        #self.frameFiller = Frame(master, bg=gStrBGColorMain)

        # Frame with the "normal" content of the App
        self.frameNormal = Frame(master, bg=gStrBGColorMain)

        self.frameLeg1 = Frame(self.frameNormal, bg=strBGColorLeg1)
        self.frameLeg2 = Frame(self.frameNormal, bg=strBGColorLeg2)
        self.frameConstraints = Frame(self.frameNormal, bg=strBGColorConstraints)
        self.frameEmptyDark = Frame(self.frameNormal, bg=gStrBGColorDark)
        self.frameComment = Frame(self.frameNormal, bg=strBGColorComment)
        self.frameLower = Frame(self.frameNormal, bg=gStrBGColorMain)

        # Frame with SoftLock type selection
        self.frameChooseSLType = Frame(master, bg=gStrBGColorMain)

        #################
        # Choose SLType #
        #################

        self.scrollSLType = Scrollbar(self.frameChooseSLType, orient=VERTICAL)
        self.lbSLType = Listbox(self.frameChooseSLType, yscrollcommand=self.scrollSLType.set,
                                width=25, height=10, selectbackground=gStrActiveColor)
        self.scrollSLType.config(command=self.lbSLType.yview)
        for slType in gListMainSLTypes:
            self.lbSLType.insert(END, slType[1])
        self.lbSLType.bind("<Double-Button-1>", self.doSLTypeOk)
        self.btnSLTypeOk=Button(self.frameChooseSLType, text=gLabelOkButton, fg='black', bg=gStrBGColorButton, bd=2,
                                command=self.doSLTypeOk, activebackground=gStrActiveColor)
        self.btnSLTypeCancel=Button(self.frameChooseSLType, text=gLabelCancelButton, fg='black', bg=gStrBGColorButton, bd=2,
                                    command=self.doSLTypeCancel, activebackground=gStrActiveColor)

        #################
        #     Title     #
        #################
        self.labelTitle=Label(self.frameUpper, text='Edit SoftLock', font=('Helvetica',15,'bold'),
                              bd=2, bg=gStrBGColorMain)

        #################
        # SoftLock Type #
        #################

        self.labelSLType = Label(self.frameSLType, text='SoftLock type', font=('Helvetica',11),
                                 bd=2, bg=strBGColorSLType, fg=strFGColorSLType)
        self.StrReqOrNot= StringVar()
        self.rbReqOrNot = []
        self.rbReqOrNot.append(Radiobutton(self.frameSLType, text='Req', variable=self.StrReqOrNot,
                                           value='Req', bg=strBGColorSLType, fg=strFGColorSLType,
                                           activebackground=gStrActiveColor))
        self.rbReqOrNot.append(Radiobutton(self.frameSLType, text='Not', variable=self.StrReqOrNot,
                                           value='Not', bg=strBGColorSLType, fg=strFGColorSLType,
                                           activebackground=gStrActiveColor))
        if self.softLock.slType.getStrReqOrNot() == 'NOT':
            self.rbReqOrNot[1].select()
        else:
            self.rbReqOrNot[0].select()
        self.StrSLType = StringVar()
        self.StrSLType.set(self.softLock.slType.getStrLockType())
        # State should be 'READONLY'
        self.entrySLType = Entry(self.frameSLType, state=DISABLED, textvariable=self.StrSLType,
                                 bg=strBGColorSLType, fg=strFGColorSLType, width=12)
        self.btnChooseSLType = Button(self.frameSLType, text='Choose', fg=strFGColorSLType, bd=2,
                                      command=self.doChooseSLType, activebackground=gStrActiveColor)

        #################
        #    Penalty    #
        #################

        self.labelPenalty = Label(self.framePenalty, text='Penalty', font=('Helvetica',11), bd=2,
                                  bg=strBGColorPenalty, fg=strFGColorPenalty)
        self.StrPenalty = StringVar()
        self.StrPenalty.set(str(self.softLock.getIntPenalty()))
        self.entryPenalty = Entry(self.framePenalty, textvariable=self.StrPenalty,
                                  bg=strBGColorPenalty, fg=strFGColorPenalty, width=10)
        self.registerHandler('Penalty', self.entryPenalty, self.StrPenalty, SoftLock.checkIntNonNeg, 0)
        
        #################
        #     Leg 1     #
        #################

        self.labelLeg1 = Label(self.frameLeg1, text='Leg 1', font=('Helvetica',11), bd=2,
                               bg=strBGColorLeg1, fg=strFGColorLeg1)
        self.labelCarrier1 = Label(self.frameLeg1, text='Carrier', font=('Helvetica',9), bd=2,
                                   bg=strBGColorLeg1, fg=strFGColorLeg1)
        self.StrCarrier1 = StringVar()
        self.StrCarrier1.set(self.softLock.getStrCarrier1())
        self.entryCarrier1 = Entry(self.frameLeg1, textvariable=self.StrCarrier1, bg=strBGColorLeg1,
                                   fg=strFGColorLeg1, width=4)
        self.registerHandler('Carrier leg 1', self.entryCarrier1, self.StrCarrier1, SoftLock.checkStrCarrier, 0)

        self.labelFlightNr1 = Label(self.frameLeg1, text='Flight no', font=('Helvetica',9), bd=2,
                                    bg=strBGColorLeg1, fg=strFGColorLeg1)
        self.StrFlightNr1 = StringVar()
        if self.softLock.getIntFlightNr1():
            self.StrFlightNr1.set(str(self.softLock.getIntFlightNr1()))
        self.entryFlightNr1 = Entry(self.frameLeg1, textvariable=self.StrFlightNr1,
                                    bg=strBGColorLeg1, fg=strFGColorLeg1, width=5)
        self.registerHandler('Flight num leg 1', self.entryFlightNr1, self.StrFlightNr1, SoftLock.checkIntFlightNr)

        self.labelDepArr1 = Label(self.frameLeg1, text='Dep-Arr', font=('Helvetica',9), bd=2,
                                  bg=strBGColorLeg1, fg=strFGColorLeg1)
        self.StrDepArr1 = StringVar()
        self.StrDepArr1.set(self.softLock.getStrDepArr1())
        self.entryDepArr1 = Entry(self.frameLeg1, textvariable=self.StrDepArr1, bg=strBGColorLeg1,
                                  fg=strFGColorLeg1, width=10)
        self.registerHandler('Dep-Arr leg 1', self.entryDepArr1, self.StrDepArr1, SoftLock.checkStrDepArr)

        
        self.labelACType = Label(self.frameLeg1, text='AC type', font=('Helvetica',9), bd=2,
                                 bg=strBGColorLeg1, fg=strFGColorLeg1)
        self.StrACType = StringVar()
        self.StrACType.set(self.softLock.getStrACType())
        self.entryACType = Entry(self.frameLeg1, textvariable=self.StrACType, bg=strBGColorLeg1,
                                 fg=strFGColorLeg1, width=5)
        self.StrActOrDH1= StringVar()
        self.rbActOrDH1 = []
        self.rbActOrDH1.append(Radiobutton(self.frameLeg1, text="Active", variable=self.StrActOrDH1,
                                           value='A', bg=strBGColorLeg1, fg=strFGColorLeg1,
                                           activebackground=gStrActiveColor))
        self.rbActOrDH1.append(Radiobutton(self.frameLeg1, text="DH", variable=self.StrActOrDH1,
                                           value='D', bg=strBGColorLeg1, fg=strFGColorLeg1,
                                           activebackground=gStrActiveColor))
        self.rbActOrDH1.append(Radiobutton(self.frameLeg1, text="Any", variable=self.StrActOrDH1,
                                           value='*', bg=strBGColorLeg1, fg=strFGColorLeg1,
                                           activebackground=gStrActiveColor))
        if self.softLock.getStrActiveOrDH1() == 'A':
            self.rbActOrDH1[0].select()
        elif self.softLock.getStrActiveOrDH1() == 'D':
            self.rbActOrDH1[1].select()
        else:
            self.rbActOrDH1[2].select()
        # Frame with day check boxes
        self.frameDays = Frame(self.frameLeg1, bg=strBGColorLeg1)
        self.toggleDay = []
        self.toggleDayValue = []
        listIxDay = self.softLock.getListDepArrFromStr(self.softLock.getStrTrafficDay())
        for ixDay in range(7):
            self.toggleDayValue.append(BooleanVar())
            self.toggleDay.append(Checkbutton(self.frameDays, text=gListDayNames[ixDay],
                                              variable=self.toggleDayValue[ixDay],
                                              bg=strBGColorLeg1, fg=strFGColorLeg1,
                                              activebackground=gStrActiveColor,
                                              indicatoron=1))
            if ixDay + 1 in listIxDay:
                self.toggleDayValue[ixDay].set(1)
        self.labelDateFrom = Label(self.frameLeg1, text='From', font=('Helvetica',9), bd=2,
                                   bg=strBGColorLeg1, fg=strFGColorLeg1)
        self.StrDateFrom = StringVar()
        self.StrDateFrom.set(self.softLock.getStrDateFrom())
        self.entryDateFrom = Entry(self.frameLeg1, textvariable=self.StrDateFrom,
                                   bg=strBGColorLeg1, fg=strFGColorLeg1, width=10)
        self.registerHandler('Date from', self.entryDateFrom, self.StrDateFrom, SoftLock.checkStrDate)

        self.labelDateTo = Label(self.frameLeg1, text='To', font=('Helvetica',9), bd=2,
                                  bg=strBGColorLeg1, fg=strFGColorLeg1)
        self.StrDateTo = StringVar()
        self.StrDateTo.set(self.softLock.getStrDateTo())
        self.entryDateTo = Entry(self.frameLeg1, textvariable=self.StrDateTo, bg=strBGColorLeg1,
                                  fg=strFGColorLeg1, width=10)
        self.registerHandler('Date to', self.entryDateTo, self.StrDateTo, SoftLock.checkStrDate)

        #################
        #     Leg 2     #
        #################

        self.labelLeg2 = Label(self.frameLeg2, text='Leg 2', font=('Helvetica',11), bd=2,
                               bg=strBGColorLeg2, fg=strFGColorLeg2)
        self.labelCarrier2 = Label(self.frameLeg2, text='Carrier', font=('Helvetica',9), bd=2,
                                   bg=strBGColorLeg2, fg=strFGColorLeg2)
        self.StrCarrier2 = StringVar()
        self.StrCarrier2.set(self.softLock.getStrCarrier2())
        self.entryCarrier2 = Entry(self.frameLeg2, textvariable=self.StrCarrier2, bg=strBGColorLeg2,
                                   fg=strFGColorLeg2, width=4)
        self.registerHandler('Carrier leg 2', self.entryCarrier2, self.StrCarrier2, SoftLock.checkStrCarrier)

        self.labelFlightNr2 = Label(self.frameLeg2, text='Flight no', font=('Helvetica',9), bd=2,
                                    bg=strBGColorLeg2, fg=strFGColorLeg2)
        self.StrFlightNr2 = StringVar()
        if self.softLock.getIntFlightNr2():
            self.StrFlightNr2.set(str(self.softLock.getIntFlightNr2()))
        self.entryFlightNr2 = Entry(self.frameLeg2, textvariable=self.StrFlightNr2,
                                    bg=strBGColorLeg2, fg=strFGColorLeg2, width=5)
        self.registerHandler('Flight num leg 2', self.entryFlightNr2, self.StrFlightNr2, SoftLock.checkIntFlightNr)
        self.labelDepArr2 = Label(self.frameLeg2, text='Dep-Arr', font=('Helvetica',9), bd=2,
                                  bg=strBGColorLeg2, fg=strFGColorLeg2)
        self.StrDepArr2 = StringVar()
        self.StrDepArr2.set(self.softLock.getStrDepArr2())
        self.entryDepArr2 = Entry(self.frameLeg2, textvariable=self.StrDepArr2, bg=strBGColorLeg2,
                                  fg=strFGColorLeg2, width=10)
        self.registerHandler('Dep-Arr leg 2', self.entryDepArr2, self.StrDepArr2, SoftLock.checkStrDepArr)

        self.StrActOrDH2 = StringVar()
        self.rbActOrDH2 = []
        self.rbActOrDH2.append(Radiobutton(self.frameLeg2, text="Active", variable=self.StrActOrDH2,
                                           value='A', bg=strBGColorLeg2, fg=strFGColorLeg2,
                                           activebackground=gStrActiveColor))
        self.rbActOrDH2.append(Radiobutton(self.frameLeg2, text="DH", variable=self.StrActOrDH2,
                                           value='D', bg=strBGColorLeg2, fg=strFGColorLeg2,
                                           activebackground=gStrActiveColor))
        self.rbActOrDH2.append(Radiobutton(self.frameLeg2, text="Any", variable=self.StrActOrDH2,
                                           value='*', bg=strBGColorLeg2, fg=strFGColorLeg2,
                                           activebackground=gStrActiveColor))
        if self.softLock.getStrActiveOrDH2() == 'A':
            self.rbActOrDH2[0].select()
        elif self.softLock.getStrActiveOrDH2() == 'D':
            self.rbActOrDH2[1].select()
        else:
            self.rbActOrDH2[2].select()

        #################
        #  Constraints  #
        #################

        self.labelConstraints = Label(self.frameConstraints, text='Constraints',
                                      font=('Helvetica',11), bd=2, bg=strBGColorConstraints,
                                      fg=strFGColorConstraints)
        self.labelLimitMin = Label(self.frameConstraints, text='Limit Min', font=('Helvetica',9),
                                   bd=2, bg=strBGColorConstraints, fg=strFGColorConstraints)
        self.StrLimitMin = StringVar()
        self.StrLimitMin.set(self.softLock.getStrLimitMin())
        self.entryLimitMin = Entry(self.frameConstraints, textvariable=self.StrLimitMin,
                                   bg=strBGColorConstraints, fg=strFGColorConstraints, width=7)
        self.registerHandler('Limit min', self.entryLimitMin, self.StrLimitMin, SoftLock.checkStrLimit)

        self.labelLimitMax = Label(self.frameConstraints, text='Limit Max', font=('Helvetica',9),
                                   bd=2, bg=strBGColorConstraints, fg=strFGColorConstraints)
        self.StrLimitMax = StringVar()
        self.StrLimitMax.set(self.softLock.getStrLimitMax())
        self.entryLimitMax = Entry(self.frameConstraints, textvariable=self.StrLimitMax,
                                   bg=strBGColorConstraints, fg=strFGColorConstraints, width=7)
        self.registerHandler('Limit max', self.entryLimitMax, self.StrLimitMax, SoftLock.checkStrLimit)

        self.labelBase = Label(self.frameConstraints, text='Base', font=('Helvetica',9), bd=2,
                               bg=strBGColorConstraints, fg=strFGColorConstraints)
        self.StrBase = StringVar()
        self.StrBase.set(self.softLock.getStrBase())
        self.entryBase = Entry(self.frameConstraints, textvariable=self.StrBase,
                               bg=strBGColorConstraints, fg=strFGColorConstraints, width=5)
        self.registerHandler('Base', self.entryBase, self.StrBase, SoftLock.checkStrBase)

        self.BoolACChg = BooleanVar()
        self.BoolACChg.set(self.softLock.getBoolACChange())
        self.cbACChg = Checkbutton(self.frameConstraints, text="Only if\nAC-\nchange",
                                   variable=self.BoolACChg, bg=strBGColorConstraints,
                                   fg=strFGColorConstraints, activebackground=gStrActiveColor)
        
        #################
        #     Empty     #
        #################

        self.labelEmptyDark = Label(self.frameEmptyDark, text='   ', bg=gStrBGColorDark)

        #################
        #    Comment    #
        #################

        self.labelComment = Label(self.frameComment, text='Comment', font=('Helvetica',11), bd=2,
                                  bg=strBGColorComment, fg=strFGColorComment)
        self.StrComment = StringVar()
        self.StrComment.set(self.softLock.getStrComment())
        self.entryComment = Entry(self.frameComment, textvariable=self.StrComment,
                                  bg=strBGColorComment, fg=strFGColorComment, width=36)
        self.registerHandler('Comment', self.entryComment, self.StrComment, SoftLock.checkStrComment, 1, 0)

        #################
        #    Buttons    #
        #################

        self.btnSave=Button(self.frameLower, text=gLabelOkButton, fg='black', bg=gStrBGColorButton, bd=2, command=self.doOk,
                            activebackground=gStrActiveColor)
        self.btnCancel=Button(self.frameLower, text=gLabelCancelButton, fg='black', bg=gStrBGColorButton, bd=2,
                              command=self.doCancel, activebackground=gStrActiveColor)
        self.setAllGrids()
        return self.entryFlightNr1
    def _validateAtEnd(self):
        self.isAtEnd = 1
        for funcValidate in self.listValidateFuncs:
            if funcValidate():
                self.isAtEnd = 0
                return 1
        self.isAtEnd = 0
        return 0
    def getButtonPressed(self):
        return self.buttonPressed
    def registerHandler(self, strName, entry, variable, funcCheck, emptyOk=1, toUpper=1):
        def handler(event=None, self=self):
            return self._validateEntry(event, strName, funcCheck, variable, emptyOk, toUpper)
        entry.bind('<FocusOut>', handler)
        self.listValidateFuncs.append(handler)
    def _validateEntry(self, event, strName, funcValidate, StrVar=None, emptyOk=1, toUpper=1):
        if StrVar.get() == '' and emptyOk or self.validateAtEndOnly and not self.isAtEnd:
            return ''
        if StrVar.get() == '' and not emptyOk:
            strWarningMessage = '%s may not be empty' %(strName)
        else:
            if toUpper and StrVar and StrVar.get() != StrVar.get().upper():
                StrVar.set(StrVar.get().upper())
            strWarningMessage = funcValidate(StrVar.get(), strName)
        if strWarningMessage and (not self.validateAtEndOnly or self.isAtEnd):
            tkMessageBox.showwarning('Warning', strWarningMessage)
            if event:
                event.widget.focus_set() # put focus back
        return strWarningMessage    
    def _updateSoftLock(self, softLock):
        if 1:
            strSLType = self.StrSLType.get()
            if strSLType != 'CXN_BUFFER':
                if strSLType in ['REST_BEF', 'REST_AFT']:
                    strSLType = 'REQ_' + strSLType
                else:
                    strSLType = self.StrReqOrNot.get().upper() + '_' + strSLType
            softLock.setStrType(strSLType)
            softLock.setStrCarrier1(self.StrCarrier1.get())
            softLock.setIntFlightNr1(self.StrFlightNr1.get())
            softLock.setStrDepArr1(self.StrDepArr1.get())
            softLock.setStrActiveOrDH1(self.StrActOrDH1.get())
            listTrafficDay = []
            for ixDay in range(7):
                if self.toggleDayValue[ixDay].get():
                    listTrafficDay.append(ixDay + 1)
            softLock.setStrTrafficDay(softLock.getStrDepArrFromList(listTrafficDay))
            softLock.setStrDateFrom(self.StrDateFrom.get())
            softLock.setStrDateTo(self.StrDateTo.get())
            softLock.setStrCarrier2(self.StrCarrier2.get())
            softLock.setIntFlightNr2(self.StrFlightNr2.get())
            softLock.setStrDepArr2(self.StrDepArr2.get())
            softLock.setStrActiveOrDH2(self.StrActOrDH2.get())
            softLock.setStrLimitMin(self.StrLimitMin.get())
            softLock.setStrLimitMax(self.StrLimitMax.get())
            softLock.setStrBase(self.StrBase.get())
            softLock.setStrACType(self.StrACType.get())
            softLock.setBoolACChange(self.BoolACChg.get())
            softLock.setIntPenalty(int(self.StrPenalty.get()))
            softLock.setStrComment(self.StrComment.get())
    def getSoftLock(self):
        return self.softLock
    def doOk(self):
        if self._validateAtEnd():
            return
        localSoftLock = self.softLock.getCopy()
        self._updateSoftLock(localSoftLock)
        listProblems = localSoftLock.correctByType()
        if listProblems:
            strMessage = '\n'.join(['Problems with SoftLock'] + listProblems + ['Please correct this'])
            tkMessageBox.showinfo('Problems', strMessage)
            return
        if self.parent.getBoolValidate():
            strReportFile = self.slEtab.getStrReportFile()
            if strReportFile:
                listNotice = validateSoftLockFromReport(localSoftLock, strReportFile)
                if listNotice:
                    printDebug('SoftLock date interval:')
                    printDebug('From: %s/%d' %(localSoftLock.getStrDateFrom(), localSoftLock.getIntDateFrom()))
                    printDebug('To:   %s/%d' %(localSoftLock.getStrDateTo(), localSoftLock.getIntDateTo()))
                    strMessage = '\n'.join(['Problems with SoftLock'] + listNotice + ['Continue anyway?'])
                    boolContinue = tkMessageBox.askyesno('Notice', strMessage)
                    if not boolContinue:
                        return
        self.buttonPressed = gLabelOkButton
        self.softLock.setListValues(localSoftLock.getListValues())
        self.slEtab.setHasChanged(1)
        self.parent.updateTitle()
        self.withdraw()
        self.update_idletasks()
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()
    def doCancel(self):
        if self.isNewDialog:
            self.slEtab.deleteSoftLock(self.softLock)
        self.buttonPressed = gLabelCancelButton
        # Put focus back to the parent window
        self.parent.focus_set()
        self.destroy()
    def doChooseSLType(self):
        self.frameNormal.grid_forget()
        self.frameChooseSLType.grid(row=6, rowspan=22, column=2, columnspan=16, sticky=NSEW)
    def showByType(self):
        self.setFrameNormal()
        if self.StrSLType.get() in ['BASE', 'TRIPSTART', 'TRIPEND', 'DUTYSTART', 'DUTYEND']:
            self.frameLeg2.grid_forget()
            self.labelLimitMin.grid_forget()
            self.entryLimitMin.grid_forget()
            self.labelLimitMax.grid_forget()
            self.entryLimitMax.grid_forget()
            self.cbACChg.grid_forget()
        elif self.StrSLType.get() in ['REST_AFT', 'REST_BEF']:
            for i in range(2):
                self.rbReqOrNot[i].grid_forget()
            self.frameLeg2.grid_forget()
            self.cbACChg.grid_forget()
        elif self.StrSLType.get() == 'CXN_BUFFER':
            for i in range(2):
                self.rbReqOrNot[i].grid_forget()
            for i in range(3):
                self.rbActOrDH1[i].grid_forget()
            self.labelACType.grid_forget()
            self.entryACType.grid_forget()
            self.labelBase.grid_forget()
            self.entryBase.grid_forget()
            for i in range(7):
                self.toggleDay[i].grid_forget()
            self.frameLeg2.grid_forget()
            self.cbACChg.grid_forget()
    def doSLTypeOk(self, dummy=None):
        if self.lbSLType.curselection():
            self.StrSLType.set(gListMainSLTypes[int(self.lbSLType.curselection()[0])][0])
            self.showByType()
        else:
            self.doSLTypeCancel()
    def doSLTypeCancel(self):
        self.frameChooseSLType.grid_forget()
        self.frameNormal.grid(row=6, rowspan=22, column=2, columnspan=16, sticky=NSEW)
    def setFrameNormal(self):
        self.setAllGrids()
        self.frameChooseSLType.grid_forget()
    def setAllGrids(self):
        self.frameUpper.grid(row=2, column=2, columnspan=16, rowspan=2, sticky=EW)
        self.frameSLType.grid(row=4, column=2, columnspan=2, rowspan=2, sticky=W)
        self.framePenalty.grid(row=4, column=4, columnspan=12, rowspan=2, sticky=W+N+S)
        self.frameNormal.grid(row=6, rowspan=22, column=2, columnspan=16, sticky=NSEW)
        self.frameLeg1.grid(row=6, column=2, columnspan=16, rowspan=8, sticky=W)
        self.frameLeg2.grid(row=14, column=2, columnspan=16, rowspan=4, sticky=W)
        self.frameConstraints.grid(row=18, rowspan=4, column=2, columnspan=2, sticky=EW)
        self.frameEmptyDark.grid(row=18, rowspan=4, column=4, columnspan=14, sticky=NSEW)
        self.frameComment.grid(row=22, column=2, columnspan=16, rowspan=4, sticky=W)
        self.frameLower.grid(row=26, column=2, columnspan=16, rowspan=2, sticky=EW)
        self.scrollSLType.grid(row=2, column=5, sticky=W+N+S)
        self.lbSLType.grid(row=2, column=1, columnspan=4, sticky=NSEW)
        self.btnSLTypeOk.grid(row=3, column=2)
        self.btnSLTypeCancel.grid(row=3, column=4)
        self.labelTitle.grid(row=2, column=2)
        self.labelSLType.grid(row=2, column=2, columnspan=6, sticky=W)
        self.rbReqOrNot[0].grid(row=4, column=2, columnspan=2, sticky=W)
        self.rbReqOrNot[1].grid(row=5, column=2, columnspan=2, sticky=W)
        self.entrySLType.grid(row=4, rowspan=2, column=4, columnspan=2, sticky=W)
        self.btnChooseSLType.grid(row=4, rowspan=2, column=6, columnspan=2, sticky=W)
        self.labelPenalty.grid(row=2, column=2)
        self.entryPenalty.grid(row=4, rowspan=2, column=2, columnspan=2, sticky=W)
        self.labelLeg1.grid(row=2, column=2)
        self.labelCarrier1.grid(row=3, column=2, sticky=SW)
        self.entryCarrier1.grid(row=4, rowspan=2, column=2, columnspan=2, sticky=NW)
        self.labelFlightNr1.grid(row=3, column=4, sticky=SW)
        self.entryFlightNr1.grid(row=4, rowspan=2, column=4, columnspan=4, sticky=NW)
        self.labelDepArr1.grid(row=3, column=8, sticky=SW)
        self.entryDepArr1.grid(row=4, rowspan=2, column=8, columnspan=4, sticky=NW)
        self.labelACType.grid(row=3, column=12, columnspan=2, sticky=SW)
        self.entryACType.grid(row=4, rowspan=2, column=12, columnspan=2, sticky=NW)
        self.rbActOrDH1[0].grid(row=2, column=14, columnspan=4, sticky=W)
        self.rbActOrDH1[1].grid(row=3, column=14, columnspan=4, sticky=W)
        self.rbActOrDH1[2].grid(row=4, rowspan=2, column=14, columnspan=4, sticky=W)
        self.frameDays.grid(row=6, column=2, columnspan=11, rowspan=4, sticky=EW)
        for ixDay in range(7):
            self.toggleDay[ixDay].grid(row=ixDay/4, column=ixDay%4, sticky=W)
        self.labelDateFrom.grid(row=6, column=13)
        self.entryDateFrom.grid(row=6, column=14, columnspan=4, sticky=W)
        self.labelDateTo.grid(row=8, column=13)
        self.entryDateTo.grid(row=8, column=14, columnspan=4, sticky=W)
        self.labelLeg2.grid(row=2, column=2)
        self.labelCarrier2.grid(row=3, column=2, sticky=SW)
        self.entryCarrier2.grid(row=4, rowspan=2, column=2, columnspan=2, sticky=NW)
        self.labelFlightNr2.grid(row=3, column=4, sticky=SW)
        self.entryFlightNr2.grid(row=4, rowspan=2, column=4, columnspan=4, sticky=NW)
        self.labelDepArr2.grid(row=3, column=8, sticky=SW)
        self.entryDepArr2.grid(row=4, rowspan=2, column=8, columnspan=6, sticky=NW)
        self.rbActOrDH2[0].grid(row=2, column=14, columnspan=4, sticky=W)
        self.rbActOrDH2[1].grid(row=3, column=14, columnspan=4, sticky=W)
        self.rbActOrDH2[2].grid(row=4, rowspan=2, column=14, columnspan=4, sticky=W)
        self.labelConstraints.grid(row=2, column=2, columnspan=16, sticky=SW)
        self.labelLimitMin.grid(row=3, column=2, sticky=SW)
        self.entryLimitMin.grid(row=4, rowspan=2, column=2, columnspan=2, sticky=NW)
        self.labelLimitMax.grid(row=3, column=4, sticky=SW)
        self.entryLimitMax.grid(row=4, rowspan=2, column=4, columnspan=4, sticky=NW)
        self.labelBase.grid(row=3, column=8, sticky=SW)
        self.entryBase.grid(row=4, rowspan=2, column=8, columnspan=6, sticky=NW)
        self.cbACChg.grid(row=3, rowspan=3, column=14, columnspan=4, sticky=W)
        self.labelEmptyDark.grid(row=2, sticky=NSEW)
        self.labelComment.grid(row=2, column=2, sticky=W)
        self.entryComment.grid(row=4, rowspan=2, column=2, columnspan=2, sticky=NW)
        self.btnSave.grid(row=2, column=6)
        self.btnCancel.grid(row=2, column=10)

############################## --------------------- ##############################
############################## execution starts here ##############################
############################## --------------------- ##############################

# python $CARMUSR/lit/python/carmusr/SoftLocksGUI.py [-debug|-noSpawn]
if __name__ == '__main__':
    if '-help' in sys.argv:
        printUsage()
        sys.exit(1)
    if '-debug' in sys.argv:
        gDebug = 1
    strEtabFile = None
    if '-etab' in sys.argv:
        ixEtab = sys.argv.index('-etab')
        if len(sys.argv) < ixEtab + 2:
            printError('Etab file name not given.')
            printUsage()
        else:
            strEtabFile = sys.argv[ixEtab + 1]
    strReportFile = None
    if '-report' in sys.argv:
        ixReport = sys.argv.index('-report')
        if os.path.isfile(sys.argv[ixReport + 1]):
            strReportFile = sys.argv[ixReport + 1]
        else:
            printError('Report file does not exist.')
            printUsage()
    try:
        if strEtabFile:
            slEtab = SoftLockEtab(strEtabFile, strReportFile)
        else:
            slEtab = SoftLockEtab(strReportFile=strReportFile)
    except:
        printError('%s - %s' %(sys.exc_type, sys.exc_value))
        slEtab = SoftLockEtab()
    root = Tk()
    root.resizable(width=NO, height=NO)
    mainFrame = Frame(root, bg=gStrBGColorDark)
    mainFrame.pack()
    AppSLList = AppSoftLockList(root, mainFrame, slEtab)
    root.mainloop()
