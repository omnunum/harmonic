CREATE MIGRATION m1mzktzlnauivinv6cebwnh6ny4wqtt2k6nevh5szu472mazj5z4fa
    ONTO m17oq4hup4cjkrdlgiyv3kskkzbzffcf7qtbxe5mneoygkeregenra
{
  ALTER TYPE default::Company {
      ALTER LINK employees {
          ALTER PROPERTY end_date {
              SET TYPE cal::local_datetime USING (cal::to_local_datetime(@end_date, 'utc'));
          };
      };
  };
  ALTER TYPE default::Company {
      ALTER LINK employees {
          ALTER PROPERTY start_date {
              SET TYPE cal::local_datetime USING (cal::to_local_datetime(@start_date, 'utc'));
          };
      };
  };
};
