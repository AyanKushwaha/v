#!/bin/sh
# $Header: /opt/Carmen/CVS/sk_cms_user/bin/get_hrdw_stats.sh,v 1.3 2009/02/27 15:13:16 gronlund Exp $
#
# This script will, using SGE, store the hardware stats into:
# - a logfile
# - an html file that presents a google chart
# Each log file has one day information.
#

debug=0

usage_text() {
    echo "Usage: `basename $0` <logfiles_path> [sgeopts...]"
    exit
}

# Test if it has at least one argument
if [ $# -lt 1 ]; then
  usage_text
fi  


# Get time variables
datetimestamp=`date '+%Y%m%d %H:%M'`
datestamp=${datetimestamp:0:8}
timestamp=${datetimestamp:9:5}
hrs=${timestamp:0:2}
hrs=${hrs##0}
mins=${timestamp:3:2}
mins=${mins##0}
daymins=$(($hrs*60+$mins))
totdaymins=$((24*60))

# Debug code
if [ ${debug} -gt 0 ]; then
  echo datetimestamp: ${datetimestamp}
  echo datestamp: ${datestamp}
  echo timestamp: ${timestamp}
  echo hrs: ${hrs}
  echo mins: ${mins}
  echo daymins: ${daymins}
fi

# Get the logfile path and name
# Create directories if they do not exist
logfilePath=$1

if [ ! -d ${logfilePath} ]; then
  echo "Error: Directory '${logfilePath}' does not exist!"
  exit 1
fi
logfilePath=${logfilePath}/hrdw_stats
logfileTxtPath=${logfilePath}/txt
logfileHtmlPath=${logfilePath}/html

mkdir -p ${logfilePath} ${logfileTxtPath} ${logfileHtmlPath}

logfile=${logfileTxtPath}/hrdw_stats_${datestamp}.txt
# Debug code
if [ ${debug} -gt 0 ]; then
  echo "Logfile: $logfile"
fi

# Remove files with more than 10 days
if [ ${debug} -gt 0 ]; then
  echo "Removing files with more than 10 days"
  find ${logfilePath} -mtime +10 -exec ls -l {} \;
fi

find ${logfilePath} -mtime +10 -exec rm {} \;

# Get the sge options
shift
_sgeopts="$@"
_sgecmd=qhost

if [ ${debug} -gt 0 ]; then
  echo "SGE Command: $_sgecmd $_sgeopts"
fi

# If SGE has not been configured yet, try to find it now
for _sge in /usr/local/share/sge /opt/Carmen/sge /opt/sge; do
    [ -z "$SGE_ROOT" -a -f ${_sge}/default/common/settings.sh ] && \
        . ${_sge}/default/common/settings.sh 2>/dev/null
done

# Get qhost resut
qhostRes=`${_sgecmd} ${_sgeopts}`


# TEXT Result
# One result is added per run

# Add the qhost result to the text logfile
echo ${timestamp} >> ${logfile}
echo -e "${qhostRes}" >> ${logfile}
echo >> ${logfile}


# One Html file is added per run and server

# Set the google chart variables
googleChartUrl="http://chart.apis.google.com/chart?"
chttCpu="CPU+Load"
chttMem="Memory+Used"
chs="700x400"
cht="lxy"
chxt="x,y"
# Encoding array http://code.google.com/apis/chart/mappings.html#extended_values
extEncArray=( A B C D E F G H I J K L M N O P Q R S T U V W X Y Z a b c d e f g h i j k l m n o p q r s t u v w x y z 0 1 2 3 4 5 6 7 8 9 - . )

# Remove header and create array
declare -a qhostArray
qhostArray=(`echo -e "${qhostRes}" | tail -n +3`)

# Write google chart link
cnt=${#qhostArray[@]}

# Debug code
if [ ${debug} -gt 0 ]; then
  echo "Number of elements: $cnt"
  for (( i = 0 ; i < cnt ; i++ )); do
    echo "Element [$i]: ${qhostArray[$i]}"
  done
fi

for (( i=0 ; i<cnt ; i=i+8 )); do
  # Calculate chxlCpu, chdCpu, chxlMem and chdMem
  serverName=${qhostArray[$i]}
  cpuType=${qhostArray[($i+1)]}
  cpuN=${qhostArray[($i+2)]}
  cpuLoad=${qhostArray[($i+3)]}
  memTot=${qhostArray[($i+4)]}
  memUsed=${qhostArray[($i+5)]}

  if [ ${cpuN} = "-" ]; then
    cpuN=4
  fi
  if [ ${cpuLoad} = "-" ]; then
    cpuLoad=-1
  else
    # Convert cpu load to decimals by multiplying by 10
    # bc -l does the float calculation
    # awk cuts off the decimal part
    cpuLoad=$( printf "%.1f\n" "${cpuLoad}" )
    cpuLoad=`echo ${cpuLoad} '*10' | bc -l | awk -F '.' '{ print $1; exit; }'`
  fi
  if [ ${memTot} = "-" ]; then
    memTot=0
  else
    # Convert Gb into Mb
    # Remove G and M strings
    if echo "${memTot}" |grep -q G; then
      memTot=${memTot/G/00}
      memTot=${memTot/./}
    else
      memTot=${memTot%*.*}
    fi
  fi
  if [ ${memUsed} = "-" ]; then
    memUsed=-1
  else
    # Convert Gb into Mb
    # Remove G and M strings
    # Divide by 10 so it fits in the URL
    if echo "${memUsed}" |grep -q G; then
      memUsed=${memUsed/G/00}
      memUsed=${memUsed/./}
    else
      memUsed=${memUsed%*.*}
    fi
    memUsed=$((${memUsed}/10))
  fi

  # Debug code
  if [ ${debug} -gt 0 ]; then
    echo serverName: ${serverName}
    echo cpuType: ${cpuType}
    echo cpuN: ${cpuN}
    echo cpuLoad: ${cpuLoad}
    echo memTot: ${memTot}
    echo memUsed: ${memUsed}
    echo
  fi

  # Sets the y scale legend up to cpuN*4 and mem to memTot
  yScaleMaxCpu=$((${cpuN}*4*10))
  yLeg1Cpu=$((${cpuN}*1))
  yLeg2Cpu=$((${cpuN}*2))
  yLeg3Cpu=$((${cpuN}*3))
  yLeg4Cpu=$((${cpuN}*4))
  yScaleMaxMem=$((${memTot}/10))
  yLeg1Mem=$((${memTot}/4))
  yLeg2Mem=$((${memTot}/2))
  yLeg3Mem=$((${memTot}/4+${memTot}/2))
  yLeg4Mem=$((${memTot}/1))

  chdsCpu="0,${totdaymins},0,${yScaleMaxCpu}"
  chxlCpu="0:|0:00|2:00|4:00|6:00|8:00|10:00|12:00|14:00|16:00|18:00|20:00|22:00|24:00|1:|0|${yLeg1Cpu}|${yLeg2Cpu}|${yLeg3Cpu}|${yLeg4Cpu}"
  chdsMem="0,${totdaymins},0,${yScaleMaxMem}"
  chxlMem="0:|0:00|2:00|4:00|6:00|8:00|10:00|12:00|14:00|16:00|18:00|20:00|22:00|24:00|1:|0|${yLeg1Mem}|${yLeg2Mem}|${yLeg3Mem}|${yLeg4Mem}"


  # Calculate the graphic data values
  # Convert into Extended format to save space in the URL
  # Scale first to the max of 4095 encoding value
  # http://code.google.com/apis/chart/mappings.html#extended_values
  if [ ${cpuLoad} = "-1" ]; then
    cpuLoadEnc="__"
  else
    if [ ${cpuLoad} -lt  ${yScaleMaxCpu} ]; then
      cpuLoadScaled=$((${cpuLoad}*4095/${yScaleMaxCpu}))
      cpuLoadEnc=${extEncArray[$((${cpuLoadScaled}/64))]}${extEncArray[$((${cpuLoadScaled}%64))]}
    else
      cpuLoadEnc=".."
    fi
  fi
  if [ ${memUsed} = "-1" ]; then
    memUsedEnc="__"
  else
    if [ ${memUsed} -lt  ${yScaleMaxMem} ]; then
      memUsedScaled=$((${memUsed}*4095/${yScaleMaxMem}))
      memUsedEnc=${extEncArray[$((${memUsedScaled}/64))]}${extEncArray[$((${memUsedScaled}%64))]}
    else
      memUsedEnc=".."
    fi
  fi
    if [ ${daymins} = "-1" ]; then
    dayminsEnc="__"
  else
    if [ ${daymins} -lt  ${totdaymins} ]; then
      dayminsScaled=$((${daymins}*4095/${totdaymins}))
      dayminsEnc=${extEncArray[$((${dayminsScaled}/64))]}${extEncArray[$((${dayminsScaled}%64))]}
    else
      dayminsEnc=".."
    fi
  fi

  # If the file exists get the history data
  serverHtmlFilename=${logfileHtmlPath}/${serverName}_${datestamp}.html
  if [ -e "${serverHtmlFilename}" ]; then
    cpuCharHtml=`cat ${serverHtmlFilename} | grep ${chttCpu} | tail -n 1`
    chdCpuOld=${cpuCharHtml#*chd=*}
    memCharHtml=`cat ${serverHtmlFilename} | grep ${chttMem} | tail -n 1`
    chdMemOld=${memCharHtml#*chd=*}

    # Add the new x and y values
    chdCpu=${chdCpuOld/,/${dayminsEnc},}${cpuLoadEnc}
    chdMem=${chdMemOld/,/${dayminsEnc},}${memUsedEnc}
  else
    chdCpu="e:${dayminsEnc},${cpuLoadEnc}"
    chdMem="e:${dayminsEnc},${memUsedEnc}"
  fi

  # Write HTML code to file
  googleCpuUrl="${googleChartUrl}chtt=${serverName}+${chttCpu}&chs=${chs}&cht=${cht}&chxt=${chxt}&chxl=${chxlCpu}&chds=${chdsCpu}&chd=${chdCpu}"
  googleCpuUrlHtml=${googleCpuUrl/&/&amp;}
  googleMemUrl="${googleChartUrl}chtt=${serverName}+${chttMem}&chs=${chs}&cht=${cht}&chxt=${chxt}&chxl=${chxlMem}&chds=${chdsMem}&chd=${chdMem}"
  googleMemUrlHtml=${googleMemUrl/&/&amp;}

  htmlOpen="<html>"
  htmlCpuLoadImg="<img src=\"${googleCpuUrlHtml}\"/>"
  htmlSpace="<p>&nbsp;</p>"
  htmlMemUsageImg="<img src=\"${googleMemUrlHtml}\"/>"
  htmlLastUpdate="<p>Last update: ${timestamp}</p>"
  htmlClose="</html>\n"
  htmlCommentOpen="<!--"
  htmlCpuComment="CPU Load:\n${googleCpuUrl}\n"
  htmlMemComment="Mem Usage:\n${googleMemUrl}"
  htmlCommentClose="-->"

  # Debug code
  if [ ${debug} -gt 0 ]; then
    echo -e ${htmlOpen}
    echo -e ${htmlCpuLoadImg}
    echo -e ${htmlSpace}
    echo -e ${htmlMemUsageImg}
    echo -e ${htmlLastUpdate}
    echo -e ${htmlClose}
    echo -e ${htmlCommentOpen}
    echo -e ${htmlCpuComment}
    echo -e ${htmlMemComment}
    echo -e ${htmlCommentClose}
  fi  

  echo -e ${htmlOpen} > ${serverHtmlFilename}
  echo -e ${htmlCpuLoadImg} >> ${serverHtmlFilename}
  echo -e ${htmlSpace} >> ${serverHtmlFilename}
  echo -e ${htmlMemUsageImg} >> ${serverHtmlFilename}
  echo -e ${htmlLastUpdate} >> ${serverHtmlFilename}
  echo -e ${htmlClose} >> ${serverHtmlFilename}
  echo -e ${htmlCommentOpen} >> ${serverHtmlFilename}
  echo -e ${htmlCpuComment} >> ${serverHtmlFilename}
  echo -e ${htmlMemComment} >> ${serverHtmlFilename}
  echo -e ${htmlCommentClose} >> ${serverHtmlFilename}
done

exit 0
