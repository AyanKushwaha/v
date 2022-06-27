# changelog {{{2
# [acosta:07/318@14:28] First version.
# }}}

"""
Utility to dump entity or list of entities to a group of XML files.
Creates XSD Schema that can be used for validation.
"""

# entity list ============================================================{{{1
# Change default list of entities here!
default_entities = (
    'account_baseline',
    'account_entry',
    'account_set',
    'accumulator_int',
    'ac_qual_map',
    'activity_category',
    'activity_group',
    'activity_group_period',
    'activity_set',
    'activity_set_period',
    'activity_status_set',
    'adhoc_flight',
    'aircraft',
    'aircraft_activity',
    'aircraft_activity_set',
    'aircraft_connection',
    'aircraft_flight_duty',
    'aircraft_position_set',
    'aircraft_type',
    'airport',
    'assignment_attr_set',
    'attr_category_set',
    'bases',
    'bought_days',
    'bought_days_svs',
    'callout_list',
    'cga_crew_group',
    'cga_crew_group_set',
    'ci_exception',
    'ci_frozen',
    'cio_event',
    'cio_status',
    'city',
    'country',
    'country_req_docs',
    'crew',
    'crew_activity',
    'crew_activity_attr',
    'crew_address',
    'crew_attr',
    'crew_attr_set',
    'crew_base_break',
    'crew_base_set',
    'crew_carrier_set',
    'crew_category_set',
    'crew_company_set',
    'crew_contact',
    'crew_contact_set',
    'crew_contact_which',
    'crew_contract',
    'crew_contract_set',
    'crew_contract_valid',
    'crew_document',
    'crew_document_set',
    'crew_employment',
    'crew_extra_info',
    'crew_flight_duty',
    'crew_flight_duty_attr',
    'crew_ground_duty',
    'crew_ground_duty_attr',
    'crew_landing',
    'crew_log_acc',
    'crew_log_acc_mod',
    'crew_log_acc_set',
    'crew_passport',
    'crew_position_set',
    'crew_publish_info',
    'crew_qual_acqual',
    'crew_qual_acqual_set',
    'crew_qualification',
    'crew_qualification_set',
    'crew_rank_set',
    'crew_region_set',
    'crew_rehearsal_rec',
    'crew_rest',
    'crew_restr_acqual_set',
    'crew_restr_acqual',
    'crew_restriction',
    'crew_restriction_set',
    'crew_sen_grp_set',
    'crew_seniority',
    'crew_training_log',
    'crew_training_need',
    'crew_trip',
    'currency_set',
    'dst',
    'dst_rule',
    'exchange_rate',
    'flight_leg',
    'flight_leg_attr',
    'flight_leg_delay',
    'meal_flight_owner',
    'ground_task',
    'ground_task_attr',
    'hotel_booking',
    'leg_attr_set',
    'leg_status_set',
    'meal_opt_out',
    'meal_flight_opt_out',
    'meal_order',
    'meal_order_line',
    'meal_order_update',
    'meal_order_update_line',
    'meal_special_code_set',
    'meal_special_order_line',
    'passive_booking',
    'pattern_acts',
    'pattern_set',
    'per_diem_compensation',
    'per_diem_department',
    'per_diem_tax',
    'published_standbys',
    'rave_paramset_set',
    'rave_string_paramset',
    'rotation',
    'rotation_activity',
    'rotation_flight_duty',
    'rotation_ground_duty',
    'rule_violation_log',
    'salary_admin_code',
    'salary_article',
    'salary_basic_data',
    'salary_convertable_crew',
    'salary_convertable_data',
    'salary_extra_data',
    'salary_region',
    'salary_run_id',
    'sb_activity_details',
    'sb_daily_lengths',
    'sb_daily_needs',
    'spec_local_trans',
    'state',
    'training_last_flown',
    'transport_booking',
    'trip',
    'trip_activity',
    'trip_flight_duty',
    'trip_ground_duty',
)


# imports ================================================================{{{1
import logging
import os
import re
import sys
import utils.xmlutil as xml

from AbsTime import AbsTime
from RelTime import RelTime
from datetime import datetime
from optparse import OptionParser

