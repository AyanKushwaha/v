-- View of non-RP crew usergroups
CREATE VIEW v_not_rp_ug AS
  SELECT ug.* FROM usergroups ug, groups g
  WHERE ug.groupid = g.groupid AND g.groupname != 'CC RP';

-- View of non-RP userids
CREATE VIEW v_not_rp_ui AS
  SELECT userid FROM v_not_rp_ug;

-- View of non-RP crew bidgroups
CREATE VIEW v_not_rp_bg AS
  SELECT bg.* FROM bidgroups bg, v_not_rp_ug ug
  WHERE bg.userid = ug.userid;

-- View of bids of non-RP crew that should be deleted
CREATE VIEW v_not_rp_bids AS
  SELECT b.*
  FROM BIDS b, v_not_rp_bg bg
  WHERE b.bidgroupid = bg.bidgroupid;
--  AND (b.ENDDATE is NULL or b.ENDDATE > CURRENT_TIMESTAMP)
--  AND (b.INVALID is NULL or b.INVALID > CURRENT_TIMESTAMP);

-- View of bid properties that belong to bids of non-RP crew that should be deleted
CREATE VIEW v_not_rp_bp AS
  SELECT bp.*
  FROM bidproperties bp, v_not_rp_bids b
  WHERE bp.bidsequenceid = b.bidsequenceid;

-- View of bid property entries that belong to bids of non-RP crew that are marked as valid but should be deleted
CREATE VIEW v_not_rp_bpe AS
  SELECT bpe.*
  FROM v_not_rp_bp bp, bidpropertyentries bpe
  WHERE bp.bidpropertyid = bpe.bidpropertyid;

-- delete from USERSETTINGS;
DELETE FROM usersettings WHERE userid IN (SELECT userid FROM v_not_rp_ui);
-- delete from BIDPROPERTYENTRIES;
DELETE FROM bidpropertyentries WHERE bidpropertyentryid IN (SELECT bidpropertyentryid FROM v_not_rp_bpe);
-- delete from BIDPROPERTIES;
DELETE FROM bidproperties WHERE bidpropertyid IN (SELECT bidpropertyid FROM v_not_rp_bp);
-- delete from BIDS;
DELETE FROM bids WHERE bidsequenceid IN (SELECT bidsequenceid FROM v_not_rp_bids);
-- delete from BIDGROUPS;
DELETE FROM bidgroups WHERE userid IN (SELECT userid FROM v_not_rp_ui);


-- Dropping views
DROP VIEW v_not_rp_ug;
DROP VIEW v_not_rp_ui;
DROP VIEW v_not_rp_bg;
DROP VIEW v_not_rp_bids;
DROP VIEW v_not_rp_bp;
DROP VIEW v_not_rp_bpe;
