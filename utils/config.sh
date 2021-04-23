#!/bin/bash

APPDIR=$HOME/Projects/Publishing_Suite
UTILSDIR=$APPDIR/utils
APPNAME="$(basename $APPDIR)"
APPSLUG="$(echo "$APPNAME" | iconv -t ascii//TRANSLIT | sed -r s/[^a-zA-Z0-9]+/-/g | sed -r s/^-+\|-+$//g | tr A-Z a-z)"
CMSDIR=$APPDIR/cms
VENV=$APPDIR/venv
