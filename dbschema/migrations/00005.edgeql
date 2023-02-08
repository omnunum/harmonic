CREATE MIGRATION m15auhkjp2lh3e7ivu6dvlolluhrxufa6qnammdjshwfq66l6zaana
    ONTO m1mzktzlnauivinv6cebwnh6ny4wqtt2k6nevh5szu472mazj5z4fa
{
  ALTER TYPE default::Company {
      ALTER LINK acquired_by {
          DROP PROPERTY merged_into_parent_company;
      };
  };
  ALTER TYPE default::Company {
      CREATE PROPERTY merged_into_parent_company -> std::bool;
  };
};
