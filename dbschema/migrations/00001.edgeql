CREATE MIGRATION m1mqxc6yosncma5vgq2xzddlcejztrdvauu5akc7wcocwgpidoy3qa
    ONTO initial
{
  CREATE FUTURE nonrecursive_access_policies;
  CREATE TYPE default::Person {
      CREATE PROPERTY name -> std::str;
      CREATE REQUIRED PROPERTY person_id -> std::int32;
  };
  CREATE TYPE default::Company {
      CREATE LINK acquired_by -> default::Company {
          CREATE PROPERTY merged_into_parent_company -> std::bool;
      };
      CREATE MULTI LINK employees -> default::Person {
          CREATE PROPERTY employment_title -> std::str;
          CREATE PROPERTY end_date -> std::datetime;
          CREATE PROPERTY start_date -> std::datetime;
      };
      CREATE REQUIRED PROPERTY company_id -> std::int32;
      CREATE REQUIRED PROPERTY company_name -> std::str;
      CREATE PROPERTY headcount -> std::int32;
  };
};
