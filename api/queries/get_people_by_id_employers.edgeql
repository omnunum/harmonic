select (
    select Person { 
        name, 
        person_id,
        employers := .<employees[IS Company] {
            company_id,
            name,
            employment_title := @employment_title,
            start_date := @start_date,
            end_date := @end_date
        }  
    }
    filter .person_id = <int32>$person_id
    limit 1
).employers
;