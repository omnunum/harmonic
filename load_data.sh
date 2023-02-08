#!/bin/bash
process_data() {
  local file_name=$1
  local type_name=$2

  echo "Processing $file_name data..."
  jq -c '.[]' "data/$file_name.json" | while read line 
  do 
    echo '{"type": "'$type_name'", "data": '$line'}' > $INGESTION_PIPE
  done
}

process_data "100 Companies" "Company"
process_data "21 Persons" "Person"
process_data "9 CompanyAcquisition" "CompanyAcquisition"
process_data "25 PersonEmployment" "PersonEmployment"

echo 'All data processed successfully!'
