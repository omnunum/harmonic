CREATE MIGRATION m1poo7bqy52hyxbrc7v4lp2bufwjbxyxmtnmlcm75q77caeq5v7oiq
    ONTO m1mqxc6yosncma5vgq2xzddlcejztrdvauu5akc7wcocwgpidoy3qa
{
  ALTER TYPE default::Company {
      ALTER LINK acquired_by {
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
