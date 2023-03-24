#!/bin/env python

# Imports ================================================================{{{1
import sys
import os
import os.path
import datetime
import getopt
import uuid

from carmensystems.dig.framework import carmentime
from carmensystems.dig.framework.dave import DaveConnector, DaveSearch
#  from carmensystems import carmlog removed from R22
import logging
from AbsTime import AbsTime
from RelTime import RelTime
from utils.xmlutil import XMLDocument, XMLElement, XMLAttributes


# Exceptions ============================================================={{{1

# UsageException ---------------------------------------------------------{{{2
class UsageException(Exception):
    """ 
    Raised for usage errors (wrong name/type of arguments, etc.). 
    """
    msg = ''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


# Support classes ========================================================{{{1

# Attributor -------------------------------------------------------------{{{2

class Attributor:
    def __init__(self, rec):
        global _tmp
    
        for key, value in rec.items():
            setattr(self, key, value)

# Crew -------------------------------------------------------------------{{{2
class Crew(Attributor):
    pass

# Employment -------------------------------------------------------------{{{2
class Employment(Attributor):
    pass

# Contract ---------------------------------------------------------------{{{2
class Contract(Attributor):
    pass

# Qualification ----------------------------------------------------------{{{2
class Qualification(Attributor):
    pass


# XML formatting classes ================================================={{{1
_groups = set()
_qualifications = set()
       
