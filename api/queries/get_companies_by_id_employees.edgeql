select (
    select Company { 
        company_id, 
        employees: {
            name,
            employment_title := @employment_title,
            start_date := @start_date,
            end_date := @end_date
        }  
    }
    filter .company_id = <int32>$company_id
    limit 1
).employees
;