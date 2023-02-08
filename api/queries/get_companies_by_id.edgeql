select Company { 
    name, 
    company_id, 
    headcount 
}
filter .company_id = <int32>$company_id
limit 1
;