from carmensystems.dave import baselib
from utils.xmlutil import xsd
from utils.dave import EC
from utils.exception import locator
from utils.selctx import BasicContext
try:
    from utils.rave import RaveIterator
    import carmensystems.rave.api as rave
    from tm import TM
except:
    class RaveIterator:
        pass
    rave = None
    TM = None



# setup logging =========================================================={{{1
console = logging.StreamHandler()
console.setFormatter(logging.Formatter('%(name)s: [%(levelname)-8s]: %(message)s'))
logging.getLogger('').handlers = []
log = logging.getLogger('utils.datadump')
log.addHandler(console)

#NOTE: Control logging by changing this.
log.setLevel(logging.INFO)


# globals ================================================================{{{1
application = 'datadump'
root_name = application
__version__ = '$Revision$'
dtd_file = '%s.dtd' % (application,)

role_map = {
    baselib.ColSpec.CTYPE_NORMAL: 'Normal',
    baselib.ColSpec.CTYPE_KEY: 'Key',
    baselib.ColSpec.CTYPE_REVID: 'Revision ID',
    baselib.ColSpec.CTYPE_DELETED: 'Deleted',
    baselib.ColSpec.CTYPE_BRANCH: 'Branch ID',
    baselib.ColSpec.CTYPE_INTERNAL: 'Internal',
}


# classes ================================================================{{{1

# DutyBlockTimeEntity ----------------------------------------------------{{{2
class DutyBlockTimeCrewEntity(RaveIterator):
    """Iterator class, also contains some constants."""
    entity_name = 'block_time_duty_time'
    comment = "Duty time and block time daily per crew."

    def __init__(self):
        fields = {
            'crew': 'crew.%id%',
        }
        iter = RaveIterator.iter('iterators.roster_set')
        RaveIterator.__init__(self, iter, fields)

# DutyBlockTimeEntity ----------------------------------------------------{{{2
class DutyBlockTimeEntity(RaveIterator):
    """Iterator class, also contains some constants."""
    colnames = (
        ('btdaily', "Block time daily"),
        ('dtsubqdaily', "Duty time daily subpart q"),
        ('dtkdaily', "Duty time daily k agreement"),
        ('dtoma16daily', "Duty time daily oma16"),
    )

    def __init__(self, lastRun):
        self.now, = rave.eval('fundamental.%now%')
        self.days = int(self.now - lastRun) / 1440
        self.startTime, = rave.eval('round_down(fundamental.%%now%% - %s*24:00, 24:00) - 24:00' % self.days)
        self.endTime = self.startTime + RelTime(24, 0)
        bt_dt_date = 'round_down(%s + fundamental.%%py_index%%*24:00, 24:00)'
        bt_in_period = 'accumulators.%%block_time_in_period_excluding_bought_days%%(%s + fundamental.%%py_index%%*24:00, %s + fundamental.%%py_index%%*24:00)'
        dt_in_period_k_agreement = 'accumulators.%%duty_time_in_period%%(%s + fundamental.%%py_index%%*24:00, %s + fundamental.%%py_index%%*24:00)'
        dt_in_period_supbart_q = 'accumulators.%%subq_duty_time_in_period%%(%s + fundamental.%%py_index%%*24:00, %s + fundamental.%%py_index%%*24:00)'
        dt_in_period_oma16 = 'accumulators.%%duty_time_in_interval%%(%s + fundamental.%%py_index%%*24:00, %s + fundamental.%%py_index%%*24:00)'
        fields = {
            'date': bt_dt_date % (self.startTime),
            'btdaily': bt_in_period % (self.startTime, self.endTime),
            'dtsubqdaily': dt_in_period_k_agreement % (self.startTime, self.endTime),
            'dtkdaily': dt_in_period_supbart_q % (self.startTime, self.endTime),
            'dtoma16daily': dt_in_period_oma16 % (self.startTime, self.endTime),
        }
        iter = RaveIterator.times(self.days)
        RaveIterator.__init__(self, iter, fields)


