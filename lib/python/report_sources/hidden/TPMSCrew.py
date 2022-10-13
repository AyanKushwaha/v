import csv
import os
import stat
from datetime import datetime, timedelta

import carmensystems.rave.api as r
from AbsTime import AbsTime
from RelTime import RelTime

import carmusr.tracking.util.time_shell as t
from report_sources.include.SASReport import SASReport
from tm import TM
import shutil

PRODEFIS_START_TIME = "01MAY2016"


"""
  Converts a Rave abstime string on format DDMONYYY HH24:MI to
  YYYY-MM-DD
"""
def cvt_dstr_to_YYYY_MM_DD(date_str):
    return datetime.strptime(date_str,"%d%b%Y %H:%S").strftime('%Y-%m-%d')

def cvt_dstr_to_YYYY_MM_DD_MINUS_1_DAY(date_str):
    return (datetime.strptime(date_str,"%d%b%Y %H:%S") - timedelta(days=1)).strftime('%Y-%m-%d')


"""
  Converts a Rave abstime string on format DDMONYYY HH24:MI to
  YYYY-MM-DD HH24:MI
"""
def cvt_dstr_to_YYYY_MM_DD_HH24_MI(date_str):
    return datetime.strptime(date_str,"%d%b%Y %H:%S").strftime('%Y-%m-%d %H:%S')

def cvt_dstr_to_YYYY_MM_DD_HH24_MI_MINUS_1_DAY(date_str):
    return (datetime.strptime(date_str,"%d%b%Y %H:%S") - timedelta(days=1)).strftime('%Y-%m-%d %H:%S')

def get_active_crew(pilots):
    rosters_bag = r.context('sp_crew').bag()

    crew_list = []
    where = ('crew.%is_pilot%' if pilots else '(crew.%is_cabin%)') + ' and crew.%is_active_at_date%(now) and crew.%debug_selected% and report_tpms.%crew_sel%'
    for crew_bag in rosters_bag.iterators.crewid_set(sort_by='crew.%id%', where = where):
        crew_list += [crew_bag.crew.id()]

    return crew_list


def header(list_of_field_keys):
    hdr =''
    for field in list_of_field_keys:
        hdr = hdr + '"'+field + '"'+';'
    # Remove last ;
    hdr = hdr[0:len(hdr)-1]
    return hdr


def write_header(fieldnames,crew_export_file,tag):
    # Write a BOM showing that is an UTF-8 file
    hdr = header(fieldnames)
    tag = '###' + tag + '###' +'\n'.encode('Latin-1)')
    # Write to file
    crew_export_file.write(tag)
    crew_export_file.write(hdr+"\n")


def nn(v):
    """"never returns None"""
    return "" if v == None else v


def nns(v):
    """always returns a str or unicode"""
    if v == None:
        return ""
    if type(v) in [str, unicode]:
        return v
    return str(v)


def write_data(fieldnames,rows,crew_export_file):
    if len(rows)!=0 and len(fieldnames)==len(rows[0]):
        data = []
        for row in rows:
            data.append(dict(zip(fieldnames,row)))
        writer = csv.DictWriter(crew_export_file,fieldnames=fieldnames, delimiter =';',quoting = csv.QUOTE_ALL)

        for row_dict in data:
            writer.writerow(dict([(k, nns(v).encode("utf-8")) for k,v in row_dict.items()]))
        return True
    else:
        print  "Data and header not equal"
        return False


def write_tab(f,fieldnames,data,tag):
    write_header(fieldnames,f,tag)
    if not write_data(fieldnames,data,f) :
        print "Write %s failed" %tag


