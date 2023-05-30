#!/bin/sh

if [ ${#TEAM} -gt 0 ] && [ ${#REPO} -gt 0 ]
then
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES --team $TEAM --repo $REPO --dependabotsecretssync $DEPENDABOTSECRETSYNC
elif [ ${#TEAM} -gt 0 ]
then
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES --team $TEAM --dependabotsecretssync $DEPENDABOTSECRETSYNC
elif [ ${#REPO} -gt 0 ]
then
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES --repo $REPO --dependabotsecretssync $DEPENDABOTSECRETSYNC
else
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES --dependabotsecretssync $DEPENDABOTSECRETSYNC
fi
