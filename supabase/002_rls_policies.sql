-- ===================================================================
-- DevFlow Supabase Row Level Security (RLS) Policies (002_rls_policies.sql)
-- ===================================================================

-- 1. Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.issues ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.fixes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.verification_results ENABLE ROW LEVEL SECURITY;

-- 2. Profiles Policies
-- Users can view their own profile; service role can view/modify all
CREATE POLICY "Users can read own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- 3. Projects Policies
-- Allow public access for MVP / Hackathon mode, or restricted to owner
CREATE POLICY "Users can view own projects"
    ON public.projects FOR SELECT
    USING (auth.uid() = owner_id OR owner_id IS NULL);

CREATE POLICY "Users can insert own projects"
    ON public.projects FOR INSERT
    WITH CHECK (auth.uid() = owner_id OR owner_id IS NULL);

CREATE POLICY "Users can update own projects"
    ON public.projects FOR UPDATE
    USING (auth.uid() = owner_id OR owner_id IS NULL);

-- 4. Analyses Policies
CREATE POLICY "Users can view analyses for accessible projects"
    ON public.analyses FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.projects
            WHERE projects.id = analyses.project_id
            AND (projects.owner_id = auth.uid() OR projects.owner_id IS NULL)
        )
    );

CREATE POLICY "Allow inserting analyses"
    ON public.analyses FOR INSERT
    WITH CHECK (true);

-- 5. Issues Policies
CREATE POLICY "Users can view issues for accessible analyses"
    ON public.issues FOR SELECT
    USING (true);

CREATE POLICY "Allow inserting issues"
    ON public.issues FOR INSERT
    WITH CHECK (true);

-- 6. Fixes & Verification Results Policies
CREATE POLICY "Allow read and write for fixes"
    ON public.fixes FOR ALL
    USING (true);

CREATE POLICY "Allow read and write for verifications"
    ON public.verification_results FOR ALL
    USING (true);
