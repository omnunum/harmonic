CREATE MIGRATION m1hll5cuxfi53lpf5m76n7r6em7el67pdwk6laykbs43vwzrpd6ozq
    ONTO m1g2gyc2y67d66phpcid7k3wiawsr4nxel5x6eh7kuu7wib334zsqq
{
  ALTER TYPE default::Company {
      CREATE MULTI LINK acquisitions := (.<acquired_by[IS default::Company]);
  };
};
