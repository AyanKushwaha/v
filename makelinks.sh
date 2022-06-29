
#!/bin/bash

# First check if in user is in correct directory
if [ ! -d "crc" ]; then
    echo "You are in wrong directory"
    exit 0
fi

# Read arguments
while getopts :m: flag
do
    case "${flag}" in
        m) version=${OPTARG};;
    esac
done

: ${version:="default"}

echo "Right directory"

declare -a softLinks=(
    "/opt/Carmen/CARMDATA/carmdata/" "current_carmdata"
    "current_carmsys_cct" "current_carmsys"
    "/opt/Carmen/CARMSYS/mr-tracking-27.8.36951_CARMSYS" "current_carmsys_cct"
    "current_carmtmp_cct" "current_carmtmp"
    "/opt/Carmen/CARMTMP/$(whoami)/CARMTMP/tracking_carmtmp_${version}" "current_carmtmp_cct"
    "local_template_SASDEV.xml" "etc/local.xml"
    "/opt/Carmen/CARMTMP/$(whoami)/CARMTMP/tracking_carmtmp_${version}/carmtmp_behave" "carmtmp_behave"
    "/opt/Carmen/cms_accounts" "etc/cms_accounts"
    "/opt/SasLinkCMS/CARMDATA/carmdata/" "current_link_carmdata"
    "/opt/Carmen/CARMUSR_Manpower/SASDEV" "current_carmusr_jmp"
)
softLinksLength=${#softLinks[@]}
for (( i=0; i<${softLinksLength}; i++));
    do
        if [ ! -L ${softLinks[$i+1]} ]; then
            ln -s ${softLinks[$i]} ${softLinks[$i+1]};
            echo "Created the link: ${softLinks[$i+1]} -> ${softLinks[$i]}"
        else
            if [[ ${softLinks[$i+1]} != /* ]] ; then
                rm -f ${softLinks[$i+1]};
                echo "Removed ${softLinks[$i+1]}"
            fi
            ln -s ${softLinks[$i]} ${softLinks[$i+1]};
            echo "Modified the link: ${softLinks[$i+1]} -> ${softLinks[$i]}"
        fi
        ((i++))
    done

# Some CARMUSR subdirectories need to be group-writeable
# Otherwise certain operations will fail for all but the owner
declare -a writeableDirs=(
    "crc/etable"
    "lib/contrib/python"
)
writeableDirsLength=${#writeableDirs[@]}
for (( i=0; i<${writeableDirsLength}; i++));
    do
        chmod g+w ${writeableDirs[$i]} # Required for Pairing help
        echo "Made ${writeableDirs[$i]} group-writeable"
    done


