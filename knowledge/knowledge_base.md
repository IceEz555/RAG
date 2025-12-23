# 🌐 System Overview

## What is this system?
The Intern Task Management System is a web-based application designed to help teams manage projects, track tasks, and collaborate effectively.

## Why is this system needed?
Without a task management system, teams often face:
- Unclear task ownership
- Missed deadlines
- Poor visibility of project progress

This system provides structure, visibility, and accountability for team-based work.

## Key Features
- Authentication & Authorization
- User Management
- Project Dashboard
- Kanban Board
- Real-time task updates

---

# 👥 User Roles & Permissions

## Admin
### What can Admin do?
- Create, edit, and delete users
- Assign user roles (Admin / Project Manager / Member)
- View system analytics
- Configure global system settings

### Why is the Admin role important?
Admins ensure system security and proper access control across the platform.

---

## Project Manager (PM)
### What can Project Managers do?
- Create and manage projects
- Assign members to projects
- Create, assign, and manage tasks
- View project progress and statistics

### Why separate PM from Admin?
The PM role focuses on project execution and delivery, while Admin focuses on system-level management.

---

## Member
### What can Members do?
- View assigned projects
- View personal tasks on the Kanban board
- Update task status (e.g., To Do → In Progress → Done)

### Why limit Member permissions?
Limiting permissions reduces accidental changes and keeps project control centralized.

---

# 📂 Task & Project Concepts

## Project
### What is a Project?
A Project represents a high-level goal or assignment (e.g., "Website Redesign").

### What does a Project contain?
- Multiple related tasks
- Assigned members
- A shared objective

---

## Task
### What is a Task?
A Task is a specific unit of work within a project (e.g., "Design Login Page").

### Task Attributes
- Title & Description
- Assignee
- Priority (Low / Medium / High)
- Due Date

### Why break work into tasks?
Breaking work into smaller tasks improves tracking, clarity, and accountability.

---

# 🔄 Task Status (Workflow)

## Task Lifecycle
Tasks move through the following stages:

### To Do
- Task is created
- Work has not started yet

### In Progress
- Task is actively being worked on
- Best Practice: Limit to 2 concurrent tasks per person

### In Review
- Task is completed
- Work is reviewed, verified, and finalized

### Done
- Task is completed
- Work is reviewed, verified, and finalized

---

## Why limit tasks in In Progress?
Too many active tasks can lead to:
- Reduced focus
- Lower work quality
- Delayed completion

---

# 📋 Kanban Board Usage

## What is a Kanban Board?
The Kanban Board is a visual tool used to track task progress and workflow.

## How does it work?
Tasks are represented as cards and moved between columns:
- To Do → In Progress → Done

## When should Kanban be reviewed?
- Daily by individual members
- During team stand-ups or project review meetings

## Common Issues
- Too many tasks in "In Progress" indicate workload overload
- Tasks stuck too long should be reviewed or reassigned

---

# 💡 Best Practices (For Developers & Teams)

## Authentication
- Always use the `useAuth()` hook to access the current user context in the frontend

## Naming Conventions
- Variables: camelCase (e.g., taskList, userProfile)
- Components: PascalCase (e.g., ProjectCard.jsx, Navbar.jsx)
- Database fields: snake_case (e.g., user_id, created_at)

## Git Workflow
- Create a new branch for every feature (feature/task-id-name)
- Never push directly to the main branch

## API Usage
- Always use the pre-configured Axios instance
- This ensures tokens and headers are handled consistently

---

# ❓ Common Questions (FAQ)

### Q: How do I become a Project Manager?
**A:** Ask an Admin to update your role in the User Management page.

### Q: I can’t see a project. Why?
**A:** You may not be added as a project member. Ask the Project Manager to add you using the "Manage Team" feature.

### Q: Can I delete a task?
**A:** Only Project Managers and Admins can delete tasks. Members can only update task status.

### Q: How do I report a bug?
**A:** Create a task with **High priority** and prefix the title with `[BUG]`.

---

# 🚀 Future Extensions

## How can this system evolve?
- Integrate AI with real-time database data
- Provide workload analysis and insights
- Recommend task prioritization
- Support decision-making for Project Managers

## Why start with knowledge-based RAG?
This approach ensures:
- Controlled and reliable AI responses
- Clear demonstration of RAG architecture
- Easy extension to real-time data sources in the future

---

