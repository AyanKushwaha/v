from adhoc.generate_migration import MigrationScript
from RelTime import RelTime
from AbsTime import AbsTime
from AbsDate import AbsDate

def main():
    migration = MigrationScript()
    hotel_table = migration.add_table("hotel", ('Sid',
                                                'Sname',
                                                'Sstreet',
                                                'Scity',
                                                'Sstate',
                                                'Spostalcode',
                                                'Scountry',
                                                'Stel',
                                                'Sfax',
                                                ('Ssi', None),
                                                'Semail'))

    hotel_contract_table = migration.add_table("hotel_contract", ('Shotel',
                                                                  'Avalidfrom',
                                                                  'Avalidto',
                                                                  ('Rxeci', RelTime('06:00')),
                                                                  ('Reci', RelTime('06:00')),
                                                                  ('Rlco', RelTime('20:00')),
                                                                  ('Rxlco', RelTime('20:00')),
                                                                  'Icostco',
                                                                  'Icostca',
                                                                  'Scur',
                                                                  'Scontact',
                                                                  ('Ssi', None)))

    hotel_transport_table = migration.add_table("hotel_transport", ('Sairport',
                                                                    'Shotel',
                                                                    'Avalidfrom',
                                                                    'Avalidto',
                                                                    'Rdurationfc',
                                                                    'Rdurationcc',
                                                                    'Icost',
                                                                    ('Ssi', None)))

    transport_table = migration.add_table("transport", ('Sid',
                                                        'Sname',
                                                        'Sstreet',
                                                        'Scity',
                                                        'Sstate',
                                                        'Spostalcode',
                                                        'Scountry',
                                                        'Stel',
                                                        'Sfax',
                                                        ('Ssi', None),
                                                        'Semail',
                                                        'Semailupd'))

    transport_contract_table = migration.add_table("transport_contract", ('Stransport',
                                                                          'Avalidfrom',
                                                                          'Avalidto',
                                                                          'Icost',
                                                                          'Scur',
                                                                          'Scontact',
                                                                          ('Ssi', None)))

    preferred_hotel_exc_table = migration.add_table("preferred_hotel_exc", ('Sairport',
                                                                            'Sregion',
                                                                            'Smaincat',
                                                                            'Bairport_hotel',
                                                                            'Avalidfrom',
                                                                            'Sarr_flight_nr',
                                                                            'Sdep_flight_nr',
                                                                            'Sweek_days',
                                                                            'Avalidto',
                                                                            'Shotel',
                                                                            ('Ssi', None)))

    airport_hotel_table = migration.add_table("airport_hotel", ('Sairport',
                                                                'Shotel',
                                                                ('Ssi', None),
                                                                'Stransport'))


    hotel = {}
    hotel['id'] = nullified_raw_input("What is the hotel id? (E.g. LPA3)\n", null_allowed=False)
    hotel['name'] = nullified_raw_input("What is the hotel name?\n", null_allowed=False)
    hotel['street'] = nullified_raw_input("What is the street?\n", null="Unknown")
    hotel['city'] = nullified_raw_input("What is the city?\n", null="Unknown")
    hotel['state'] = nullified_raw_input("What is the state?\n")
    hotel['postalcode'] = nullified_raw_input("What is the postal code?\n")
    hotel['country'] = nullified_raw_input("What is the country? (E.g. FI)\n", null_allowed=False)
    hotel['tel'] = nullified_raw_input("What is the phone number?\n")
    hotel['fax'] = nullified_raw_input("What is the fax number?\n")
    hotel['email'] = nullified_raw_input("What is the email address? (Comma seperated, if more than one)\n", null_allowed=False)

    hotel_table.add_row(hotel)

    hotel_contract = {}
    hotel_contract['hotel'] = hotel['id']
    hotel_contract['validfrom'] = nullified_raw_input("When is it valid from?\n", null_allowed=False, convert_type=AbsTime)
    hotel_contract['validto'] = AbsTime("01JAN2035")
    # hotel_contract['validto'] = AbsTime(nullified_raw_input("When is it valid to?\n"))
    hotel_contract['cur'] = nullified_raw_input("What is the currency?\n")
    hotel_contract['costco'] = nullified_raw_input("What is the hotel cost?\n", convert_type=int)
    hotel_contract['costca'] = hotel_contract['costco']
    hotel_contract['contact'] = nullified_raw_input("Who is the hotel contact?\n")

    hotel_contract_table.add_row(hotel_contract)

    hotel_transport = {}
    hotel_transport['airport'] = nullified_raw_input("What is the airport?\n", null_allowed=False)
    hotel_transport['hotel'] = hotel['id']
    hotel_transport['validfrom'] = AbsDate(hotel_contract['validfrom'])
    hotel_transport['validto'] = AbsDate(hotel_contract['validto'])
    hotel_transport['durationfc'] = nullified_raw_input("What is the transport time?\n", convert_type=RelTime)
    hotel_transport['durationcc'] = hotel_transport['durationfc']
    hotel_transport['cost'] = nullified_raw_input("What is the transport cost?\n", convert_type=int)
    hotel_transport_table.add_row(hotel_transport)

    transport = {}
    transport['name'] = nullified_raw_input("What is the transport company name? (Empty name => no transport company)\n")
    if transport['name'] == None:
        transport['id'] = None
    else:
        transport['id'] = hotel['id']
        transport['street'] = nullified_raw_input("What is the transport company street?\n", null='Unknown')
        transport['city'] = nullified_raw_input("What is the transport company city?\n", null='Unknown')
        transport['state'] = hotel['state']
        transport['postalcode'] = nullified_raw_input("What is the transport company postal code?\n")
        transport['country'] = hotel['country']
        transport['tel'] = nullified_raw_input("What is the transport company phone number?\n")
        transport['fax'] = nullified_raw_input("What is the transport company fax number?\n")
        transport['email'] = nullified_raw_input("What is the transport company email address?\n", null_allowed=False)
        transport['emailupd'] = transport['email']

        transport_table.add_row(transport)

        transport_contract = {}
        transport_contract['transport'] = transport['id']
        transport_contract['validfrom'] = hotel_contract['validfrom']
        transport_contract['validto'] = hotel_contract['validto']
        transport_contract['cur'] = hotel_contract['cur']
        transport_contract['cost'] = hotel_transport['cost']
        transport_contract['contact'] = nullified_raw_input("Who is the transport company contact?\n")

        transport_contract_table.add_row(transport_contract)

    while True:
        preferred_hotel_exc = {}
        preferred_hotel_exc['arr_flight_nr'] = nullified_raw_input("What is the arrival flight number? (E.g. SK666 or *) Empty flight number => no more flights)\n")
        if preferred_hotel_exc['arr_flight_nr'] == None:
            break
        preferred_hotel_exc['dep_flight_nr'] = nullified_raw_input("What is the departure flight number? (E.g. SK42 or *)\n", null_allowed=False)
        preferred_hotel_exc['airport'] = hotel_transport['airport']
        preferred_hotel_exc['validfrom'] = nullified_raw_input("When is it valid from?\n", null_allowed=False, convert_type=AbsDate)
        preferred_hotel_exc['validto'] = nullified_raw_input("When is it valid to?\n", null_allowed=False, convert_type=AbsDate)
        preferred_hotel_exc['week_days'] = nullified_raw_input("For which week days? (Default 1234567, 1=Monday ... 7=Sunday)\n", null='1234567')
        preferred_hotel_exc['hotel'] = hotel['id']
        for region in ['SKS', 'SKD', 'SKN', 'SKI']:
            for maincat in ['C', 'F']:
                for airport_hotel in [True, False]:
                    preferred_hotel_exc['region'] = region
                    preferred_hotel_exc['maincat'] = maincat
                    preferred_hotel_exc['airport_hotel'] = airport_hotel
                    preferred_hotel_exc_table.add_row(preferred_hotel_exc)

    airport_hotel = {}
    airport_hotel['airport'] = hotel_transport['airport']
    airport_hotel['hotel'] = hotel['id']
    airport_hotel['transport'] = transport['id']

    airport_hotel_table.add_row(airport_hotel)

    migration.create_files("add_hotel_%s" % hotel['id'])


def nullified_raw_input(info, null=None, null_allowed=True, convert_type=None):
    while True:
        output = raw_input(info)
        if output == '':
            if null_allowed:
                return null
            else:
                print "Empty value not allowed!"
        else:
            if convert_type == None:
                return output
            else:
                return convert_type(output)


if __name__ == '__main__':
    main()
