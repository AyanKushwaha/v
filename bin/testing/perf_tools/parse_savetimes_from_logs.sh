#!/bin/sh

function parse_files()
{
    _time_diff=$1
    _data_file=$2
    rm ${_data_file} 2>/dev/null
    touch ${_data_file}
    _files=`find ${_dir} -maxdepth 1 -name ${_application} -mtime ${_time_diff} | xargs grep -l "${_look_for_in_log}"`
    _times=()
    _file_times=()
    _ix=0
    for _file in ${_files}; do
	_new_times=(`grep "${_look_for_in_log}" ${_file} | sed -r "s/^.*: (.*) s$/\1/g"`)
	_new_file_times=()
	for (( i=0 ; i<${#_new_times[*]} ; i++ ));do
	    _new_file_times[${i}]=`stat -c "%Y" ${_file}`
	done
	_times=(${_times[*]} ${_new_times[*]})
	_file_times=(${_file_times[*]} ${_new_file_times[*]})
    done
    _mean=0
    for _time in ${_times[@]}; do
	 _mean=`echo "scale=2; ${_mean} + ${_time}" | bc -l ` 
    done
    _cnt=${#_times[*]}
    if [ ${_cnt} -gt 0 ]; then
	_mean=`echo "scale=2; ${_mean} / ${_cnt}" | bc -l`
    fi
    if [ ${_cnt} -eq 0 ];then 
	echo `date +%s`", 0" >> ${_data_file}
    else
	for (( i=0 ; i<${_cnt} ; i++ )); do
	    `echo "${_file_times[${i}]}, ${_times[${i}]}" >> ${_data_file}`
	done 
    fi
    #`echo ${_times[*]} | tr " " "\n" | sort -n | awk -v OFS=' ' '{print FNR, $0}' > ${_data_file}` #transpose
    echo  "${_times[*]}" | tr " " "\n" | sort -n | tr "\n" " "
    echo "" 
    echo "Avg ${_look_for_in_log} for time_diff "${_time_diff}" is :"${_mean}" ("${_cnt}" samples)"
    
}

function parse_files_complete()
{
#*********************************************
#  Save Plan Times:
#    Total: 8.45 s (cpu: 4.08 s)
#    Passive booking run: 0.00 s (cpu: 0.00 s)
#    Training log run: 0.00 s (cpu: 0.00 s)
#    Accounthandler run: 0.00 s (cpu: 0.00 s)
#    Cleaning attributes tables: 0.03 s (cpu: 0.02 s)
#    Publish pre-processing: 0.03 s (cpu: 0.01 s)
#    Actual (sys) save: 5.27 s (cpu: 1.90 s)
#    Publish post-processing: 3.12 s (cpu: 2.14 s)
#*********************************************   
#*********************************************
#  Open Plan Times:
#    Total: 167.90 s (cpu: 162.96 s)
#    Loading parameters and rule set: 0.39 s (cpu: 0.36 s)
#    Getting to setDaveLoadFilter: 0.25 s (cpu: 0.07 s)
#    Setup of filter: 2.64 s (cpu: 1.01 s)
#    CARMSYS Loading time: 119.80 s (cpu: 127.22 s)
#    Starting JVM: 0.04 s (cpu: 0.01 s)
#    Preloading tables to model: 35.13 s (cpu: 25.86 s)
#    Create informed temptable: 2.71 s (cpu: 2.71 s)
#    Preloading tables to rave: 5.66 s (cpu: 5.25 s)
#    Copying activity codes to temporary Etable: 1.30 s (cpu: 0.48 s)
#*********************************************

    cmd="find ${_dir} -name '${_application}' | xargs grep -l '${_look_for_in_log}' > ${_out_file}"
    eval $cmd

    _OPEN_MATCHES=("Total:"
                   "CARMSYS Loading time:"
		   "Preloading tables to model:"
		   "Preloading tables to rave:")
    _SAVE_MATCHES=("Total:"
	"Passive booking run:"
	"Training log run:"
	"Accounthandler run:"
	"Cleaning attributes tables:"
	"Publish pre-processing:"
	"Actual (sys) save:"
	"Publish post-processing:")
   # _nr_open_matches=${#_OPEN_MATCHES[*]}
    _nr_save_matches=${#_SAVE_MATCHES[*]}
    _header='File, Start, End, Days, Area, Datestamp, Timestamp, '
 #   for (( i=0 ; i<${_nr_open_matches} ; i++ )); do
#	_txt=`echo ${_OPEN_MATCHES[$i]} | tr -d [:punct:] | tr " " "_"`
#	_header=${_header}'Open_'${_txt}'_REAL, Open_'${_txt}'_CPU, '
#    done
    for (( i=0 ; i<${_nr_save_matches} ; i++ )); do
	_txt=`echo ${_SAVE_MATCHES[$i]} | tr -d [:punct:] | tr " " "_"`
	_header=${_header}'Save_'${_txt}'_REAL, Save_'${_txt}'_CPU, '
    done
    echo ${_header}
    while read _file; do
	_nr_saves=`grep "${_look_for_in_log}" ${_file} | wc -l` 
	_lines=()
	_start=`grep 'DaveFilterTool.py:: Set Filter: period.start = ' ${_file} | cut -d " " -f6`
	_end=` grep 'DaveFilterTool.py:: Set Filter: period.end = ' ${_file} | cut -d " " -f6`
	_start_s=`date -d "${_start}" +%s`
	_end_s=`date -d "${_end}" +%s`
	_length=`echo "scale=0;(${_end_s} - ${_start_s}) / ( 60 * 60 * 24 )" | bc -l`
	_area=`grep "'PLANNINGAREA':" ${_file} | tr -d ",'" | cut -d " " -f2` 
	if [ -z ${_area} ]; then
	    _area=`grep 'DaveFilterTool.py:: Set Filter: crew_user_filter_cct.rankregion1 = ' ${_file} | cut -d " " -f6 | tr -d "_|"`
	    if [ -z ${_area} ]; then
		_area='ALL'
	    fi
	fi
	_date=`echo ${_file} | cut -d "." -f4 | sed -r 's/([0-9]{4})([0-9]{2})([0-9]{2})/\1-\2-\3/g'`
	_time=`echo ${_file} | cut -d "." -f5 | sed -r 's/([0-9]{2})([0-9]{2})/\1:\2:00/g'`
	for (( i=0 ; i<${_nr_saves} ; i++ )); do
	    _lines[$i]=${_file}', '${_start}', '${_end}', '${_length}', '${_area}', ' 
	done
#	cslDispatcher: dispatching PythonEvalExpr("carmensystems.studio.Tracking.OpenPlan.savePlan()")
	
#	for (( j=0 ; j<${_nr_open_matches} ; j++ )); do
#	    _real=`grep -A10 'Open Plan Times:' ${_file} | \
#                   grep "${_OPEN_MATCHES[$j]}"  |\
#		   tr -d '[:alpha:] ()-' | cut -d ':' -f2`
#	    
#	    _cpu=`grep -A10 'Open Plan Times:' ${_file} | \
#                   grep "${_OPEN_MATCHES[$j]}"  |\
#		   tr -d '[:alpha:] ()-' | cut -d ':' -f3`
#	    for (( i=0 ; i<${_nr_saves} ; i++ )); do
#		_lines[$i]=${_lines[$i]}${_real}', '${_cpu}', ' 
#	    done
#	done
	for (( j=0 ; j<${_nr_save_matches} ; j++ )); do
	    _times=(`grep -A1 -r 'cslDispatcher: dispatching PythonEvalExpr("carmensystems.studio.Tracking.OpenPlan.save.*Plan()")' ${_file} | grep 'Time:'`)
	    _real=(`sed -n '/Save Plan Times:/,$p' ${_file} | \
                   grep "${_SAVE_MATCHES[$j]}"  |\
		   tr -d '[:alpha:] ()-' | cut -d ':' -f2`)
	    
	    _cpu=(`sed -n '/Save Plan Times:/,$p' ${_file} | \
                   grep "${_SAVE_MATCHES[$j]}"  |\
		   tr -d '[:alpha:] ()-' | cut -d ':' -f3`)

	    for (( i=0 ; i<${_nr_saves} ; i++ )); do	
		if [[ `echo ${_file} | grep 'TI3_BATCH_SAVE'` != ""  &&  $j -eq 0 ]]; then
		    _lines[$i]=${_lines[$i]}${_date}', '${_time}', '
		elif [ $j -eq 0 ]; then
		    _date_ix=`echo "scale=0;1 + $i * 3" | bc -l`
		    _time_ix=`echo "scale=0;2 + $i * 3" | bc -l`
		    _date=`echo  ${_times[${_date_ix}]} | sed -r 's/([0-9]{4})([0-9]{2})([0-9]{2})/\1-\2-\3/g'`
		    _time=${_times[${_time_ix}]}
		    _lines[$i]=${_lines[$i]}${_date}', '${_time}', '  
		fi
		_lines[$i]=${_lines[$i]}${_real[$i]}', '${_cpu[$i]}','
	    done
	done
	for (( i=0 ; i<${_nr_saves} ; i++ )); do
	    echo ${_lines[$i]} 
	done
    done <${_out_file}
    
    
}

_dir="${2%/}/"
_application="studio.*"
_out_file=".tmp"
rm ${_out_file} 2>/dev/null
touch ${_out_file}
case $1 in
    -d)
	_look_for_in_log="Actual (sys) save:"
	_out_file=".tmp"
	_interval=`echo "$3" | tr -d [:alpha:]`
	if [ -z ${_interval} ];then
	    _now=`date -u +%s`
	    _change=`date -d "25Feb2009 10:00" +%s`
	    _interval=`echo "scale=2; (${_now}-${_change})/(60*60*24)" | bc -l | awk '{print int($1)}'`
	fi
	parse_files "+${_interval}" "before.dat"
	parse_files "-${_interval}" "after.dat"
	;;
    -c)
	_look_for_in_log="Save Plan Times:"
	parse_files_complete "$2"
	;;
    *) echo -e "Usage: parse_savetimes_from_logs.sh -c log_dir\nGives a CSV-output of save times. With headers, real and cpu times.\nMakes assumptions on content of logfiles to grep for and looks for files named studio.*"
	exit 1;;
esac
rm ${_out_file} 2>/dev/null
exit 0
