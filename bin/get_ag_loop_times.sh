#!/bin/sh
# Looks in files called alertgenerator.SAS_ALERT_[0-9].*.* (without number at the end)
# changed the last interval minutes
# and searches for the string:
#  Thu, 26 Feb 2009 11:57:02 INFO AlertGenerator::getAlertListFromIllegal::
#  Rave illegality sp_crrs found 4519 alerts in 2(2)s (Rave 1(1)s)

# It collects the diff in seconds between two of these rows 
# (and takes into account the sp_crew and sp_crrs logs)
# and nr of alerts and given times.

# The data is averaged over the interval and written to
# $CARMTMP/performace/ag_loop_time/alertgenerator.SAS_ALERT_[0-9].*.*.xml
# One file per alertgenerator is written!

usage(){
echo -e "USAGE: get_ag_loop_times.sh option dir|file [interval] 

xml)
This script looks in alergenerator logfiles and parses loop-times
The arguments are:  dir and [interval] 
where dir is the logdir to search for logfiles and interval (in minutes)
is the timeinterval to average over. 
Will only look at logfiles changed in the last interval minutes.
Default interval is 5 minutes

csv)
Print csv-summary of given xml-file file for easy excel-pasting!

csv_h)
Print last <interval> loops as csv-summary of given dir to stdout
"

}

