-- CreateTable
CREATE TABLE "Entity" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "color" TEXT NOT NULL,
    "logo_url" TEXT NOT NULL,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "Gift" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "tiktok_gift_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "icon_url" TEXT NOT NULL,
    "point_value" INTEGER NOT NULL DEFAULT 1,
    "entity_id" INTEGER NOT NULL,
    CONSTRAINT "Gift_entity_id_fkey" FOREIGN KEY ("entity_id") REFERENCES "Entity" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "Score" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "entity_id" INTEGER NOT NULL,
    "total_score" INTEGER NOT NULL DEFAULT 0,
    "updated_at" DATETIME NOT NULL,
    CONSTRAINT "Score_entity_id_fkey" FOREIGN KEY ("entity_id") REFERENCES "Entity" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "EventLog" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "tiktok_gift_id" INTEGER NOT NULL,
    "gift_name" TEXT NOT NULL,
    "sender_username" TEXT NOT NULL,
    "repeat_count" INTEGER NOT NULL DEFAULT 1,
    "entity_id" INTEGER,
    "points_awarded" INTEGER NOT NULL DEFAULT 0,
    "raw_event" TEXT NOT NULL,
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "EventLog_entity_id_fkey" FOREIGN KEY ("entity_id") REFERENCES "Entity" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- CreateIndex
CREATE UNIQUE INDEX "Entity_slug_key" ON "Entity"("slug");

-- CreateIndex
CREATE UNIQUE INDEX "Gift_tiktok_gift_id_key" ON "Gift"("tiktok_gift_id");

-- CreateIndex
CREATE UNIQUE INDEX "Gift_entity_id_key" ON "Gift"("entity_id");

-- CreateIndex
CREATE UNIQUE INDEX "Score_entity_id_key" ON "Score"("entity_id");
