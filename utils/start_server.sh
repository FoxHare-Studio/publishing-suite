#!/bin/bash

source $HOME/Projects/Publishing_Suite/utils/config.sh

cd $CMSDIR
tmux new -s $APPSLUG -d
tmux send-keys -t $APPSLUG 'source ../venv/bin/activate; python3 manage.py runserver' C-m
tmux split-window -v -t $APPSLUG
tmux send-keys -t $APPSLUG 'sass-watch inventory/static/css/style.sass' C-m
tmux select-window -t $APPSLUG:1
tmux attach -t $APPSLUG
