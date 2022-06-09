#!/bin/bash

etabdiff -c $DATABASE -s $SCHEMA "$@" "$(dirname $0)"/*.etab
