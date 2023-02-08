CREATE MIGRATION m1fjgwpuciggu7tts7tkzenvuu6hz6z4ko36vplvzfzkseowppjcba
    ONTO m15b5y6ep765tbxogedhb7yvjx4oxnyrrw5fqjg2k66tjz6xusz27q
{
  ALTER TYPE default::Person {
      DROP LINK employers;
  };
};
