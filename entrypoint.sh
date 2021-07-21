#!/bin/bash

if [ ${#TEAM} -gt 0 ]
then
  python main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES --team $TEAM
else
  python main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES
fi
