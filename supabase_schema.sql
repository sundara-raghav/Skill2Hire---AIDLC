-- Skill2Hire — Supabase Schema
-- Run this in the Supabase SQL Editor to create required tables

-- ── Predictions Table ────────────────────────────────────
create table if not exists predictions (
  id                    bigserial primary key,
  name                  text default '',
  cgpa                  numeric(4,2),
  aptitude_score        int,
  programming_skills    int,
  communication_skills  int,
  num_projects          int,
  internship_experience int,
  certifications_count  int,
  branch                text,
  placement_probability numeric(5,1),
  confidence            numeric(5,1),
  model_predictions     jsonb default '{}',
  job_skills_found      jsonb default '[]',
  skill_gap_suggestions jsonb default '[]',
  created_at            timestamptz default now()
);

-- Enable RLS (Row-Level Security)
alter table predictions enable row level security;

-- Allow anonymous inserts (for API logging)
create policy "Allow anon insert" on predictions
  for insert to anon with check (true);

-- Allow authenticated reads
create policy "Allow authenticated reads" on predictions
  for select to authenticated using (true);


-- ── Job Analyses Table ────────────────────────────────────
create table if not exists job_analyses (
  id                       bigserial primary key,
  job_description_snippet  text,
  skills_found             jsonb default '[]',
  total_skills             int default 0,
  created_at               timestamptz default now()
);

-- Enable RLS
alter table job_analyses enable row level security;

-- Allow anonymous inserts
create policy "Allow anon insert" on job_analyses
  for insert to anon with check (true);

-- Allow authenticated reads
create policy "Allow authenticated reads" on job_analyses
  for select to authenticated using (true);
