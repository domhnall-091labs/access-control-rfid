BEGIN TRANSACTION;
-- SQLite has no specific date/time fields, so we're settling on using TEXT
-- fields instead, the format will be "YYYY-MM-DD HH:MM:SS.SSS".
-- <password> and <keycode> should be an SHA512 sum of the original data - i.e.
-- the login password to the system (for users) or the numeric value on the 
-- key card (for keys)
CREATE TABLE access_log (id INTEGER PRIMARY KEY, timestamp TEXT, event TEXT, key_id INTEGER);
CREATE TABLE keyholders (id INTEGER PRIMARY KEY, name_given TEXT, name_family TEXT, member_id INTEGER);
CREATE TABLE keys (id INTEGER PRIMARY KEY, keyholder_id INTEGER, valid_start TEXT, valid_end TEXT, keycode TEXT);
CREATE TABLE users (id INTEGER PRIMARY KEY, name_given TEXT, name_family TEXT, username TEXT, password TEXT);
COMMIT;
