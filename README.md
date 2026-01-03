# Finance Made Simple

A Streamlit-based financial analysis platform with AI-powered insights.

## Manual QA Checklist

### 1. Sign-up Modal
- [ ] Click "Sign Up" button in sidebar
- [ ] Verify modal appears with form fields INSIDE (not behind overlay)
- [ ] Verify all fields present: Full Name, Email, Phone, Age, Password, Confirm Password
- [ ] Click X button in top-right corner
- [ ] Verify modal closes and returns to previous page without changing state
- [ ] **Note:** Click-outside-to-close is NOT supported by Streamlit dialogs (documented constraint)

### 2. Chat Icon / AI Chatbot
- [ ] Verify floating chat icon (robot emoji) appears at bottom-right of screen
- [ ] Click the chat icon
- [ ] Verify chat panel opens with message history area, input box, send button, close button
- [ ] Type a question (e.g., "What is a P/E ratio?")
- [ ] Verify "Thinking..." spinner appears while waiting
- [ ] Verify AI response is returned from Perplexity API
- [ ] If a ticker is selected, verify chatbot uses it as context (e.g., "Tell me about this stock")
- [ ] Click Close button to dismiss chat

### 3. User Progress Persistence
- [ ] Sign up with a new account
- [ ] Navigate to Company Analysis and select a ticker (e.g., AAPL)
- [ ] Toggle Unhinged Mode in sidebar (if age 18+)
- [ ] Close browser/tab completely
- [ ] Reopen the app and log in
- [ ] Verify selected ticker is restored
- [ ] Verify Unhinged Mode toggle state is restored

### 4. Unhinged Mode / Roast Commentary
- [ ] Verify Unhinged Mode toggle appears in sidebar under "Settings"
- [ ] If user age < 18, verify toggle is disabled with message "Unhinged Mode requires age 18+"
- [ ] Enable Unhinged Mode (if age 18+)
- [ ] Navigate to Start Here page
- [ ] Verify at most ONE roast appears per session (not on every page)
- [ ] Verify roasts are safe (no slurs, no self-harm jokes, no explicit sexual content)

### 5. Robinhood-style Guidance
- [ ] Navigate to "Start Here" page
- [ ] Verify short guidance caption appears: "Welcome! This is your starting point..."
- [ ] Navigate to "Company Analysis" page
- [ ] Verify short guidance caption appears: "Search for any company to see its financial health..."

## Supabase Tables Required

Run these SQL commands in your Supabase SQL Editor to create the required tables:

```sql
-- Profiles table for storing user profile data
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    phone TEXT,
    age INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read/write their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- User state table for persisting user progress
CREATE TABLE IF NOT EXISTS user_state (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    state JSONB DEFAULT '{}',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE user_state ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read/write their own state
CREATE POLICY "Users can view own state" ON user_state
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own state" ON user_state
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own state" ON user_state
    FOR INSERT WITH CHECK (auth.uid() = user_id);
```

## Streamlit Constraints

1. **Click-outside-to-close for dialogs**: Streamlit's `@st.dialog` decorator does not support dismissing dialogs by clicking outside the modal. Users must click the X button or Close button to dismiss.

2. **Session state persistence**: Streamlit session state is lost on page refresh. User progress is persisted to Supabase and restored on login.

## Environment Variables

Required environment variables for deployment:
- `FMP_API_KEY` - Financial Modeling Prep API key
- `PERPLEXITY_API_KEY` - Perplexity API key for AI chatbot
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon/public key
