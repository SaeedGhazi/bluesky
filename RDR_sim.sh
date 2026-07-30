#!/bin/bash
trap "kill 0" EXIT

fuser -k 8000/tcp 2>/dev/null
fuser -k 8080/tcp 2>/dev/null
sleep 1

python3 -m http.server 8000 --directory ~/Desktop/SIM/MAP/ &

source ./v311/bin/activate

cd ATG/
python3 bluesky-bridge.py &
python3 BlueSky.py