# Type conversions -------------------------------------------------------{{{2
class types_(tuple):
    def __new__(cls, *x):
        return tuple.__new__(cls, x)

    def __init__(self, *x):
        self.dave_type, self.conv, self.xml_type = x

    def asXSD(self):
        if self.dave_type == 'daveChar':
            return xsd.simpleType(xsd.restriction(base=self.xml_type, length=1,
                whiteSpace="preserve"), name=self.dave_type)
        else:
            return xsd.simpleType(xsd.restriction(base=self.xml_type), name=self.dave_type)


type_map = {
    baselib.TYPE_INT: types_('daveInt', xml.integer, 'xs:integer'),
    baselib.TYPE_DATE: types_('daveDate', xml.date, 'xs:date'),
    baselib.TYPE_ABSTIME: types_('daveAbsTime', xml.dateTime, 'xs:dateTime'),
    baselib.TYPE_RELTIME: types_('daveRelTime', xml.duration, 'xs:duration'),
    baselib.TYPE_FLOAT: types_('daveFloat', xml.decimal, 'xs:decimal'),
    baselib.TYPE_CHAR: types_('daveChar', xml.char, 'xs:string'),
    baselib.TYPE_BOOL: types_('daveBool', xml.boolean, 'xs:boolean'),
    baselib.TYPE_STRING: types_('daveString', xml.string, 'xs:string'),
    baselib.TYPE_UUID: types_('daveUUID', xml.string, 'xs:string'),
    #baselib.TYPE_INVALID: types_('Invalid', xml.string, 'xs:string'),
}


