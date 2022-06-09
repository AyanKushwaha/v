#!/bin/sh
# $Header: /opt/Carmen/CVS/sk_cms_user/etc/buildenv.sh,v 1.3 2010/01/28 09:26:23 ADV329 Exp $
#
# This script sets up the environment for a new SAS user. It does not build the user,
# but can be sourced from a script that does so.
#
# Every time a tag is set, a new version of this file should be checked in so that its
# preferred carmsys is specified. Usually, only the CARMSYS_XXX_PREFERRED_VERSION needs
# to be set.

################################################################################
# SET THESE VARIABLES IN A BRANCH THAT IS TO WORK AGAINST A PARTICULAR CARMSYS #
################################################################################

# Note: Let these variables be empty to use the latest nightjob.

CARMSYS_CCT_PREFERRED_VERSION=
CARMSYS_CAS_PREFERRED_VERSION=
CARMSYS_CMP_PREFERRED_VERSION=

################################################################################
# YOU SHOULD NOT NORMALLY HAVE TO CHANGE ANYTHING BELOW THIS TEXT              #
################################################################################

CARMSYS_CCT_NIGHTJOB=/carm/carmen_CMS2/nightjob/Tracking/CARMSYS
CARMSYS_CAS_NIGHTJOB=/carm/carmen_CMS2/nightjob/Planning/CARMSYS
CARMSYS_CMP_NIGHTJOB=/carm/carmen_CMS2/nightjob/Manpower/CARMSYS

CARMSYS_CCT_PREFERRED=/carm/release/Tracking/Tracking-CMS2.${CARMSYS_CCT_PREFERRED_VERSION}_CARMSYS
CARMSYS_CAS_PREFERRED=/carm/release/Planning/Planning-CMS2.${CARMSYS_CAS_PREFERRED_VERSION}_CARMSYS
CARMSYS_CMP_PREFERRED=/carm/release/Manpower/Manpower-CMS2.${CARMSYS_CMP_PREFERRED_VERSION}_CARMSYS

if [ -z $CARMSYS_CCT_PREFERRED_VERSION ]; then
  BUILD_CARMSYS_CCT=$CARMSYS_CCT_NIGHTJOB
else
  if [ ! -d $CARMSYS_CCT_PREFERRED ]; then
    echo "###########################################"
    echo "# CARMSYS_CCT version $CARMSYS_CCT_PREFERRED_VERSION not found"
    echo "###########################################"
    exit 1
  fi
  BUILD_CARMSYS_CCT=$CARMSYS_CCT_PREFERRED
fi

if [ -z $CARMSYS_CAS_PREFERRED_VERSION ]; then
  BUILD_CARMSYS_CAS=$CARMSYS_CAS_NIGHTJOB
else
  if [ ! -d $CARMSYS_CAS_PREFERRED ]; then
    echo "###########################################"
    echo "# CARMSYS_CAS version $CARMSYS_CAS_PREFERRED_VERSION not found"
    echo "###########################################"
    exit 1
  fi
  BUILD_CARMSYS_CAS=$CARMSYS_CAS_PREFERRED
fi

if [ -z $CARMSYS_CMP_PREFERRED_VERSION ]; then
  BUILD_CARMSYS_CMP=$CARMSYS_CMP_NIGHTJOB
else
  if [ ! -d $CARMSYS_CMP_PREFERRED ]; then
    echo "###########################################"
    echo "# CARMSYS_CMP version $CARMSYS_CMP_PREFERRED_VERSION not found"
    echo "###########################################"
    exit 1
  fi
  BUILD_CARMSYS_CMP=$CARMSYS_CMP_PREFERRED
fi
