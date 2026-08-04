-- SQL dump generated using DBML (dbml.dbdiagram.io)
-- Database: PostgreSQL
-- Generated at: 2026-07-14T16:42:17.888Z

CREATE TYPE "order_status" AS ENUM (
  'pending_payment',
  'paid',
  'restaurant_accepted',
  'preparing',
  'ready_for_pickup',
  'delivering',
  'delivered',
  'delivery_failed',
  'refunding',
  'refunded',
  'cancelled'
);

CREATE TYPE "payment_status" AS ENUM (
  'initiated',
  'authorized',
  'captured',
  'voided',
  'refunded',
  'partially_refunded',
  'failed'
);

CREATE TYPE "payment_method" AS ENUM (
  'cod',
  'card',
  'ewallet'
);

CREATE TYPE "delivery_status" AS ENUM (
  'assigned',
  'picked',
  'delivering',
  'delivered',
  'failed'
);

CREATE TABLE "customers" (
  "id" uuid PRIMARY KEY,
  "name" varchar(120) NOT NULL,
  "phone" varchar(20) UNIQUE NOT NULL,
  "default_address" varchar(255),
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "restaurants" (
  "id" uuid PRIMARY KEY,
  "name" varchar(160) NOT NULL,
  "address" varchar(255) NOT NULL,
  "is_open" boolean NOT NULL DEFAULT true
);

CREATE TABLE "menu_items" (
  "id" uuid PRIMARY KEY,
  "restaurant_id" uuid NOT NULL,
  "name" varchar(160) NOT NULL,
  "price" integer NOT NULL,
  "available" boolean NOT NULL DEFAULT true
);

CREATE TABLE "orders" (
  "id" uuid PRIMARY KEY,
  "customer_id" uuid NOT NULL,
  "restaurant_id" uuid NOT NULL,
  "status" order_status NOT NULL DEFAULT 'pending_payment',
  "payment_method" payment_method NOT NULL,
  "total_amount" integer NOT NULL,
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "order_lines" (
  "id" uuid PRIMARY KEY,
  "order_id" uuid NOT NULL,
  "menu_item_id" uuid NOT NULL,
  "quantity" integer NOT NULL DEFAULT 1,
  "line_total" integer NOT NULL
);

CREATE TABLE "payments" (
  "id" uuid PRIMARY KEY,
  "order_id" uuid UNIQUE NOT NULL,
  "status" payment_status NOT NULL DEFAULT 'initiated',
  "amount" integer NOT NULL,
  "gateway_ref" varchar(80),
  "created_at" timestamp DEFAULT (now())
);

CREATE TABLE "shippers" (
  "id" uuid PRIMARY KEY,
  "name" varchar(120) NOT NULL,
  "phone" varchar(20) UNIQUE NOT NULL,
  "vehicle" varchar(40)
);

CREATE TABLE "deliveries" (
  "id" uuid PRIMARY KEY,
  "order_id" uuid UNIQUE NOT NULL,
  "shipper_id" uuid,
  "status" delivery_status NOT NULL DEFAULT 'assigned',
  "picked_at" timestamp,
  "delivered_at" timestamp
);

CREATE TABLE "reviews" (
  "id" uuid PRIMARY KEY,
  "order_id" uuid UNIQUE NOT NULL,
  "rating" smallint NOT NULL,
  "comment" text,
  "created_at" timestamp DEFAULT (now())
);

CREATE INDEX ON "restaurants" ("is_open");

CREATE INDEX ON "menu_items" ("restaurant_id", "available");

CREATE INDEX ON "orders" ("customer_id");

CREATE INDEX ON "orders" ("restaurant_id", "status");

CREATE INDEX ON "orders" ("created_at");

CREATE INDEX ON "order_lines" ("order_id");

CREATE INDEX ON "deliveries" ("shipper_id");

COMMENT ON COLUMN "menu_items"."price" IS 'VND';

COMMENT ON COLUMN "orders"."total_amount" IS 'VND, gồm phí ship + khuyến mãi';

COMMENT ON COLUMN "payments"."gateway_ref" IS 'mã giao dịch cổng thanh toán';

COMMENT ON COLUMN "reviews"."rating" IS '1..5';

ALTER TABLE "menu_items" ADD FOREIGN KEY ("restaurant_id") REFERENCES "restaurants" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "orders" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "orders" ADD FOREIGN KEY ("restaurant_id") REFERENCES "restaurants" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "order_lines" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "order_lines" ADD FOREIGN KEY ("menu_item_id") REFERENCES "menu_items" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "payments" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "deliveries" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "deliveries" ADD FOREIGN KEY ("shipper_id") REFERENCES "shippers" ("id") DEFERRABLE INITIALLY IMMEDIATE;

ALTER TABLE "reviews" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("id") DEFERRABLE INITIALLY IMMEDIATE;
