module default {


type Person {
    property name -> str;
    required property person_id -> int32 {
        constraint exclusive;
    };
}


type Company {
    required property company_id -> int32 {
        constraint exclusive;
    };
    required property name -> str;
    property headcount -> int32;

    link acquired_by -> Company {
        constraint exclusive;
    }
    multi link acquisitions := .<acquired_by[IS Company]; 
    property merged_into_parent_company -> bool;

    multi link employees -> Person {
        property employment_title -> str;
	    property start_date -> cal::local_datetime;
	    property end_date -> cal::local_datetime;
    }
}
}
