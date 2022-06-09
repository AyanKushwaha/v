import sys, os
from carmensystems.dig.framework.dave import DaveSearch, DaveMultiSearch, DaveConnector, DaveStorer, createOp as _createop
from AbsTime import AbsTime
from datetime import datetime
import subprocess
import re
import tempfile
import fileinput

__C = None
def _C():
    from utils import ServiceConfig
    global __C
    if __C == None: __C = ServiceConfig.ServiceConfig()
    return __C
    
def _sqlparse():
    try:
        import sqlparse
    except ImportError:
        contrib = os.path.expandvars("$CARMUSR/lib/python/contrib")
        if os.path.isdir(contrib) and not contrib in sys.path:
            sys.path.append(contrib)
        try:
            import sqlparse
        except ImportError:
            print >>sys.stderr, "sqlparse not found"
            sys.exit(1)
    return sqlparse

def _config(useAdm=True, includeOracle=True, history=False):
    connect_env_var = "DB%s_URL%s" % ("_ADM" if useAdm else "",
                                      "_HISTORY" if history else "")
    schema_env_var = "DB_SCHEMA%s" % ("_HISTORY" if history else "")
    connect = os.environ[connect_env_var]
    schema = os.environ[schema_env_var]

    if not includeOracle and connect.startswith("oracle:"):
        connect = connect[len("oracle:"):]
    if '%' in connect+schema:
        print >>sys.stderr, "Database configuration not correct"
        print >>sys.stderr, "  Connect:",connect
        print >>sys.stderr, "  Schema:",schema
        sys.exit(1) 
    return connect, schema

_dc = None
_dca = None
_ec = None
_eca = None
def _getdaveconnector(useAdm):
    global _dc, _dca
    c,s = _config(useAdm)
    if useAdm:
        if not _dca: _dca = DaveConnector("%s" % c, s)
        return _dca
    else:
        if not _dc: _dc = DaveConnector("%s" % c, s)
        return _dc


def _getentityconnection(schema=None, connect=None, useAdm=True):
    try:
        import carmensystems.dave.dmf as dmf
    except ImportError:
        raise RuntimeError("DAVE not available. CARMSYS = %s" % os.environ.get("CARMSYS", "not set"))

    global _ec, _eca
    connect, schema = _config(useAdm)
    if useAdm:
        if not _eca:
            _eca = dmf.EntityConnection()
            _eca.open('%s'%connect, schema)
        return _eca
    else:
        if not _ec:
            _ec = dmf.EntityConnection()
            _ec.open('%s'%connect, schema)
        return _ec

    
def _dbsearch(entity, expr=[], entity2=None, expr2=[], withDeleted=False,useAdm=False):
    if isinstance(expr, str):
        expr = [expr]
    if isinstance(expr2, str):
        expr = [expr2]
    dc = _getdaveconnector(useAdm)
    if entity2:
        return dict(dc.runSearch(DaveMultiSearch([DaveSearch(entity, expr, withDeleted), DaveSearch(entity2, expr2, withDeleted)])))
    else:
        return list(dc.runSearch(DaveSearch(entity, expr, withDeleted)))
def _dbexec(query,useAdm=False):
    dc = _getdaveconnector(useAdm)
    conn = dc.getL1Connection()
    conn.begin()
    conn.rexec(query, None)
    conn.commit()

def _dbsql(query,useAdm=False):
    dc = _getdaveconnector(useAdm)
    query = str(query)
    conn = dc.getL1Connection()
    conn.rquery(query, None)
    rv = []
    while True:
        a = conn.readRow()
        if a == None: break
        rv.append(a.valuesAsList())
    conn.endQuery()
    return rv
    
def url():
    "Prints the URL and schema for the current database configuration"
    print "URL:",os.environ.get("DB_URL", "(not set)")
    print "Schema:",os.environ.get("DB_SCHEMA", "(not set)")
    print "Adm. URL:",os.environ.get("DB_ADM_URL", "(not set)")
    
schema = url