# Main -------------------------------------------------------------------{{{2
class Main:
    """
    Can be called as:
       main('-i', '-s', schema, '-c', connect)
    or
       run(schema=schema, connect=connect, incremental=True)

    The output dir will contain a file ".cid" which has one line with the CID
    (commitid) that was used the last time, this to be able to run incremental
    dumps. It will also contain a file ".dtbt" whis has one line with the Date 
    of the last run, of dump_bt_dt.
    """
    def __init__(self):
        """Set default values."""
        self.entities = default_entities
        # let it fail if CARMTMP not in env
        self.dir = os.environ['CARMTMP']
        self.ec = None
        self.incremental = False
        self.sync = False
        self.root_name = root_name
        self.schema = None
        # Use dutytime and block time calculations from Rave.
        self.use_bt_dt = True

    def __call__(self, connect, schema, entities=default_entities, branch=None,
            incremental=False, sync=False, dir=None, dtd_only=False, xsd_only=False,
            use_bt_dt=True):
        """For programmatic uses."""
        self.schema = schema
        self.entities = entities
        self.incremental = incremental
        self.sync = sync
        self.use_bt_dt = use_bt_dt

        self.ec = EC(connect, self.schema, branch)

        if not dir is None:
            self.dir = check_dir(dir)

        self.dump_schema()
        if dtd_only:
            self.dump_dtd()
        if not (xsd_only or dtd_only):
            self.dump_tables()

        self.ec.close()

    def main(self, *argv):
        """When called from command line."""
        log.debug("%s(%s)" % (locator(self), argv))
        try:
            if len(argv) == 0:
                argv = sys.argv[1:]
            descr = 'Export a number of entities to XML files and additionally create XML Schema definition.'
            parser = OptionParser(version="%%prog %s" % self.version, description=descr)
            parser.add_option('-b', '--branch',
                    dest='branch',
                    help="Branch id to use.",
                    metavar='branchid')
            parser.add_option('-c', '--connect',
                    dest='connect',
                    help="Connect string to database e.g. 'oracle:user/pass@service'.",
                    metavar='connect')
            parser.add_option('-d', '--dir',
                    dest='dir',
                    help="Output directory.",
                    metavar='dir')
            parser.add_option('-D', '--dtd',
                    dest='dtd_only',
                    action='store_true',
                    default=False,
                    help="Only create DTD, don't dump tables.")
            parser.add_option('-i', '--incremental',
                    dest='incremental',
                    action='store_true',
                    default=False,
                    help="Get only changes since last run (stored in file '.cid').",
                    metavar="CID")
            parser.add_option('-y', '--sync',
                    dest='sync',
                    action='store_true',
                    default=False,
                    help="Get all changes upto last run (stored in file '.cid').",
                    metavar="CID")
            parser.add_option('-s', '--schema',
                    dest='schema',
                    help="Database schema to use",
                    metavar='schema')
            parser.add_option('-u', '--use-bt-dt',
                    dest='use_bt_dt',
                    action='store_false',
                    default=True,
                    help="Don't create XSD for entity block_time_duty_time. Default is to use this option.")
            parser.add_option('-x', '--xsd',
                    dest='xsd_only',
                    action='store_true',
                    default=False,
                    help="Only create W3C XSD schema, don't dump tables. Default is to dump tables AND create schema definition file.")
            (opts, args) = parser.parse_args(list(argv))
            log.debug("... (opts, args) = (%s, %s)" % (opts, args))

            if opts.connect is None or opts.schema is None:
                parser.error("Must give connection options 'connect' and 'schema'.")

            if args:
                entities = args
            else:
                entities = default_entities

            self(opts.connect, opts.schema, entities=entities,
                    branch=opts.branch, incremental=opts.incremental,
                    dir=opts.dir, dtd_only=opts.dtd_only,
                    xsd_only=opts.xsd_only, use_bt_dt=opts.use_bt_dt)

        except SystemExit, e:
            log.debug("Finished: %s" % str(e))
        except Exception, e:
            log.error("%s: Exception: %s" % (locator(self), e))
            raise

    def colspec2xsd(self, e, cs):
        """Convert ColSpec to XSD."""
        col_name = cs.getName()
        element = xsd.element(name=col_name)
        if not cs.isRequired():
            element['minOccurs'] = 0
        element['type'] = type_map[cs.getApiType()].dave_type
        return element

    def dump_dtd(self):
        """Create DTD, this is optional."""
        filename = os.path.join(self.dir, dtd_file)
        output = open(filename, "w")
        efmt = '<!ELEMENT %s (%s)>'
        print >>output, xml.COMMENT(self.get_comment())
        print >>output, efmt % ('datadump', 'columns,records')
        print >>output, '\n'.join((
            '<!ATTLIST datadump entity CDATA #REQUIRED>',
            '<!ATTLIST datadump timestamp CDATA #REQUIRED>',
            '<!ATTLIST datadump type (full|incremental) #REQUIRED>',
            '<!ATTLIST datadump minCID CDATA #REQUIRED>',
            '<!ATTLIST datadump maxCID CDATA #REQUIRED>',
            '<!ATTLIST datadump schema CDATA #REQUIRED>',
        ))
        entity_columns = {}
        columns = set()
        for e in self.entities:
            entity_columns[e] = []
            for colname, required in ((x.getName(), x.isRequired()) for x in self.get_cslist(e)):
                entity_columns[e].append(colname + ("?", "")[required])
                columns.add(colname)
        if self.use_bt_dt:
            e = DutyBlockTimeCrewEntity.entity_name
            entity_columns[e] = []
            entity_columns[e].append('crew')
            entity_columns[e].append('date' + "?")
            for colname, _ in DutyBlockTimeCrewEntity.colnames:
                entity_columns[e].append(colname + "?")
                columns.add(colname)
        print >>output, efmt % ('columns', 'column+')
        print >>output, '\n'.join((
            '<!ELEMENT column EMPTY>',
            '<!ATTLIST column name CDATA #REQUIRED>',
            '<!ATTLIST column type CDATA #REQUIRED>',
            '<!ATTLIST column isRequired CDATA #REQUIRED>',
            '<!ATTLIST column foreignEntity CDATA #IMPLIED>',
            '<!ATTLIST column foreignColumn CDATA #IMPLIED>',
            '<!ATTLIST column desc CDATA #IMPLIED>',
        ))
        print >>output, efmt % ('records', '|'.join(['%s+' % x for x in sorted(self.entities)]))
        for table in sorted(entity_columns):
            print >>output, efmt % (table, ','.join(entity_columns[table]))
            print >>output, '<!ATTLIST %s deleted CDATA #IMPLIED>' % table
        for col in sorted(columns):
            print >>output, efmt % (col, '#PCDATA')
        output.close()
        log.info("DTD was written to '%s'" % (filename,))

    def dump_entity_schema(self, e, bt_dt=False):
        """Create XSD schema, this will always be created."""
        xsd_schema = xsd.schema()
        xsd_root = xsd.element(name=self.root_name)
        xsd_schema.append(xsd_root)

        cols_and_records = xsd.sequence()
        defs_and_attrs = xsd.complexType(cols_and_records)
        defs_and_attrs.append(xsd.attribute(use="required", name="entity", type="xs:string"))
        defs_and_attrs.append(xsd.attribute(use="required", name="timestamp", type="xs:dateTime"))
        defs_and_attrs.append(xsd.attribute(
                xsd.simpleType(
                    xsd.restriction(enumeration=("full", "incremental"), base="xs:string")),
            use="required", name="type"))
        defs_and_attrs.append(xsd.attribute(name="minCID", type="xs:integer"))
        defs_and_attrs.append(xsd.attribute(name="maxCID", type="xs:integer"))
        defs_and_attrs.append(xsd.attribute(name="schema", type="xs:string"))
        xsd_root.append(defs_and_attrs)

        xsd_columns = xsd.element(xsd.complexType(xsd.sequence(self.xsd_column())))
        xsd_columns['name'] = 'columns'
        cols_and_records.append(xsd_columns)

        rec_types = xsd.choice(minOccurs="0")
        xsd_records = xsd.element(xsd.complexType(rec_types))
        xsd_records['name'] = 'records'
        cols_and_records.append(xsd_records)

        if bt_dt:
            # Add entity to entity_list (in root def)
            rec_types.append(xsd.element(name=e, type=e, maxOccurs="unbounded"))
            xsd_schema.append(xsd_bt_dt())
        else:
            es = self.ec.getEntitySpec(e)
            # Add entity to entity_list (in root def)
            rec_types.append(xsd.element(name=e, type=e, maxOccurs="unbounded"))

            # Create Entity definition
            entity_def = xsd.complexType(name=e)
            entity_def.append(self.get_entity_desc(e))
            entity_def.append(self.xsd_record(e))
            entity_def.append(xsd.attribute(name="deleted", type="xs:boolean"))
            xsd_schema.append(entity_def)

        # Add mappings from Dave types to XML Schema types
        for type_ in [type_map[x].asXSD() for x in type_map]:
            xsd_schema.append(type_)

        schema_file = '%s.xsd' % (e,)
        filename = os.path.join(self.dir, schema_file)
        output = open(filename, "w")
        print >>output, str(xml.XMLDocument(xml.COMMENT(self.get_comment()), xsd_schema))
        output.close()
        log.info("Schema definition was written to file '%s'." % (filename,))

    def dump_schema(self):
        """Create XSD schema, this will always be created."""
        for e in self.entities:
            self.dump_entity_schema(e)

        if self.use_bt_dt:
            self.dump_entity_schema(DutyBlockTimeCrewEntity.entity_name, bt_dt=True)

    def dump_tables(self):
        """Export whole set of tables."""
        start_cid = 0
        end_cid = self.ec.cid
        if self.sync:
            try:
                cidfile = self.get_cidfile()
                for line in cidfile:
                    end_cid = int(line)
                    break
                cidfile.close()
                log.debug("First CID will be '%d', last CID will be '%d'." % (start_cid, end_cid))
                self.ec._rev_filter(maxcid=end_cid, mincid=start_cid, with_deleted=True)
            except:
                log.info("No last commitid recorded, will revert to full dump.")
                self.ec._rev_filter(maxcid=end_cid, mincid=start_cid)
        elif self.incremental:
            try:
                cidfile = self.get_cidfile()
                for line in cidfile:
                    start_cid = int(line)
                    break
                cidfile.close()
                log.debug("First CID will be '%d', last CID will be '%d'." % (start_cid, end_cid))
                self.ec._rev_filter(maxcid=end_cid, mincid=start_cid, with_deleted=True)
            except:
                log.info("No last commitid recorded, will revert to full dump.")
                self.ec._rev_filter(maxcid=end_cid, mincid=start_cid)
        else:
            log.debug("Last CID will be '%d'." % (end_cid))
            self.ec._rev_filter(maxcid=end_cid, mincid=start_cid)
        log.info("Starting to export tables...")
        for e in self.entities:
            self.dump_table(e, start_cid, end_cid)
        log.info("Finished exporting tables.")
        if not self.sync:
            cidfile = self.get_cidfile("w")
            print >>cidfile, end_cid
            cidfile.close()

    def dump_table(self, e, start_cid, end_cid):
        """Export one entity (table), argument start_cid, and end_cid are only
        for information. The values are already set."""
        filename = os.path.join(self.dir, "%s.xml" % (e,))
        output = open(filename, "w")
        print >>output, str(xml.XMLDocument(xml.COMMENT(self.get_comment()), encoding="iso-8859-1"))
        print >>output, '<%s entity="%s" timestamp="%s" type="%s" minCID="%s" maxCID="%s" schema="%s">' % (
            self.root_name,
            e,
            self.now, 
            ('full', 'incremental')[self.incremental], 
            start_cid,
            end_cid,
            self.schema
        )
        cslist = self.get_cslist(e)
        print >>output, str(self.xml_columns(e, cslist))
        print >>output, "<records>"
        for r in getattr(self.ec, e):
            xml_record = xml.XMLElement(e)
            if r.deleted == "Y":
                xml_record['deleted'] = 'true'
            for cs in cslist:
                val = self.encode_record(r, cs)
                if not val is None:
                    xml_record.append(val)
            print >>output, str(xml_record)
        print >>output, "</records>"
        print >>output, "</%s>" % (self.root_name,)
        log.info("Entity '%s' exported to file '%s'." % (e, filename))

    def dumper(self, e):
        """For basic tests."""
        es = self.ec.getEntitySpec(e)
        print "---"
        print "entity:", e
        for i in xrange(es.getColumnCount()):
            cs = es.getColumnByNum(i)
            name = cs.getName()
            print " - name       :", name
            print "   alias      :", cs.getAlias()
            print "   size       :", cs.getSize()
            print "   role       :", cs.getRole(), role_map[cs.getRole()]
            print "   isActive   :", cs.isActive()
            print "   isRequired :", cs.isRequired()
            print "   ApiType    :", cs.getApiType(), type_map[cs.getApiType()].dave_type
            print "   DBType     :", cs.getDBType()
            print "   public     :", cs.publicCol()
            print "   fallback   :", cs.getFallbackExpression()
            if name in fkeys:
                print "   reference  :", fkeys[name]
            for k, v in self.get_colattrs(e, name).iteritems():
                print "  %-11s:" % (k,), v

    def encode_record(self, rec, cs):
        """Encode field value."""
        name = cs.getName()
        value = getattr(rec, name)
        if value is None:
            return None
        else:
            return type_map[cs.getApiType()].conv(name, value)

    def get_cidfile(self, mode="r"):
        """Get file that stores latest CID."""
        return open(os.path.join(self.dir, ".cid"), mode)

    def get_colattrs(self, e, name):
        """Return mapping with attribute names/values."""
        s = {}
        self.ec.selectAttribConfig(e, name)
        x = self.ec.readConfig()
        while x:
            # entity, name, type, group, attr, value
            attr, value = x.valuesAsList()[4:6]
            s[attr] = value
            x = self.ec.readConfig()
        return s

    def get_comment(self):
        return """Created by %s (rev %s) at %s for schema %s.""" % (
                application, self.version, self.now, self.schema)

    def get_cslist(self, e):
        """Return list of ColSpec objects for public columns."""
        C = []
        es = self.ec.getEntitySpec(e)
        for i in xrange(es.getColumnCount()):
            cs = es.getColumnByNum(i)
            if cs.publicCol():
                C.append(cs)
        return C

    def get_entity_desc(self, e):
        """Return XSD annotation for an entity."""
        desc = None
        self.ec.selectEntityConfig(e)
        x = self.ec.readConfig()
        while x:
            # entity, cfgType, cfgGroup, cfgName, cfgValue
            name, value = x.valuesAsList()[3:5]
            if name == 'desc':
                desc = value
                break
            x = self.ec.readConfig()
        return xsd.annotation(xsd.documentation(desc))

    def get_foreign_keys(self, e):
        """Return mapping columnname -> (foreign entity, foreign column)."""
        fks = {}
        self.ec.listForeignKeys(e)
        x = self.ec.readConfig()
        while x:
            fkName, tgtEntityName, srcColumnList, tgtColumnList, entity = x.valuesAsList()
            src_cols = srcColumnList.split(',')
            tgt_cols = tgtColumnList.split(',')
            for i in xrange(len(src_cols)):
                fks[src_cols[i]] = (tgtEntityName, tgt_cols[i])
            x = self.ec.readConfig()
        return fks

    def get_version(self):
        """Get version of this module."""
        log.debug("%s()" % (locator(self),))
        regexp = re.compile('\$' + 'Revision: (.*)' + '\$$')
        m = regexp.match(__version__)
        if m:
            return m.groups(0)
        else:
            return "0.0"
    version = property(get_version)

    @property
    def now(self):
        """Return current time in ISO format."""
        return datetime.now().isoformat()

    def xml_columns(self, e, cslist):
        """Return XML columns element."""
        columns = xml.XMLElement('columns')
        fkeys = self.get_foreign_keys(e)
        for cs in cslist:
            x = xml.XMLElement('column')
            name = cs.getName()
            x['name'] = name
            x['type'] = type_map[cs.getApiType()].dave_type
            x['isRequired'] = xsd.boolean(cs.isRequired())
            if name in fkeys:
                x['foreignEntity'], x['foreignColumn'] = fkeys[name]
            colattrs = self.get_colattrs(e, name)
            if 'desc' in colattrs:
                x['desc'] = colattrs['desc']
            columns.append(x)
        return columns

    def xsd_column(self):
        """Return Schema definition of column attributes."""
        ct = xsd.complexType()
        ct.append(xsd.attribute(name='name', type='xs:string', use='required'))
        ct.append(xsd.attribute(name='type', type='xs:string', use='required'))
        ct.append(xsd.attribute(name='isRequired', type='xs:boolean', use='required'))
        ct.append(xsd.attribute(name='foreignEntity', type='xs:string'))
        ct.append(xsd.attribute(name='foreignColumn', type='xs:string'))
        ct.append(xsd.attribute(name='desc', type='xs:string'))
        return xsd.element(ct, name='column', maxOccurs='unbounded')

    def xsd_record(self, e):
        """Return Schema definition of record contents."""
        columns = xsd.sequence()
        for cs in self.get_cslist(e):
            columns.append(self.colspec2xsd(e, cs))
        return columns