class TPMSRoutines():

    def __init__(self,f,pilot_list, cabin_list, now):
        self.f = f
        self.pilot_list = pilot_list
        self.cabin_list = cabin_list
        self.now = now

    def tab_staff_nk(self,f):
        # TAB II_StaffNK
        iistafnk_from_date_time_key     ='IISTAFNK_FROM_DATE_TIME'
        iistafnk_from_date_time_lt_key  ='IISTAFNK_FROM_DATE_TIME_LT'
        iistafnk_to_date_time_key       ='IISTAFNK_TO_DATE_TIME'
        iistafnk_to_date_time_lt_key    ='IISTAFNK_TO_DATE_TIME_LT'
        iistafnk_staff_id_key           ='IISTAFNK_STAFF_ID'

        fieldnames_staff_nk = [
            iistafnk_from_date_time_key,
            iistafnk_from_date_time_lt_key,
            iistafnk_to_date_time_key,
            iistafnk_to_date_time_lt_key,
            iistafnk_staff_id_key,]

        # Populate data
        staff_nk_data_rows =[]

        #Add rows
        rosters_bag = r.context('sp_crew').bag()
        for crew_bag in rosters_bag.iterators.crewid_set(sort_by='crew.%id%', where='crew.%debug_selected% and report_tpms.%crew_sel%'):
            if crew_bag.crew.is_active_at_date(self.now):
                iistafnk_from_date_time     =''
                iistafnk_from_date_time_lt  =''
                iistafnk_to_date_time       =''
                iistafnk_to_date_time_lt    =''
                iistafnk_staff_id           =crew_bag.crew.id()

                data_row = [iistafnk_from_date_time,
                            iistafnk_from_date_time_lt,
                            iistafnk_to_date_time,
                            iistafnk_to_date_time_lt,
                            iistafnk_staff_id,]

                staff_nk_data_rows.append(data_row)

        write_tab(f,fieldnames_staff_nk,staff_nk_data_rows,'II_StaffNK')

    def tab_crew_mem_exp_qualif(self,f):
        # TAB CrewMemExpQualif
        iicmeq_act_group_name_key       ='IICMEQ_ACT_GROUP_NAME'
        iicmeg_act_group_version_key    ='IICMEQ_ACT_GROUP_VERSION'
        iicmeq_end_date_key             ='IICMEQ_END_DATE'
        iicmeq_examination_date_key     ='IICMEQ_EXAMINATION_DATE'
        iicmeq_qual_code_key            ='IICMEQ_QUAL_CODE'
        iicmeq_qual_code_type_key       ='IICMEQ_QUAL_CODE_TYPE'
        iicmeq_qual_version_key         ='IICMEQ_QUAL_VERSION'
        iicmeq_remark_key               ='IICMEQ_REMARK'
        iicmeq_staff_id_key             ='IICMEQ_STAFF_ID'
        iicmeq_valid_from_key           ='IICMEQ_VALID_FROM'
        iicmeq_oml_key                  ='IICMEQ_OML'

        fieldnames_crew_mem_exp_qualif = [
            iicmeq_act_group_name_key,
            iicmeg_act_group_version_key,
            iicmeq_end_date_key,
            iicmeq_examination_date_key,
            iicmeq_qual_code_key,
            iicmeq_qual_code_type_key,
            iicmeq_qual_version_key,
            iicmeq_remark_key,
            iicmeq_staff_id_key,
            iicmeq_valid_from_key,
            iicmeq_oml_key,]

        TM(["crew_document"])

        # use list comprehension to build set of queries for each pilot from pilot_list.
        p_str = " ".join([("(crew.id=%s)" % p) for p in (self.pilot_list + self.cabin_list)])

        # build complete search string
        #search_str = "(&  (!   (| (doc.typ=LICENCE) (doc.typ=VISA) (doc.typ=PASSPORT) )   )      (validto>"+PRODEFIS_START_TIME +") (| %s ))" % p_str
        search_str = "(& (doc.typ=REC) (validto>"+PRODEFIS_START_TIME +") (| %s ))" % p_str
        crew_document_data_rows =[]

        for cd in TM.crew_document.search(search_str):

            if cd.ac_qual != None :
                iicmeq_act_group_name           = cd.ac_qual
                iicmeg_act_group_version        = 'Initial'
            else :
                iicmeq_act_group_name           = "ALL"
                iicmeg_act_group_version        = "Initial"

            iicmeq_qual_version             = 'Initial'
            iicmeq_remark                   =''
            iicmeq_staff_id                 = cd.crew.id
            iicmeq_valid_from               = cvt_dstr_to_YYYY_MM_DD(str(cd.validfrom))
            iicmeq_oml                      ='FALSE'

            iicmeq_end_date                 = cvt_dstr_to_YYYY_MM_DD_MINUS_1_DAY(str(cd.validto))
            iicmeq_examination_date         = cvt_dstr_to_YYYY_MM_DD(str(cd.validfrom))

            iicmeq_qual_code        = cd.doc.subtype
            iicmeq_qual_code_type   = cd .doc.typ

            if cd.doc.typ == "REC":
              if (cd.doc.subtype in ["OPCA3", "OPCA4", "OPCA5", "OPCA3A5", "OTSA3", "OTSA4", "OTSA5", "OTSA3A5", "LPCA3", "LPCA4", "LPCA5", "LPCA3A5"]):
                tmp = cd.doc.subtype
                tmp2=tmp.split("C")
                iicmeq_qual_code = tmp2[0] + "C"
                iicmeq_act_group_name = tmp2[1]TPMSCrew.py
              elif (cd.doc.subtype in ["CRM", "CRMC"]):
                iicmeq_qual_code = cd.doc.subtype
            elif cd.doc.typ == "MEDICAL" :
                iicmeq_qual_code= "MED"

            # if cd.doc.typ == "VACCINATION":
            #     iicmeq_qual_code        = cd.doc.type
            #     iicmeq_qual_code_type   = "REC"

            data_row = [    iicmeq_act_group_name,
                            iicmeg_act_group_version,
                            iicmeq_end_date,
                            iicmeq_examination_date,
                            iicmeq_qual_code,
                            iicmeq_qual_code_type,
                            iicmeq_qual_version,
                            iicmeq_remark,
                            iicmeq_staff_id,
                            iicmeq_valid_from,
                            iicmeq_oml
                            ]

            crew_document_data_rows.append(data_row)

        write_tab(f,fieldnames_crew_mem_exp_qualif,crew_document_data_rows,'II_CrewMemExpQualif')

    def tab_cabin_crew_attestation(self, f):
        # TAB II_CabinCrewAttestation
        d = {
            'IICAAT_ATTESTATION_NUMBER': '',
            'IICAAT_CALCULATED_END_DATE': '',
            'IICAAT_COUNTRY_CODE': '',
            'IICAAT_DATEOF_ISSUE': '',
            'IICAAT_REMARK': '',
            'IICAAT_STAFF_ID': '',
            'IICAAT_TO_DATE': ''
        }
        TM(["crew_document"])
        p_str = " ".join([("(crew.id=%s)" % p) for p in self.cabin_list])
        search_str = "(& (doc.subtype=CC ATTEST) (validto>" + PRODEFIS_START_TIME + ") (| %s ))" % p_str
        crew_document_data_rows =[]
        for cd in TM.crew_document.search(search_str):
            try:
                d['IICAAT_ATTESTATION_NUMBER'] = cd.docno
            except:
                pass
            try:
                d['IICAAT_COUNTRY_CODE'] = cd.issuer
            except:
                pass
            d['IICAAT_DATEOF_ISSUE']  = cvt_dstr_to_YYYY_MM_DD(str(cd.validfrom))
            d['IICAAT_TO_DATE'] = cvt_dstr_to_YYYY_MM_DD(str(cd.validto))
            d['IICAAT_STAFF_ID'] = cd.crew.id
            if d['IICAAT_COUNTRY_CODE'] is None and d['IICAAT_ATTESTATION_NUMBER'] is not None:
                if len(d['IICAAT_ATTESTATION_NUMBER']) > 1 and d['IICAAT_ATTESTATION_NUMBER'][0].isalpha() and d['IICAAT_ATTESTATION_NUMBER'][1].isalpha():
                    d['IICAAT_COUNTRY_CODE'] = d['IICAAT_ATTESTATION_NUMBER'][:2]
            crew_document_data_rows.append(d.values())
        write_tab(f, d.keys(), crew_document_data_rows, 'II_CabinCrewAttestation')

    def tab_pilot_license(self,f):
        # TAB PilotLicense
        iipili_country_code_key         ='IIPILI_COUNTRY_CODE'
        iipili_dateof_first_issue_key   ='IIPILI_DATEOF_FIRST_ISSUE'
        iipili_licence_number_key       ='IIPILI_LICENSE_NUMBER'
        iipili_licence_type_code_key    ='IIPILI_LICENSE_TYPE_CODE'
        iipili_remark_key               ='IIPILI_REMARK'
        iipili_staff_id_key             ='IIPILI_STAFF_ID'
        iipili_to_date_key              ='IIPILI_TO_DATE'

        fieldnames_tab_pilot_licence =[
            iipili_country_code_key,
            iipili_dateof_first_issue_key,
            iipili_licence_number_key,
            iipili_licence_type_code_key,
            iipili_remark_key,
            iipili_staff_id_key,
            iipili_to_date_key,]

        # Populate data

        # preload tables (and any dependencies)
        TM(["crew_document"])

        # use list comprehension to build set of queries for each pilot from pilot_list.
        p_str = " ".join([("(crew.id=%s)" % p) for p in self.pilot_list])

        # build complete search string
        search_str = "(& (doc.typ=LICENCE) (validfrom<=%s) (validto>=%s) (| %s ))" % (self.now, self.now, p_str)

        pilot_licence_data_rows =[]

        if len(self.pilot_list)>0:
          for cd in TM.crew_document.search(search_str):

            iipili_country_code         = "" if cd.issuer==None else cd.issuer
            iipili_dateof_first_issue   = cvt_dstr_to_YYYY_MM_DD(str(cd.validfrom))
            iipili_licence_number       = cd.docno
            iipili_licence_type_code    = cd.doc.subtype
            iipili_remark               = ''
            iipili_staff_id             = cd.crew.id
            iipili_to_date              = cvt_dstr_to_YYYY_MM_DD_MINUS_1_DAY(str(cd.validto))

            data_row=[  iipili_country_code,
                        iipili_dateof_first_issue,
                        iipili_licence_number,
                        iipili_licence_type_code,
                        iipili_remark,
                        iipili_staff_id,
                        iipili_to_date,]
            if iipili_licence_type_code != "Temp LPC" :
                pilot_licence_data_rows.append(data_row)

        write_tab(f,fieldnames_tab_pilot_licence,pilot_licence_data_rows,'II_PilotLicense')

    def tab_staff(self,f):
        # TAB staff
        iistaf_birth_date_key       ='IISTAF_BIRTH_DATE'
        iistaff_current_staff_id_key='IISTAF_CURRENT_STAFF_ID'
        iistaf_date_of_joining_key  ='IISTAF_DATE_OF_JOINING'
        iistaf_date_of_quitting_key ='IISTAF_DATE_OF_QUITTING'
        iistaf_first_name_key       ='IISTAF_FIRST_NAME'
        iistaf_gender_key           ='IISTAF_GENDER'
        iistaf_last_name_key        ='IISTAF_LAST_NAME'
        iistaf_letter_code_key      ='IISTAF_LETTER_CODE'
        iistaf_notes_key            ='IISTAF_NOTES'
        iistaf_staff_id_key         ='IISTAF_STAFF_ID'
        iistaf_title_key            ='IISTAF_TITLE'
        iistaf_company_name_key     ='IISTAF_COMPANY_NAME'
        iistaf_account_key          ='IISTAF_ACCOUNT'

        fieldnames_tab_staff =[
            iistaf_birth_date_key,
            iistaff_current_staff_id_key,
            iistaf_date_of_joining_key,
            iistaf_date_of_quitting_key,
            iistaf_first_name_key,
            iistaf_gender_key,
            iistaf_last_name_key,
            iistaf_letter_code_key,
            iistaf_notes_key,
            iistaf_staff_id_key,
            iistaf_title_key,
            iistaf_company_name_key,
            iistaf_account_key,]

        # Populate data
        staff_data_rows =[]

        # Add rows
        rosters_bag = r.context('sp_crew').bag()

        for crew_bag in rosters_bag.iterators.crewid_set(sort_by='crew.%extperkey_at_now%', where='crew.%debug_selected% and report_tpms.%crew_sel% '):
            if crew_bag.crew.is_active_at_date(self.now) :
                #Add data
                try:
                    iistaf_birth_date = cvt_dstr_to_YYYY_MM_DD(str(crew_bag.crew.birthday()))
                except:
                    iistaf_birth_date = ''
                iistaf_current_staff_id = crew_bag.crew.extperkey_at_now()
                iistaf_date_of_joining  =''
                if crew_bag.crew.retirement_date() != None :
                    iistaf_date_of_quitting = cvt_dstr_to_YYYY_MM_DD(str(crew_bag.crew.retirement_date()))
                else:
                    iistaf_date_of_quitting =''
                iistaf_first_name       = crew_bag.report_tpms.crew_first_name().decode("latin-1")
                iistaf_last_name        = crew_bag.report_tpms.crew_last_name().decode("latin-1")
 
                iistaf_gender           = crew_bag.crew.sex()
                iistaf_letter_code      = crew_bag.crew.extperkey_at_now()
                iistaf_notes            ='Imported'
                iistaf_staff_id         = crew_bag.crew.id()
                iistaf_title            = ''
                iistaf_company          = crew_bag.crew.Company()
                if iistaf_company == None :
                    iistaf_company = 'SK'
                iistaf_account          = crew_bag.crew.extperkey_at_now()

                data_row = [    iistaf_birth_date,
                                iistaf_current_staff_id,
                                iistaf_date_of_joining,
                                iistaf_date_of_quitting,
                                iistaf_first_name,
                                iistaf_gender,
                                iistaf_last_name,
                                iistaf_letter_code,
                                iistaf_notes,
                                iistaf_staff_id,
                                iistaf_title,
                                iistaf_company,
                                iistaf_account,]

                staff_data_rows.append(data_row)

        write_tab(f,fieldnames_tab_staff,staff_data_rows,'II_Staff')

    def tab_staff_home_base(self,f):
        # TAB StaffHomebase

        iisthb_from_date_key    ='IISTHB_FROM_DATE'
        iisthb_iata_key         ='IISTHB_IATA'
        iisthb_remark_key       ='IISTHB_REMARK'
        iisthb_staff_id_key     ='IISTHB_STAFF_ID'
        iisthb_to_date_key      ='IISTHB_TO_DATE'

        fieldnames_tab_staff_home_base =[
            iisthb_from_date_key,
            iisthb_iata_key,
            iisthb_remark_key,
            iisthb_staff_id_key,
            iisthb_to_date_key,]

        # Populate data
        home_base_data_rows =[]

        # Add rows
        rosters_bag = r.context('sp_crew').bag()

        # Populate data

        # preload tables (and any dependencies)
        TM(["crew_employment"])

        # Search for actual homebase for active pilots
        p_str = " ".join([("(crew.id=%s)" % p) for p in (self.pilot_list + self.cabin_list)])

        # build complete search string
        search_str_1 = " (| %s )" % p_str
        search_str_2 = " (& (validfrom<=%s) (validto>=%s)%s)" % (self.now,self.now,search_str_1)

        employment_pilots = TM.crew_employment.search(search_str_2)

        for pemp in employment_pilots:

            iisthb_from_date        =  cvt_dstr_to_YYYY_MM_DD(str(pemp.validfrom))
            iisthb_iata             = pemp.base.id
            iisthb_remark           = ''
            iisthb_staff_id         = pemp.crew.id
            iisthb_to_date          = cvt_dstr_to_YYYY_MM_DD_MINUS_1_DAY(str(pemp.validto))

            data_row = [    iisthb_from_date,
                            iisthb_iata,
                            iisthb_remark,
                            iisthb_staff_id,
                            iisthb_to_date,]

            home_base_data_rows.append(data_row)

        write_tab(f,fieldnames_tab_staff_home_base,home_base_data_rows,'II_StaffHomebase')

    def tab_staff_type_rating(self,f):
        # TAB StaffTypeRating
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

        # Populate data

        # preload tables (and any dependencies)
        TM(["crew_qualification","crew_employment"])

        write_header(fieldnames_tab_staff_type_rating,f,"II_StaffTypeRating")
        for p in (self.pilot_list + self.cabin_list) :
            crew_staff_type_rating_data_rows = self.get_crew_data(p)
            if crew_staff_type_rating_data_rows:
                 write_data(fieldnames_tab_staff_type_rating ,crew_staff_type_rating_data_rows,f)

        # crew_staff_type_rating_data_rows = []
        # crew_staff_type_rating_data_rows = self.get_crew_data(10214)
        # write_data(fieldnames_tab_staff_type_rating ,crew_staff_type_rating_data_rows,f)

    def get_crew_data(self,crew_id) :
        # Fetch Ac qualifications valid from 1JAN 2016 and in the future
        qual_search_str = " (&(qual.typ=ACQUAL)(validto >="+ PRODEFIS_START_TIME +")(crew.id=%s))" %crew_id
        crew_qualification_list = list(TM.crew_qualification.search(qual_search_str))

        from_date_map = {}

        # Find all validfrom dates in and put them in a map
        for crew_qual in crew_qualification_list:
            from_date_map[crew_qual.validfrom]=1

        # Get the lowest valid from in crew_qual
        tmp_list = sorted(from_date_map.keys())

        if len(tmp_list)==0:
            return None #no employement/qual

        emp_search_str = "(&(crew.id=%s)(validto >= %s))" % (crew_id,tmp_list[0])
        crew_employment_list = list(TM.crew_employment.search(emp_search_str))

        last_employment = crew_employment_list[len(crew_employment_list)-1]
        last_employment_date = last_employment.validto

        # Remove qualification period for which we do not have any employment
        for l in tmp_list :
            if last_employment_date <=l:
                del from_date_map[l]

        for crew_employment in crew_employment_list:
                from_date_map[crew_employment.validfrom] = 2

        # Here we have all valid from dates in crew_qualifications and crew employment sorted, this is in order
        # to find the valid time intervals for qualification and rank
        from_date_list = sorted(from_date_map.keys())
        # print "From date list : %s" %from_date_list

        crew_staff_type_rating_data_rows=[]

        # Go through each period
        for i in range(len(from_date_list)):

            # Find pilot employment for date
            i_date=from_date_list[i]
            found_ce = None
            for ce in crew_employment_list :
                if ((ce.validfrom<= i_date) and (i_date< ce.validto)):
                    found_ce = ce
                    # print "  ##ranks : %s %s %s " %(pe.validfrom,pe.validto,pe.crewrank.id)

            if found_ce != None:
                #Find qualifications for date
                found_qualifications = {}
                for q in crew_qualification_list :
                    if (q.validfrom<=  i_date < q.validto) and (q.validto >= AbsTime(PRODEFIS_START_TIME + "00:00")):
                        if q.qual.subtype in found_qualifications:
                            if q.validfrom > found_qualifications[q.qual.subtype].validfrom:
                                found_qualifications[q.qual.subtype] = q # take first matching for duplicates 
                        else:
                            found_qualifications[q.qual.subtype] = q
 
                       # print "  ## quals: %s %s %s " % (q.validfrom,q.validto,q.qual.subtype)

                for q2 in found_qualifications.values() :

                    if not (i==len(from_date_list)-1) :
                        end_date =from_date_list[i+1]
                    else :
                        end_date = min(q2.validto,found_ce.validto)

                    if end_date >= AbsTime(PRODEFIS_START_TIME):
                        iictra_act_group_name       =  q2.qual.subtype
                        iictra_act_group_version    = "Initial"
                        iictra_from_date            = cvt_dstr_to_YYYY_MM_DD(str(i_date))
                        try:
                            iictra_rank = found_ce.titlerank.id
                        except:
                            iictra_rank = ""
                        iictra_remark               = ""
                        iictra_staff_id             = crew_id
                        iictra_to_date              = cvt_dstr_to_YYYY_MM_DD_MINUS_1_DAY(str(end_date))

                        data_row =[ iictra_act_group_name,
                                    iictra_act_group_version,
                                    iictra_from_date,
                                    iictra_rank,
                                    iictra_remark,
                                    iictra_staff_id,
                                    iictra_to_date,]

                        crew_staff_type_rating_data_rows.append(data_row)
        
        #Go through the list of qualifications and concatenate A3 and A5 with the same from date                
        for crewQualRow in crew_staff_type_rating_data_rows:
            if 'A5'in crewQualRow:
                if 'FP' in crewQualRow or 'FC' in crewQualRow:
                    a5fromDate = crewQualRow[2]
                    removeCrewQualRow2 = False
                    for crewQualRow2 in crew_staff_type_rating_data_rows:
                        if crewQualRow2[2] == a5fromDate and crewQualRow2[0] == 'A3':
                            crewQualRow[0] = 'A3A5'
                            removeCrewQualRow2 = True
                            break
                    if removeCrewQualRow2 == True:
                        crew_staff_type_rating_data_rows.remove(crewQualRow2)
                        removeCrewQualRow2 = False

        return crew_staff_type_rating_data_rows

    def tab_staff_communication(self,f):
        # TAB Staff communication

        iistco_business_channel_key     ='IISTCO_BUSINESS_CHANNEL'
        iistco_channel_type_key         ='IISTCO_CHANNEL_TYPE'
        iistco_remark_key               ='IISTCO_REMARK'
        iistco_staff_id_key             ='IISTCO_STAFF_ID'
        iistco_value_key                ='IISTCO_VALUE'

        fieldnames_tab_staff_communication =[
            iistco_business_channel_key,
            iistco_channel_type_key,
            iistco_remark_key,
            iistco_staff_id_key,
            iistco_value_key,]

        # Populate data

        rosters_bag = r.context('sp_crew').bag()

        staff_communication_data_rows = []

        for crew_bag in rosters_bag.iterators.crewid_set(sort_by='crew.%id%', where='crew.%debug_selected% and report_tpms.%crew_sel%'):

            if crew_bag.crew.is_active_at_date(self.now) :

                iistco_business_channel     ='TRUE'
                iistco_channel_type         ='EM'
                iistco_remark               =''
                iistco_staff_id             = crew_bag.crew.id()
                iistco_value                = crew_bag.report_tpms.crew_email(self.now)

                data_row =[ iistco_business_channel,
                            iistco_channel_type,
                            iistco_remark,
                            iistco_staff_id,
                            iistco_value,]

                staff_communication_data_rows.append(data_row)

        write_tab(f,fieldnames_tab_staff_communication,staff_communication_data_rows,'II_StaffCommunication')

    def tab_seniority(self,f):
        # TAB Staff seniority
        iistse_seniority_key            ='IISTSE_SENIORITY'
        iistse_staff_id_key             ='IISTSE_STAFF_ID'

        fieldnames_tab_staff_seniority =[
            iistse_seniority_key,
            iistse_staff_id_key,]

        seniority_data_rows = []
        # Populate date

        rosters_bag = r.context('sp_crew').bag()

        for crew_bag in rosters_bag.iterators.crewid_set(sort_by='crew.%id%', where='crew.%is_pilot% and crew.%debug_selected% and report_tpms.%crew_sel%'):
            if crew_bag.crew.is_active_at_date(self.now) :

                iistse_seniority            = crew_bag.crew.seniority_value(self.now)
                iistse_staff_id             =crew_bag.crew.id()

                data_row =[ iistse_seniority,
                            iistse_staff_id,]

                seniority_data_rows.append(data_row)

        write_tab(f,fieldnames_tab_staff_seniority,seniority_data_rows,'II_StaffSeniority')

    def tab_staff_address(self,f):
        # TAB Staff address
        iistad_complete_address_key      ='IISTAD_COMPLETE_ADDRESS'
        iistad_description_key          ='IISTAD_DESCRIPTION'
        iistad_staff_id_key             ='IISTAD_STAFF_ID'
        iistad_state_key               ='IISTAD_STATE'
        iistad_street_key               ='IISTAD_STREET'
        iistad_technical_nk_key         ='IISTAD_TECHNICAL_NK'
        iistad_zip_code_key             ='IISTAD_ZIP_CODE'
        iistad_number_of_address_key    ='IISTAD_NUMBER_OF_ADDRESS'
        iistad_city_name_key            ='IISTAD_CITY_NAME'

        fieldnames_tab_staff_address =[
            iistad_complete_address_key,
            iistad_description_key,
            iistad_staff_id_key,
            iistad_state_key,
            iistad_street_key,
            iistad_technical_nk_key,
            iistad_zip_code_key,
            iistad_number_of_address_key,
            iistad_city_name_key, ]

        # Populate date

        rosters_bag = r.context('sp_crew').bag()

        staff_address_data_rows = []

        for crew_bag in rosters_bag.iterators.crewid_set(sort_by='crew.%id%', where='crew.%debug_selected% and report_tpms.%crew_sel%'):
            if crew_bag.crew.is_active_at_date(self.now) :

                if crew_bag.crew.street(self.now) :
                    tmp_str = crew_bag.report_tpms.crew_street(self.now) +", "+crew_bag.report_tpms.crew_country(self.now) + \
                                                    "-" + crew_bag.report_tpms.crew_postal_code(self.now) + " "+crew_bag.report_tpms.crew_city(self.now)
                    iistad_complete_address     =tmp_str.decode("latin-1")

                else:
                    iistad_complete_address="No value"

                iistad_description          =''
                iistad_staff_id             = crew_bag.crew.id()
                iistad_state                =''
                iistad_street               =''
                iistad_technical_nk         =''
                iistad_zip_code             =''
                iistad_number_of_address    =''
                iistad_city_name            =''

                data_row =[ iistad_complete_address,
                            iistad_description,
                            iistad_staff_id,
                            iistad_state,
                            iistad_street,
                            iistad_technical_nk,
                            iistad_zip_code,
                            iistad_number_of_address,
                            iistad_city_name,]

                staff_address_data_rows.append(data_row)

        write_tab(f,fieldnames_tab_staff_address,staff_address_data_rows,'II_StaffAddress')


