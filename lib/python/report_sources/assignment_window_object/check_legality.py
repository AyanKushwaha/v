"""<rst only="default_jcr" suffix="#object_reports#">

.. index::
   single: Report; Check Legality

.. _check_legality_report_crew:

Check Legality
---------------

To evaluate illegalities in the JCR system, a legality report is available.
The report contains detailed information on broken rules and any exceptions,
and allows the user to change views and display objects in Studio.
This report is used for input and output data checks, in preparation of manual
planning steps, and for the checks of the final solutions.
It can be created with the command *Check Legality...* in the
*Crew Reports* and *Assignment Object* menus.

The legality report has two views:
the **Roster View**, where the data is grouped by crew member,
and the **Rule View**, where the data is grouped by rule.
The view is chosen by selecting **Roster** or **Rule** in the report.

These two options are also used to refresh the report after operations
are performed in the report (see below).


Roster View
............

In this view, the report lists crew members that have illegalities and/or
rule exceptions on their rosters.

For each such crew member, broken rules are first listed.
If rules have extra information about the violation in the form of failtexts,
an expandable field will be added under the rule name, the visibility of which
is toggled by an arrow in front the rule name.

Depending on the type of rule, detailed information about the failure may be
provided, namely in which wop, trip, duty, and leg the rule is violated,
the current value of the quantity constrained by the rule,
the limit for the rule, and the difference between these two.

Secondly, any rule exceptions created for this crew member are listed,
with information about the violations.

.. see also:: :ref:`rule_exceptions`

**Available actions in the Roster View**

 * Click on **Except** next to a rule failure to create a rule exception
   for that specific instance. To create exceptions for all illegalities on
   a roster, click **Except all failures**.

 * To remove rule exceptions, either click on **remove** next to a rule failure
   to remove that specific instance, or click on **Remove all exceptions** to
   remove all rule exceptions for that roster.

 * Click **Show** on the table headers to focus on the crew member in question.
   Their roster will be loaded in the Studio area opposite the one
   from where the report was started.

 * Click on a rule name in the *Rule Failures* table to switch to Rule View.

 * Click on **Explore** next to a rule illegality (available only for developers)
   to use Rave Explorer on the specific failure.


Rule View
..........

This view provides similar information to the Roster View,
except the data is grouped by rule.
For all rules with violations and/or exceptions, the crew members which have
these on their rosters are listed in the relevant table.
For ease of navigation, a list of these rules is provided under a table of
contents at the top of the report.


**Available actions in the Rule View**

 * Click on **Except** next to a rule failure to create a rule exception
   for that specific instance. To create exceptions for all the rule violations
   across all crew rosters in the report, click **Except all failures**.

 * To remove rule exceptions, either click on **remove** next to a rule failure
   to remove that specific instance,
   or click on **Remove rule exceptions from all crew** to
   remove the listed exceptions from all crew rosters in the report.

 * Click **Show** on table headers to focus on the crew members listed.
   Their roster will be loaded in the Studio area opposite the one from where
   the report was started.

 * Click on **Explore** next to a rule illegality (available only for developers)
   to use Rave Explorer on the specific failure.


**Files Location**

    ``lib/python/report_sources/crew_margin_window_object/check_legality_roster.py``

</rst>
"""
from Localization import MSGR
import report_sources.include.check_legality_roster as check_legality_roster

import carmstd.select


class Report(check_legality_roster.Report):

    def get_report_view_name(self):
        """The name visual in the report. E.g. Trip or Rotation."""
        return MSGR("Roster")

    def get_identifier(self, bag):
        """Gets the name of the crew members"""
        return bag.crew.id()

    def get_name(self, bag):
        """Gets the name of the crew members"""
        return "%s - %s" % (bag.crew.id(), bag.crew.signature())

    @staticmethod
    def show_in_studio(*args, **kw):
        """Displays the crew in studio"""
        carmstd.select.show_crew(*args, **kw)

    def get_scope(self):
        """
        Should return the scope of the report, .i.e. 'window', 'margin'(, or 'plan')
        """
        return "window"

    def get_type(self):
        """
        Should return the type of the report, i.e. 'roster', 'trip'(, 'duty', or 'leg')
        """
        return "roster"

    def get_header_text(self):
        """
        Return the name of the report
        """
        return MSGR("Check Legality")


if __name__ == "__main__":
    import carmstd.report_generation as rg
    #reload(check_legality_roster)
    rg.reload_and_display_report()
