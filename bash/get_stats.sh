#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/"

CPU=cpu
LA=la
CONTAINER=container_stats
MEM=memory
DISK=disk
PG=postgres
PROC=proc

PROCS=`echo $(echo '[' && docker exec container_name ps -e -o etime,args | grep -e proc_name1 -e proc_name2 | grep -v ELAPSED | awk -F'   ' '{print$1"|"$2}' | awk -F'|' '{for(i=1;i<=NF;i+=2) print "{\"runtime\": \""$i"\",\"command\":\""$(i+1)"\"},"}' | sed ':a;N;$!ba;s/\n//g' | sed 's/\},$/\}/' | sed 's/,$//' && echo ']') | jq -M -c ""`

# do not run script if no runnnig processes
if [ "${PROCS}" = '[]' ] ; then
  exit 0
fi

for ONE_DIR in $CPU $LA $CONTAINER $MEM $PG $DISK $PROC; do
  mkdir -p ${SCRIPT_DIR}${ONE_DIR}
done

# save processes in file
echo "${PROCS}" > "${SCRIPT_DIR}${PROC}/$(date +'%Y%m%d-%H%M%S')_proc.json"

# get LA
cat /proc/loadavg | awk '{print"{\"1min\": "$1", \"5min\": "$2", \"15min\": "$3"}"}' | jq "" -M -c > "${SCRIPT_DIR}${LA}/$(date +'%Y%m%d-%H%M%S')_la.json"

# get CPU usage for all cores
mpstat -P ALL -o JSON | jq -M -c '.sysstat.hosts[].statistics[]."cpu-load"' > "${SCRIPT_DIR}${CPU}/$(date +'%Y%m%d-%H%M%S')_cpu.json"

# add container statistics json
docker stats container_name --no-stream --no-trunc --format "{{ json . }}" | jq -M -c 'del(.Container, .ID, .Name)' > "${SCRIPT_DIR}${CONTAINER}/$(date +'%Y%m%d-%H%M%S')_container_stats.json"

# get memory
free -m -w | xargs | awk '{print"[{\"type\": \"ram\",\""$1"\": "$9",\""$2"\": "$10",\""$3"\": "$11",\""$4"\": "$12",\""$5"\": "$13",\""$6"\": "$14",\""$7"\": "$15"},{\"type\": \"swap\",\""$1"\": "$17",\""$2"\": "$18",\""$3"\": "$19"}]"}' | jq "" -M -c > "${SCRIPT_DIR}${MEM}/$(date +'%Y%m%d-%H%M%S')_memory.json"

# get disk (for sda + sdb case)
df -m | grep "dev/sd" | xargs | awk '{print"[{\"disk\": \""$1"\",\"size\": "$2",\"used\": "$3",\"available\": "$4"},{\"disk\": \""$7"\",\"size\": "$8",\"used\": "$9",\"available\": "$10"}]"}' 2>/dev/null | jq "" -M -c > "${SCRIPT_DIR}${DISK}/$(date +'%Y%m%d-%H%M%S')_disk.json"

# get postgres data
docker exec db_container_name bash -c "printf '[' && export PAGER= && export PGPASSWORD=\${POSTGRES_PASSWORD} && psql --host=\$(hostname) --username=\${POSTGRES_USER} \${POSTGRES_DB} --command=\"SELECT ROW_TO_JSON(t) from (SELECT * FROM table_name) t;\" 2>/dev/null | awk /./ | grep -v -e row_to_json -e \"\-\-\-\-\-\" -e \"rows)\" | sed 's/\}\$/\},/g' | sed ':a;N;\$!ba;s/\n//g' | sed 's/\},\$/\}/' && printf ']'" | jq "" -M -c > "${SCRIPT_DIR}${PG}/$(date +'%Y%m%d-%H%M%S')_postgres.json"