class TPMSExport(SASReport):
    def __init__(self):
        self.now = t.abstime_now()
        self.pilot_list = get_active_crew(True)
        self.cabin_list = get_active_crew(False)

    def create(self):
        dir_path = os.getenv("CARMDATA")
        
        archivePath =dir_path + "/REPORTS/TPMS_ARCHIVE/"
        mypath = dir_path + "/REPORTS/TPMS_EXPORT/"
        if not os.path.exists(mypath):
            os.makedirs(mypath)
        if not os.path.exists(archivePath):
            os.makedirs(archivePath)

        tmp_str = str(datetime.now())
        date_str = tmp_str.replace(" ","_")
        date_str = date_str.replace(":","")
        date_str = date_str[:-9]
        reportName = "TPMS_Crew_"+date_str
        myFile = mypath + reportName + '.csv'
        
        
        
        with open(myFile,'wb') as f:
            r = TPMSRoutines(f, self.pilot_list, self.cabin_list, self.now)

            r.tab_staff_nk(f)
            r.tab_crew_mem_exp_qualif(f)
            r.tab_cabin_crew_attestation(f)
            r.tab_pilot_license(f)
            r.tab_staff(f)
            r.tab_staff_home_base(f)
            r.tab_staff_type_rating(f)
            r.tab_staff_communication(f)
            r.tab_seniority(f)
            r.tab_staff_address(f)
            
        os.chmod(myFile,stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO )
        shutil.copyfile(myFile, archivePath + reportName + '.csv')
            

def main():
    export = TPMSExport()
    export.create()

#main()
