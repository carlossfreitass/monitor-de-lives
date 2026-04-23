/*
  Warnings:

  - You are about to drop the column `entity_id` on the `Gift` table. All the data in the column will be lost.

*/
-- CreateTable
CREATE TABLE "GiftMap" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "entity_id" INTEGER NOT NULL,
    "gift_id" INTEGER NOT NULL,
    CONSTRAINT "GiftMap_entity_id_fkey" FOREIGN KEY ("entity_id") REFERENCES "Entity" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "GiftMap_gift_id_fkey" FOREIGN KEY ("gift_id") REFERENCES "Gift" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- RedefineTables
PRAGMA defer_foreign_keys=ON;
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_Entity" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "slug" TEXT NOT NULL,
    "color" TEXT NOT NULL,
    "logo_url" TEXT NOT NULL DEFAULT '',
    "created_at" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO "new_Entity" ("color", "created_at", "id", "logo_url", "name", "slug") SELECT "color", "created_at", "id", "logo_url", "name", "slug" FROM "Entity";
DROP TABLE "Entity";
ALTER TABLE "new_Entity" RENAME TO "Entity";
CREATE UNIQUE INDEX "Entity_slug_key" ON "Entity"("slug");
CREATE TABLE "new_Gift" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "tiktok_gift_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "icon_url" TEXT NOT NULL DEFAULT '',
    "point_value" INTEGER NOT NULL DEFAULT 1
);
INSERT INTO "new_Gift" ("icon_url", "id", "name", "point_value", "tiktok_gift_id") SELECT "icon_url", "id", "name", "point_value", "tiktok_gift_id" FROM "Gift";
DROP TABLE "Gift";
ALTER TABLE "new_Gift" RENAME TO "Gift";
CREATE UNIQUE INDEX "Gift_tiktok_gift_id_key" ON "Gift"("tiktok_gift_id");
PRAGMA foreign_keys=ON;
PRAGMA defer_foreign_keys=OFF;

-- CreateIndex
CREATE UNIQUE INDEX "GiftMap_entity_id_gift_id_key" ON "GiftMap"("entity_id", "gift_id");
