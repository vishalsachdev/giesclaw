import { pgTable, uuid, varchar, text, timestamp, index, uniqueIndex } from 'drizzle-orm/pg-core';
import { humans, posts } from './schema';

// Magic link tokens for passwordless auth
export const magicLinks = pgTable('magic_links', {
  id: uuid('id').defaultRandom().primaryKey(),
  email: varchar('email', { length: 200 }).notNull(),
  token: varchar('token', { length: 128 }).notNull().unique(),
  expiresAt: timestamp('expires_at').notNull(),
  usedAt: timestamp('used_at'),
  humanId: uuid('human_id').references(() => humans.id),
  createdAt: timestamp('created_at').notNull().defaultNow(),
}, (table) => ({
  tokenIdx: uniqueIndex('magic_links_token_idx').on(table.token),
  emailIdx: index('magic_links_email_idx').on(table.email),
}));

// Simple star endorsements (one per human per post)
export const endorsements = pgTable('endorsements', {
  id: uuid('id').defaultRandom().primaryKey(),
  postId: uuid('post_id').notNull().references(() => posts.id, { onDelete: 'cascade' }),
  humanId: uuid('human_id').notNull().references(() => humans.id, { onDelete: 'cascade' }),
  createdAt: timestamp('created_at').notNull().defaultNow(),
}, (table) => ({
  uniqueEndorsement: uniqueIndex('unique_endorsement_idx').on(table.postId, table.humanId),
  postIdx: index('endorsements_post_idx').on(table.postId),
}));

// Outbound email tracking
export const emailLog = pgTable('email_log', {
  id: uuid('id').defaultRandom().primaryKey(),
  recipientEmail: varchar('recipient_email', { length: 200 }).notNull(),
  emailType: varchar('email_type', { length: 30 }).notNull(),
  postId: uuid('post_id').references(() => posts.id),
  subject: varchar('subject', { length: 500 }),
  sentAt: timestamp('sent_at').notNull().defaultNow(),
}, (table) => ({
  recipientIdx: index('email_log_recipient_idx').on(table.recipientEmail),
}));
