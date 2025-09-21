# Quadrant Planner - Product Requirements Document

**Version 1.0** | **Date: August 2025** 

---

## Executive Summary

Quadrant Planner is a philosophy-driven productivity web application that transforms how users approach task management by implementing Stephen Covey's Time Management Matrix from "7 Habits of Highly Effective People." Unlike traditional to-do apps that treat all tasks equally, Quadrant Planner visually guides users to focus on Important, Not Urgent activities (Quadrant II) that drive long-term success.

**The Problem:** Most productivity apps encourage reactive task completion rather than proactive priority management, leading to busy-but-unproductive cycles.

**The Solution:** A visual quadrant system that connects goals to tasks, provides priority clarity, and includes reflection tools to build sustainable productivity habits.

---

## Product Vision & Philosophy

### Vision Statement

"Transform task management from reactive completion to intentional time investment, helping users build lives of significance rather than just efficiency."

### Core Philosophy

- **Habit 2 (Begin With the End in Mind):** Goals drive task creation
- **Habit 3 (Put First Things First):** Visual quadrant prioritization
- **Habit 7 (Sharpen the Saw):** Reflection and continuous improvement
- **Cal Newport's Deep Work:** Protect high-value work through intentional scheduling

---

## Target Users & Use Cases

### Primary Personas

**1. The Ambitious Professional (Primary)**

- **Profile:** 25-40, knowledge worker with side projects/goals
- **Pain Point:** Drowning in urgent-but-unimportant tasks, neglecting long-term growth
- **Use Case:** "I want to ensure my daily work aligns with my career advancement and side business goals"

**2. The Overwhelmed Entrepreneur (Secondary)**

- **Profile:** Small business owner or startup founder
- **Pain Point:** Everything feels urgent; struggling to work *on* business vs *in* business
- **Use Case:** "I need clarity on which tasks actually move my business forward"

**3. The Intentional Student (Secondary)**

- **Profile:** Graduate students, professionals in career transition
- **Pain Point:** Balancing immediate academic/work demands with long-term skill development
- **Use Case:** "I want to invest time in skills that matter for my future, not just current requirements"

---

## User Stories & Acceptance Criteria

Mocks: https://app.visily.ai/projects/52a9408c-553e-462c-aadd-63ed3f9b1573/boards/2137690

### Epic 1: User Authentication & Onboarding

**As a user, I want to create an account with Google and get guided through the app's philosophy so that I understand how to use it effectively.**

**User Stories:**

- As a new user, I can sign up with Google OAuth (one-click authentication)
- As a returning user, I can log in securely with Google
- As a new user, I receive a guided onboarding that explains Covey's quadrants
- As a user, I can log out and my data remains secure
- As a user, my Google profile information is used to personalize the experience

**Acceptance Criteria:**

- Google OAuth integration with Supabase Auth
- No email verification required (Google handles verification)
- Automatic profile creation from Google account data
- 3-step onboarding: Welcome → Quadrant explanation → Create first goal
- Session management with auto-logout after 30 days inactive
- Seamless login experience (no password management)

**Future Scope (Post-MVP):**

- GitHub OAuth integration
- Guest mode with limited functionality (no data persistence)
- Manual email/password as fallback option

### Epic 2: Goals Foundation

**As a user, I want to define and manage my high-level goals so that my tasks connect to meaningful outcomes.**

**User Stories:**

- As a user, I can create goals in categories (Career, Health, Relationships, Learning, Financial)
- As a user, I can edit and delete goals
- As a user, I can set target timeframes for goals (3 months, 6 months, 1 year, ongoing)
- As a user, I can see all my goals in a clean, organized view

**Acceptance Criteria:**

- Maximum 12 active goals (prevents overcommitment)
- Goals have titles, descriptions, and category tags
- Goals can be archived but not permanently deleted (for analytics)

### Epic 3: Staging Zone & Quick Capture

**As a user, I want to quickly capture thoughts and ideas before organizing them into quadrants so that I don't lose important insights.**

**User Stories:**

- As a user, I can quickly stage tasks for later organization without friction
- As a user, I'm gently prompted when my staging zone reaches capacity (5 items)
- As a user, I can promote staged items directly to appropriate quadrants via drag-and-drop
- As a user, I receive weekly reminders to process items in my staging zone
- As a user, I can edit and delete staged items

**Acceptance Criteria:**

- Staging zone has maximum capacity of 5 items (forces regular processing)
- Staged tasks require only: title (goal assignment happens during promotion)
- Visual distinction from quadrants (dashed border, lighter styling, staging icon)
- Easy promotion workflow: drag from staging zone to quadrants
- Gentle notifications: "3 items staged and ready to organize"
- Empty state guidance: "Stage quick thoughts here, then organize into quadrants"

