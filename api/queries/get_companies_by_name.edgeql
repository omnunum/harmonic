select Company { 
    name, 
    company_id, 
    headcount 
}
filter .name ilike '%' ++ <str>$name ++ '%'
;