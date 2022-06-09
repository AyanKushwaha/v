#!/bin/sh
# @(#) $Header$
# Convert tabs '\t' to semicolons ';', remove empty spaces at ends of lines.
exec tr -d '\015' | sed 's/\t/;/g;s/[ ]\+$//'