### Epic 4: Quadrant Task Management

**As a user, I want to create and organize tasks in Covey's four quadrants so that I can focus on what truly matters.**

**User Stories:**

- As a user, I can add tasks directly to specific quadrants (Q1: Urgent+Important, Q2: Important+Not Urgent, Q3: Urgent+Not Important, Q4: Neither)
- As a user, I can promote tasks from staging zone to quadrants with goal assignment
- As a user, I can set due dates and priority levels for tasks
- As a user, I can mark tasks as complete and see completion status
- As a user, I can edit and delete tasks within quadrants
- As a user, I can drag tasks between quadrants to reclassify them
- As a user, my tasks sync across devices in real-time

**Acceptance Criteria:**

- Quadrant tasks require: title, quadrant, and goal assignment
- Tasks optionally include: description, due date, estimated time
- Visual quadrant grid with clear labels, color coding, and task counts
- Color-coding by goal category for quick visual identification
- Completed tasks move to a "Done" section but remain visible for analytics
- Real-time sync using Supabase subscriptions
- Clear quadrant labels with Covey's definitions

### Epic 5: Introspection & Analytics

**As a user, I want to visualize my task patterns and time investment so that I can make better priority decisions.**

**User Stories:**

- As a user, I can see what percentage of my tasks fall into each quadrant
- As a user, I can view my task distribution over time (weekly/monthly)
- As a user, I can see which goals receive the most/least attention
- As a user, I can track my staging zone processing efficiency
- As a user, I receive gentle nudges when Quadrant II tasks are under 30% of my workload
- As a user, I can see analytics on staged vs. organized task ratios
- As a user, I can export my task data for external analysis

**Acceptance Criteria:**

- Dashboard shows current quadrant distribution as pie chart
- Historical view shows trends over 4-week periods
- Goal-based analytics show task count and completion rate per goal
- Staging zone analytics: processing time, items staged vs. organized
- Warning indicator when Q2 tasks < 30% of total active tasks
- "Items in staging" vs "Items processed from staging" metrics
- Simple CSV export functionality

---

## Technical Requirements

### Architecture

- **Frontend:** React.js with TypeScript
- **Styling:** Tailwind CSS for responsive design
- **State Management:** React Context API (MVP), Redux Toolkit (future)
- **Data Storage:** LocalStorage (MVP), Firebase/Supabase (Phase 2)
- **Charts/Visualizations:** Recharts or Chart.js

### Performance Requirements

- Page load time: < 2 seconds
- Task creation/editing: < 500ms response time
- Support 500+ tasks per user without performance degradation
- Mobile-responsive (tablet and phone)

### Browser Support

- Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Mobile web browsers (iOS Safari, Chrome Mobile)

---

## User Interface Requirements

### Navigation Structure

```
Landing Page: [Hero] [Features] [Sign In with Google]

Authentication:
├── Sign In with Google (OAuth)
├── Automatic Profile Creation
├── Onboarding (3 steps)
└── Return User Auto-Login

Future Authentication Options:
├── GitHub OAuth (Phase 2)
└── Guest Mode (Phase 3)

App Header: [Quadrant Planner Logo] [Goals] [Tasks] [Introspect] [Profile Menu]

Goals Tab:
├── Add New Goal (+)
├── Goal Categories (Career, Health, Learning, Financial, Personal)
└── Goal Cards (Title, Category Badge, Progress Bar, Active Task Count)

Tasks Tab (Primary View):
┌─────────────────────────────────────────────────────────────┐
│ 📦 STAGING ZONE (5 max items) - Dashed border, light blue   │
│ "Stage quick thoughts here, then organize into quadrants"   │
│ [+ Stage Task] button                                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────┬─────────────────────────────────┐
│ 🚨 Q1: DO FIRST         │ 🎯 Q2: SCHEDULE                 │
│ Important & Urgent      │ Important, Not Urgent           │
│ (Red theme, fire icon)  │ (Green theme, target icon)      │
│ [+ Add Q1 Task]         │ [+ Add Q2 Task]                 │
├─────────────────────────┼─────────────────────────────────┤
│ ⚡ Q3: DELEGATE         │ 🗑️ Q4: ELIMINATE                │
│ Urgent, Not Important   │ Not Important, Not Urgent       │
│ (Yellow theme, bolt)    │ (Gray theme, trash icon)        │
│ [+ Add Q3 Task]         │ [+ Add Q4 Task]                 │
└─────────────────────────┴─────────────────────────────────┘

Task Cards Design:
├── Goal color-coded left border
├── Task title (bold)
├── Goal badge (small, colored)
├── Due date (if set)
├── Completion checkbox
└── Drag handle (⋮⋮)

Quick Actions Panel:
├── Filter by Goal
├── Filter by Due Date
├── Show Completed Toggle
└── Quick Stats (Q2 %, Staging items)

Introspect Tab:
├── 📊 Quadrant Distribution (Pie Chart with Q2 emphasis)
├── 📈 Weekly Trends (Line Chart - tasks created/completed)
├── 🎯 Goal Progress (Horizontal bar charts)
├── ⚡ Staging Efficiency ("Average time in staging: 2.3 days")
├── 🏆 Insights Panel
│   ├── "Great! 35% of your tasks are in Q2 this week"
│   ├── "You have 3 items staged for 5+ days"
│   └── "Your 'Health' goal needs more attention"
└── [Export Data] button

```

