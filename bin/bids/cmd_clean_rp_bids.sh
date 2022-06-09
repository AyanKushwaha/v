#!/bin/sh

LOG=${CARMTMP}/logfiles/`basename $0 .sh`.${USER}.$(date +%Y%m%d.%H%M.%S).`hostname -s`.log
{
echo "[$(date)] Starting script `basename $0`"
echo
echo "========================================================================"
echo "To restore deleted bids, use the following INSERT statements with sqlcp."
echo "========================================================================"
echo

_DB_LOC="`echo $DB_CP_URL |sed -e 's/oracle:\(.\+\)%.\+\//\1\//' | sed -e 's/oracle://'`";

sqlplus -S $_DB_LOC <<EOF ;
SET linesize 2000
SET heading off


-- View of non-RP crew usergroups
CREATE VIEW v_not_rp_ug AS
  SELECT ug.* FROM usergroups ug, groups g
  WHERE ug.groupid = g.groupid AND g.groupname != 'CC RP';

-- View of non-RP crew bidgroups
CREATE VIEW v_not_rp_bg AS
  SELECT bg.* FROM bidgroups bg, v_not_rp_ug ug
  WHERE bg.userid = ug.userid;

-- View of bids of non-RP crew that are marked as valid but should be deleted
CREATE VIEW v_bids_dfp AS
  SELECT b.*
  FROM BIDS b, v_not_rp_bg bg
  WHERE b.bidgroupid = bg.bidgroupid
  AND b.BIDTYPE = 'days_for_production'
  AND (b.ENDDATE is NULL or b.ENDDATE > CURRENT_TIMESTAMP)
  AND (b.INVALID is NULL or b.INVALID > CURRENT_TIMESTAMP);


-- View of bid properties that belong to bids of non-RP crew that are marked as valid but should be deleted
CREATE VIEW v_bp_dfp AS
  SELECT bp.*
  FROM bidproperties bp, v_bids_dfp b
  WHERE bp.bidsequenceid = b.bidsequenceid;


-- View of bid property entries that belong to bids of non-RP crew that are marked as valid but should be deleted
CREATE VIEW v_bpe_dfp AS
  SELECT bpe.*
  FROM v_bp_dfp bp, bidpropertyentries bpe
  WHERE bp.bidpropertyid = bpe.bidpropertyid;


-- View of RP crew usergroups
CREATE VIEW v_rp_ug AS
  SELECT ug.* FROM usergroups ug, groups g
  WHERE ug.groupid = g.groupid AND g.groupname = 'CC RP';


-- View of RP crew bidgroups
CREATE VIEW v_rp_bg AS
  SELECT bg.* FROM bidgroups bg, v_rp_ug ug
  WHERE bg.userid = ug.userid;


-- View of bids of RP crew that are marked as valid but should be deleted
CREATE VIEW v_rp_bids_not_dfp AS
  SELECT b.*
  FROM BIDS b, v_rp_bg bg
  WHERE b.BIDGROUPID = bg.bidgroupid
  AND b.BIDTYPE != 'days_for_production'
  AND (b.ENDDATE is NULL or b.ENDDATE > CURRENT_TIMESTAMP)
  AND (b.INVALID is NULL or b.INVALID > CURRENT_TIMESTAMP);


-- View of bid properties that belong to bids of RP crew that are marked as valid but should be deleted
CREATE VIEW v_rp_bp_not_dfp AS
  SELECT bp.*
  FROM bidproperties bp, v_rp_bids_not_dfp b
  WHERE bp.bidsequenceid = b.bidsequenceid;


-- View of bid property entries that belong to bids of RP crew that are marked as valid but should be deleted
CREATE VIEW v_rp_bpe_not_dfp AS
  SELECT bpe.*
  FROM v_rp_bp_not_dfp bp, bidpropertyentries bpe
  WHERE bp.bidpropertyid = bpe.bidpropertyid;


-- Show bids as SQL inserts, for logging purposes
CREATE view sql_bids_dfp AS
SELECT 'INSERT INTO bids values(' || BIDSEQUENCEID || ', '
                                  || 'TO_TIMESTAMP(''' || REVISIONDATE || '''), '
                                  || BIDID  || ', '
                                  || '''' || BIDTYPE || ''', '
                                  || NAME || 'NULL, '
                                  || BIDGROUPID || ', '
                                  || 'TO_TIMESTAMP(''' || STARTDATE || '''), '
                                  || 'TO_TIMESTAMP(''' || ENDDATE || '''), '
                                  || '''' || CREATEDBY || ''', '
                                  || 'TO_TIMESTAMP(''' || CREATED || '''), '
                                  || '''' || UPDATEDBY || ''', '
                                  || 'TO_TIMESTAMP(''' || UPDATED || '''), '
                                  || 'TO_TIMESTAMP(''' || INVALID || '''));' sql FROM v_bids_dfp;


-- Show bid properties as SQL inserts, for logging purposes
CREATE VIEW sql_bp_dfp AS
SELECT 'INSERT INTO bidproperties values(' || bidpropertyid || ', ' || bidsequenceid || ', ' || sortorder || ', ''' || bidpropertytype || ''');' sql FROM v_bp_dfp;


-- Show bid property entries as SQL inserts, for logging purposes
CREATE VIEW sql_bpe_dfp AS
SELECT 'INSERT INTO bidpropertyentries values(' || bidpropertyentryid || ', '
                                                || bidpropertyid || ', '
                                                || '''' || entrykey || ''', '
                                                || '''' || entryvalue || ''');' sql FROM v_bpe_dfp;



