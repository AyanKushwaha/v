"""
 $Header$

 Training Info Report. For more information, see ../include/TrainingInfo.py
"""

from report_sources.include.TrainingInfo import TrainingInfo as Report

class TrainingInfo(Report):

    def create(self):
        Report.create(self, scope='object', context='marked_in_window_left')

