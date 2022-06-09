@TRACKING
Feature: Testing rules related to FS placement in relation to VA and other activities. SKCMS-1915 introduces a length check
for VA and other activities, SKCMS-2001 adds F0 as an activity to take into account and SKCMS-1947 adds an exception when 
placing FS directly before VA activities.
########################################################################
# SKCMS-1915, SKCMS-2001, SKCMS-1947, SKWD-273
########################################################################

  Background: Set up for tracking
    Given Tracking
    Given planning period from 1Oct2018 to 31Oct2018

    ###################################################################################################
    # Scenarios that shall pass for FD
    ###################################################################################################
        @FC @FS @FC_PASS_1 @VG
        Scenario: Case passes if FS are placed at least 6 days before and at least 3 days after whenever
        the other activity is equal or longer than 7 days. Crew shall be in agmt group VG.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00265"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 8OCT2018 22:00 and ends at 9OCT2018 22:00
        Given crew member 1 has a personal activity "LA" at station "ARN" that starts at 16OCT2018 22:00 and ends at 23OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 26OCT2018 22:00 and ends at 27OCT2018 22:00

        When I show "crew" in window 1
        #When I load rule set "rule_set_jcr_fc"
        #When I set parameter "fundamental.%start_para%" to "1OCT2018 00:00"
        #When I set parameter "fundamental.%end_para%" to "31OCT2018 00:00"
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 3 on roster 1
        and rave "rules_indust_ccr.%valid_activity%" shall be "True" on leg 1 on trip 2 on roster 1


    ###################################################################################################

        @FC @FS @FC_PASS_2 @VG
        Scenario: Case passes if FS are placed 5 days or less prior to or 2 days or less after
        other activity with length less than 7 days. Crew shall be in agmt group VG.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00265"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 13OCT2018 22:00 and ends at 14OCT2018 22:00
        Given crew member 1 has a personal activity "LA" at station "ARN" that starts at 15OCT2018 22:00 and ends at 19OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 19OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 3 on roster 1


    ######################################################################################################

        @FC @FW @ @FC_PASS_3
        Scenario: Case passes if FW are placed at least 6 days before whenever
        the other activity is equal or longer than 7 days. Crew shall be in agmt group VG.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00265"

        Given crew member 1 has a personal activity "F" at station "ARN" that starts at 2OCT2018 22:00 and ends at 3OCT2018 22:00
        Given crew member 1 has a personal activity "F" at station "ARN" that starts at 3OCT2018 22:00 and ends at 4OCT2018 22:00
        Given crew member 1 has a personal activity "FW" at station "ARN" that starts at 5OCT2018 22:00 and ends at 6OCT2018 22:00
        Given crew member 1 has a personal activity "FW" at station "ARN" that starts at 6OCT2018 22:00 and ends at 7OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 14OCT2018 22:00 and ends at 21OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 4 on roster 1

    ####################################################################################################

        @FC @FS @FW @VG @FC_PASS_4
        Scenario: Case passes if FW are placed incorrectly before other activity that is less than 7 days when FD is in agmt group VG.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00265"

        Given crew member 1 has a personal activity "LA" at station "ARN" that starts at 16OCT2018 22:00 and ends at 19OCT2018 22:00
        Given crew member 1 has a personal activity "FW" at station "ARN" that starts at 19OCT2018 22:00 and ends at 21OCT2018 22:00

        When I show "crew" in window 1
        Then rave "crew.%in_variable_group_trip_start%" shall be "True" on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fw_can_be_granted_sk_fd" shall pass on leg 1 on trip 2 on roster 1

    ####################################################################################################

        @FC @FS @FW @VG @FC_PASS_5
        Scenario: Case passes if FW are placed incorrectly after other activity that is less than 7 days when FD is in agmt group VG.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00265"

        Given crew member 1 has a personal activity "FW" at station "ARN" that starts at 19OCT2018 22:00 and ends at 21OCT2018 22:00
        Given crew member 1 has a personal activity "LA" at station "ARN" that starts at 23OCT2018 22:00 and ends at 26OCT2018 22:00

        When I show "crew" in window 1
        Then rave "crew.%in_variable_group_trip_start%" shall be "True" on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fw_can_be_granted_sk_fd" shall pass on leg 1 on trip 1 on roster 1
        
    
    ###################################################################################################
    # Scenarios that shall fail for FD
    ###################################################################################################

        @FC @FS @VG @FC_FAIL_1
        Scenario: Case fails if FS are placed 2 days or less after other activity with length
        equal or longer than 7 days that is splitted VA and VA1 activity. Crew shall be in agmt group VG.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00863"

        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 15OCT2018 22:00 and ends at 20OCT2018 22:00
        Given crew member 1 has a personal activity "VA1" at station "ARN" that starts at 20OCT2018 22:00 and ends at 22OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 22OCT2018 22:00 and ends at 23OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 3 on roster 1
    
    ####################################################################################################

        @FC @FS @VG @FC_FAIL_2
        Scenario: Case fails if FS are placed 2 days or less after other activity with length
        equal or longer than 7 days. Crew shall be in agmt group VG.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00863"

        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 15OCT2018 22:00 and ends at 22OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 22OCT2018 22:00 and ends at 23OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

     ###################################################################################################

        @FC @FW @VG @FC_FAIL_3
        Scenario: Case fails if FW are placed 2 days or less after other activity with length
        equal or longer than 7 days. Crew shall be in agmt group VG.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00863"

        Given crew member 1 has a personal activity "LA" at station "ARN" that starts at 17OCT2018 22:00 and ends at 24OCT2018 22:00
        Given crew member 1 has a personal activity "FW" at station "ARN" that starts at 26OCT2018 22:00 and ends at 28OCT2018 23:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fw_can_be_granted_sk_fd" shall fail on leg 1 on trip 2 on roster 1

     ###################################################################################################

        @FC @FW @VG @FC_FAIL_4
        Scenario: Case fails if FW are placed 4 days or less before other activity with length
        equal or longer than 7 days. Crew shall be in agmt group VG.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00863"

        Given crew member 1 has a personal activity "FW" at station "ARN" that starts at 19OCT2018 23:00 and ends at 21OCT2018 23:00
        Given crew member 1 has a personal activity "LA" at station "ARN" that starts at 23OCT2018 22:00 and ends at 31OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fw_can_be_granted_sk_fd" shall fail on leg 1 on trip 1 on roster 1
        
    ###################################################################################################

       @FC @FW @FS @VG @FC_FAIL_5
       Scenario: Case fails if FW are placed 5 days or less before and FS 2 days or less after other splitted activity with length
       equal or longer than 7 days. Crew shall be in agmt group VG.

       Given a crew member with
       | attribute  | value   | valid from  | valid to  |
       | base       | STO     |             |           |
       | title rank | FP      |             |           |
       | region     | SKS     |             |           |
       Given crew member 1 has contract "V00863"

       Given crew member 1 has a personal activity "FW" at station "ARN" that starts at 12OCT2018 22:00 and ends at 14OCT2018 22:00
       Given crew member 1 has a personal activity "LA" at station "ARN" that starts at 17OCT2018 22:00 and ends at 20OCT2018 22:00
       Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 20OCT2018 22:00 and ends at 22OCT2018 22:00
       Given crew member 1 has a personal activity "F7" at station "ARN" that starts at 22OCT2018 22:00 and ends at 24OCT2018 22:00
       Given crew member 1 has a personal activity "LA66" at station "ARN" that starts at 24OCT2018 22:00 and ends at 26OCT2018 22:00
       Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 28OCT2018 22:00 and ends at 29OCT2018 22:00

       When I show "crew" in window 1
       Then the rule "rules_indust_ccr.ind_fw_can_be_granted_sk_fd" shall fail on leg 1 on trip 1 on roster 1
       and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 6 on roster 1
       
   ###################################################################################################

       @FC @FW @FS @VG @FC_FAIL_6
       Scenario: Case fails if FW are placed 5 days or less before and FS 2 days or less after other splitted activity with length
       equal to 7 days. Crew shall be in agmt group VG. Activity combination is VA and LA

       Given a crew member with
       | attribute  | value   | valid from  | valid to  |
       | base       | STO     |             |           |
       | title rank | FP      |             |           |
       | region     | SKS     |             |           |
       Given crew member 1 has contract "V00863"

       Given crew member 1 has a personal activity "FW" at station "ARN" that starts at 12OCT2018 22:00 and ends at 14OCT2018 22:00
       Given crew member 1 has a personal activity "LA" at station "ARN" that starts at 16OCT2018 22:00 and ends at 18OCT2018 22:00
       Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 18OCT2018 22:00 and ends at 23OCT2018 22:00
       Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 25OCT2018 22:00 and ends at 26OCT2018 22:00

       When I show "crew" in window 1
       Then the rule "rules_indust_ccr.ind_fw_can_be_granted_sk_fd" shall fail on leg 1 on trip 1 on roster 1
       and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 4 on roster 1
      
  ###################################################################################################

       @FC @FW @FS @VG @FC_FAIL_7
       Scenario: Case fails if FW are placed 5 days or less before and FS 2 days or less after other splitted activity with length
       equal to 7 days. Crew shall be in agmt group VG. Activity combination is VA and F7

       Given a crew member with
       | attribute  | value   | valid from  | valid to  |
       | base       | STO     |             |           |
       | title rank | FP      |             |           |
       | region     | SKS     |             |           |
       Given crew member 1 has contract "V00863"

       Given crew member 1 has a personal activity "FW" at station "ARN" that starts at 12OCT2018 22:00 and ends at 14OCT2018 22:00
       Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 16OCT2018 22:00 and ends at 19OCT2018 22:00
       Given crew member 1 has a personal activity "F7" at station "ARN" that starts at 19OCT2018 22:00 and ends at 23OCT2018 22:00
       Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 25OCT2018 22:00 and ends at 26OCT2018 22:00

       When I show "crew" in window 1
       Then the rule "rules_indust_ccr.ind_fw_can_be_granted_sk_fd" shall fail on leg 1 on trip 1 on roster 1
       and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 4 on roster 1

    ###################################################################################################
    # Scenarios that shall pass for CC
    ###################################################################################################
        @CC @FS @VG @CC_PASS_1
        Scenario: Case passes if FS are placed at least 5 days before and at least 3 days after
        other activity such as VA at a minimum length of 5 days. Crew shall be in agmt group VG.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AH      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00262"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 9OCT2018 22:00 and ends at 10OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 16OCT2018 22:00 and ends at 23OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 26OCT2018 22:00 and ends at 27OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1

    ###################################################################################################

        @CC @FS @VG @CC_PASS_2
        Scenario: Case passes if FS are placed less than 5 days prior and less than 3 days
        after other activity such as VA or LA at maximum length of 4 days. Crew shall be in agmt group VG

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AH      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00262"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 14OCT2018 22:00 and ends at 15OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 16OCT2018 22:00 and ends at 18OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 19OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1

    ##################################################################################################

        @CC @F0 @VG @SKN @CC_PASS_3 @CC_F0
        Scenario: Case passes if F0 are placed at least 5 days before F0 at
        a minimum length of 5 days. Crew shall be CC in agmt group VG and SKN

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 9OCT2018 22:00 and ends at 10OCT2018 22:00
        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 16OCT2018 22:00 and ends at 21OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

    ###################################################################################################

        @CC @F0 @VG @SKN @CC_PASS_4 @CC_F0
        Scenario: Case passes if F0 are placed at least 3 days after F0 at
        a minimum length of 5 days. Crew shall be CC in agmt group VG and SKN

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"


        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 16OCT2018 22:00 and ends at 21OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 24OCT2018 22:00 and ends at 25OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1
        and rave "duty.%is_F0%" shall be "True" on leg 1 on trip 1 on roster 1

   ###################################################################################################

        @CC @F0 @VG @SKN @CC_PASS_5 @CC_F0
        Scenario: Case passes if F0 are placed less than 3 days after F0 at
        a maximum length of 4 days. Crew shall be CC in agmt group VG and SKN

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"


        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 18OCT2018 22:00 and ends at 21OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 22OCT2018 22:00 and ends at 23OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1


    ###################################################################################################

        @CC @F0 @VG @SKN @CC_PASS_6 @CC_F0
        Scenario: Case passes if F0 are placed less than 5 days before F0 at
        a maximum length of 4 days. Crew shall be CC in agmt group VG and SKN

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 17OCT2018 22:00 and ends at 18OCT2018 22:00
        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 18OCT2018 22:00 and ends at 21OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

     ###################################################################################################

        @CC @FS @VG @SKD @CC_PASS_7
        Scenario: Case passes if FS is placed less than 5 days before another activity (VA) at
        a maximum length of 4 days. Crew shall be CC in agmt group VG and SKD

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V11"

        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 17OCT2018 22:00 and ends at 18OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 18OCT2018 22:00 and ends at 21OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

    ###################################################################################################

        @CC @VG @SKN @CC_PASS_8 @SKCMS-1910
        Scenario: Case passes if FS is placed on weekend directly after VA longer than 6 days. Test for SKCMS-1910

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 12OCT2018 22:00 and ends at 19OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 19OCT2018 22:00 and ends at 21OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

     ###################################################################################################

        @CC @VG @SKN @CC_PASS_9 @SKCMS-1910
        Scenario: Case passes if FS1 is placed on weekend directly after VA longer than 6 days. Test for SKCMS-1910

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 12OCT2018 22:00 and ends at 19OCT2018 22:00
        Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 19OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

     ###################################################################################################

        @CC @VG @SKN @CC_PASS_10
        Scenario: Case passes if FS1 is placed at least 5 days prior to VA at length of at least 5 days

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 6OCT2018 22:00 and ends at 7OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 12OCT2018 22:00 and ends at 19OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1

    ###################################################################################################

        @CC @VG @SKN @CC_PASS_11
        Scenario: Case passes if FS is placed on fri-sun directly after VA longer than 6 days. SKWD-273

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

       	Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 12OCT2018 22:00 and ends at 18OCT2018 22:00
       	Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 18OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 2 on roster 1

      ###################################################################################################

        @CC @VG @SKN @CC_PASS_12
        Scenario: Case passes if FS1 is placed at least 3 days after VA at length of at least 5 days

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 6OCT2018 22:00 and ends at 12OCT2018 22:00
        Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 19OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

    ###################################################################################################
    # Scenarios that shall fail for CC
    ###################################################################################################

        @CC @FS @VG @CC_FAIL_1
        Scenario: Case fails if FS are placed less than 5 days prior other activity such as
        VA or LA with length of at least 5 days. Crew shall be in agmt group VG

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AA      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00262"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 12OCT2018 22:00 and ends at 13OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 16OCT2018 22:00 and ends at 23OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1

    ######################################################################################################

        @CC @FS @VG @CC_FAIL_2
        Scenario: Case fails if FS are placed less than 3 days after other activity such as
        VA or LA with length of at least 5 days. Crew shall be in agmt group VG

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AA      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00262"

        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 19OCT2018 22:00 and ends at 26OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 26OCT2018 22:00 and ends at 27OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

    ###################################################################################################

        @CC @FS @F0 @CC_FAIL_3 @CC_F0
        Scenario: Case fails if FS are placed less than 5 days before F0 at
        a minimum length of 5 days. Crew shall be in agmt group VG and SKN

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 14OCT2018 22:00 and ends at 15OCT2018 22:00
        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 16OCT2018 22:00 and ends at 21OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1

    ###################################################################################################

        @CC @FS @F0 @CC_FAIL_4 @CC_F0
        Scenario: Case fails if FS are placed less than 3 days after a period of F0 days of minimum length of 5.
        Crew shall be in agmt group VG and SKN

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 16OCT2018 22:00 and ends at 21OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 21OCT2018 22:00 and ends at 22OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

    ###################################################################################################

        @CC @FS1 @CC_FAIL_5
        Scenario: Case fails if FS1 are placed less than 3 days after a period of VA days of minimum length of 5.
        Crew shall be in agmt group VG and SKN

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 14OCT2018 22:00 and ends at 19OCT2018 22:00
        Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 19OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

    ###################################################################################################

        @CC @FS1 @CC_FAIL_6
        Scenario: Case fails if FS1 are placed less than 5 days before a period of VA days of minimum length of 5.
        Crew shall be in agmt group VG and SKN

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 6OCT2018 22:00 and ends at 7OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 9OCT2018 22:00 and ends at 22OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1

    ###################################################################################################

        @CC @FS1 @F0 @CC_FAIL_7 @CC_F0
        Scenario: Case fails if FS1 are placed less than 3 days after a period of F0 days of minimum length of 5.
        Crew shall be in agmt group VG and SKN

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 13OCT2018 22:00 and ends at 18OCT2018 22:00
        Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 19OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

    ###################################################################################################

        @CC @FS1 @F0 @CC_FAIL_8 @CC_F0
        Scenario: Case fails if FS are placed less than 5 days before a period of F0 days of minimum length of 5.
        Crew shall be in agmt group VG and SKN

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "FS1" at station "OSL" that starts at 6OCT2018 22:00 and ends at 7OCT2018 22:00
        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 9OCT2018 22:00 and ends at 14OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1

        ###################################################################################################

        @CC @FS @F0 @CC_FAIL_9 @CC_F0
        Scenario: Case fails if FS are placed less than 5 days before a period of F0 and VA days of minimum length of 5.
        Crew shall be in agmt group VG and SKN

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 6OCT2018 22:00 and ends at 7OCT2018 22:00
        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 9OCT2018 22:00 and ends at 11OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 11OCT2018 22:00 and ends at 16OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1
        
        ###################################################################################################

        @CC @FS @F0 @CC_FAIL_10
        Scenario: Case fails if FS are placed less than 5 days before and less than 3 days after a period of a splitted activity of minimum length of 5.
        Crew shall be in agmt group VG and SKN

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 6OCT2018 22:00 and ends at 7OCT2018 22:00
        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 9OCT2018 22:00 and ends at 10OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 10OCT2018 22:00 and ends at 12OCT2018 22:00
        Given crew member 1 has a personal activity "F7" at station "OSL" that starts at 12OCT2018 22:00 and ends at 16OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 18OCT2018 22:00 and ends at 19OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 5 on roster 1
        
        ###################################################################################################

        @CC @FS @F0 @CC_FAIL_11
        Scenario: Case fails if FS are placed less than 5 days before and less than 3 days after a period of a splitted activity with length of 5 days.
        Crew shall be in agmt group VG and SKN

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "V00204"

        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 6OCT2018 22:00 and ends at 7OCT2018 22:00
        Given crew member 1 has a personal activity "F0" at station "OSL" that starts at 9OCT2018 22:00 and ends at 10OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "OSL" that starts at 10OCT2018 22:00 and ends at 12OCT2018 22:00
        Given crew member 1 has a personal activity "F7" at station "OSL" that starts at 12OCT2018 22:00 and ends at 14OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "OSL" that starts at 16OCT2018 22:00 and ends at 17OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 5 on roster 1


     ###################################################################################################
     # Special cases
     ###################################################################################################

        @CC @VG @SKD @SINGLE_FS_WEEKEND
        Scenario: Saturday FS passes if full FS weekend when VA longer than 5 days are placed at least 5 days after Saturday.
        Crew shall be SKD. Case is OK for SKS and SKD.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | CPH     |             |           |
        | title rank | AH      |             |           |
        | region     | SKD     |             |           |
        Given crew member 1 has contract "V12"

        Given crew member 1 has a personal activity "FS" at station "CPH" that starts at 5OCT2018 22:00 and ends at 6OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "CPH" that starts at 6OCT2018 22:00 and ends at 7OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "CPH" that starts at 11OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and  the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

    ######################################################################################################

        @CC @VG @SKS @SINGLE_FS_WEEKEND
        Scenario: Saturday FS passes if full FS weekend when VA longer than 5 days are placed at least 5 days after Saturday.
        Crew shall be SKS. Case is OK for SKS and SKD.8

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AH      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00262"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 5OCT2018 22:00 and ends at 6OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 6OCT2018 22:00 and ends at 7OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 11OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and  the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

    ######################################################################################################

        @CC @VG @SKS
        Scenario: First FS passes if 2 FS in row when VA longer than 5 days are placed at least 5 days after first day.
        Crew shall be SKS. Case is OK for SKS and SKD.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AH      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00262"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 1OCT2018 22:00 and ends at 2OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 3OCT2018 22:00 and ends at 4OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 7OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and  the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

    ######################################################################################################

        @CC @VG @SKS
        Scenario: First FS passes if 2 FS in row when VA longer than 5 days are placed at least 5 days after first day.
        Crew shall be SKS. Case is OK for SKS and SKD.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AH      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00262"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 1OCT2018 22:00 and ends at 2OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 3OCT2018 22:00 and ends at 4OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 7OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and  the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

    ######################################################################################################

        @CC @VG @SKS @FSEXCEPTION1
        Scenario: FS passes when placed 1 day before VA longer, or equal to, 5 days.
        Crew shall be SKS. Case is OK for SKS and SKD.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AH      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00262"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 3OCT2018 22:00 and ends at 4OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 4OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1

    ######################################################################################################

        @CC @VG @SKS @FSEXCEPTION2
        Scenario: FS passes when placed 1 and 2 days before VA longer, or equal to, 5 days.
        Crew shall be SKS. Case is OK for SKS and SKD.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AH      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00262"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 2OCT2018 22:00 and ends at 3OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 3OCT2018 22:00 and ends at 4OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 4OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

    ######################################################################################################

        @CC @VG @SKS @FSEXCEPTION3
        Scenario: FS fails when placed 1 and 2 days before LOA longer, or equal to, 5 days.
        Crew shall be SKS. Case is OK for SKS and SKD.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AH      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00262"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 2OCT2018 22:00 and ends at 3OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 3OCT2018 22:00 and ends at 4OCT2018 22:00
        Given crew member 1 has a personal activity "LA" at station "ARN" that starts at 4OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 2 on roster 1

    ######################################################################################################

        @CC @VG @SKS @FSEXCEPTION4
        Scenario: FS fails when placed outside of exception area, but passes inside.
        Crew shall be SKS. Case is OK for SKS and SKD.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AH      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00262"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 1OCT2018 22:00 and ends at 2OCT2018 22:00
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 2OCT2018 22:00 and ends at 3OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 4OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 2 on roster 1

    ######################################################################################################

        @CC @VG @SKS @FSEXCEPTION5
        Scenario: FS1 passes when placed right before VA.
        Crew shall be SKS. Case is OK for SKS and SKD.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AH      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00262"

        Given crew member 1 has a personal activity "FS1" at station "ARN" that starts at 7OCT2018 22:00 and ends at 8OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 8OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1

    ######################################################################################################

        @CC @VG @SKS @FSEXCEPTION6
        Scenario: FS1 fails when placed right before LA.
        Crew shall be SKS. Case is OK for SKS and SKD.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AH      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00262"

        Given crew member 1 has a personal activity "FS1" at station "ARN" that starts at 7OCT2018 22:00 and ends at 8OCT2018 22:00
        Given crew member 1 has a personal activity "LA" at station "ARN" that starts at 8OCT2018 22:00 and ends at 20OCT2018 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1

    ######################################################################################################

        @CC @VG @SKS @FSEXCEPTION7
        Scenario: FS fails when placed right before VA followed by F14 and crew is SKS_FD

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00265"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 3OCT2018 22:00 and ends at 4OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 4OCT2018 22:00 and ends at 20OCT2018 22:00
        Given crew member 1 has a personal activity "F14" at station "ARN" that starts at 20OCT2018 22:00 and ends at 21OCT2018 22:00
        
        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1

    ######################################################################################################

        @CC @VG @SKS @FSEXCEPTION8
        Scenario: FS fails when placed two days before VA followed by F14 for SKS_FD crew

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | FC      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has contract "V00265"

        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 2OCT2018 22:00 and ends at 3OCT2018 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 4OCT2018 22:00 and ends at 20OCT2018 22:00
        Given crew member 1 has a personal activity "F14" at station "ARN" that starts at 20OCT2018 22:00 and ends at 21OCT2018 22:00
        
        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1

    ###################################################################################################
    # Scenarios that shall pass for SKN CC >= 19 days Summer Vacation
    ###################################################################################################
        @FS @VG @19_VA_P1
        Scenario: Case passes if two fs days are placed saturday and sunday followed by two empty days, and then a vacation that is at least 19 days long. Crew shall be in agmt group VG.

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "SNK_V1030"

        Given crew member 1 has a personal activity "FS" at station "TRD" that starts at 28JUN2019 22:00 and ends at 30JUN2019 22:00
        Given crew member 1 has a personal activity "VA" at station "TRD" that starts at 02JUL2019 22:00 and ends at 23JUL2019 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 1 on roster 1

        ###################################################################################################
        @FS @VG @19_VA_P1.1
        Scenario: Case passes if two single fs days are placed saturday and sunday followed by two empty days, and then a vacation that is at least 19 days long. Crew shall be in agmt group VG.
        Given planning period from 1Jun2019 to 31Aug2019

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "SNK_V1030"

        Given crew member 1 has a personal activity "FS" at station "TRD" that starts at 28JUN2019 22:00 and ends at 29JUN2019 22:00
        Given crew member 1 has a personal activity "FS" at station "TRD" that starts at 29JUN2019 22:00 and ends at 30JUN2019 22:00
        Given crew member 1 has a personal activity "VA" at station "TRD" that starts at 02JUL2019 22:00 and ends at 17JUL2019 22:00
        Given crew member 1 has a personal activity "VA1" at station "TRD" that starts at 17JUL2019 22:00 and ends at 23JUL2019 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 2 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 2 on trip 1 on roster 1


        ###################################################################################################
        @FS @VG @19_VA_P1.2
        Scenario: Case passes if two FS1 days are placed saturday and sunday followed by two empty days, and then a vacation that is at least 19 days long. Crew shall be in agmt group VG.
        Given planning period from 1Jun2019 to 31Aug2019

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "SNK_V1030"

        Given crew member 1 has a personal activity "FS1" at station "TRD" that starts at 28JUN2019 22:00 and ends at 29JUN2019 22:00
        Given crew member 1 has a personal activity "FS1" at station "TRD" that starts at 29JUN2019 22:00 and ends at 30JUN2019 22:00
        Given crew member 1 has a personal activity "VA" at station "TRD" that starts at 02JUL2019 22:00 and ends at 17JUL2019 22:00
        Given crew member 1 has a personal activity "VA1" at station "TRD" that starts at 17JUL2019 22:00 and ends at 23JUL2019 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 2 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 2 on trip 1 on roster 1


        ###################################################################################################
        @FS @VG @19_VA_P2
        Scenario: Case passes if a single FS1 day is placed on sunday followed by two empty days, and then a vacation that is at least 19 days long. Crew shall be in agmt group VG.
        Given planning period from 1Jun2019 to 31Aug2019

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "SNK_V1030"

        Given crew member 1 has a personal activity "FS1" at station "TRD" that starts at 29JUN2019 22:00 and ends at 30JUN2019 22:00
        Given crew member 1 has a personal activity "VA" at station "TRD" that starts at 02JUL2019 22:00 and ends at 23JUL2019 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 1 on roster 1


        ###################################################################################################
        @FS @VG @19_VA_P3
        Scenario: Case passes if a single FS day is placed on monday followed by one empty day, and then a vacation that is at least 19 days long. Crew shall be in agmt group VG.
        Given planning period from 1Jun2019 to 31Aug2019


        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "SNK_V1030"

        Given crew member 1 has a personal activity "FS" at station "TRD" that starts at 30JUN2019 22:00 and ends at 01JUL2019 22:00
        Given crew member 1 has a personal activity "VA" at station "TRD" that starts at 02JUL2019 22:00 and ends at 23JUL2019 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 1 on roster 1


        ###################################################################################################
        @FS @VG @19_VA_P4
        Scenario: Case passes if a single FS day is placed on tuesday followed by 
        a vacation that is at least 19 days long. Crew shall be in agmt group VG.
        Given planning period from 1Jun2019 to 31Aug2019


        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "SNK_V1030"

        Given crew member 1 has a personal activity "FS" at station "TRD" that starts at 01JUL2019 22:00 and ends at 02JUL2019 22:00
        Given crew member 1 has a personal activity "VA" at station "TRD" that starts at 02JUL2019 22:00 and ends at 23JUL2019 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 1 on roster 1


        ###################################################################################################
        @FS @VG @19_VA_P5
        Scenario: Case passes if two fs days are placed on monday and tuesday followed by a
        vacation on wednesday that is at least 19 days long. Crew shall be in agmt group VG.
        Given planning period from 1Jun2019 to 31Aug2019

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "SNK_V1030"

        Given crew member 1 has a personal activity "FS" at station "TRD" that starts at 30JUN2019 22:00 and ends at 02JUL2019 22:00
        Given crew member 1 has a personal activity "VA" at station "TRD" that starts at 02JUL2019 22:00 and ends at 23JUL2019 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 1 on roster 1

        ###################################################################################################
        @FS @VG @19_VA_P6
        Scenario: Case passes if two fs days are placed saturday and sunday followed by two empty days, and then a vacation that is at least 19 days long. Crew shall be in agmt group VG.
        Given planning period from 1Jun2019 to 31Aug2019

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "SNK_V1030"

        Given crew member 1 has a personal activity "FS" at station "TRD" that starts at 27JUN2019 22:00 and ends at 30JUN2019 22:00
        Given crew member 1 has a personal activity "VA" at station "TRD" that starts at 02JUL2019 22:00 and ends at 23JUL2019 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall pass on leg 1 on trip 1 on roster 1
        and the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall pass on leg 1 on trip 1 on roster 1


    ###################################################################################################
    # Scenarios that shall fail for SKN CC >= 19 days Summer Vacation
    ###################################################################################################
        @FS @VG @19_VA_F1
        Scenario: Case fails when one fs day is placed on saturday followed by a
        vacation on wednesday. Crew shall be in agmt group VG.
        Given planning period from 1Jun2019 to 31Aug2019

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "SNK_V1030"

        Given crew member 1 has a personal activity "FS" at station "TRD" that starts at 28JUN2019 22:00 and ends at 29JUN2019 22:00
        Given crew member 1 has a personal activity "VA" at station "TRD" that starts at 02JUL2019 22:00 and ends at 23JUL2019 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_days_in_weekend_covers_both_saturday_and_sunday" shall fail on leg 1 on trip 1 on roster 1

        ###################################################################################################
        @FS @VG @19_VA_F2
        Scenario: Case fails when one fs day is placed on sunday followed by a
        vacation on wednesday. Crew shall be in agmt group VG.
        Given planning period from 1Jun2019 to 31Aug2019

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "SNK_V1030"

        Given crew member 1 has a personal activity "FS" at station "TRD" that starts at 29JUN2019 22:00 and ends at 30JUN2019 22:00
        Given crew member 1 has a personal activity "VA" at station "TRD" that starts at 02JUL2019 22:00 and ends at 23JUL2019 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_days_in_weekend_covers_both_saturday_and_sunday" shall fail on leg 1 on trip 1 on roster 1

        ###################################################################################################
        @FS @VG @19_VA_F3
        Scenario: Case fails when 19 days VA isn't in summer
        Given planning period from 01Feb2019 to 01Mar2019

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | OSL     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "SNK_V1030"

        Given crew member 1 has a personal activity "FS" at station "TRD" that starts at 1FEB2019 22:00 and ends at 3FEB2019 22:00
        Given crew member 1 has a personal activity "VA" at station "TRD" that starts at 5FEB2019 22:00 and ends at 27FEB2019 22:00

        When I show "crew" in window 1
        Then the rule "rules_indust_ccr.ind_fs_weekend_can_be_granted" shall fail on leg 1 on trip 1 on roster 1

        ###################################################################################################
        @FS @VG @19_VA_F4 @SKS
        Scenario: Case fails when 19 days VA for crew not SKN
        Given planning period from 01JUN2019 to 01AUG2019

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | STO     |             |           |
        | title rank | AH      |             |           |
        | region     | SKS     |             |           |
        Given crew member 1 has a personal activity "FS" at station "ARN" that starts at 29JUN2019 22:00 and ends at 30JUN2019 22:00
        Given crew member 1 has a personal activity "VA" at station "ARN" that starts at 2JUL2019 22:00 and ends at 21JUL2019 22:00

        When I show "crew" in window 1
        When I set parameter "rules_indust_ccr.%param_allow_fs_immediately_after_summer_va%" to "TRUE"
        When I set parameter "rules_indust_ccr.%param_allow_fs_immediately_before_summer_va%" to "TRUE"
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1

        ###################################################################################################
        @FS @VG @19_VA_F5
        Scenario: Case fails when an fs1 day is placed on saturday followed by a
        vacation on wednesday. Crew shall be in agmt group VG.
        Given planning period from 1Jun2019 to 31Aug2019

        Given a crew member with
        | attribute  | value   | valid from  | valid to  |
        | base       | TRD     |             |           |
        | title rank | AH      |             |           |
        | region     | SKN     |             |           |
        Given crew member 1 has contract "SNK_V1030"

        Given crew member 1 has a personal activity "FS1" at station "TRD" that starts at 28JUN2019 22:00 and ends at 29JUN2019 22:00
        Given crew member 1 has a personal activity "VA" at station "TRD" that starts at 02JUL2019 22:00 and ends at 23JUL2019 22:00

        When I show "crew" in window 1
        When I set parameter "rules_indust_ccr.%param_allow_fs_immediately_after_summer_va%" to "TRUE"
        When I set parameter "rules_indust_ccr.%param_allow_fs_immediately_before_summer_va%" to "TRUE"
        Then the rule "rules_indust_ccr.ind_fs_day_scheduled_correct_all" shall fail on leg 1 on trip 1 on roster 1