-- Show bids as SQL inserts, for logging purposes
CREATE view sql_rp_bids_not_dfp AS
SELECT 'INSERT INTO bids values(' || BIDSEQUENCEID || ', '
                                  || 'TO_TIMESTAMP(''' || REVISIONDATE || '''), '
                                  || BIDID  || ', '
                                  || '''' || BIDTYPE || ''', '
                                  || NAME || 'NULL, '
                                  || BIDGROUPID || ', '
                                  || 'TO_TIMESTAMP(''' || STARTDATE || '''), '
                                  || 'TO_TIMESTAMP(''' || ENDDATE || '''), '
                                  || '''' || CREATEDBY || ''', '
                                  || 'TO_TIMESTAMP(''' || CREATED || '''), '
                                  || '''' || UPDATEDBY || ''', '
                                  || 'TO_TIMESTAMP(''' || UPDATED || '''), '
                                  || 'TO_TIMESTAMP(''' || INVALID || '''));' sql FROM v_rp_bids_not_dfp;




-- Show bid properties as SQL inserts, for logging purposes
CREATE VIEW sql_rp_bp_not_dfp AS
SELECT 'INSERT INTO bidproperties values(' || bidpropertyid || ', ' || bidsequenceid || ', ' || sortorder || ', ''' || bidpropertytype || ''');' sql FROM v_rp_bp_not_dfp;


-- Show bid property entries as SQL inserts, for logging purposes
CREATE VIEW sql_rp_bpe_not_dfp AS
SELECT 'INSERT INTO bidpropertyentries values(' || bidpropertyentryid || ', '
                                                || bidpropertyid || ', '
                                                || '''' || entrykey || ''', '
                                                || '''' || entryvalue || ''');' sql FROM v_rp_bpe_not_dfp;

-- Do the actual selections
SELECT * FROM sql_bids_dfp;
SELECT * FROM sql_bp_dfp;
SELECT * FROM sql_bpe_dfp;
SELECT * FROM sql_rp_bids_not_dfp;
SELECT * FROM sql_rp_bp_not_dfp;
SELECT * FROM sql_rp_bpe_not_dfp;

-- Delete the bids
DELETE FROM bidpropertyentries WHERE bidpropertyentryid IN (SELECT bidpropertyentryid FROM v_bpe_dfp);
DELETE FROM bidproperties WHERE bidpropertyid IN (SELECT bidpropertyid FROM v_bp_dfp);
DELETE FROM bids WHERE bidsequenceid IN (SELECT bidsequenceid FROM v_bids_dfp);
DELETE FROM bidpropertyentries WHERE bidpropertyentryid IN (SELECT bidpropertyentryid FROM v_rp_bpe_not_dfp);
DELETE FROM bidproperties WHERE bidpropertyid IN (SELECT bidpropertyid FROM v_rp_bp_not_dfp);
DELETE FROM bids WHERE bidsequenceid IN (SELECT bidsequenceid FROM v_rp_bids_not_dfp);

-- Dropping views
DROP VIEW v_not_rp_ug;
DROP VIEW v_not_rp_bg;
DROP VIEW v_bids_dfp;
DROP VIEW sql_bids_dfp;
DROP VIEW v_bp_dfp;
DROP VIEW sql_bp_dfp;
DROP VIEW v_bpe_dfp;
DROP VIEW sql_bpe_dfp;

DROP VIEW v_rp_ug;
DROP VIEW v_rp_bg;
DROP VIEW v_rp_bids_not_dfp;
DROP VIEW sql_rp_bids_not_dfp;
DROP VIEW v_rp_bp_not_dfp;
DROP VIEW sql_rp_bp_not_dfp;
DROP VIEW v_rp_bpe_not_dfp;
DROP VIEW sql_rp_bpe_not_dfp;

EOF
} | tee -a ${LOG}
