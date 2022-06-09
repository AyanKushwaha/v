"""
application
Module for doing:
Keeping track of SK_APP and product
@date:19Nov2008
@author: Per Groenberg (pergr) (added header)
@org: Jeppesen Systems AB
"""

import os
import carmensystems.rave.api as rave
import Errlog

__version__ = "$Revision$"

isTracking = False
isPlanning = False
isPreplanning = False
isServer = False
isAlertGenerator = False
isAccumulator = False
isBatchDeamon = False
isReportWorker = False
isDayOfOps = False

isPairing = False
isRostering = False

# Product "enums"
ROSTERING = 'CCR'
PAIRING = 'CCP'
TRACKING = 'CCT'
PREPLANNING = 'PRE'
PRODUCT_OPTIONS = {ROSTERING: 'rostering', PAIRING: 'pairing', TRACKING: 'tracking', PREPLANNING: 'preplanning'}


def get_product_from_ruleset():
    """ Check current ruleset for product string """
    if rave.ruleset_loaded():
        try:
            current_product, = rave.eval('base_product.%product%')
            if current_product.upper() not in PRODUCT_OPTIONS.keys():
                raise Exception("Unknown product from rave ruleset")
            return current_product.upper()
        except Exception, err:
            Errlog.log('application: Error getting current product: %s' % err)
            return None
    else:
        return None


def get_product_name():
    """ Get the current name via mapping of ruleset product"""
    return PRODUCT_OPTIONS.get(get_product_from_ruleset(), None)


def ruleset_is_tracking():
    return ruleset_is_product(TRACKING)


def ruleset_is_preplanning():
    return ruleset_is_product(PREPLANNING)


def ruleset_is_pairing():
    return ruleset_is_product(PAIRING)


def ruleset_is_rostering():
    return ruleset_is_product(ROSTERING)


def ruleset_is_product(product):
    ruleset = get_product_from_ruleset()
    return ruleset is not None and ruleset == product

# We start with role checks, then product checks
if bool(os.environ.get("SERVER_MODE")) or os.path.expandvars("$SK_APP").lower() == "server":
    isServer = True
elif os.path.expandvars("$SK_APP").lower() == "planning":
    isPlanning = True
elif os.path.expandvars("$SK_APP").lower() == "preplanning":
    isPreplanning = True
elif os.path.expandvars("$SK_APP").lower() == "tracking":
    isTracking = True
elif os.path.expandvars("$SK_APP").lower() == "dayofops":
    isDayOfOps = True

if os.path.expandvars("$APPLICATION").lower() == "alertgenerator":
    isAlertGenerator = True
elif os.path.expandvars("$APPLICATION").lower() == "reportworker":
    isReportWorker = True
    
if os.path.expandvars("$SK_APP_NAME").lower() == "accumulators":
    isAccumulator = True
elif os.path.expandvars("$SK_APP_NAME").lower() == "batchdeamon":
    isBatchDeamon = True
