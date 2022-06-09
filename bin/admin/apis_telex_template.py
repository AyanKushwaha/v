#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# This script facilitates generating telex messages.
# So far you need to update data directly in the script before running it, so there is room for improvements.
# It is known to work for delete messages. It probably needs some changes for add and update to work.

from jinja2 import Template as tmp
import datetime

non_accii_nordic = ['À', 'Á', 'Â', 'Ã', 'Ä', 'Å', 'Æ', 'Ç', 'È', 'É', 'Ê', 'Ë', 'Ì', 'Í', 'Î', 'Ï', 'Ð', 'Ñ', 'Ò', 'Ó', 'Ô', 'Õ', 'Ö' ] 

# Update to your contact info
operator_name = "NIKLAS"
operator_family = "STROEM"
operator_phone = "0046721551772"

current_date = datetime.date.today().strftime('%y%m%d')
current_time = datetime.datetime.now().strftime('%H%M')

actions = { 'add': 'G',
            'delete': 'H',
            'change': 'I',
            'update': 'I'}

# Write the action you want to perform
operator_action = actions['delete']


# Modify and add/delete crew data
# No special characters like ÅÄÖ allowed. Translate to AA, AE, OE counterparts.
# Space is allowed in for example double names
crew_list = []  
crew_list.append({ 
    'family_name': 'CREW_FAMILY',
    'given_name': 'CREW NAME1',
    'sex': 'M', # M/F
    'cat': '1', # cockpit: 1 and cabin: 2
    'birthdate': 'YYMMDD', # like '800120'
    'nationality': 'XXX', # like SWE or DNK
    'passport_number': 'XXXXXXXXX',
    'passport_country': 'XXX' # like SWE or DNK
})
crew_list.append({
    'family_name': 'CREW_FAMILY',
    'given_name': 'CREW_NAME2',
    'sex': 'F',
    'cat': '2', # cockpit: 1 and cabin: 2
    'birthdate': 'YYMMDD', # like '800120'
    'nationality': 'XXX', # like SWE or DNK
    'passport_number': 'XXXXXXXXX',
    'passport_country': 'XXX' # like SWE or DNK
})

# Headers taken from templates, there are some small differences in SKxxxxxx-numbers, not sure if it matters
# insert: UNA:+.? 'UNB+UNOA:4+MCCL*TSA:ZZ+USCSAPIS:ZZ+YYMMDD:0100+SK099855++APIS'UNG+PAXLST+SCANDINAVIAN AIRLINES+USCSAPIS:ZZ+YYMMDD:HHMM+SK09985510+UN+D:05B'UNH+SK09985511+PAXLST:D:05B:UN:IATA+SK01MCLYYMMDD01+01'BGM+336+G'RFF+TN:SK01MCLYYMMDD:::1'NAD+MS+++MALMQVIST:HAN'COM+004687972974 :TE+004687974:FX'TDT+20+SK01MCL+++SK'LOC+188+XXX'DTM+554:YYMMDDHHMM:201'LOC+172+TST'DTM+554:YYMMDDHHMM:201'
# update: UNA:+.? 'UNB+UNOA:4+MCCL*TSA:ZZ+USCSAPIS:ZZ+YYMMDD:0104+SK138456++APIS'UNG+PAXLST+SCANDINAVIAN AIRLINES+USCSAPIS:ZZ+YYMMDD:HHMM+SK13845610+UN+D:05B'UNH+SK13845611+PAXLST:D:05B:UN:IATA+SK01MCLYYMMDD01+01'BGM+336+I'RFF+TN:SK01MCLYYMMDD:::1'NAD+MS+++MALMQVIST:HAN'COM+004687972974 :TE+004687974:FX'TDT+20+SK01MCL+++SK'LOC+188+XXX'DTM+554:YYMMDDHHMM:201'LOC+172+TST'DTM+554:YYMMDDHHMM:201'
# Footers also have some differences, maybe it works anyway
# Note: There are many more fields available when for example creating or updating crew info
# (like place of birth and passport expiration date). These needs to be added if relevant.
# We're not sure which fields are used as keys, but family name is for sure one of them. Please document if you find out.
#
# Some notes about the syntax:
#  + is a separator, so multiple +s in a sequence indicates potential fields to be filled in.
#  ' seems to indicate the end of a section/row

header_template = tmp("""
UNA:+.? 'UNB+UNOA:4+MCCL*TSA:ZZ+USCSAPIS:ZZ+{{ current_date }}:{{ current_time }}+SK299479++APIS'UNG+PAXLST+SCANDINAVIAN AIRLINES+USCSAPIS:ZZ+{{ current_date }}:{{ current_time }}+SK29947910+UN+D:05B'UNH+SK29947911+PAXLST:D:05B:UN:IATA+SK01MCL{{ current_date }}03+01'BGM+336+{{ operator_action }}'RFF+TN:SK01MCL{{ current_date }}:::1'NAD+MS+++{{ operator_family|upper }}:{{ operator_name|upper }}'COM+{{ operator_phone }}:TE+{{ operator_phone }}:FX'TDT+20+SK01MCL+++SK'LOC+188+XXX'DTM+554:{{ current_date }}{{ current_time }}:201'LOC+172+TST'DTM+554:{{ current_date }}{{ current_time }}:201'
""")
body_template = tmp("""
{% for crew in crew_list %}


NAD+FM+++{{ crew.family_name|upper }}:{{ crew.given_name|upper }}+++++'
ATT+2++{{ crew.sex|upper }}'
DTM+329:{{ crew.birthdate }}'
LOC+174+{{ crew.nationality|upper }}'
EMP+1+CR{{ crew.cat }}:110:111'
NAT+2+{{ crew.nationality|upper }}'
DOC+P:110:111+{{ crew.passport_number }}'
LOC+91+{{ crew.passport_country|upper }}'

{% endfor %}
""")

for crew in crew_list:
    for char in crew['given_name']:
        if char.upper() in non_accii_nordic:
            print("Warning:  crew name contais non accii charecter please update them with non accii char!!!")
            print(u"Example: Ö should be 'OE'")
            exit(1)
    for char in crew['family_name']:
        if char.upper() in non_accii_nordic:
            print("Warning:  crew name contais non accii charecter please update them with non accii char!!!")
            print(u"Example: Ö should be 'OE'")
            exit(1)
 
# This is the footer of a delete message, update and add may have to be different
footer_tamplate = tmp("""
CNT+41:{{ crew_list| length  }}'UNT+102+SK29947911'UNE+1+SK29947910'UNZ+1+SK299479'
""")
telex = header_template.render(current_date=current_date, current_time=current_time, operator_family=operator_family, operator_name=operator_name, operator_phone=operator_phone, operator_action=operator_action) + \
    body_template.render(crew_list=crew_list) + \
    footer_tamplate.render(crew_list=crew_list)
print(telex)



