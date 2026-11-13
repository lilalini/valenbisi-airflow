CREATE TABLE lecturas (
    number      integer      NOT NULL,
    address     text,
    open        boolean,
    available   integer,
    free        integer,
    total       integer,
    ticket      boolean,
    actualizado timestamptz  NOT NULL,
    lon         double precision,
    lat         double precision,
    pct_libres  numeric(5,1),
    PRIMARY KEY (number, actualizado)
);
