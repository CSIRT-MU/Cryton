#!/bin/bash

function test() {
  # Default input variables.
  toCall=$1  # Command to call.
  toParse=$2  # What regex to use for parsing call's stdOut.
  toCheck=$3  # Word to check in call's stdOut.
  checkStateId=$4  # Which run's state should we check.
  checkState=$5  # What state should we check.
  timeOut=$6  # For how long should we check.

  # Get stdOut from call.
  stdOut=$($toCall 2>&1)
  stdOut=${stdOut//[$'\t\r\n']/" "}

  # Parse Id from stdOut.
  if [[ "$toParse" != -1 ]]; then
    parsedId=$(echo "$stdOut" | sed -n "$toParse")
  else
    parsedId=-1
  fi

  # Perform checks if call and id parsing were successful.
  stdOutOk=$(containsSubString "$stdOut" "$toCheck")
  idOk=$(isNumber "$parsedId")
  if [[ "$idOk" != 0 ]]; then
      parsedId=-1
  fi

  # Get test result and optionally wait for state.
  result=1
  if [[ ($toParse == -1 || "$stdOutOk" == "$idOk") && "$stdOutOk" == 0 ]]; then
    if [[ $checkStateId == -1 || $(runWaitForState "$checkStateId" "$checkState" "$timeOut") == 0 ]]; then
        result=0
    else
      stdOut="$stdOut - !!Timeout occurred!!"
    fi
  fi
  echo "$parsedIdˇ$resultˇ$stdOut"
}


function runWaitForState() {
  runId=$1
  state=$2
  timeOut=$(($3*2))
  while : ; do
    currentState=$(cryton-cli runs show "$runId" | sed -n "s/^.*state: \(.*\), plan_model.*$/\1/p")
    if [[ "$currentState" == "$state" ]]; then
      echo 0
      break
    elif [[ timeOut -le 0 ]]; then
      echo 1
      break
    fi
    sleep 0.5
    ((timeOut--))
  done
}

function containsSubString() {
  if [[ $1 = *$2* ]]; then
    echo 0
  else
    echo 1
  fi
}

function isNumber() {
  if [[ $1 =~ ^[0-9]+$ ]]; then
    echo 0
  else
    echo 1
  fi
}


checkWord="successfully"


# Create Worker
resultRaw=$(test "cryton-cli workers create worker -f" "s/^.*'id': \(.*\),.*$/\1/p" "$checkWord" -1 "" 0)
IFS="ˇ" read -ra resultParsed <<< "$resultRaw"
workerId=${resultParsed[0]};
echo "${resultParsed[2]}"


# Health-check Worker
resultRaw=$(test "cryton-cli workers health-check $workerId" -1 "$checkWord" -1 "" 0)
IFS="ˇ" read -ra resultParsed <<< "$resultRaw"
echo "${resultParsed[2]}"


# Validate template
resultRaw=$(test "cryton-cli plans validate /opt/resources/template.yml -i /opt/resources/inventory.yml" -1 "$checkWord" -1 "" 0)
IFS="ˇ" read -ra resultParsed <<< "$resultRaw"
echo "${resultParsed[2]}"


# Template create
resultRaw=$(test "cryton-cli plan-templates create /opt/resources/template.yml" "s/^.*'id': \(.*\),.*$/\1/p" "$checkWord" -1 "" 0)
IFS="ˇ" read -ra resultParsed <<< "$resultRaw"
templateId=${resultParsed[0]}
echo "${resultParsed[2]}"


# Plan create
resultRaw=$(test "cryton-cli plans create $templateId -i /opt/resources/inventory.yml" "s/^.*'id': \(.*\),.*$/\1/p" "$checkWord" -1 "" 0)
IFS="ˇ" read -ra resultParsed <<< "$resultRaw"
planId=${resultParsed[0]}
echo "${resultParsed[2]}"


# Run create
resultRaw=$(test "cryton-cli runs create $planId $workerId" "s/^.*'id': \([0-9]*\), .*$/\1/p" "$checkWord" -1 "" 0)
IFS="ˇ" read -ra resultParsed <<< "$resultRaw"
runId=${resultParsed[0]}
echo "${resultParsed[2]}"


# Run execute
echo "Run executed. This may take a while.. "
resultRaw=$(test "cryton-cli runs execute $runId" -1 "$checkWord" "$runId" "FINISHED" 1000)
IFS="ˇ" read -ra resultParsed <<< "$resultRaw"
_=${resultParsed[0]}
echo "${resultParsed[2]}"


# Run report
cryton-cli runs report $runId
