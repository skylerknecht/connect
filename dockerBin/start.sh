#!/bin/bash
cd /connect
#echo $CALLBACK_IP
#echo $CALLBACK_PORT

nohup ./server.sh 2>/dev/null &
for run in {1..20}; do
	if ! [ -f nohup.out ]; then sleep .5; continue; fi
	if ! grep -qi "http" nohup.out; then
		sleep .5
		continue
	fi
	break
done
if ! grep -qi "http" nohup.out; then echo "ERROR CREATING SERVER"; cat nohup.out; exit; fi;

urlKey=$(cat nohup.out | cut -d ' ' -f 5-6);
#key=$(cat nohup.out | cut -d ' ' -f 6);

#echo "URL: $url"
#echo "KEY: $key"
python -m connect.client.cli $urlKey