### Key UI Principles

- **Staging Zone Emphasis:** Dashed border, light blue background, staging icon (📦)
- **Quadrant II Prominence:** Green color, larger visual weight, target icon (🎯)
- **Visual Hierarchy:** Staging → Q2 → Q1 → Q3 → Q4 in terms of visual importance
- **Color Psychology:**
    - Q1 Red (urgency/fire) 🚨
    - Q2 Green (growth/success) 🎯
    - Q3 Yellow (caution/delegation) ⚡
    - Q4 Gray (elimination/minimal) 🗑️
    - Staging Blue (temporary/processing) 📦
- **Gentle Guidance:** Subtle notifications, encouraging copy, not aggressive gamification
- **Goal Integration:** Color-coded left borders on task cards matching goal categories
- **Drag & Drop:** Clear visual feedback when moving between staging and quadrants
- **Empty State Messaging:**
    - Staging: "Stage quick thoughts here, then organize into quadrants"
    - Q2: "Your most important work lives here - schedule time for these"
    - Q4: "Question whether these tasks are necessary"

---

## Success Metrics & KPIs

### Primary Metrics

1. **Quadrant II Focus:** % of tasks created in Q2 (Target: >30%)
2. **Staging Efficiency:** Average time items spend in staging zone (Target: <3 days)
3. **User Engagement:** Weekly active usage (Target: 4+ sessions/week)
4. **Goal Completion:** Tasks completed per goal per month
5. **User Retention:** 30-day retention rate (Target: >60%)

### Secondary Metrics

- Staging zone processing rate (staged items → organized per week)
- Average session duration
- Task completion rate by quadrant
- Goal distribution balance (no single goal >50% of tasks)
- Time from task creation to completion
- Drag-and-drop usage frequency
- User satisfaction score (post-MVP survey)

---

## MVP Scope & Timeline

### Phase 1: Core MVP (10-12 weeks)

**Week 1-2:** Project setup, Supabase configuration, Google OAuth integration
**Week 3-4:** User onboarding flow and landing page with Google sign-in
**Week 5-6:** Goals management (CRUD operations) with database integration
**Week 7-8:** Task management with staging zone and quadrant assignment
**Week 9-10:** Basic analytics and introspection dashboard
**Week 11-12:** Polish, testing, deployment, user feedback collection

### MVP Feature List

✅ **Google OAuth Authentication**

- One-click Google sign-in/sign-up
- Automatic profile creation from Google account
- Secure session management with Supabase
- No password management complexity

✅ **Streamlined Onboarding**

- Welcome flow explaining Covey's quadrants
- Google profile integration for personalization
- Guided first goal creation
- Tutorial hints for staging zone and task creation

✅ **Staging Zone System**

- Quick task capture with 5-item limit
- Visual distinction (dashed border, staging icon)
- Gentle processing prompts and notifications
- Drag-and-drop promotion to quadrants

✅ **Goals Management**

- Create/edit/delete goals with database persistence
- Categorize goals (Career, Health, Learning, Financial, Personal)
- Goals overview with task counts and progress visualization

✅ **Enhanced Task Management**

- Create tasks in staging zone or directly in quadrants
- Assign tasks to goals with visual color-coding
- Mark complete/incomplete with real-time sync
- Drag-and-drop between staging and quadrants
- Edit and delete capabilities
- Cross-device synchronization

✅ **Visual Quadrant Dashboard**

- 2x2 visual grid with staging zone above
- Color-coded quadrants with meaningful icons and labels
- Task cards with goal badges and completion status
- Real-time task counts per section
- Drag-and-drop reclassification

✅ **Enhanced Analytics**

- Quadrant distribution with Q2 emphasis
- Staging zone efficiency metrics
- Task completion trends over time
- Goal progress tracking and balance analysis
- Processing time analytics (staging → organized)
- Gentle insights and recommendations

✅ **Data Infrastructure**

- Supabase database with proper schemas
- Real-time subscriptions for live updates
- Data backup and recovery
- User data privacy and security

### MVP Non-Goals