# functions =============================================================={{{1

# run --------------------------------------------------------------------{{{2
# import utils.datadump
# schema = 'sk_acosta_98'
# connect = 'oracle:%s/%s@testnet-s4:1521/gtn01tst' % (schema, schema)
# utils.datadump.run(connect, schema, ['salary_basic_data'], incremental=True)
run = Main()


# main -------------------------------------------------------------------{{{2
# When called inside this module (for command line parsing.)
main = run.main

# get_dtbtfile --------------------------------------------------------------{{{2
def get_dtbtfile(dir, mode="r"):
    """Get file that stores latest run of DutyTime BlockTime."""
    return open(os.path.join(dir, ".dtbt"), mode)

# get_dtbt_lastrun --------------------------------------------------------------{{{2
def get_dtbt_lastrun(dir):
    """Get latest run of DutyTime BlockTime."""
    try:
        dtbt_file = get_dtbtfile(dir)
        for line in dtbt_file:
            lastRun = AbsTime(line)
            break
        dtbt_file.close()
        log.debug("First date for DutyTime/BlockTime will be '%s'." % (lastRun))
        return lastRun
    except:
        log.info("No last run recorded for DutyTime/BlockTime, will revert to dump yesterday.")
        return AbsTime(str(datetime.now().date()).replace('-','')).adddays(-1)