# CrewDataDocument -------------------------------------------------------{{{2
class CrewDataDocument(XMLDocument):
    """
    Class for creation of crew data document.
    """
    
    def __init__(self, dbconn, from_time, logger):
        XMLDocument.__init__(self)
        
        global _groups
        global _qualifications
        
        from_time = carmentime.toCarmenTime(from_time)
                          
        # Get data from database.
        crew_table = dbconn.runSearch(DaveSearch('crew', []))
        tbl_crew_employment = dbconn.runSearch(DaveSearch('crew_employment', [('validto', '>', from_time),
                                                                    ('company', '!=', 'SVS')])) 
        non_svs_crew = []                                                                    
        for ce in tbl_crew_employment:
            if ce['crew'] not in non_svs_crew:
                non_svs_crew.append(ce['crew'])
           
        tbl_crew_rank_set = dbconn.runSearch(DaveSearch('crew_rank_set',[]))
        tbl_crew_contract = dbconn.runSearch(DaveSearch('crew_contract', [('validto', '>', from_time),
                ('contract', '!=', 'VSVS-001'), ('contract', '!=', 'VSVS-101')]))
        tbl_crew_contract_set = dbconn.runSearch(DaveSearch('crew_contract_set',[('id', '!=', 'VSVS-001'), 
                                                ('id', '!=', 'VSVS-101')]))
        tbl_crew_qualification = dbconn.runSearch(DaveSearch('crew_qualification', [('qual_typ','=','ACQUAL'),                                                                                      
                                                                                    ('validto', '>', from_time)]))
        tbl_bid_periods = dbconn.runSearch(DaveSearch('bid_periods', [('window_open', '>', from_time)]))

        # Prepare data.
        crew_employments = self._to_attributor(tbl_crew_employment, 'crew', Employment)                              
        for l in crew_employments.itervalues():
            l.sort(self._sort_by_period)       
        crew_contracts = self._to_attributor(tbl_crew_contract, 'crew', Contract)
        for l in crew_employments.itervalues():
            l.sort(self._sort_by_period)
        crew_qualifications = self._to_attributor(tbl_crew_qualification, 'crew', Qualification)            
        for l in crew_employments.itervalues():
            l.sort(self._sort_by_period)
        crew_rank_set = self._to_dictionary(tbl_crew_rank_set, 'id', ['maincat'])        
        crew_contract_set = self._to_dictionary(tbl_crew_contract_set, 'id', ['grouptype', 'desclong'])
        
        # Create counter for added/skipped crew.
        crew_counter = {'added': 0,
                        'skipped': 0}

        # Create XML data for crew.
        xmlCrew = XMLElement('crew')  
        for rec in crew_table:           
            # Create a Crew object and set employments, contracts and qualifications.
            if rec['id'] in non_svs_crew:
                crew = Crew(rec)
                crew.employments = crew_employments.get(crew.id, [])
                crew.contracts = crew_contracts.get(crew.id, [])
                crew.qualifications = crew_qualifications.get(crew.id, [])
                
                #Set maincat for each employment record.
                for employment in crew.employments:
                    employment.maincat = crew_rank_set.get(employment.crewrank, None)[0]          
                #Set grouptype and contracttype for each contract record.
                for contract in crew.contracts:
                    contract.grouptype = crew_contract_set.get(contract.contract, None)[0]
                    if contract.grouptype == 'F':
                        contract.contracttype = 'FG'
                    else:
                        contract.contracttype = 'VG'
                    contract.desclong = crew_contract_set.get(contract.contract, None)[1]
                    if contract.desclong == 'Temp':
                        # To disable the Interbids Resource Pool group, change this to False
                        contract.temp = True
                    else:
                        contract.temp = False
                
                xmlCrewElement = CrewElement(crew, logger)
                xmlCrew.append(xmlCrewElement)
                crew_counter['added'] += 1
    
        # Create XML data for groups.
        xmlGroups = XMLElement('groups')
        for group in _groups:
            xmlGroups.append(XMLElement("group", {'name': group}))
    
        # Create XML data for qualifications.
        xmlQualifications = XMLElement('qualifications')
        for qualification in _qualifications:
            xmlQualifications.append(XMLElement("qualification", {'name': qualification}))
            
        # Create XML data for bid periods.
        period_groups = {}
        period_groups['FD SH SKN VG'] = set(['FD SH SKN VG'])
        period_groups['FD SH SKS VG'] = set(['FD SH SKS VG'])
        period_groups['FD SH SKD VG'] = set(['FD SH SKD VG'])
        period_groups['FD SH SKN FG'] = set(['FD SH SKN FG'])
        period_groups['FD SH SKS FG'] = set(['FD SH SKS FG'])
        period_groups['FD SH SKD FG'] = set(['FD SH SKD FG'])
        period_groups['FD LH'] = set(['FD LH'])
        period_groups['CC RP'] = set(['CC RP'])
        period_groups['CC SKN VG'] = set(['CC SKN VG'])
        period_groups['CC SKN FG'] = set(['CC SKN FG'])
        period_groups['CC SKS VG'] = set(['CC SKS VG'])
        period_groups['CC SKS FG'] = set(['CC SKS FG'])
        period_groups['CC SKD VG'] = set(['CC SKD VG'])
        period_groups['CC SKD FG'] = set(['CC SKD FG'])    
        
        period_groups['FD SH'] = period_groups['FD SH SKN VG'] | period_groups['FD SH SKD VG'] | period_groups['FD SH SKS VG'] | period_groups['FD SH SKN FG'] | period_groups['FD SH SKD FG'] | period_groups['FD SH SKS FG']
        period_groups['FD SH VG'] =  period_groups['FD SH SKN VG'] | period_groups['FD SH SKD VG'] | period_groups['FD SH SKS VG']
        period_groups['FD SH FG'] =  period_groups['FD SH SKN FG'] | period_groups['FD SH SKD FG'] | period_groups['FD SH SKS FG']
        period_groups['FD SH SKN'] =  period_groups['FD SH SKN FG'] | period_groups['FD SH SKN VG']
        period_groups['FD SH SKS'] =  period_groups['FD SH SKS FG'] | period_groups['FD SH SKS VG']
        period_groups['FD SH SKD'] =  period_groups['FD SH SKD FG'] | period_groups['FD SH SKD VG']
        period_groups['FD ALL'] = period_groups['FD SH'] | period_groups['FD LH']

        period_groups['CC SKN'] = period_groups['CC SKN VG'] | period_groups['CC SKN FG']
        period_groups['CC SKS'] = period_groups['CC SKS VG'] | period_groups['CC SKS FG']
        period_groups['CC SKD'] = period_groups['CC SKD VG'] | period_groups['CC SKD FG']
        period_groups['CC ALL'] = period_groups['CC SKN'] |  period_groups['CC SKS'] |  period_groups['CC SKD']

        period_groups['ALL'] = period_groups['FD ALL'] | period_groups['CC ALL']

        _periods = {}        
        
        bid_periods = []
        for period in tbl_bid_periods:
            if period['bid_group'] in period_groups:
                bid_periods.append(period)
        bid_periods.sort(lambda x, y : cmp(len(x['bid_group']), len(y['bid_group'])), reverse=True)

        for period in bid_periods:
            for group in period_groups[period['bid_group']]:
                if not group in _groups:
                    break
                type = period['bid_type']
                if not (group, type) in _periods:
                    _periods[(group, type)] = []
                    
                # Check for bid window overlaps:
                window_overlap = False
                for existing_period in _periods[(group, type)]:
                    if (period['window_open'] >= existing_period['window_open'] and
                        period['window_open'] < existing_period['window_close'] or
                        period['window_close'] > existing_period['window_open'] and
                        period['window_close'] < existing_period['window_close']):
                        window_overlap = True
                if not window_overlap:
                    _periods[(group, type)].append(period)

        xmlPeriods = XMLElement('periods')
        for (group, type) in _periods:
            for period in _periods[(group, type)]:               
                xmlPeriods.append(XMLElement("period", {'group_name': group,
                                                        'type': type,
                                                        'start': _date_time(AbsTime(period['period_start'])),
                                                        'end':  _date_time(AbsTime(period['period_end']), True),
                                                        'open': _date_time(AbsTime(period['window_open'])),
                                                        'close': _date_time(AbsTime(period['window_close']), True)}))

        # Create XML root element.
        root_attributes = {"xmlns": "http://carmen.jeppesen.com/crewweb/framework/xmlschema/import",
                           "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                           "xsi:schemaLocation": "http://carmen.jeppesen.com/crewweb/framework/xmlschema/import import.xsd"}
    
        xmlRoot = XMLElement('import', root_attributes)

        # Append XML data to document.
        xmlRoot.append(xmlGroups)
        xmlRoot.append(xmlQualifications)
        xmlRoot.append(xmlPeriods)
        xmlRoot.append(xmlCrew)
        self.append(xmlRoot)

    """
    Support functions
    """    
    def _to_attributor(self, table, key, Attributor):
        map = {}
        for rec in table:
            if not rec[key] in map:
                map[rec[key]] = []
            map[rec[key]].append(Attributor(rec))
        return map

    def _to_dictionary(self, table, keyColumn, valueColumns):
        map = {}
        for rec in table:
            values = []
            for valueColumn in valueColumns:
                values.append(rec[valueColumn])
            map[rec[keyColumn]] = values
        return map
                
    def _sort_by_period(self, m, n):
        if m.validto > n.validto:
            return 1
        elif m.validto < n.validto:
            return -1
        return 0
    
# CrewElement ------------------------------------------------------------{{{2
class CrewElement(XMLElement):   
    """
    Class for creation of crew data XML elements. 
    Creates groups, qualifications and attributes for a given crew.
    """
        
    def __init__(self, crew, logger):  
        XMLElement.__init__(self, 'crew')

        global _groups
        global _qualifications
        self.crew = crew
        self.logger = logger
        self._has_groups = True
        self._has_qualifications = True
        self._has_attributes = True


        # Find employment number
        empno = None
        for x in crew.employments:
            if x.extperkey is not None:
                empno = x.extperkey
        if empno is None:
            # no empno means that this crew member should not be able to login. But we still need to send something in login_id.
            empno = str(uuid.uuid4()).replace('-','')

        # Set crew element attributes.
        self.attributes = XMLAttributes({'first_name': crew.forenames,
                                         'last_name': crew.name,
                                         'login_id': empno,
                                         'user_id': crew.id})
       
        """
        Add crew attributes.
        """
        # Define attributes to export. 
        export_attributes = [(crew.employments, 'region'),
                             (crew.employments, 'base'),
                             (crew.employments, 'station'),
                             (crew.employments, 'crewrank'),
                             (crew.employments, 'titlerank'),
                             (crew.contracts, 'contracttype')]
                
        # Create a list of attributes.
        attributes = []
        for (lst, key) in export_attributes:
            attribute = []
            for item in lst:
                attribute.append({'name': key, 
                                  'value': getattr(item, key),
                                  'start': item.validfrom,
                                  'end': item.validto})
            # Merge adjacent and overlapping equal attributes values.
            attribute = self._merge_adjacent_items(attribute, 'value')
            # Only export current attribute value.
            bp = int(AbsTime(*tuple((datetime.date.today() + datetime.timedelta(days=45)).timetuple())[:5]))
            tmp = None
            for attr in attribute:
                if int(attr['start']) <= bp and int(attr['end']) > bp:
                    tmp = attr
            if tmp:
                attributes.append(tmp)
            elif len(attribute) > 0:
                attributes.append(attribute[0])
            #attributes.extend(attribute)
                    
        if attributes:
            # Create XML attribute data.
            xmlAttributes = XMLElement('attributes')
            for attribute in attributes:
                xmlAttributes.append(XMLElement('attribute', self._xml_datetime(attribute)))
            self.append(xmlAttributes)
        else:
            self._has_attributes = False

        """
        Add crew groups.
        """
        # Create a sorted list of possible group change dates.
        group_dates = set()
        for obj in crew.employments + crew.contracts + crew.qualifications:
            group_dates.add(obj.validto)
            group_dates.add(obj.validfrom)
        group_dates = list(group_dates)
        group_dates.sort()
        
        # Create a list of groups.
        groups = []
        for (start, end) in zip(group_dates[:-1], group_dates[1:]):
            name = self._get_group_at_date(start)
            if name:               
                groups.append({'name': name,
                               'start': start,
                               'end': end})
        
        # SKBMM-359: Interbids doesn't support valid from and valid to.
        # As a workaround, send the group at now+50d as the only group
        group_date = int(AbsTime(*tuple((datetime.date.today() + datetime.timedelta(days=50)).timetuple())[:5]))
        group = self._get_group_at_date(group_date)
        if group is None:
            groups = []
        else:
            groups = [{'name':  group,
                       'start': AbsTime("19900101"),
                       'end':   AbsTime("20360101")}]
        # End SKBMM-359 workaround

        if groups:
            # Merge adjacent and overlapping equal groups. 
            groups = self._merge_adjacent_items(groups, 'name')
        
            # Create XML group data.
            xmlGroups = XMLElement('groups')
            for group in groups:
                xmlGroups.append(XMLElement('group', self._xml_datetime(group)))
                _groups.add(group['name'])
            self.append(xmlGroups)
        else:
            self._has_groups = False

        """
        Add crew qualifications.
        """     
        # Create a list of qualifications.
        
        qualifications = []        
        for q in crew.qualifications:
            qualifications.append({'name': q.qual_subtype, 
                                   'start': q.validfrom,
                                   'end': q.validto})

        #Changes done for SKCMS-2785
        start_contract = 0
        end_contract = 0
        
        for contract in [x for x in crew.contracts if x.contracttype == 'VG']:
             
            if (start_contract == 0):
                start_contract = contract.validfrom
            end_contract = contract.validto
            
        if (start_contract):
            qualifications.append({'name': 'CONTRACTVG', 
                                   'start': start_contract,
                                   'end': end_contract})

        if (qualifications):
        # Create XML qualification data.
            xmlQualifications = XMLElement('qualifications')
            for qualification in qualifications:
                xmlQualifications.append(XMLElement('qualification', self._xml_datetime(qualification)))
                _qualifications.add(qualification['name'])
            self.append(xmlQualifications)
        else:
            self._has_qualifications = False
            
        """
        Add crew roles.
        """
        xmlRoles = XMLElement('roles')
        xmlRoles.append(XMLElement('role', 'interbids-bidding-crew'))
        xmlRoles.append(XMLElement('role', 'vacation-bidding'))
        xmlRoles.append(XMLElement('role', 'career-bidding'))
        self.append(xmlRoles)

        if not self.valid():
            self.attributes["inactive"] = "true"

    def valid(self):
        """
        A crew is valid only if there are groups, qualifications and attributes.
        """
        return (self._has_groups and
                self._has_qualifications and
                self._has_attributes)
    
    """
    Support functions
    """
    def _get_group_at_date(self, date):
        """
        Returns the crew group name for a given date as a string. 
        If no group is valid at the date given, None is returned.
        The function requires that the lists of employments, contracts and 
        qualifications are sorted in validfrom date order.
        """
        employments = [i for i in self.crew.employments if i.validfrom <= date and i.validto > date]
        contracts = [i for i in self.crew.contracts if i.validfrom <= date and i.validto > date]
        qualifications = [i for i in self.crew.qualifications if i.validfrom <= date and i.validto > date] + [{'name': 'CONTRACTVG', 
                                                                                                               'start': i.validfrom,
                                                                                                               'end': i.validto} for i in self.crew.contracts if i.validfrom <= date and i.validto > date and i.contracttype == 'VG']
        
        if employments and contracts and qualifications:
            maincat = employments[0].maincat
            region = employments[0].region
            base = employments[0].base
            contracttype = contracts[0].contracttype
            temp = contracts[0].temp
            
            if maincat == 'F':           
                if region in ['SKD', 'SKN', 'SKS']:
                    return 'FD SH ' + region + ' ' +  contracttype
                elif region == 'SVS' and base == 'BGO':
                    return 'FD SH SKN ' + contracttype
                elif region == 'SVS' and base == 'CPH':
                    return 'FD SH SKD ' + contracttype
                else:
                    return 'FD LH'                    
            else:
                if region in ['SKD', 'SKN', 'SKS']:
                    if temp:
                        return 'CC RP'
                    else:
                        return 'CC' + ' ' + region + ' ' + contracttype
        return None
    
    def _merge_adjacent_items(self, lst, key):
        """
        Returns a list where adjacent values of 'key' are merged if they overlap in time.  
        """
        merged_lst = []
        if lst:
            merged_lst.append(lst[0])
            for item in lst[1:]:
                if item[key] == merged_lst[-1][key] and item['start'] <= merged_lst[-1]['end']:
                    merged_lst[-1]['end'] = max(merged_lst[-1]['end'], item['end'])
                else:
                    merged_lst.append(item)
        return merged_lst
    
    def _xml_datetime(self, attribute):
        """
        Converts the time keys 'start' and 'end' of an XML attribute to the 
        time format 'YYYY-MM-DD hh:mm'. 
        One minute is subtracted from 'end' if hh:mm = 00:00. 
        """
        if 'start' in attribute:
            attribute['start'] = _date_time(AbsTime(attribute['start']))       
        if 'end' in attribute:
            attribute['end'] = _date_time(AbsTime(attribute['end']), True)
        return attribute
    
# Functions =============================================================={{{1

# _date_time --------------------------------------------{{{2
def _date_time(abstime, lex24=False):
    """
    Converts an AbsTime to format 'YYYY-MM-DD hh:mm'
    """
    (year, month, day, hour, minute) = abstime.split()
       
    if lex24 and hour == 0 and minute == 0:
        t = abstime - RelTime(0, 1)
        (year, month, day) = t.split()[:3]
        hour = 23
        minute = 59

    return "%04d-%02d-%02d %02d:%02d" % (year, month, day, hour, minute)

# generate_crew_data_document --------------------------------------------{{{2
def generate_crew_data_document(dbconn, time, logger,):
    """
    Retunrs a crew data XML document as a string.
    """
    return CrewDataDocument(dbconn, time, logger)

# main -------------------------------------------------------------------{{{2
def main(argv):
    """
    ExportCrewData -c connect_string -s schema [-o output_file]
        [-v] [-h]
        [-n mqserver -p mqport -k mqchannel -m mqmanager -q mqqueue [-a mqaltuser]]

    usage:
        -c  connect_string
        --connect connect_string
            Use this connect string to connect to database.

        -s  schema
        --schema schema
            Use this schema.

        -o  output_file
        --output output_file
            Print output to this file. (If no filename given the result
            will be printed to stdout).

        --crewportal-ds
            Print output to default Crew Portal datasource directory.

        -n  mqhost
        --mqhost mqhost

        -p  mqport
        --mqport mqport

        -k  mqchannel
        --mqchannel mqchannel

        -m  mq queue manager
        --mqmanager mqmanager

        -q  queue
        --mqqueue queue
            MQ output queue (overrides option -o)

        -a altuser
        --mqaltuser altuser
            Alternate MQ user.

        -v
        --verbose
            Print verbose log messages.

        -h
        --help
            This help text.
    """
    options = {}
    try:
        try:
            (opts, args) = getopt.getopt(argv, "a:c:ho:s:vn:p:k:m:q:",
                [
                    "connect=",
                    "help",
                    "mqaltuser="
                    "mqchannel=",
                    "mqhost=",
                    "mqmanager=",
                    "mqport=",
                    "mqqueue=",
                    "output=",
                    "crewportal-ds",
                    "schema=",
                    "verbose",
                ])
        except getopt.GetoptError, msg:
            raise UsageException(msg)

        for (opt, value) in opts:
            if opt in ('-h', '--help'):
                print __doc__
                print main.__doc__
                return 0
            if opt in ('-v', '--verbose'):
                options['verbose'] = True
            elif opt in ('-c', '--connect'):
                options['connect'] = value
            elif opt in ('-o', '--output'):
                options['output'] = value
            elif opt == '--crewportal-ds':
                options['crewportal-ds'] = True
                options['connect'] = os.environ['DATABASE']
                options['schema'] = os.environ['SCHEMA']
            elif opt in ('-s', '--schema'):
                options['schema'] = value
            elif opt in ('-n', '--mqhost'):
                options['mqhost'] = value
            elif opt in ('-p', '--mqport'):
                options['mqport'] = int(value)
            elif opt in ('-k', '--mqchannel'):
                options['mqchannel'] = value
            elif opt in ('-m', '--mqmanager'):
                options['mqmanager'] = value
            elif opt in ('-q', '--mqqueue'):
                options['mqqueue'] = value
            elif opt in ('-a', '--mqaltuser'):
                options['mqaltuser'] = value
            else:
                pass
            
        try:
            connect = options['connect']
            schema = options['schema']
        except:
            raise UsageException("The arguments '-c connect' and '-s schema' are mandatory.")

        # Setup logging.
        logger = logging.getLogger("replication.CrewDataExport")


        # Setup database connection.
        conn = DaveConnector(connect, schema)
        
        # Get current time.
        tnow = datetime.datetime.now()

        if 'mqqueue' in options:
            from carmensystems.dig.jmq import jmq
            logger.info("Output to MQ queue '%s'." % (options['mqqueue']))

            if 'mqport' in options:
                options['mqport'] = int(options['mqport'])

            mqm = jmq.Connection(**dictTranslate(options, {
                'mqhost': 'host',
                'mqport': 'port',
                'mqmanager': 'manager',
                'mqchannel': 'channel',
            }))
            if 'mqaltuser' in options:
                mqq = mqm.openQueue(queueName=options['mqqueue'], altUser=options['mqaltuser'], mode='w')
            else:
                mqq = mqm.openQueue(queueName=options['mqqueue'], mode='w')

            try:
                msg = jmq.Message(content=generate_crew_data_document(conn, tnow, logger))
                mqq.writeMessage(msg)
                mqm.commit()
            except:
                mqm.rollback()
                mqq.close()
                mqm.disconnect()
                raise

            mqq.close()
            mqm.disconnect()

        elif 'output' in options:
            of = open(options['output'], 'w')
            logger.info("Output to file '%s'." % (options['output']))
            print >>of, generate_crew_data_document(conn, tnow, logger)
            of.close()
        elif 'crewportal-ds' in options:
            # Generate in tmp file and move to new to avoid Crew Portal to pick up partly written file
            tmp_file = os.path.join(os.environ['CARMDATA'],
                                    'crewportal',
                                    'datasource',
                                    'import',
                                    'tmp',
                                    'import-%s.xml'%datetime.datetime.now().isoformat())
            of = open(tmp_file, 'wb')
            logger.info("Output to file '%s'." % (tmp_file))
            doc = generate_crew_data_document(conn, tnow, logger)
            of.write(str(doc).decode("iso-8859-15").encode("utf-8"))
            of.close()
            os.chmod(tmp_file, 0666)

            new_file = os.path.join(os.path.dirname(os.path.dirname(tmp_file)),
                                    "new",
                                    os.path.basename(tmp_file))
            os.rename(tmp_file, new_file)
        else:
            logger.info("Output to stdout.")
            print generate_crew_data_document(conn, tnow, logger) 

        logger.info("Finished.")

    except UsageException, err:
        print str(err)
        print "for help use --help"
        return 2
    except SystemExit, err:
        pass
    except Exception, e:
        print str(e)
        raise

    return 0


# main ==================================================================={{{1
if __name__ == '__main__':
    main(sys.argv[1:])


# modeline ==============================================================={{{1
# vim: set fdm=marker fdl=1:
# eof