❌ GitHub OAuth (Phase 2 roadmap)
❌ Guest mode (Phase 3 roadmap)
❌ Email/password authentication
❌ Password reset functionality
❌ Email verification flows
❌ Calendar integration
❌ AI task classification

❌ Time tracking/Pomodoro timers
❌ Collaboration features
❌ Mobile app (web-responsive only)
❌ Advanced reporting/exports beyond CSV
❌ Third-party integrations
❌ Offline functionality
❌ Automatic staging zone organization
❌ Task dependencies or subtasks

---

## Post-MVP Roadmap

### Phase 2: Enhanced Authentication & Smart Insights (3 months post-MVP)

- GitHub OAuth integration for developer audience
- Historical trend analysis and enhanced analytics
- Smart task classification suggestions
- Goal progress tracking with deadlines

### Phase 3: Accessibility & Time Integration (6 months post-MVP)

- Guest mode with limited functionality (no data persistence)
- Calendar sync (Google Calendar)
- Time blocking for Q2 tasks
- Deep work session planning

### Phase 4: Advanced Features (12 months post-MVP)

- Email/password authentication as fallback
- Team/collaboration features
- Mobile native apps
- API for third-party integrations

---

## Risk Assessment & Mitigation

### Technical Risks

- **Risk:** Google OAuth dependency and service outages
- **Mitigation:** Clear error handling, status page monitoring, fallback messaging
- **Risk:** User lock-in to Google ecosystem concerns
- **Mitigation:** Clear data export options, roadmap communication for GitHub auth
- **Risk:** Supabase real-time performance with high task volumes
- **Mitigation:** Implement pagination, optimize queries, monitor performance metrics
- **Risk:** Authentication security vulnerabilities
- **Mitigation:** Follow Supabase + Google OAuth security best practices, proper RLS policies

### Product Risks

- **Risk:** Users uncomfortable with Google-only authentication
- **Mitigation:** Clear privacy messaging, roadmap showing future auth options
- **Risk:** Developer audience expecting GitHub login immediately
- **Mitigation:** Prominent "GitHub coming soon" messaging, early access list
- **Risk:** Users reverting to familiar flat task lists
- **Mitigation:** Strong onboarding that demonstrates quadrant value, guided tutorials
- **Risk:** Staging zone becoming a permanent dumping ground
- **Mitigation:** 5-item limit, gentle processing prompts, weekly review nudges

### Market Risks

- **Risk:** Crowded productivity app market
- **Mitigation:** Focus on philosophy differentiation, not feature parity

---

## Definition of Done

### MVP Ready Criteria

- [ ]  All MVP user stories completed with acceptance criteria
- [ ]  Cross-browser testing completed
- [ ]  Mobile responsiveness verified
- [ ]  Basic accessibility compliance (WCAG 2.1 AA)
- [ ]  Performance benchmarks met
- [ ]  User onboarding flow tested
- [ ]  Analytics implementation verified
- [ ]  Error handling and edge cases covered

### Launch Readiness

- [ ]  Production deployment successful
- [ ]  User feedback collection system in place
- [ ]  Support documentation created
- [ ]  Monitoring and error tracking active
- [ ]  Backup and data recovery tested

---

## Appendix

### Competitive Analysis

**Traditional Task Apps (Todoist, Things, TickTick):**

- Strength: Feature-rich, established
- Weakness: No priority philosophy, overwhelming options

**Notion, Obsidian:**

- Strength: Flexibility, power users love them
- Weakness: Complexity, steep learning curve

**Our Differentiation:**

- Philosophy-first approach
- Visual simplicity with depth
- Focus on reflection and growth, not just completion

### Technical Architecture Diagram

```
Frontend (React + TypeScript + Tailwind)
├── Pages/
│   ├── Landing/
│   ├── Auth/ (Login, Signup, Reset)
│   ├── Onboarding/
│   └── App/ (Goals, Tasks, Analytics)
├── Components/
│   ├── Auth/
│   ├── Goals/
│   ├── Tasks/
│   ├── Quadrants/
│   └── Analytics/
├── Hooks/
├── Utils/
└── Types/

Backend (Supabase)
├── Authentication
│   ├── Email/Password
│   ├── Social Logins (Google, GitHub)
│   └── Session Management
├── Database (PostgreSQL)
│   ├── Users Table
│   ├── Goals Table
│   ├── Tasks Table
│   └── Analytics Views
├── Real-time Subscriptions
├── Row Level Security (RLS)
└── Storage (future: file attachments)

Database Schema:
Users: id, email, created_at, last_login, onboarded
Goals: id, user_id, title, description, category, timeframe, created_at, archived
Tasks: id, user_id, goal_id, title, description, quadrant, due_date, completed, is_staged, created_at, updated_at, staged_at, organized_at
Analytics_Views: User staging efficiency, quadrant distribution, goal progress

```