if [ $# -lt 1 ]; then usage; exit 1;fi




function _parse_ag_log_file () {

    # remove all unwanted lines
    # Lines we look for is in this format (but no linebreak):
    #  Thu, 26 Feb 2009 11:57:02 INFO AlertGenerator::getAlertListFromIllegal::
    #  Rave illegality sp_crrs found 4519 alerts in 2(2)s (Rave 1(1)s)
    # Put result in tmp-file
    _tmp=`mktemp`
    rm ${_tmp} 2>/dev/null
    grep -e 'getAlertListFromIllegal.*sp_cr' $1>${_tmp}

    #Assume logfile is sorted by timestamps
    _last_time_s=0
    _time_array=() # timestamps diff
    _crew_0_array=() # alerts
    _crew_1_array=() # real loop time
    _crew_2_array=() # cpu time
    _crew_3_array=() # rave real time
    _crew_4_array=() # rave cpu time
    _crr_0_array=() # alerts
    _crr_1_array=() # real loop time
    _crr_2_array=() # cpu time
    _crr_3_array=() # rave real time
    _crr_4_array=() # rave cpu time
    _ix=0
    _init_skip_flag=-1
    while read _time_line; do
	# Parse log into shell variables
	# Format is '%d %b % Y %H:%M%S'
	_time_stamp=`echo ${_time_line} | sed -r 's/^[A-Z][a-z][a-z]\, (.*) INFO.*$/\1/g'`
	_area=`echo ${_time_line} | sed -r 's/.*(sp_crew|sp_crr).*/\1/g'`
	# 0=no of alerts, 1=real looptime, 2=cpu looptime, 3=real ravetime, 4=rave cpu time
	_log_ints=(`echo ${_time_line} | sed -r 's/.*found(.*)$/\1/g' | tr -c [:digit:] " "`)
	# Timestamp in seconds
	_time_stamp_s=`date -d "${_time_stamp} UTC" +%s`
	# First two loops if first timestamp is in interval, set "baseline" for timestamps!
	# Bit of an hack, but hey!
	if [[ ${_init_skip_flag} -le 0 && ${_time_stamp_s} -ge ${_interval_begin_s} ]]; then
	    if [ ${_area} = 'sp_crew' ]; then
		_last_time_s=${_time_stamp_s}
	    fi
	    let "_init_skip_flag += 1" #Skip next sp_crr as well
	    continue
	fi
	
	# Sort values into arrays if timestamp in interval
	if [ ${_time_stamp_s} -ge ${_interval_begin_s} ]; then
	    case ${_area} in
		    'sp_crew') 
	                _time_array[${_ix}]=`expr ${_time_stamp_s} - ${_last_time_s}`
			_crew_0_array[${_ix}]=${_log_ints[0]} # alerts
			_crew_1_array[${_ix}]=${_log_ints[1]} # real loop time
			_crew_2_array[${_ix}]=${_log_ints[2]} # cpu time
			_crew_3_array[${_ix}]=${_log_ints[3]} # rave real time
			_crew_4_array[${_ix}]=${_log_ints[4]} # rave cpu time 		
			;;
		    'sp_crr') 
			_crr_0_array[${_ix}]=${_log_ints[0]} # alerts
			_crr_1_array[${_ix}]=${_log_ints[1]} # real loop time
			_crr_2_array[${_ix}]=${_log_ints[2]} # cpu time
			_crr_3_array[${_ix}]=${_log_ints[3]} # rave real time
			_crr_4_array[${_ix}]=${_log_ints[4]} # rave cpu time 
			# Increase index every other row (sp_crew is followed by sp_crr)
			let "_ix += 1" 
				;;
		    *) continue ;;#should not happen
	    esac
	fi
	#Only measure between crew log rows
	if [ ${_area} = 'sp_crew' ]; then
	    _last_time_s=${_time_stamp_s}
	    #_last_time=${_time_stamp}
	fi
    done < ${_tmp} #Insert tmp-file here!
    # Done with tmp-file!
    rm ${_tmp} 2>/dev/null
    # Ok, now we got the values for last ${_interval} minutes in arrays
 
    _count=${#_time_array[*]}
    # Zero-init
    _time=0; _crew_0=0; _crew_1=0; _crew_2=0; 
    _crew_3=0; _crew_4=0; _crr_0=0;  _crr_1=0;
    _crr_2=0;  _crr_3=0;  _crr_4=0
    # sum it up
    for (( i=0 ; i < ${_count} ; i++ ));do 
	let "_time += ${_time_array[$i]}"
	let "_crew_0 += ${_crew_0_array[$i]}"
	let "_crew_1 += ${_crew_1_array[$i]}"
	let "_crew_2 += ${_crew_2_array[$i]}"
	let "_crew_3 += ${_crew_3_array[$i]}"
	let "_crew_4 += ${_crew_4_array[$i]}"
	let "_crr_0 += ${_crr_0_array[$i]}"
	let "_crr_1 += ${_crr_1_array[$i]}"
	let "_crr_2 += ${_crr_2_array[$i]}"
	let "_crr_3 += ${_crr_3_array[$i]}"
	let "_crr_4 += ${_crr_4_array[$i]}"
    done
    # In case no loop parsed, don't divide by zero
    if [ ${_count} -gt 0 ]; then
	_time=`echo "scale=2; ${_time}/${_count}" | bc -l`;echo "Loop time avg: "$_time
	_crew_0=`echo "scale=2; ${_crew_0}/${_count}" | bc -l`;#echo "Alerts crew avg: "$_crew_0
	_crew_1=`echo "scale=2; ${_crew_1}/${_count}" | bc -l`;#echo "Real time crew avg: "$_crew_1
	_crew_2=`echo "scale=2; ${_crew_2}/${_count}" | bc -l`;#echo "CPU time crew avg: "$_crew_2
	_crew_3=`echo "scale=2; ${_crew_3}/${_count}" | bc -l`;#echo "Rave time crew avg: "$_crew_3
	_crew_4=`echo "scale=2; ${_crew_4}/${_count}" | bc -l`;#echo "Rave CPU time crew avg: "$_crew_4
	_crr_0=`echo "scale=2; ${_crr_0}/${_count}" | bc -l`;#echo "Alerts crr avg: "$_crr_0
	_crr_1=`echo "scale=2; ${_crr_1}/${_count}" | bc -l`;#echo "Real time crr avg: "$_crr_1
	_crr_2=`echo "scale=2; ${_crr_2}/${_count}" | bc -l`;#echo "CPU time crr avg: "$_crr_2
	_crr_3=`echo "scale=2; ${_crr_3}/${_count}" | bc -l`;#echo "Rave time crr avg: "$_crr_3
	_crr_4=`echo "scale=2; ${_crr_4}/${_count}" | bc -l`;#echo "Rave CPU time crr avg: "$_crr_4
    fi
    # Output to logfile

    _out_file=${_out_dir}`basename $1`".xml"
    # if no file exists, create one with xml-tag open
    if [[ ! ( -e  ${_out_file} ) ]]; then
	echo '<?xml version="1.0" encoding="ISO-8859-1" ?>' > ${_out_file}
	echo "<alert_loop_times>" >> ${_out_file}
    else
	#else remove last tag before filling new data!
	sed -i 's,</alert_loop_times>,,g' ${_out_file}
    fi
    echo '<avg_values timestamp="'`date -u +'%Y-%m-%d %H:%M'`'" interval="'${_interval}'">' >> ${_out_file}
    echo '<time>'${_time}'</time>' >> ${_out_file}
    echo '<loops>'${_count}'</loops>'>> ${_out_file}
    echo '<crew>'>> ${_out_file}
    echo '<alerts>'${_crew_0}'</alerts>'>> ${_out_file}
    echo '<real_time>'${_crew_1}'</real_time>'>> ${_out_file}
    echo '<cpu_time>'${_crew_2}'</cpu_time>'>> ${_out_file}
    echo '<rave_time>'${_crew_3}'</rave_time>'>> ${_out_file}
    echo '<rave_cpu_time>'${_crew_4}'</rave_cpu_time>'>> ${_out_file}
    echo '</crew>' >> ${_out_file}
    echo '<crrs>' >> ${_out_file}
    echo '<alerts>'${_crr_0}'</alerts>'>> ${_out_file}
    echo '<real_time>'${_crr_1}'</real_time>'>> ${_out_file}
    echo '<cpu_time>'${_crr_2}'</cpu_time>'>> ${_out_file}
    echo '<rave_time>'${_crr_3}'</rave_time>'>> ${_out_file}
    echo '<rave_cpu_time>'${_crr_4}'</rave_cpu_time>'>> ${_out_file}
    echo '</crrs>'>> ${_out_file}
    echo '</avg_values>'>> ${_out_file}
    # Restore final tag
    echo '</alert_loop_times>' >> ${_out_file}

    #echo $_out_file
    
}

