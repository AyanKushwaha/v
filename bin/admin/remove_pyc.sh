#!/usr/bin/env bash

# removes all .pyc files recursively from all (sub-) directories
find . -name "*.pyc" -exec rm -f {} \;