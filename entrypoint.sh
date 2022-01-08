#!/bin/sh

if [ ${#TEAM} -gt 0 ] && [ ${#REPO} -gt 0 ]
then
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES --team $TEAM --repo $REPO
elif [ ${#TEAM} -gt 0 ]
then
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES --team $TEAM
elif [ ${#REPO} -gt 0 ]
then
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES --repo $REPO
else
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES
fi
