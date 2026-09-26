-- ===================================================================
-- DevFlow Supabase Initial Schema (001_initial_schema.sql)
-- ===================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Profiles Table (Developer users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    role TEXT DEFAULT 'developer',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Projects Table
CREATE TABLE IF NOT EXISTS public.projects (
    id TEXT PRIMARY KEY,
    owner_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'UPLOADED', -- 'UPLOADED', 'ANALYZED', 'VERIFIED', 'READY'
    health_score INTEGER,
    file_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Analyses Table
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id TEXT REFERENCES public.projects(id) ON DELETE CASCADE NOT NULL,
    summary TEXT,
    health_score INTEGER NOT NULL,
    raw_ai_response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Issues Table
CREATE TABLE IF NOT EXISTS public.issues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_id UUID REFERENCES public.analyses(id) ON DELETE CASCADE NOT NULL,
    issue_code TEXT NOT NULL, -- e.g., 'ISSUE-001'
    title TEXT NOT NULL,
    category TEXT NOT NULL,   -- 'Security', 'Bug', 'Testing', 'Maintainability'
    severity TEXT NOT NULL,   -- 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    file_path TEXT NOT NULL,
    line_number INTEGER,
    description TEXT,
    impact TEXT,
    recommendation TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 5. Fixes Table
CREATE TABLE IF NOT EXISTS public.fixes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    issue_id TEXT NOT NULL,
    root_cause TEXT,
    files_to_change JSONB,
    implementation_steps JSONB,
    regression_tests JSONB,
    code_diff TEXT,
    applied BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. Verification Results Table
CREATE TABLE IF NOT EXISTS public.verification_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id TEXT REFERENCES public.projects(id) ON DELETE CASCADE NOT NULL,
    passed BOOLEAN NOT NULL,
    total_files INTEGER NOT NULL,
    failed_files JSONB,
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create helpful indexes
CREATE INDEX IF NOT EXISTS idx_projects_owner ON public.projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_analyses_project ON public.analyses(project_id);
CREATE INDEX IF NOT EXISTS idx_issues_analysis ON public.issues(analysis_id);
CREATE INDEX IF NOT EXISTS idx_verification_project ON public.verification_results(project_id);