function _parse_files()
{
    # Initial setups
    #Clear trailing / and replace 
    _in_dir="${1%/}/"
    _out_dir="${1%/}/performance/ag_loop_time/"
    mkdir -p $_out_dir
    
    _interval=`echo $2 | tr -d [:alpha:]`
    if [ -z ${_interval} ]; then
	_interval=5 #Default case
    fi
    
    _interval_s=`expr ${_interval} \* 60`
    _now_s=`date -u +%s`
    _interval_begin_s=`expr ${_now_s} - ${_interval_s}`
   # Get alertgenerator logfile changed since 
   # last run and filter away old log files
    _log_files=`find ${_in_dir} -mmin -${_interval} -maxdepth 1 |
	    sed '/.*alertgenerator.SAS_ALERT_.*/!d' | 
	    sed '/.*alertgenerator.SAS_ALERT_[0-9].*\.[0-9]$/d' |
	    sed '/.*alertgenerator.SAS_ALERT_[0-9].*studio.*$/d'`

    for _file in ${_log_files}; do
	now=`date -u +'%Y-%m-%d %H:%M'`
	echo $now
	echo $_file
	_parse_ag_log_file $_file
    done
}

function _get_loop_times_as_csv()
{
    _in_file=$1
    _out_xsl=`mktemp`
    echo -e "<xsl:stylesheet version=\"1.0\" xmlns:xsl=\"http://www.w3.org/1999/XSL/Transform\">
<xsl:output method=\"text\"/>

<xsl:variable name=\"newline\">
<xsl:text>
</xsl:text>
</xsl:variable>

<xsl:template match=\"/\">
<xsl:text>\"datestamp\",\"timestamp\", \"looptime\",\"number of loops\",\"crew alerts\",\"crr alerts\",
</xsl:text>
<xsl:apply-templates/>
</xsl:template>

<xsl:template match=\"/alert_loop_times\">
  <xsl:for-each select=\"avg_values\">
   <xsl:value-of select=\"concat('&quot;',substring-before(@timestamp,' '),'&quot;, ')\"/>
   <xsl:value-of select=\"concat('&quot;',substring-after(@timestamp,' '),'&quot;, ')\"/>
   <xsl:value-of select=\"concat('&quot;',time,'&quot;, ')\"/>
   <xsl:value-of select=\"concat('&quot;',loops,'&quot;,')\"/>
   <xsl:value-of select=\"concat('&quot;',crew/alerts,'&quot;,')\"/>
   <xsl:value-of select=\"concat('&quot;',crrs/alerts,'&quot;,')\"/>
   <xsl:value-of select=\"\$newline\"/>
  </xsl:for-each>
  <xsl:text>&#10;</xsl:text>
</xsl:template>
</xsl:stylesheet>
"  > ${_out_xsl}
    xsltproc ${_out_xsl} ${_in_file}
    rm ${_out_xsl} 2>/dev/null
}

function _get_loop_times_as_csv_hourly()
{
    if [[ "z$2" == "z" ]]; then
	_lines=24
    else
	_lines=$2
    fi
    _files=`find $1 -name "*SAS_ALERT*.xml" | sort`
    for _file in ${_files[*]};do
	echo ${_file}
	_get_loop_times_as_csv ${_file} | tail -n${_lines}
    done
}

case $1 in
    xml)
	_parse_files $2 $3;;
    csv)
	_get_loop_times_as_csv $2;;
    csv_h) _get_loop_times_as_csv_hourly $2 $3;;
    *) usage ;;
esac
exit 0


