#!/bin/sh

if [ ${#TEAM} -gt 0 ]
then
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES --team $TEAM
else
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES
fi
