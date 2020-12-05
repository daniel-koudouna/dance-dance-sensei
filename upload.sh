#!/bin/sh

scp $1 root@macdoniel.co.uk:/root/code/GGR-Server/temp/
ssh root@macdoniel.co.uk "mv /root/code/GGR-Server/temp/$1 /root/code/GGR-Server/releases/"
