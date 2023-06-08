#!/bin/sh

if [ ${#TEAM} -gt 0 ] && [ ${#REPO} -gt 0 ]
then
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES --team $TEAM --repo $REPO --dependabotsecretssync $DEPENDABOTSECRETSYNC --repoowner $REPOSITORYOWNER 
elif [ ${#TEAM} -gt 0 ]
then
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES --team $TEAM --dependabotsecretssync $DEPENDABOTSECRETSYNC --repoowner $REPOSITORYOWNER
elif [ ${#REPO} -gt 0 ]
then
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES --repo $REPO --dependabotsecretssync $DEPENDABOTSECRETSYNC --repoowner $REPOSITORYOWNER
else
  python /app/main.py $ACTION --token $TOKEN --names $NAMES --values $VALUES --dependabotsecretssync $DEPENDABOTSECRETSYNC --repoowner $REPOSITORYOWNER
fi