def _updateschema(logdir, doit, history):
    connect, schema = _config(useAdm=False, includeOracle=False, history=history)
    if not schema:
        print "\n### No %s schema specified in DB configuration file - migration skipped\n" %\
              ("history" if history else "live")
        return

    print "\n### Update %s schema: %s" % ("history" if history else "live", schema)
    sys.stdout.flush()
    logdir = "%s/%s" % (logdir, schema)

    ###########################################################################
    # Defining functions
    def generate_sqls():
        """ Runs dave_model_migrator"""

        # The list below contains modules for both CMS and JMP.
        # The JMP list should be kept in sync with the list in etc/datamodel.xml in the JMP Carmusr.
        model_dirs = (
            "$CARMUSR/current_carmsys_cct/data/config/models/udm_admin2,"
            "$CARMUSR/current_carmsys_cct/data/config/models/udm_air1,"
            "$CARMUSR_JMP/data/config/models,"
            "$CARMUSR/data/config/models,"
            "$CARMUSR_JMP/current_carmsys/data/config/models/udmAirManpower"
            )

        model_lst_files = (
            "$CARMUSR/current_carmsys_cct/data/config/models/udm_air1/udm.air1-complete.lst,"
            "$CARMUSR_JMP/current_carmsys/data/config/models/udmAirManpower/master/udmair_manpower.lst,"
            "$CARMUSR_JMP/data/config/models/sas_manpower_db_model_extensions.lst,"
            "$CARMUSR/data/config/models/db.lst"
            )


        # Note: Support for migrating data is not implemented. Implement if/when needed.
        # See dave_model_migrator documentation regarding the option --data-config-file=FILE
        cmd = os.path.expandvars(
            "$CARMRUNNER dave_model_migrator -c oracle:%s -s %s -u sqlplus -d %s -f %s -o %s" %
            (connect, schema, model_dirs, model_lst_files, logdir))
        print "\nExecuting %s\n" % cmd
        sys.stdout.flush()
        error_code = os.system(cmd)
        if error_code != 0:
            raise RuntimeError("ERROR: Running dave_model_migrator failed. Aborting.\n")

    def set_tablespace_on_created_indexes():
        """
        Modifies migrate.sql to create indexes in tablespace FLM_BIG_IDX. Otherwise they are put in
        the default tablespace which we do not want as it would fill up the storage.
        It turns lines like:
            CREATE INDEX indexname ON tablename ( columname );
            CREATE UNIQUE INDEX indexname ON tablename ( columname );
        into
            CREATE INDEX indexname ON tablename ( columname ) TABLESPACE FLM_BIG_IDX;
            CREATE UNIQUE INDEX indexname ON tablename ( columname ) TABLESPACE FLM_BIG_IDX;
        and lines like:
            CREATE TABLE tablename (
                ...
                CONSTRAINT tablename_pk PRIMARY_KEY (...));
        into
            CREATE TABLE tablename (
                ...
                CONSTRAINT tablename_pk PRIMARY_KEY (...) USING INDEX TABLESPACE FLM_BIG_IDX);
        and lines like:
            ALTER TABLE tablename[!_tmp] ADD CONSTRAINT tablename_pk PRIMARY KEY (...);
        into:
            ALTER TABLE tablename[!_tmp] ADD CONSTRAINT tablename_pk PRIMARY KEY (...) USING INDEX TABLESPACE FLM_BIG_IDX;
        """
        re_index = re.compile(r'(^CREATE (UNIQUE)*.*INDEX.*);$', re.IGNORECASE)
        re_create_constraint = re.compile(r'(^\s*CONSTRAINT .* PRIMARY KEY \(.*\))(\).*)', re.IGNORECASE)
        re_add_constraint = re.compile(r'(^ALTER TABLE .*(?<!_tmp) ADD CONSTRAINT .* PRIMARY KEY \(.*\));$', re.IGNORECASE)
        re_create_table = re.compile(r'^CREATE TABLE.*', re.IGNORECASE)
        creating_table = False
        for line in fileinput.input("%s/migrate.sql" % logdir, inplace=1):
            # Rewrite all lines and make necessary changes
            if creating_table:
                # Only set tablespace for constraints on main tables, not "global temporary" tables
                line = re.sub(re_create_constraint, r'\1 USING INDEX TABLESPACE FLM_BIG_IDX\2', line)
                if ';' in line:
                    creating_table = False
            elif re.match(re_create_table, line):
                creating_table = True
            else:
                line = re.sub(re_add_constraint, r'\1 USING INDEX TABLESPACE FLM_BIG_IDX;', line)
                line = re.sub(re_index, r'\1 TABLESPACE FLM_BIG_IDX;', line)
            sys.stdout.write(line)  # fileinput directs stdout to the file

    def summary():
        """
        Calculates and prints a summary of the SQL operations.
        This gives a hint for deciding if the update seems reasonable.

        Returns:
            A dict with the op_counts
        """
        operations = set(["CREATE", "DROP", "ALTER", "INSERT", "DELETE", "UPDATE"])
        op_counts = dict()
        for op in operations:
            op_counts[op] = 0
        with open("%s/migrate.sql" % logdir) as fp:
            for line in fp:
                first_word_of_line = line.lstrip().split(' ', 1)[0]
                if first_word_of_line in operations:
                    op_counts[first_word_of_line] += 1
        print "## This migration will perform the following number of operations:"
        for k, v in op_counts.items():
            print "  %s:  \t%s" % (k, v)
        print "## For details review the migrate scripts."
        sys.stdout.flush()
        return op_counts

    def migration_needed(op_counts):
        """
        Checks if migration is needed.

        migrate_dave.sql is only generated if dave needs migration.
        migrate.sql is always generated and always includes an insert and delete operation
        for the migration lock in the dave_metadata_status table. Thus, if there are more than these
        two operations, migration is needed.

        :param op_counts: From summary()
        :return:
            True - Migration is needed
            False - Migration is not needed
        """
        return sum(op_counts.values()) > 2 or os.path.isfile('%s/%s' % (logdir, "migrate_dave.sql"))

    def run_migration_sql(sqlfile, precheck=False):
        """
        Runs the given sql-script if it exists and checks for errors.
        """
        if not os.path.isfile('%s/%s' % (logdir, sqlfile)):
            print "%s not generated, skipping" % sqlfile
            return

        cmd = "echo exit | sqlplus -S -L '%s' @%s/%s" % (connect, logdir, sqlfile)
        print "Executing", cmd
        sys.stdout.flush()
        proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                                stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        errors = []
        error_start_line = 0
        for line in proc.stdout:
            line = line.rstrip()
            if line and not line.startswith("Pre-checking") and not line.startswith("==="):
                if not precheck and line.startswith("ERROR") and error_start_line is 0:
                    # Used to only display lines with relevant error information plus some context
                    error_start_line = max(len(errors) - 5, 0)
                errors.append(line)

        """Prechecks always return 0 so failure is assumed if the output includes
        any unexpected lines. The migrate-scripts have a less predictable output
        but returns an error code on failure."""
        return_code = proc.wait()
        if (precheck and errors) or return_code is not 0:
            print "ERROR: %s failed" % sqlfile
            for line in errors[error_start_line:]:
                print "  %s" % line
            print "Aborting"
            raise RuntimeError("Execution failed. Check ORA error messages")
        else:
            print "%s run successfully" % sqlfile

    ###########################################################################
    # Function main definition
    if not os.path.isdir(logdir):
        os.mkdir(logdir)

    generate_sqls()
    set_tablespace_on_created_indexes()
    run_migration_sql("precheck_dave.sql", precheck=True)
    run_migration_sql("precheck.sql", precheck=True)

    op_counts = summary()
    migration_needed = migration_needed(op_counts)

    if doit:
        run_migration_sql("migrate_dave.sql")
        run_migration_sql("migrate.sql")
        print "### Migration of %s completed" % schema

    return migration_needed


def updateschema(logdir="", doit=""):
    """Updates the existing database schema with changes to the model.
    Practically this is a wrapper around dave_model_migrator.
    Both live and history schema is migrated (if defined in the etc/db/XXX.xml)

    Call like this for a dry run:
        db updateschema
    Or like this to execute the migration
        db updateschema mylogdir doit

    Returns True (1) if migration is needed and False (0) if no migration is needed.
    Note that a migration is always performed when 'doit' is given, even if it wasn't needed
    """
    if logdir:
        if not os.path.isdir(logdir):
            sys.exit("Given logdir is not a directory: %s" % logdir)
    else:
        logdir = tempfile.mkdtemp(prefix="migrate_")

    doit = True if doit == "doit" else False
    if not doit:
        print "### DRY RUN"

    migration_needed = dict()
    migration_needed[_config(history=False)[1]] = _updateschema(logdir=logdir, doit=doit, history=False)
    migration_needed[_config(history=True)[1]] = _updateschema(logdir=logdir, doit=doit, history=True)
    any_migration_needed = any(migration_needed.values())

    if not doit:
        if any_migration_needed:
            print "\n#################################################################################\n" \
                  "### THE FOLLOWING SCHEMA(S) DO NOT MATCH THE DATA MODEL AND NEEDS TO BE UPDATED:"
            for schema_name, migrate in migration_needed.items():
                if migrate:
                    print "###     {}".format(schema_name.upper())
            print "#################################################################################\n"
        else:
            print "\n#################################################################################\n" \
                  "### THE SCHEMA(S) MATCH THE DATA MODEL. NO MIGRATION NEEDED.\n" \
                  "#################################################################################\n"

    print "\n### SQL-scripts can be found in: ", logdir
    if not doit:
        print "### In PROD, ensure you have created a backup of the schemas before migrating in case of errors!\n"\
              "### Review the SQL-scripts. Execute the migration by running:\n"\
              "###   db updateschema <logdir> doit\n" \
              "### Or if needed, edit the files manually and run:\n" \
              "###   echo exit | sqlplus -L ${{DB_URL#\"oracle:\"}} @{0}/migrate_dave.sql\n"\
              "###   echo exit | sqlplus -L ${{DB_URL#\"oracle:\"}} @{0}/migrate.sql\n".format(logdir)

    return any_migration_needed


def describeschema():
    """ Describe the existing database schema """
    model_name = "model_%s" % os.environ['DB_SCHEMA']
    cmd = os.path.expandvars(
        "$CARMRUNNER dave_model_describer -c $DB_ADM_URL -s $DB_SCHEMA -m %s" % model_name)
    print "Executing",cmd
    os.system(cmd)
    print "Generated %s.lst and %s.xml" % (model_name, model_name)

