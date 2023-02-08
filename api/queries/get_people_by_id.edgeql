select Person { 
    name, 
    person_id
}
filter .person_id = <int32>$person_id
limit 1
;