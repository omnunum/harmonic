CREATE MIGRATION m17oq4hup4cjkrdlgiyv3kskkzbzffcf7qtbxe5mneoygkeregenra
    ONTO m1poo7bqy52hyxbrc7v4lp2bufwjbxyxmtnmlcm75q77caeq5v7oiq
{
  ALTER TYPE default::Company {
      ALTER PROPERTY company_id {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  ALTER TYPE default::Person {
      ALTER PROPERTY person_id {
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
