CREATE MIGRATION m15b5y6ep765tbxogedhb7yvjx4oxnyrrw5fqjg2k66tjz6xusz27q
    ONTO m1hll5cuxfi53lpf5m76n7r6em7el67pdwk6laykbs43vwzrpd6ozq
{
  ALTER TYPE default::Company {
      ALTER PROPERTY company_name {
          RENAME TO name;
      };
  };
};
