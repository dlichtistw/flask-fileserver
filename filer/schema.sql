DROP TABLE IF EXISTS "user";
CREATE TABLE IF NOT EXISTS "user" (
	"id" INTEGER PRIMARY KEY,
	"username" TEXT UNIQUE NOT NULL,
	"password" TEXT NOT NULL
);

DROP TABLE IF EXISTS "post";
CREATE TABLE IF NOT EXISTS "post" (
	"id" INTEGER PRIMARY KEY,
	"author_id" INTEGER NOT NULL
		REFERENCES "user" ("id")
		ON UPDATE CASCADE
		ON DELETE NO ACTION,
	"created" TIMESTAMP NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	"title" TEXT NOT NULL,
	"body" TEXT
);
