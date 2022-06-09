#!/usr/bin/python 

import cx_Oracle as oc
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import logging



query_old = '''
         select b.tablespace_name, tbs_size SizeMb, a.free_space FreeMb from
         (select tablespace_name, round(sum(bytes)/1024/1024, 2) as free_space
         from dba_free_space
         group by tablespace_name) a,
         (select tablespace_name, sum(bytes)/1024/1024 as tbs_size
         from dba_data_files
         group by tablespace_name) b
         where a.tablespace_name(+)=b.tablespace_name
       '''
query = '''
    SELECT tablespace_name, NULL ts_size, ROUND(SUM(ts_free)/1024/1024/1024) ts_free_gb
    FROM (
        -- Free space inside already allocated datafile
        SELECT tablespace_name, SUM(bytes) ts_free FROM dba_free_space GROUP BY tablespace_name
        UNION ALL
        -- Space left to allocate up to autoextend maxbytes
        SELECT tablespace_name, SUM(GREATEST(bytes,maxbytes)-bytes) ts_free FROM dba_data_files GROUP BY tablespace_name
    )
    GROUP BY tablespace_name
    ORDER BY tablespace_name
    '''


def parse_args():
    args = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    args.add_argument('-c', '--connection', help="Connection string", required=True)
    args.add_argument('-q', '--query', help="Query to the database")
    args.add_argument('-v', '--verbose', help="Increase output verbosity", default=False, action='store_true')
    return args.parse_args()


def execute(connection, query, tble_check=True):
    cur = connection.cursor()
    s = {}
    try:
       cur.execute("%s" % query)
       if tble_check:
           for row  in cur:
               s[row[0]]= [row[1], row[2]]
       else:
          for (index,element) in enumerate(cur):
              s[index] = element 
       return s
    except Exception, e: 
        logging.error("Could not execute query %s" % query)
        logging.error(str(e))
        return None
    finally:
        cur.close()
   


def query_db(connection, query, tbl_check=True):
    con = None
    try:
        con = oc.connect(connection)
        logging.debug("Oracle conection established with: %s" % connection)
        cur = execute(con, "%s" %query, tbl_check)
        if cur is not None and tbl_check:
            # PLEASE DONOT REMOVE THE PRINT LINE, ANSIBLE RELIES ON IT
            print "FLM_BIG_DATA: %s" % cur['FLM_BIG_DATA'][1]
            logging.info("FLM_BIG_DATA: %s" % cur['FLM_BIG_DATA'][1])
            logging.debug("%r" % cur)
        else:
            logging.info("%r" % cur)
    except oc.DatabaseError as e:
        err, = e.args
        logging.debug("Oracle error code: %s" % err.code)
        logging.debug("Oracle error message: %s" % err.message)
        exit(1)
    finally:
        if con is not None:
            logging.debug("Oracle connection closed")
            con.close()

def main():
   args = parse_args()
   if args.verbose:
       loglevel = logging.DEBUG
   else:
       loglevel = logging.INFO
   logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)
   logging.debug("Quering the database...")
   checker = args.query is None
   if not args.query:
       args.query = query
   clean_connection_name = args.connection.replace('oracle:','')    
   query_db(clean_connection_name, args.query, checker)
   # query_db(args.connection, args.query, checker)
   logging.info("Result is in GB. END OF EXEC")
      


if __name__ == '__main__':
    main()
