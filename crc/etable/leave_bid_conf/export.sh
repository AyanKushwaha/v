#!/bin/bash

"$CARMSYS/bin/carmrunner" etabdump -v -c "$DATABASE" -s "$SCHEMA" -f "$(dirname $0)"/etabdump.xml "$(dirname $0)"
