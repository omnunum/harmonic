CREATE MIGRATION m1g2gyc2y67d66phpcid7k3wiawsr4nxel5x6eh7kuu7wib334zsqq
    ONTO m15auhkjp2lh3e7ivu6dvlolluhrxufa6qnammdjshwfq66l6zaana
{
  ALTER TYPE default::Person {
      CREATE MULTI LINK employers := (.<employees[IS default::Company]);
  };
};
