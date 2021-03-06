BEGIN;
--
-- Create model User
--
CREATE TABLE "user" (
  "id" serial NOT NULL PRIMARY KEY,
  "password" varchar(128) NOT NULL,
  "username" varchar(30) NOT NULL UNIQUE,
  "first_name" varchar(30) NOT NULL,
  "last_name" varchar(30) NOT NULL,
  "email" varchar(254) NOT NULL,
  "date_joined" timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);
--
-- Create model Album
--
CREATE TABLE "album" (
  "id" serial NOT NULL PRIMARY KEY,
  "artist" varchar(250) NOT NULL,
  "album_title" varchar(500) NOT NULL,
  "genre" varchar(100),
  "album_logo" varchar(100),
  "is_favorite" boolean NOT NULL DEFAULT FALSE,
  "user_id" integer NOT NULL
);
--
-- Create model Song
--
CREATE TABLE "song" (
  "id" serial NOT NULL PRIMARY KEY,
  "song_title" varchar(250) NOT NULL,
  "audio_file" varchar(100) NOT NULL,
  "is_favorite" boolean NOT NULL DEFAULT FALSE,
  "album_id" integer NOT NULL
);
--
-- Create model Session
--
CREATE TABLE "session" (
  "session_key" varchar(40) NOT NULL PRIMARY KEY,
  "user_id"     integer     NOT NULL
);
--
-- Add foreign key constraints
--
ALTER TABLE "song" ADD CONSTRAINT "song_album_id_fk_album_id" FOREIGN KEY ("album_id") REFERENCES "album" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "album" ADD CONSTRAINT "album_user_id_fk_user_id" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "session" ADD CONSTRAINT "session_user_id_fk_user_id" FOREIGN KEY ("user_id") REFERENCES "user" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;

CREATE INDEX "song_index" ON "song" ("album_id");
CREATE INDEX "user_username_index" ON "user" ("username" varchar_pattern_ops);
CREATE INDEX "album_index" ON "album" ("user_id");
CREATE INDEX "session_index" ON "session" ("user_id");
CREATE INDEX "session_key_like" ON "session" ("session_key" varchar_pattern_ops);


COMMIT;