def updatefilters():
    "Updates the filter tables from initial_load/dave_*"
    passwd = os.environ["DB_URL"].split('@')[0].split('/',1)[1]
    cmd = os.path.expandvars("$CARMUSR/bin/db/populateFilterTabs.sh $DB_SCHEMA %s" % passwd)
    print "Executing",cmd
    os.system(cmd)

def flushpool():
    connect, schema = _config(includeOracle=False)
    proc = subprocess.Popen("sqlplus -s '%s'" % connect, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate("alter system flush shared_pool;")
    if not "System altered." in stdout:
        print >>sys.stderr, "ERROR: Failed to flush shared pool:"
        print >>sys.stderr, stdout
        print >>sys.stderr, stderr
        sys.exit(1)
    print >>sys.stderr, "Shared pool flushed"

# Tablestats is no longer used by any scheduled jobs, could potentially be removed
def _tablestats(cmp=False, history=False):
    connect, schema = _config(includeOracle=False, history=history)
    if cmp:
        tables = file(os.path.expandvars("$CARMUSR/etc/analyzetables_cmp")).read().split()
        tables_no_hist = []
    else:
        tables = file(os.path.expandvars("$CARMUSR/etc/analyzetables")).read().split()
        tables_no_hist = file(os.path.expandvars("$CARMUSR/etc/analyzetables_no_histogram")).read().split()
        
    proc = subprocess.Popen("sqlplus -s '%s'" % connect, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    cmd = "exec dbms_stats.gather_table_stats(ownname => '%s',tabname => '%%s',estimate_percent => dbms_stats.auto_sample_size, cascade => TRUE, degree => 6);" % schema
    cmd_nostats = "exec dbms_stats.gather_table_stats(ownname => '%s',tabname => '%%s',estimate_percent => dbms_stats.auto_sample_size,method_opt=> 'FOR ALL COLUMNS SIZE 1',NO_INVALIDATE  => false ,cascade => true, degree => 6);" % schema
    stdout, stderr = proc.communicate('\n'.join([cmd % x for x in tables]))
    
    if not "PL/SQL procedure successfully completed" in stdout:
        print >>sys.stderr, "ERROR: Database operation failed:"
        print >>sys.stderr, stdout
        print >>sys.stderr, stderr
        sys.exit(1)

    print "[%s] Gathered statistics for %d table(s)" % (datetime.now(), len(tables))
    
    if len(tables_no_hist) > 0:
        proc = subprocess.Popen("sqlplus -s '%s'" % connect, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate('\n'.join([cmd % x for x in tables_no_hist]))
        if not "PL/SQL procedure successfully completed" in stdout:
            print >>sys.stderr, "ERROR: Database operation failed:"
            print >>sys.stderr, stdout
            print >>sys.stderr, stderr
            sys.exit(1)
        print "[%s] Gathered no-histogram statistics for %d table(s)" % (datetime.now(), len(tables_no_hist))
    flushpool()

def tablestats(cmp=False):
    _tablestats(cmp=cmp)

def tablestats_history(cmp=False):
    _tablestats(cmp=cmp, history=True)

def _schemastats(history=False, alt_schema=None, alt_connect=None):
    print "[%s] Gathering schema statistics ..." % datetime.now()
    connect = alt_connect or _config(includeOracle=False, history=history)[0] 
    schema = alt_schema or _config(includeOracle=False, history=history)[1]
    print 'connect %s schema %s' % (connect, schema)
    proc = subprocess.Popen("sqlplus -s '%s'" % connect, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate("exec dbms_stats.gather_schema_stats(ownname => '%s',estimate_percent => dbms_stats.auto_sample_size, cascade =>TRUE, degree=>6 );" % schema)
    if not "PL/SQL procedure successfully completed" in stdout:
        print >>sys.stderr, "ERROR: Database operation failed:"
        print >>sys.stderr, stdout
        print >>sys.stderr, stderr
        sys.exit(1)
    print "[%s] Gathered schema statistics" % datetime.now()
    flushpool()

def schemastats(alt_schema=None, alt_connect=None):
    """Use arguments alt_schema and alt_connect to run schemastats on other
    schemas than default set in /etc/db/<ENV>.xml."""
    _schemastats(False, alt_schema, alt_connect)

def schemastats_history():
    _schemastats(history=True)


def truncate():
    "Execute dave_truncate_history"
    cmd = os.path.expandvars('dave_truncate_history -c "$DB_URL" -v -s "$DB_SCHEMA" -g $CARMUSR/etc/programs/dave_truncate_history.xml')
    sys.exit(os.system(cmd))
    
def tables():
    "List all the tables"
    for tab in _dbsql("select table_name from user_tables order by table_name"):
        if tab[0][-4:] != "_TMP": 
            print tab[0].lower()
    
def table(name):
    "Show columns for a specific table"
    match = False
    for tab in _dbsql("select column_name,data_type,CHAR_COL_DECL_LENGTH from user_tab_columns where table_name='%s' order by column_name" % name.upper()):
        if tab[2]:
            print "%-20s%-10s" % (tab[0].lower(), "%s(%d)" % (tab[1], tab[2]))
        else:
            print "%-20s%-10s" % (tab[0].lower(), tab[1])
        match = True
    if not match: print >>sys.stderr, "Table not found"

def updatepubrev():
    "Update the DAVE_PUB_REVISION table"
    import carmensystems.studio.plans.DavePubRevisionManager as PM
    pm = PM.DavePubRevisionManager()
    print "[%s] Updating table DAVE_PUB_REVISION ..." % datetime.now()
    pm.populateDavePubRevTable()

def execsql(sqlstmt, admin=False):
    _dbexec(sqlstmt, admin)

def sql(qry, admin=False, output='txt',headers=True):
    """Evaluates a SQL query using the Dave drivers. Arguments are:
    [--admin=True|False] (default: False)  - whether to use the DB_ADM connection string
    [--output=txt|csv|jira] (default: txt) - output format (jira: suitable for pasting in a JIRA comment)
    """
    def cf(v):
        if v is None:
            return ""
        elif isinstance(v, str):
            return '"%s"' % v
        else:
            return str(v)
    outputs = {'csv':lambda l:','.join(map(cf,l)),
               'txt':lambda l:'\t'.join(map(str,l)),
               'jira':lambda l:'|'+'|'.join(map(str,l))+'|'
              }
    houtputs = outputs.copy()
    houtputs['jira'] = lambda l:'||'+'||'.join(map(str,l))+'||'
    outp = outputs.get(output.lower())
    if not outp:
        print >>sys.stderr, "Invalid output format %s" % output
    for l in _dbsql(qry, admin):
        print outp(l)

def listindexes(status=None):
    query = "select INDEX_NAME, TABLE_NAME, STATUS from user_indexes"
    if status:
        if status[0] == '-':
            query += " where status <> '%s'" % status[1:].upper()
        else:
            query += " where status = '%s'" % status.upper()
    query += " order by TABLE_NAME, INDEX_NAME"
    print "%-30s%-30s%s" % ('Name', 'Table', 'Status')
    print '-' * 79
    for l in _dbsql(query, False):
        print "%-30s%-30s%s" % (l[0], l[1], l[2])


def listdumpfiles(dpumpdir=None):
    """List dumpfiles
    [dpumpdir]- Path to dpumpdir
    """
    dpumpdir = "/carm/proj/oradpump"
    prefix = "dpexp_cms_production"
    postfix = ".dmp"
    if not os.path.isdir(dpumpdir):
        print "No such directory: %s" % dpumpdir
        sys.exit(1)
    for f in os.listdir(dpumpdir):
        if f.startswith(prefix) and f.endswith(postfix):
            print os.path.join(dpumpdir, f)
    
def import_dump(dumpfile, parallel=1, schema=None,dpumpdir=None):
    """Generates commands for importing a dumpfile to a new schema
    dumpfile - Mandatory name of the dumpfile to import
    [parallel] (default: 1) - number of dumpfiles
    [schema] (default: $DB_SCHEMA) - schema name
    [dpumpdir]- Path to dpumpdir   
    """
    schema = schema or os.environ["DB_SCHEMA"]
    schema = schema.upper()    
    host =  _C().getPropertyValue("db/host")
    adm = _C().getPropertyValue("db/adm/schema")
    pwd = _C().getPropertyValue("db/adm/password")
    useAdm = True
    
    print "## Set up envirionment"
    print "ssh %s" % host
    print "cd /u05/oracle/gps01dev"
    print "bash"
    print ". set_gps01dev.ksh"
    
    print "## Connect to oracle"
    print "sqlplus %s/%s" % (adm,pwd)
    
    # Make sure no users are connected
    print "## Drop connected users"
    query = "select sid,serial#,osuser,status from v$session where username = '%s' AND status != 'KILLED'" % schema
    for r in _dbsql(query, useAdm):
        sid = r[0]
        serial = r[1]
        query = "exec sys.kill_session(%s,%s);" % (sid, serial)
        print query
        #_dbexec(query,useAdm)
    
    # Drop schema
    print "## Drop schema"
    query = "drop user %s cascade;" % schema
    print query
    #_dbexec(query,useAdm)
   
    # Exit oracle
    print "exit"
   
    # Do the import
    dumpfile = os.path.basename(dumpfile)
    dumpfile = re.sub(r'UTC_[0-9].', 'UTC_%u', dumpfile) 
    import datetime
    dateStr = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = "%s_%s.log" % (schema.lower(), dateStr)
    
    cmd = "time impdp %s/%s DUMPFILE=%s PARALLEL=%s DIRECTORY=dpump_dir REMAP_SCHEMA=cms_production:%s LOGFILE=%s REMAP_TABLESPACE=\"(FLM_BIG_DATA:flm_data1,FLM_BIG_IDX:flm_data1)\"" \
	% (adm, pwd, dumpfile, parallel, schema,logfile)
    print "## Perform the import"
    print cmd
 
    
    # Change password
    user = schema.lower()
    passwd = schema.lower()
    query = "alter user %s identified by %s;" % (user,passwd)
    print "## Change password"
    print "sqlplus %s/%s" % (adm, pwd)
    print query
    #_db_exec(query,useAdm)
    # Exit sqlplus
    print "exit"
    
    # Exit bash
    print "exit"
    
    #Exit host
    print "exit"
    
    # Fix sequences
    print "## Fix sequences"
    print "db fixseq %s" % schema
    
    print "## Don't forget to run $CARMUSR/data/migration/CMS2_SASXX/runmigration.sh"
    
    

def fixindexes():
    "Rebuild the indexes"
    indexes = set()
    for l in _dbsql("select INDEX_NAME from user_indexes where STATUS = 'UNUSABLE'"):
        indexes.add(l[0])
    print "Will fix %d indices" % len(indexes)
    for l in indexes:
        print "  Fixing", l
        _dbexec("ALTER INDEX %s REBUILD" % l)

def listconnectedusers():
    "List the current active sessions"
    schema = _C().getPropertyValue("db/schema")
    query = "select OSUSER, MACHINE from v$session where username='%s' and status='ACTIVE' order by OSUSER, MACHINE" % schema.upper().__str__()
    print "Listing users connected to %s:" % schema
    users =  _dbsql(query,useAdm=True)
    if not users:
        print " No users are currently connected to the database"
    else:
        distinct_users = set()
        for u in users:
            print " %s (from host: %s)" % (u[0], u[1])
            distinct_users.add((u[0], u[1]))
        print "%d users are currently connected (%d distinct)" % (len(users), len(distinct_users))

def changesummary(*revid):
    "Prints a brief summary what has been changed for a given revid"
    chg = False
    for l in _dbsql("select clihost, cliprogram, cliuser, committs, remark from dave_revision where revid in (%s)" % ",".join(revid)):
        print "Host: %s, Program: %s, User: %s, Committs, %s, Remark: %s" % (l[0], l[1], l[2], str(AbsTime(int(l[3])/60)), l[4] or "")
        for l in _dbsql("select distinct tablename from dave_updated_tables where revid in(%s) order by tablename" % ','.join(revid)):
            chg = True
            inserted = deleted = changed = 0
            print "%s:" % l[0]
            for ll in _dbsql("select prev_revid, next_revid, deleted from %s where revid in(%s)" % (l[0], ','.join(revid))):
                if ll[2] == 'Y':
                    deleted += 1
                elif ll[0] == 0:
                    inserted += 1
                else:
                    changed += 1
            if deleted: print "   %d deleted" % deleted
            if changed: print "   %d changed" % changed
            if inserted: print "   %d inserted" % inserted
        if not chg: print "Revid %s not found in database" % revid

def commitid2revid(*commitid):
    "Return the revid given a specific commitid"
    chg = False
    header = False
    for l in _dbsql("select commitid,revid from dave_revision where commitid in(%s) order by revid" % ','.join(commitid)):
        chg = True
        if not header:
            print "Commitid\tRevid"
        print "%s\t%s" % (l[0], l[1])
    if not chg: print "Commitid %s not found in database" % commitid




def rollback(revid,table=None,onlylatest=True):
    """Undo the specified Dave revision by creating a reverse change set.
    NOTE: Currently only supports inserts and deletes, not updates.
    revid - the revid to undo
    [table] - only undo the specified table(s) (comma-separated)
    [--onlylatest=True|False] (default: True) - If true, only undo if no later record exists
                                                If false, always undo, even if newer records exist"""
    revid = int(revid)
    onlylatest = not str(onlylatest).lower() in ("false", "0", "no")
    tables = set()
    if table: tables = set(str(table).split(','))
    else: tables = set([l[0] for l in _dbsql("select distinct tablename from dave_updated_tables where revid=%s" % revid)])

    skipped = 0
    ops = []
    numundeleteds = 0
    numlaterdeleted = 0
    numuninserteds = 0
    numunupdateds = 0
    numunsupported = 0
    changedtables = set()
    for table in tables:
        cols = [l[0].lower() for l in _dbsql("select column_name from user_tab_columns where table_name='%s' order by column_name" % table.upper())
           if not l[0].lower() in ('next_revid', 'prev_revid', 'branchid', 'deleted', 'revid')]
        prevrecs = None
        pks = None
        sql = "select revid,next_revid,prev_revid,deleted,%s from %s where revid=%s" % (','.join(cols), table, revid)
        rows = list(_dbsql(sql))
        rows.sort(key=lambda r:r[4:])
        for idx,row in enumerate(rows):
            if onlylatest and row[1] > 0:
                skipped += 1
                continue
            f = {}
            for col in cols:
                if not row[4+cols.index(col)] is None:
                    f[col] = row[4+cols.index(col)]
            if row[3] == "Y":
                ops.append ( _createop(table, 'N', f) )
                changedtables.add(table)
                numundeleteds += 1
            elif row[2] == 0:
                ops.append ( _createop(table, 'D', f) )
                changedtables.add(table)
                numuninserteds += 1
            elif row[2] > row[0]:
                numlaterdeleted += 1
            else:
                if not prevrecs:
                    sql="select revid,next_revid,prev_revid,deleted,%s from %s where next_revid=%s" % (','.join(cols), table, revid)
                    prevrecs = list(_dbsql(sql))
                    ec = _getentityconnection(useAdm=False)
                    pks = set(ec.findPK(table,"").split(','))
                    if "revid" in pks: pks.remove('revid')
                    if "branchid" in pks: pks.remove('branchid')
                    if "deleted" in pks: pks.remove('deleted')
                def keyMatch(x):
                    if x[1] != row[0]: return False
                    for kc in pks:
                        idx = cols.index(kc)
                        if x[4+idx] != row[4+idx]: return False
                    return True
                prevrec = [x for x in prevrecs if keyMatch(x)]
                if len(prevrec) != 1:
                    numunsupported += 1
                else:
                    prevrec = prevrec[0]
                    for col in cols:
                        if not row[4+cols.index(col)] is None:
                            f[col] = prevrec[4+cols.index(col)]
                    ops.append ( _createop(table, 'U', f) )
                    changedtables.add(table)
                    numunupdateds += 1
    if skipped > 0 : print "%d records skipped due to out of date" % skipped
    if numunsupported > 0:
        print "%d unsupported changes will not be rolled back. Improve this script and try again" % numunsupported
    if numlaterdeleted > 0:
        print "%d inserted rows have later been deleted (will not check if they reappeared)" % numlaterdeleted
    if numundeleteds > 0:
        print "%d deleted rows will be un-deleted" % numundeleteds
    if numuninserteds > 0:
        print "%d inserted rows will be removed" % numuninserteds
    if numunupdateds > 0:
        print "%d updated rows will be reverted" % numunupdateds
    if len(ops) > 0:
        print "%d operations in total will be executed on the following tables:" % len(ops)
        for tab in sorted(changedtables):
            print "    %s" % tab
        print ""
        print "Are you sure? This will BATCH EDIT LIVE DATA"
        try:
           raw_input("Press OK to continue, Ctrl+C to ABORT !")
        except KeyboardInterrupt:
           print ""
           return
        print "Rolling back revision %s..." % revid
        commitid = DaveStorer(_getdaveconnector(False), reason="Rollback revid %s" % revid).store(ops, returnCommitId=True)
        print "Revision %s rolled back. New commitid = %s" % (revid, commitid)
        for row in _dbsql("select revid from dave_revision where commitid = %s" % commitid):
            print "New revid: %s" %  row[0]

def mkstub(schema=None, connect=None, overwrite=False):
    """Creates a schema stub in $CARMDATA
    [schema] (default: $DB_SCHEMA) - schema name
    [connect] (default: $DB_URL) - connection string
    [overwrite] (default False) - overwrite existing subplan?
    """
    os.umask(022)
    schema = schema or os.environ["DB_SCHEMA"]
    connect = connect or os.environ["DB_URL"]
    fileprefix = _C().getPropertyValue("data_model/plan_dir")
    plandir = os.path.join(os.path.expandvars("$CARMDATA/LOCAL_PLAN"), fileprefix)
    lplanpath = os.path.join(plandir, schema)
    splanpath = os.path.join(lplanpath, schema)
    if os.path.isfile(os.path.join(splanpath, "subplanHeader")):
        print >>sys.stderr, "Subplan already exists in %s" % splanpath
        if overwrite:
            print >>sys.stderr, "Overwriting subplan"
        else:
            print >>sys.stderr, "** Not overwriting existing subplan. Aborting. **"
            sys.exit(1)
    splocal = os.path.join(splanpath, "etable", "SpLocal")
    lplocal = os.path.join(lplanpath, "etable", "LpLocal")
    basedefs = os.path.join(splocal, ".BaseDefinitions")
    baseconstr = os.path.join(splocal, ".BaseConstraints")
    username = os.environ["USER"]
    if not os.path.exists(lplocal): os.makedirs(lplocal)
    if not os.path.exists(basedefs): os.makedirs(basedefs)
    if not os.path.exists(baseconstr): os.makedirs(baseconstr)
    ltmpfile = os.path.join(lplanpath, "localplan.tmp")
    f = file(ltmpfile, "w")
    print >>f, "SECTION local_plan_header"
    print >>f, "557;LOCAL_PLAN_HEADER_KEY;LOCAL_PLAN_HEADER_CONNECTOR_KEY;LOCAL_PLAN_HEADER_NAME;LOCAL_PLAN_HEADER_COMMENT;LOCAL_PLAN_LAST_DB_READ;LOCAL_PLAN_LAST_LOG_READ;LOCAL_PLAN_STANDARD_OR_DATED;LOCAL_PLAN_RRL_VERSION;LOCAL_PLAN_SELECTION;LOCAL_PLAN_OAG_FPLN;LOCAL_PLAN_TRAFFICDAYTABLE;LOCAL_PLAN_HEADER_DB_PATH;"
    print >>f, "559;;;%(fileprefix)s/%(schema)s;;05Apr2007 07:20;;DATED;70;Ctf2Rrl -i notused.ctf;;;%(schema)s+%(connect)s;" % locals()
    print >>f, "SECTION net"
    print >>f, "124;NET_CODE;NET_FLIGHT_ID;NET_CREW_EMPLOYER;NET_GDOR;NET_START_TIME;NET_START_DATE;NET_END_TIME;NET_END_DATE;NET_ROTATION_NUM;NET_OPTION;NET_EMPNO_NO;NET_GROUP;NET_AREA;NET_DAY_NUM;NET_DEP_AIRP;NET_ARR_AIRP;NET_FREQ_ONLY;NET_ON_FREQ;NET_FIRST_CLASS_CAP;NET_BUSINESS_CLASS_CAP;NET_ECONOMY_CLASS_CAP;NET_REST_TIME_BV;NET_REST_TIME_LBA;NET_REST_TIME_MTV;NET_SPECIAL_REST_TIME;NET_SIS_VERSION_NUM;NET_STATUS;NET_AC_TYPE1;NET_AC_TYPE2;NET_AC_TYPE3;NET_AC_TYPE4;NET_FLEET1;NET_FLEET2;NET_FLEET3;NET_FLEET4;NET_IATA1;NET_IATA2;NET_IATA3;NET_IATA4;NET_IATA5;NET_QUAL1;NET_QUAL2;NET_MANUAL_CREW_COMP;NET_CALC_CREW_COMP;NET_CHANGED_CREW_COMP;NET_AC_OWNER;NET_CONFIG;NET_PBASE;NET_SIS_FP_ID;NET_USER_ID;NET_SIS_FP_ID_2;NET_SIS_VERSION_NUM_2;NET_START_TIME_2;NET_START_DATE_2;NET_END_TIME_2;NET_END_DATE_2;NET_AREA_TYPE;NET_CRR_TYPE;NET_MAIN_CAT;NET_REINF_CAB_CALC;NET_REINF_CAB_MAN;NET_REINF_COC_CALC;NET_REINF_COC_MAN;NET_SERVICE_TYPE;NET_SUFFIX;NET_TIME_BASE;NET_FILTER_DH;NET_GDP_VERSION_NUMBER;NET_GDP_ID;NET_GDP_VERSION_NUMBER_2;NET_GDP_ID_2;NET_GDP_START_TIME;NET_GDP_END_TIME;NET_GDP_START_TIME_2;NET_GDP_END_TIME_2;NET_GDP_START_DATE;NET_GDP_END_DATE;NET_GDP_START_DATE_2;NET_GDP_END_DATE_2;"
    print >>f, "125;;;;;0000;20070405;2359;20100405;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;GDOR;;;;;;;;;;;;;;"
    f.close()
    os.system("compress '%s'" % ltmpfile)
    ltmpfile = "%s.Z" % ltmpfile
    lplanfile = os.path.join(lplanpath, "localplan")
    if not os.path.isfile(ltmpfile):
        print >>sys.stderr, "Failed to create localplan"
        sys.exit(1)
    os.system("mv '%s' '%s'" % (ltmpfile, lplanfile))
    
    os.system("cp -r ${CARMUSR}/crc/etable/.BaseConstraints/* '%s/'" % baseconstr)
    os.system("cp -r ${CARMUSR}/crc/etable/.BaseDefinitions/* '%s/'" % basedefs)
    f = file(os.path.join(splanpath, "subplanRules"), "w")
    print >>f, "SECTION rules"
    print >>f, "_builtin.MasterRule on #D> on"
    print >>f, "<PARAMETERS>"
    print >>f, "<END>"
    for _ in range(6): print >>f
    f.close()
    f = file(os.path.join(splanpath, "subplanHeader"), "w")
    print >>f, "SECTION sub_plan_header"
    print >>f, "552;SUB_PLAN_HEADER_KEY;SUB_PLAN_HEADER_CONNECTOR_KEY;SUB_PLAN_HEADER_NAME;SUB_PLAN_HEADER_AGREEMENT;SUB_PLAN_HEADER_COMMENT;SUB_PLAN_HEADER_AREA;SUB_PLAN_HEADER_AIRLINE;SUB_PLAN_HEADER_CREW_COMPLEMENT;SUB_PLAN_HEADER_ASSIGN_COMPLEMENT;SUB_PLAN_HEADER_DUTY_TYPE;SUB_PLAN_HEADER_CITY;SUB_PLAN_HEADER_PLANNER;SUB_PLAN_HEADER_PREVIOUS_NAME;SUB_PLAN_HEADER_STATUS;SUB_PLAN_HEADER_PERIOD_START_1;SUB_PLAN_HEADER_PERIOD_END_1;SUB_PLAN_HEADER_PERIOD_START_2;SUB_PLAN_HEADER_PERIOD_END_2;SUB_PLAN_HEADER_PERIOD_START_3;SUB_PLAN_HEADER_PERIOD_END_3;SUB_PLAN_HEADER_START_PLANNING;SUB_PLAN_HEADER_RULE_SET_NAME;SUB_PLAN_HEADED_PPP_START;SUB_PLAN_HEADER_PPP_START;SUB_PLAN_HEADER_PPP_END;SUB_PLAN_HEADER_CREW_FILTER;SUB_PLAN_HEADER_RRL_VERSION;SUB_PLAN_HEADER_CRR_NO;SUB_PLAN_HEADER_CREW_PLAN;SUB_PLAN_HEADER_TAG_INFO;SUB_PLAN_HEADER_TAG_LEVEL_INFO;SUB_PLAN_HEADER_CREW_TAG_INFO;SUB_PLAN_HEADER_BASE_DEF_FILE_NAME;SUB_PLAN_HEADER_BASE_CONSTR_FILE_NAME;SUB_PLAN_HEADER_DB_PATH;"
    print >>f, "554;;;%(fileprefix)s/%(schema)s/%(schema)s;;;;;;;;HEL+;%(username)s;%(fileprefix)s/%(schema)s/%(schema)s;;20060814;20061019;;;;;07Sep2006 07:21;;20060814;20060814;20061019;5;210;8817;crew_data.etab;#0#USER_TAG_0#1#USER_TAG_1#2#USER_TAG_2#3#USER_TAG_3#4#USER_TAG_4#5#USER_TAG_5#6#USER_TAG_6#7#USER_TAG_7#8#USER_TAG_8#9#USER_TAG_9;#0#Default#1#Default#2#Default#3#Default#4#Default#5#Default#6#Default#7#Default#8#Default#9#Default;#0#USER_TAG_0#1#USER_TAG_1#2#USER_TAG_2#3#USER_TAG_3#4#USER_TAG_4#5#USER_TAG_5#6#USER_TAG_6#7#USER_TAG_7#8#USER_TAG_8#9#USER_TAG_9;DefaultBaseDefinitions;DefaultBaseConstraints;%(schema)s+%(connect)s;" % locals()
    print >>sys.stderr, "Stub files made for %s" % schema

def mkstub_history():
    mkstub(_C().getPropertyValue("db/dave/history/schema"), _C().getPropertyValue("db/dave/history/url"))


def singlelegs(startDate, endDate=None, numberOfResults=3):
    """Find a massive deletion of trips. It was used when working on SASCMS-2905, 
    The benefits of this method is that it only requires a two reference points in time. One before the corruption and one after.
    startDate - A date before the deletion of trips
    endDate - A date after the deletion of trips, default now
    
    """
    sql = "select min(revid), max(revid) from dave_revision where committs > %s" % (int(AbsTime(startDate))*60)
    if endDate != None:
        sql += " and committs < %s" % (int(AbsTime(endDate))*60)
    l = _dbsql(sql)
    min_revid =l[0][0]
    max_revid =l[0][1]
    
    sql = "SELECT revid, COUNT(revid) FROM trip_flight_duty where revid > '%s' and revid < '%s' and deleted='Y' GROUP BY revid ORDER BY COUNT(revid) DESC" % (min_revid, max_revid)
    l = _dbsql(sql)
    print "Possible candidates are:"
    i = 0
    for r,c in l:
        print 40*"*"
        print "%10s %10s" % ("Revid", "Number")
        print "%10d %10s" % (r,c)
        sql = "SELECT * FROM dave_revision WHERE revid = %s" %r
        changesummary(str(r))
        i += 1
        if i >= numberOfResults:
            break
    
def fixseq(schema=None, revseq=True, commitseq=True):
    """Checks and eventually fixes the rev and commit sequences
    [schema] (default: $DB_SCHEMA) - schema name
    """
    
    schema = schema or os.environ["DB_SCHEMA"]
    useAdm = True

    if revseq:
        print "Checking rev sequence"
        query = "select max(revid) from %s.dave_revision" % schema    
        max_revid = _dbsql(query,useAdm)[0][0]
        query = "select %s.revseq.nextval from dual" % schema
        revseq = _dbsql(query,useAdm)[0][0]
        print "%15s: %s" %  ("Max commitid", max_revid)
        print "%15s: %s" %  ("Old revseq", revseq)
        print "Creating new rev sequence"
        query = "drop sequence %s.revseq" % schema
        _dbexec(query,useAdm)
        query = "create sequence %s.revseq minvalue 1 increment by 1 start with %s nocache noorder nocycle" % (schema, max_revid+1)
        _dbexec(query,useAdm)
        query = "select %s.revseq.nextval from dual" % schema
        revseq = _dbsql(query,useAdm)[0][0]
        print "%15s: %s" %  ("New revseq", revseq)
        if commitseq:
            print 40*"*"
        
    if commitseq:
        print "Checking commit sequence"
        query = "select max(commitid) from %s.dave_revision where commitid < 999999999" % schema    
        max_commitid = _dbsql(query,useAdm)[0][0]
        query = "select %s.commitseq.nextval from dual" % schema
        commitseq = _dbsql(query,useAdm)[0][0]
        print "%15s: %s" %  ("Max commitid", max_commitid)
        print "%15s: %s" %  ("Old commitseq", commitseq)
        print "Creating new commit sequence"
        query = "drop sequence %s.commitseq" % schema
        _dbexec(query,useAdm)
        query = "create sequence %s.commitseq minvalue 1 increment by 1 start with %s nocache noorder nocycle" % (schema, max_commitid+1)
        _dbexec(query,useAdm)
        query = "select %s.commitseq.nextval from dual" % schema
        commitseq = _dbsql(query,useAdm)[0][0]
        print "%15s: %s" %  ("New commitseq", commitseq)
      
sqlparse = None
class _DaveAPI:
    class Ref(object):
        def __init__(self, name, tab=None):
            self.name = name
            self.tab = tab
        def __repr__(self):
            if not self.tab is None:return str("Ref<%s.%s>" % (self.tab, self.name))
            return "Ref<%s>" % self.name
        def __str__(self):
            if not self.tab is None:return "%s.%s" % (str(self.tab), str(self.name))
            return str(self.name)
    class DaveQuery(object):
        def __init__(self, stmt):
            self.stmt = stmt
        def eval(self, dc):
            raise Exception, "Operation not supported"
        def _columnlist(self, tkn):
            ret = []
            if tkn.is_group():
                tokens = [t for t in tkn.tokens if not t.is_whitespace()]
                if len(tokens) == 3 and tokens[1].ttype == sqlparse.tokens.Punctuation and tokens[1].value == '.':
                    ret.append(self._column(tkn))
                else:
                    for si in tkn.tokens:
                        if si.ttype == sqlparse.tokens.Punctuation: continue
                        ret.append(self._column(si))
            else:
                ret.append(self._column(tkn))
            return ret
        def _assignment(self, tkns):
            for i,e in enumerate(tkns):
                if e.value == '=':
                    return (":=", self._column(tkns[:i]), self._condition(tkns[i+1:]))
            raise ValueError,"Invalid assignment"
        def _column(self, tkn):
            if isinstance(tkn, list):
                tkn = [str(t.value) for t in tkn if t.ttype != sqlparse.tokens.Punctuation and not t.is_whitespace()]
                if len(tkn) == 1: return tkn[0]
                else: return tuple(tkn)
            if tkn.is_group():
                return tuple([t.value for t in tkn.tokens if t.ttype != sqlparse.tokens.Punctuation and not t.is_whitespace()])
            else:
                return tkn.value
        def _sourcelist(self, tkn):
            ret = []
            if tkn.is_group():
                tokens = [t for t in tkn.tokens if not t.is_whitespace()]
                if len(tokens) == 2:
                    ret.append(self._source(tkn))
                else:
                    for si in tokens:
                        if si.ttype == sqlparse.tokens.Punctuation: continue
                        ret.append(self._source(si))
            else:
                ret.append(self._source(tkn))
            return ret
        def _source(self, tkn):
            if tkn.is_group():
                t = tuple([t.value or t.get_name() for t in tkn.tokens if t.ttype not in (sqlparse.tokens.Punctuation,sqlparse.tokens.Keyword) and not t.is_whitespace()])
                if len(t) == 1: t = t[0]
                return t
            else:
                return tkn.value
        def _condition(self, stkn):
            expr = []
            if isinstance(stkn, list):
                expr = stkn
            else:
                for e in [x for x in stkn.tokens[1:] if not x.is_whitespace()]:
                    expr.extend(e.flatten()) # sqlparser gets precedence wrong, so we do it right. Gor om, gor ratt :)
            prio = []
            def match(ttype, tvals):
                def f(tkns):
                    next = prio[prio.index(f)+1]
                    for i,t in enumerate(tkns):
                        if (ttype is None or t.ttype == ttype) and t.value.lower() in tvals:
                            if i == 0: return (t,f(tkns[i+1:]))
                            return (t.value.lower(),next(tkns[:i]),f(tkns[i+1:]))
                    return next(tkns)
                return f
            def matchtkn(ttype, tvals):
                def f(tkns):
                    next = prio[prio.index(f)+1]
                    for i,t in enumerate(tkns):
                        if (ttype is None or t.ttype == ttype) and t.value.lower() in tvals:
                            if i == 0: return (t,f(tkns[i+1:]))
                            return (t.value.lower(),next(tkns[:i]),f(tkns[i+1:]))
                    return next(tkns)
                return f
            def terminal(tkns):
                t = tkns[0]
                if t.ttype == sqlparse.tokens.Number.Integer:
                    return int(t.value)
                elif t.ttype == sqlparse.tokens.Number.Float:
                    return float(t.value)
                elif t.ttype == sqlparse.tokens.String.Single:
                    return tkns[0].value
                elif t.ttype == sqlparse.tokens.Name:
                    if len(tkns) == 3:
                        return _DaveAPI.Ref(tkns[2].value, tkns[0].value)
                    else:
                        return _DaveAPI.Ref(tkns[0].value)
                raise ValueError,"Unknown primitive type %r" % t.ttype
            prio = [match(sqlparse.tokens.Keyword, ("or","all","any","between","in","some")),
                    match(sqlparse.tokens.Keyword, ("and",)),
                    match(sqlparse.tokens.Keyword, ("not",)),
                    matchtkn(sqlparse.tokens.Comparison, ("=", ">", "<", ">=", "<=", "<>", "!=", "!>", "!<")),
                    matchtkn(sqlparse.tokens.Operator, ("+","-","&","^","|")),
                    matchtkn(None, ("*","/","%")),
                    matchtkn(None, ("~",)),
                    terminal]
            return prio[0](expr)
            
        def _tablename(self, tablespec):
            if isinstance(tablespec,tuple): return str(tablespec[0])
            return str(tablespec)
            
        def _daveexpr(self, where, tablespec, validspecs, requireAlias):
            if where is None or isinstance(where, list) and len(where) == 0: return []
            alias = tablespec
            if isinstance(alias,tuple) and len(alias) > 0:
                alias = alias[1]
            if isinstance(where, tuple):
                op,l,r = where
                l = self._daveexpr(l,alias,validspecs,requireAlias)
                r = self._daveexpr(r,alias,validspecs,requireAlias)
                if op == "and":
                    if l is None: return r
                    if r is None: return l
                    return l+r
                else:
                    if l is None or r is None: return None
                    return ["%s %s %s" % (str(" and ".join(l)),str(op),str(" and ".join(r)))]
            else:
                if isinstance(where, _DaveAPI.Ref):
                    if requireAlias and where.tab is None:
                        raise ValueError,"Unqualified columns not valid"
                    if not where.tab is None and not where.tab in validspecs:
                        raise ValueError,"Table alias '%s' not specified" % where.tab
                    elif not where.tab is None:
                        if where.tab == alias:
                            return [str(where.name)]
                        else:
                            return None
                return [str(where)]
            
        def getsearch(self, sources, where, withDeleted=False):
            if isinstance(sources,str): sources = [sources]
            srcs = []
            for src in sources:
                if isinstance(src, tuple): srcs.append(src[1])
                else: srcs.append(src)
            if len(sources) == 1:
                expr = self._daveexpr(where, sources[0], srcs, False) or []
                return DaveSearch(self._tablename(sources[0]), expr, withDeleted)
            else:
                searches = []
                for src in sources:
                    expr = self._daveexpr(where, src, srcs, True) or []
                    searches.append(DaveSearch(self._tablename(src), expr, withDeleted))
                raise ValueError,"Can only search one table at a time"
    
    class SELECT(DaveQuery):
        def __init__(self, stmt):
            super(_DaveAPI.SELECT, self).__init__(stmt)
            self.columns = []
            self.sources = []
            self.where = []
            pos = 1
            for tkn in self.stmt.tokens[pos:]:
                pos += 1
                if tkn.is_whitespace(): continue
                self.columns = self._columnlist(tkn)
                break
            for tkn in self.stmt.tokens[pos:]:
                pos += 1
                if tkn.is_whitespace(): continue
                if tkn.ttype == sqlparse.tokens.Keyword:
                    if tkn.value.lower() == 'from': break
                raise ValueError,"Expected FROM"
            for tkn in self.stmt.tokens[pos:]:
                pos += 1
                if tkn.is_whitespace(): continue
                self.sources = self._sourcelist(tkn)
                break
            for tkn in self.stmt.tokens[pos:]:
                pos += 1
                if tkn.is_whitespace(): continue
                self.where = self._condition(tkn)
                break
        def eval(self, dc):
            if len(self.sources) == 1:
                search = self.getsearch(self.sources[:1], self.where)
                return dc.runSearch(search)
            else:
                search = self.getsearch(self.sources, self.where)
    
    class UPDATE(DaveQuery):
        def __init__(self, stmt):
            super(_DaveAPI.UPDATE, self).__init__(stmt)
            self.setters = []
            self.sources = []
            self.where = []
            pos = 1
            for tkn in self.stmt.tokens[pos:]:
                pos += 1
                if tkn.is_whitespace(): continue
                self.sources = self._sourcelist(tkn)
                break
            for tkn in self.stmt.tokens[pos:]:
                pos += 1
                if tkn.is_whitespace(): continue
                if tkn.ttype == sqlparse.tokens.Keyword:
                    if tkn.value.lower() == 'set': break
                raise ValueError,"Expected SET"
            wpc = []
            for tkn in self.stmt.tokens[pos:]:
                if tkn.__class__ == sqlparse.sql.Where: break
                pos += 1
                if tkn.is_whitespace(): continue
                wpc.extend(tkn.flatten())
            ist = 0
            self.setters = []
            for i,w in enumerate(wpc):
                if w.ttype == sqlparse.tokens.Punctuation and w.value == ',':
                    self.setters.append(self._assignment(wpc[ist:i]))
                    ist = i+1
            if ist < len(wpc):
                self.setters.append(self._assignment(wpc[ist:]))
            for tkn in self.stmt.tokens[pos:]:
                pos += 1
                if tkn.is_whitespace(): continue
                self.where = self._condition(tkn)
                break
        def eval(self, dc):
            if len(self.sources) == 1:
                search = self.getsearch(self.sources[:1], self.where)
                alias = lambda x: isinstance(x,tuple) and str(x[1]) or str(x)
                tableref = lambda x: isinstance(x,tuple) and str(x[0]) or str(x)
                srcs = map(alias,self.sources)
                table = tableref(self.sources[0])
                assignments = {}
                for op,col,val in self.setters:
                    if op != ':=': continue
                    if isinstance(col, tuple):
                        t,col = col
                        if not t in srcs:
                            raise ValueError, ("Table reference '%s' not found in assignment (%r)" % (t, ','.join(srcs)))
                    if col in assignments:
                        raise ValueError, "Column %s specified more than once" % col
                    assignments[col] = val
                ops = []
                for i,l in enumerate(dc.runSearch(search)):
                    if i<10: print "%4d: " % (i+1),
                    for col,v in assignments.items():
                        if isinstance(v, _DaveAPI.Ref):
                            v = l[v.name]
                        elif isinstance(v, str) or isinstance(v, unicode):
                            if v[0] == "'": v = v[1:-1]
                        if i<10: print "%s: %s->%s  " % (col, l[col], v),
                        l[col] = v
                    if i==10: print "...",
                    if i<=10: print
                    if "revid" in l: del l["revid"]
                    ops.append(_createop(table, 'U', l))
                print "Updating %d record(s) in %s" % (len(ops), table)
                print "Are you sure? This will BATCH EDIT LIVE DATA"
                try:
                   raw_input("Press OK to continue, Ctrl+C to ABORT !")
                except KeyboardInterrupt:
                   print ""
                   return
                commitid = DaveStorer(_getdaveconnector(False), reason="DaveConsole").store(ops, returnCommitId=True)
                print "Rows updated. New commitid = %s" % commitid
            else:
                raise ValueError,"Cannot update multiple tables at once"

def _printsearchresults(results):
    if results is None: return
    s = []
    cols = {}
    hdr = False
    def _fmt(l):
        for c in cols:
            val = l.get(c,None)
            if val is None: val = '-'
            else: val = repr(val)
            print ("%%-%ds" % (2+cols[c])) % val,
        print
    def _printhdr():
        for c in cols:
            print ("%%-%ds" % (2+cols[c])) % c,
        print
        for c in cols:
            print ("%%-%ds" % (2+cols[c])) % ('='*(2+cols[c])),
        print
    for i,l in enumerate(results):
        if i < 100:
            for k in l:
                cols[k] = max(cols.get(k,0), len(repr(l[k])))
            s.append(l)
        elif len(s) > 0:
            _printhdr()
            hdr = True
            for ll in s:
                _fmt(ll)
            s = []
            _fmt(l)
        else:
            _fmt(l)
    if not hdr: _printhdr()
    for ll in s:
        _fmt(ll)
    
def dave(stmts=None, schema=None, connect=None):
    """SQL-like DAVE interface / console
    [stmts] - The statement(s) to evaluate. If not specified, a console will be shown."""
    global sqlparse
    sqlparse = _sqlparse()
    if not schema: schema = os.environ["DB_SCHEMA"]
    
    def _eval(stmts):
        q, = sqlparse.parse(stmts)
        try:
            cls = getattr(_DaveAPI, q.get_type().upper())
        except AttributeError:
            if q.get_type().upper() == "UNKNOWN":
                raise ValueError, "Unsupported statement"
            raise ValueError, "%s statements not supported" % q.get_type().upper()
        return cls(q).eval(_getdaveconnector(False))
    if not stmts:
        import readline
        try:
            while True:
                s = raw_input("%s >>> " % schema)
                for q in sqlparse.split(s):
                    try:
                        _printsearchresults(_eval(q))
                    except:
                        print >>sys.stderr, sys.exc_info()[1]
        except EOFError:
            print
            return
    for q in sqlparse.split(stmts):
        try:
            _printsearchresults(_eval(q))
        except:
            import traceback
            traceback.print_exc()
            print >>sys.stderr, "%s:\n  %s" % (q, sys.exc_info()[1])
            
