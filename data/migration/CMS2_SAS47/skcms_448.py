import adhoc.fixrunner as fixrunner
import AbsTime

__version__ = '2017-03-29.0'


@fixrunner.once
@fixrunner.run
def fixit(dc, *a, **k):

    # This list is just "documentation"/requirement
    table_names = [
        # From Annika:
        "ac_qual_map",  # in read_all only
        "activity_group",  # in read_all only
        "activity_group_period",  # in read_all only
        "activity_set",  # in read_all only
        "aircraft_type",  # in read_all only
        # "crew_need", # No such table
        "coterminals",  # in read_all only
        "crew_base_set",  # in read_all only

        # Have access already from crew meal
        "meal_airport",  # in read_all only
        "meal_cons_correction",   # in read_all only
        "meal_consumption_code",   # in read_all only
        "meal_load_correction",   # in read_all only

        # Not used (?)
        "special_weekends",   # in read_all only

        # All hotel tables:
        "hotel",  # in read_all only
        "hotel_booking",  # in read_all only
        "hotel_contract",  # in upd_superuser
        "hotel_customer",  # in read_all only
        "hotel_transport",  # in upd_superuser

        # From Johan and Oscar
        "crew_qualification_set",  # in read_all only
        "activity_set_period",  # in upd_superuser
        "crew_contract_set",  # in read_all only
        "account_entry",  # in read_all only
        "course",  # in read_all only
        "crew",  # in read_all only

        # Same as Superuser:
        "crew_document",  # 4  # view -> crew_document
        "read_all",  # 4
        "read_crewbase",  # 4  # view -> crew_dental_info, crew_passport, salary_convertable_crew
        "upd_superuser",  # 6  # view
        "crewinfo",  # 6  # view -> crewinfo
        "new_hire_follow_up",  # 6  # in upd_roster
        "crew_leased",  # 6  # view -> crew_leased
        "upd_roster",  # 6
    ]

    # These will be added to cms_views with the specified ACL
    views = [
        # Same as Superuser:
        ["crew_document", 4],
        ["read_all", 4],
        ["read_crewbase", 4],
        ["upd_superuser", 6],
        ["crewinfo", 6],
        ["new_hire_follow_up", 6],
        ["crew_leased", 6],
        ["upd_roster", 6],
        # new view for SystemSpecialist:
        ["upd_systemspecialist", 6]
    ]

    # These will be added to cms_view_objects for the new view "upd_systemspecialist"
    # They will give write-access to most of the things that are read_all only
    view_objects = [
        "ac_qual_map",
        "activity_group",
        "activity_group_period",
        "activity_set",
        "aircraft_type",
        "coterminals",
        "crew_base_set",

        "meal_airport",
        "meal_cons_correction",
        "meal_consumption_code",
        "meal_load_correction",

        "special_weekends",

        "hotel",
        "hotel_booking",
        "hotel_customer",

        "crew_qualification_set",
        "crew_contract_set",
        "account_entry",
        "course",
        "crew",
        "agreement_validity",
    ]

    ops = []

    for view, acl in views:
        ops.append(fixrunner.createOp('cms_views', 'W', {
            "cms_view": view,
            "cms_role": "SystemSpecialist",
            "cms_view_acl": acl,
        }))

    for obj in view_objects:
        ops.append(fixrunner.createOp('cms_view_objects', 'W', {
            "cms_view": "upd_systemspecialist",
            "cms_object_type": "TABLE",
            "cms_object_name": obj
        }))

    print "done"
    return ops


fixit.program = 'skcms_448.py (%s)' % __version__

if __name__ == '__main__':
    try:
        fixit()
    except fixrunner.OnceException:
        print "    - migration already run with key ", __version__