# set_dtbt_lastrun --------------------------------------------------------------{{{2
def set_dtbt_lastrun(dir):
    """Set latest run of DutyTime BlockTime."""
    dtbt_file = get_dtbtfile(dir, "w")
    print >>dtbt_file, str(datetime.now().date()).replace('-','')
    dtbt_file.close()

# check_dir --------------------------------------------------------------{{{2
def check_dir(dir, mode=0775):
    """Try to create output directory if not already there."""
    if not os.path.exists(dir):
        os.makedirs(dir, mode)
        log.info("Created directory '%s'." % (dir,))
    return dir


# dump_bt_dt -------------------------------------------------------------{{{2
def dump_bt_dt(dir=os.environ['CARMTMP']):
    """Export the Dutytime Blocktime "entity" as XML."""
    dir = check_dir(dir)
    filename = os.path.join(dir, "%s.xml" % (DutyBlockTimeCrewEntity.entity_name,))
    output = open(filename, "w")

    dbtce = DutyBlockTimeCrewEntity()
    dbte = DutyBlockTimeEntity(get_dtbt_lastrun(dir))
    dbtce.link(vals=dbte)

    e = dbtce.entity_name
    bc = BasicContext()

    print >>output, str(xml.XMLDocument(xml.COMMENT(DutyBlockTimeCrewEntity.comment), encoding="iso-8859-1"))
    print >>output, '<%s entity="%s" timestamp="%s" type="%s" minCID="%s" maxCID="%s" schema="%s">' % (
        root_name,
        e,
        dbte.now, 
        'full',
        0,
        0,
        TM.getSchemaStr()
    )

    columns = xml.XMLElement('columns')
    columns.append(xml.XMLElement('column', name='crew', type='daveString',
            isRequired='true', desc="Crew ID"))
    columns.append(xml.XMLElement('column', name='date', type='daveAbsTime',
            isRequired='false', desc="Date"))
    for c, desc in dbte.colnames:
        columns.append(xml.XMLElement('column', name=c, type='daveRelTime',
                isRequired='false', desc=desc))
    print >>output, str(columns)
    print >>output, "<records>"
    for crew in dbtce.eval(bc.getGenericContext()):
        for r in crew.chain('vals'):
            xml_record = xml.XMLElement(e)
            xml_record.append(xml.string('crew', crew.crew))
            xml_record.append(xml.dateTime('date', getattr(r, 'date')))
            for col, _ in dbte.colnames:
                val = getattr(r, col)
                if not val is None:
                    xml_record.append(xml.duration(col, val))
            print >>output, str(xml_record)
    print >>output, "</records>"
    print >>output, "</%s>" % (root_name,)
    log.info("Entity '%s' exported to file '%s'." % (e, filename))
    set_dtbt_lastrun(dir)


