select Person { 
    name, 
    person_id
}
filter .name ilike '%' ++ <str>$name ++ '%'
;