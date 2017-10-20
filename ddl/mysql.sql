DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions (
    id CHAR(32) NOT NULL PRIMARY KEY,
    a_session TEXT NOT NULL
);
DROP TABLE IF EXISTS chara;
CREATE TABLE chara (
    id VARCHAR(8) NOT NULL PRIMARY KEY,
    pass VARCHAR(8) NOT NULL,
    site TEXT NOT NULL,
    url TEXT NOT NULL,
    name TEXT NOT NULL,
    sex INT UNSIGNED NOT NULL,
    chara INT UNSIGNED NOT NULL,
    n_0 BIGINT UNSIGNED NOT NULL,
    n_1 BIGINT UNSIGNED NOT NULL,
    n_2 BIGINT UNSIGNED NOT NULL,
    n_3 BIGINT UNSIGNED NOT NULL,
    n_4 BIGINT UNSIGNED NOT NULL,
    n_5 BIGINT UNSIGNED NOT NULL,
    n_6 BIGINT UNSIGNED NOT NULL,
    syoku INT UNSIGNED NOT NULL,
    hp BIGINT UNSIGNED NOT NULL,
    maxhp BIGINT UNSIGNED NOT NULL,
    ex BIGINT UNSIGNED NOT NULL,
    lv BIGINT UNSIGNED NOT NULL,
    gold BIGINT UNSIGNED NOT NULL,
    lp BIGINT UNSIGNED NOT NULL,
    total BIGINT UNSIGNED NOT NULL,
    kati BIGINT UNSIGNED NOT NULL,
    waza TEXT NOT NULL,
    item BIGINT UNSIGNED NOT NULL,
    mons BIGINT UNSIGNED NOT NULL,
    host TEXT NOT NULL,
    date BIGINT UNSIGNED NOT NULL
);
DROP TABLE IF EXISTS winner;
CREATE TABLE winner (
    no bigint(20) unsigned NOT NULL auto_increment PRIMARY KEY,
    id VARCHAR(8) NOT NULL,
    pass VARCHAR(8) NOT NULL,
    site TEXT NOT NULL,
    url TEXT NOT NULL,
    name TEXT NOT NULL,
    sex INT UNSIGNED NOT NULL,
    chara INT UNSIGNED NOT NULL,
    n_0 BIGINT UNSIGNED NOT NULL,
    n_1 BIGINT UNSIGNED NOT NULL,
    n_2 BIGINT UNSIGNED NOT NULL,
    n_3 BIGINT UNSIGNED NOT NULL,
    n_4 BIGINT UNSIGNED NOT NULL,
    n_5 BIGINT UNSIGNED NOT NULL,
    n_6 BIGINT UNSIGNED NOT NULL,
    syoku INT UNSIGNED NOT NULL,
    hp BIGINT UNSIGNED NOT NULL,
    maxhp BIGINT UNSIGNED NOT NULL,
    ex BIGINT UNSIGNED NOT NULL,
    lv BIGINT UNSIGNED NOT NULL,
    gold BIGINT UNSIGNED NOT NULL,
    lp BIGINT UNSIGNED NOT NULL,
    total BIGINT UNSIGNED NOT NULL,
    kati BIGINT UNSIGNED NOT NULL,
    waza TEXT NOT NULL,
    item BIGINT UNSIGNED NOT NULL,
    mons BIGINT UNSIGNED NOT NULL,
    host TEXT NOT NULL,
    date BIGINT UNSIGNED NOT NULL,
    count BIGINT UNSIGNED NOT NULL,
    lsite TEXT NOT NULL,
    lurl TEXT NOT NULL,
    lname TEXT NOT NULL
);
DROP TABLE IF EXISTS message;
CREATE TABLE message (
    no bigint(20) unsigned NOT NULL auto_increment PRIMARY KEY,
    mesid VARCHAR(8) NOT NULL,
    id VARCHAR(8) NOT NULL,
    name TEXT NOT NULL,
    mes TEXT NOT NULL,
    dname TEXT NOT NULL,
    date BIGINT UNSIGNED NOT NULL
);
