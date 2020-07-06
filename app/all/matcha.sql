CREATE TABLE IF NOT EXISTS 'users' (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
  username varchar(255) NOT NULL,
  firstname varchar(255) NOT NULL,
  lastname varchar(255) NOT NULL,
  gender varchar(255) NOT NULL,
  orientation varchar(255) DEFAULT "m,f,t,o",
  email varchar(255) NOT NULL,
  password varchar(255) NOT NULL,
  confirm INTEGER DEFAULT 0,
  token varchar(255),
  bio TEXT DEFAULT "Hey there! I'm using Matcha",
  birthdate varchar(255) NOT NULL,
  age INTEGER,
  main_photo varchar(255),
  photos TEXT,
  tags TEXT DEFAULT '',
  popularity INTEGER DEFAULT 2,
  longitude varchar(255),
  latitude varchar(255),
  last_connection TIMESTAMP DEFAULT 0,
  is_connected INTEGER,
  blocked TEXT,
  city varchar(255),
  socket varchar(255)
);

CREATE TABLE IF NOT EXISTS 'chats' (
  id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  from_id INTEGER,
  dest_id INTEGER,
  from_unread INTEGER DEFAULT 0,
  dest_unread INTEGER DEFAULT 1,
  content TEXT,
  'date' TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS 'tags' (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
  text varchar(255)
);

CREATE TABLE IF NOT EXISTS 'likes' (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
  from_id INTEGER,
  dest_id INTEGER,
  returned INTEGER DEFAULT 0,
  'date' TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS 'visits' (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
  from_id INTEGER,
  dest_id INTEGER,
  unread INTEGER,
  'date' TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS 'notifs' (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
  from_username INTEGER,
  dest_id INTEGER,
  'type' varchar(255),
  unread INTEGER DEFAULT 1,
  'date' TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS 'reports' (
  id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  from_id INTEGER,
  dest_id INTEGER,
  'date' TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS 'blocks' (
  id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  blocker_id INTEGER,
  blocked_id INTEGER
);
