#!/bin/bash

curl_command="curl https://localhost:7800/api/throughput_download?size_kb=20000 -k --limit-rate 5m -H \"Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMSIsImV4cCI6MTcxMTEzMTcxM30.MFxtF2EIjskXj9-MQ9rXpF8IQXErkqf4kDW80_l3JGw\""

for ((i=1; i<=20; i++)); do
    echo "Starting test number $1"
    eval "$curl_command" >/dev/null 2>&1 &
    sleep 1  # To not send the traffic at the same time
done

wait

echo "All traffic sent."
