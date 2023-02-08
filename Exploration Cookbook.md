# Exploration Cookbook
## LinkedIn -> Microsoft
Bare bones company search.  The `.` refers to current object thats in scope, can also use Company.name
```
select Company {
  name
}
filter .name ilike '%microsoft%'
;
```

Add in employees but its just IDs (by default)
```
select Company {
  name,
  employees
}
filter .name ilike '%microsoft%'
;
```

Let's get the names of every employee
```
select Company {
  name,
  employees: {
    name
  }
}
filter .name ilike '%microsoft%'
;
```

Use link properties to find only current employees. We need to use a nested select to add filters
```
select Company {
  name,
  employees := (
    select .employees{
      name
    } 
    filter not exists @end_date
      and exists @start_date
  )
}
filter .name ilike '%microsoft%'
;
```

Dive another layer to get the previous employers of current employees.  Check that the previous company is linkedin
```
select Company {
  name,
  employees := (
    select .employees{
      name,
      previous_employers := (
        select .<employees[is Company]{name} 
        filter exists @end_date
          and .name ilike 'linkedin'
      )
    } 
    filter not exists @end_date
      and exists @start_date
      
  )
}
filter .name ilike 'microsoft'
;
```

Last result actually just filtered out the previous employers if they weren't linkedin, but we want to filter out the employees if they haven't worked for linked in. We need to filter from up one level in the employees subquery
```
select Company {
  name,
  employees := (
    select .employees{
      name,
      previous_employers := (
        select .<employees[is Company]{name} 
        filter exists @end_date
      )
    } 
    filter not exists @end_date
      and exists @start_date
      and .previous_employers.name ilike 'linkedin'
  )
}
filter .name ilike 'microsoft'
;
```

If we don't actually need the names of the previous employers then we can save a level of subquerying
```
select Company {
  name,
  employees := (
    select .employees{name}
    filter not exists @end_date
      and exists @start_date
      and exists .<employees[is Company]@end_date
      and .<employees[is Company].name ilike 'linkedin'
  )
}
filter .name ilike '%microsoft%'
;
```

## Aggregates
Group all companies by how many employees they've had
```
with 
  C := (
    select Company {
      name, 
      on_record_headcount := count(.employees)
    } filter .on_record_headcount > 0
  )
group C {name}
by .on_record_headcount
;
```