# xsd_bt_dt --------------------------------------------------------------{{{2
def xsd_bt_dt():
    """Create schema definition for the dutytime / blocktime "entity"."""
    edef = xsd.complexType(name=DutyBlockTimeCrewEntity.entity_name)
    edef.append(xsd.annotation(xsd.documentation(DutyBlockTimeCrewEntity.comment)))
    columns = xsd.sequence()
    columns.append(xsd.element(name="crew", type="daveString"))
    columns.append(xsd.element(name="date", type="daveAbsTime"))
    for x, desc in DutyBlockTimeEntity.colnames:
        columns.append(xsd.element(name=x, minOccurs=0, type="daveRelTime"))
    edef.append(columns)
    return edef
    

# __main__ ==============================================================={{{1
if __name__ == '__main__':
    #log.setLevel(logging.DEBUG)
    #schema = 'sk_acosta_98'
    #conn = "oracle:%s/%s@testnet-s4:1521/gtn01tst" % (schema, schema)
    #main(*(['--schema', schema, '--connect', conn] + sys.argv[1:]))
    main()


# Usage examples ========================================================={{{1
### First create XSD (schema definition) and dump all defined database tables.
# import utils.datadump
# utils.datadump.run(schema="sk_cms_he_bz26529",
#     connect="oracle:sk_cms_he_bz26529/sk_cms_he_bz26529@flm:1521/gpd01dev",
#     dir="/tmp/datadump")

### Then get the dutytime and blocktime values as XML
# utils.datadump.dump_bt_dt(dir="/tmp/datadump")

### Or from report server.
# import report_sources.report_server.rs_bt_dt_stat
# report_sources.report_server.rs_bt_dt_stat.generate()


# modeline ==============================================================={{{1
# vim: set fdm=marker:
# eof
