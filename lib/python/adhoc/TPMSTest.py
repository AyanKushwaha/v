from report_sources.hidden.TPMSCrew import TPMSRoutines
import carmusr.tracking.util.time_shell as t
import os
import carmensystems.rave.api as r
import csv


def header(list_of_field_keys):
    hdr =''
    for field in list_of_field_keys:
        hdr = hdr + field + ';'
    # Remove last ;
    hdr = hdr[0:len(hdr)-1]
    return hdr

def write_header(fieldnames,crew_export_file,tag):

    hdr = header(fieldnames)
    tag = '*** ' + tag + ' ***' +'\n'
    # Write to file

    crew_export_file.write(tag)
    crew_export_file.write(hdr+"\n")

def write_data(fieldnames,data,crew_export_file):
    if len(data)!=0 and len(fieldnames)==len(data[0]):
        data_to_be_printed=[]

        for i in range(len(data)):
            element = dict(zip(fieldnames,data[i]))
            data_to_be_printed.append(element)


        writer = csv.DictWriter(crew_export_file,fieldnames=fieldnames, delimiter =';',quoting = csv.QUOTE_ALL)
        for row in data_to_be_printed:
            writer.writerow(row)
        return True
    else:
        print  "Data and header not equal"
        return False


def get_crew_data(f,crewid,r):
    c=r.get_crew_data(crewid)

    iictra_act_group_name_key       ='IICTRA_ACT_GROUP_NAME'
    iictra_act_group_version_key    ='IICTRA_ACT_GROUP_VERSION'
    iictra_from_date_key            ='IICTRA_FROM_DATE'
    iictra_rank_key                 ='IICTRA_RANK'
    iictra_remark_key               ='IICTRA_REMARK'
    iictra_staff_id_key             ='IICTRA_STAFF_ID'
    iictra_to_date_key              ='IICTRA_TO_DATE'

    fieldnames_tab_staff_type_rating =[
        iictra_act_group_name_key,
        iictra_act_group_version_key,
        iictra_from_date_key,
        iictra_rank_key,
        iictra_remark_key,
        iictra_staff_id_key,
        iictra_to_date_key,]

    write_header(fieldnames_tab_staff_type_rating,f,"II_StaffTypeRating")
    write_data(fieldnames_tab_staff_type_rating ,c,f)


def get_active_pilots(now_time) :

    rosters_bag = r.context('sp_crew').bag()

    pilot_list=[]

    for crew_bag in rosters_bag.iterators.crewid_set(sort_by=("crew.%id%"),where=("crew.is_pilot")):
        if crew_bag.crew.is_active_at_date(now_time) :
            pilot_list.append(crew_bag.crew.id())

    return pilot_list


now = t.abstime_now()
pilot_list = get_active_pilots(now)


samba_path = os.getenv('SAMBA', "/samba-share")
mypath = "%s/%s/" %(samba_path, 'reports/TPMS/CMSOutput')
if not os.path.isdir(mypath):
    os.makedirs(mypath)

reportName = "TPMS_Crew"
myFile = mypath + reportName + '.csv'

try:
    os.remove(myFile)
except:
    None
with open(myFile,'w') as f:

    r = TPMSRoutines(f,pilot_list,now)

    r.tab_staff_nk(f)
    #r.tab_crew_mem_exp_qualif(f)
    #r.tab_pilot_license(f)
    #r.tab_staff(f)
    #r.tab_staff_home_base(f)
    #r.tab_staff_type_rating(f)
    #r.tab_staff_communication(f)
    #r.tab_seniority(f)
    #r.tab_staff_visa(f)
    #r.tab_staff_passport(f)
    #r.tab_staff_address(f)
    #get_crew_data(f,85540,r)

