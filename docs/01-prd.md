# Product Requirements Document (PRD): AccessDesk

| Field | Value |
|---|---|
| Project | AccessDesk |
| Course | CSE309 |
| Version | 1.0 (Draft) |
| Date | October 2026 |
| Author(s) | [Md. Ahsan Habib] |
| Repository | [GitHub repository link] |

---

## 1. Overview

AccessDesk is a web portal for managing requests for access to company tools (for example GitHub, AWS, Jira). Employees browse a tool catalog and submit access requests, managers approve or reject requests from their team, and admins manage the tool catalog and users and review a full audit trail of every action.

**In short:** Employees request access to tools, managers approve or reject, and admins manage tools and view audit logs.

AccessDesk records requests and decisions. It does not provision accounts inside the external tools themselves.

## 2. Problem Statement

In many small and mid-sized teams, access to tools is requested over chat or email. This causes three problems:

- **No standard process.** Requests are incomplete, and nobody is sure who can approve what.
- **No visibility.** An employee cannot see whether a request is pending, approved or rejected.
- **No history.** When someone asks "who approved this access, and why?", the answer is buried in old messages.

AccessDesk replaces this with one place to request, decide and audit, where each person can only do what their role permits.

## 3. Goals and Non-Goals

### Goals

| ID | Goal |
|---|---|
| G1 | Provide a single place to submit and track tool access requests. |
| G2 | Let managers approve or reject requests with a recorded comment. |
| G3 | Enforce least privilege through role-based access control (RBAC) and security scopes. |
| G4 | Keep an audit trail of every important action. |
| G5 | Deliver a complete, secure, well-structured web application using React + TypeScript and FastAPI. |

### Non-Goals

- No machine learning, AI, LLMs or RAG.
- No automatic provisioning of access in external tools (AccessDesk tracks decisions only).
- No email, Slack or push notifications.
- No single sign-on (SSO) or third-party login.
- No mobile application.

## 4. Users and Roles

| Role | Description | Typical need |
|---|---|---|
| **Employee** | A regular team member. | "I need access to the staging AWS account for my task." |
| **Manager** | Leads a team; approves requests from direct reports. Can also request access for themselves. | "I want to see what my team has asked for and decide quickly." |
| **Admin** | Back-office role that runs the system. | "I need to keep the tool list correct and see who did what." |

Each Employee and Manager is assigned one manager (their approver). The detailed permission matrix is in the SRS.

## 5. User Stories

Priority: all stories are Must-have unless stated. Release: **MVP** = mid-term demo, **Beta** = final demo.

| ID | As a... | I want to... | So that... | Release |
|---|---|---|---|---|
| US-01 | Employee | browse the tool catalog | I know which tools I can request | MVP |
| US-02 | Employee | submit an access request with a justification | my manager can judge it | MVP |
| US-03 | Employee | see my requests and their status | I know where each one stands | MVP |
| US-04 | Employee | cancel a pending request | I can withdraw a request I no longer need | MVP |
| US-05 | Manager | see pending requests from my team | I can act on them | MVP |
| US-06 | Manager | approve or reject a request with a comment | the decision is explained | MVP |
| US-07 | Admin | add, edit and deactivate tools | the catalog stays accurate | MVP |
| US-08 | Admin | create and update users, set their role and manager | the right people have the right role | MVP |
| US-09 | Admin | have every change and decision recorded in an audit log | actions can be traced | MVP |
| US-10 | User | log in with email and password | the system knows who I am | Beta |
| US-11 | User | be limited to the actions my role allows | the system follows least privilege | Beta |
| US-12 | User | see a profile dashboard (my details, role, scopes, request summary) | I understand my access in the system | Beta |
| US-13 | User | see only the menus and buttons I am allowed to use | the interface is not confusing | Beta |
| US-14 | Admin | view and filter the audit log | I can investigate who did what | Beta |
| US-15 | Team | use the app from a public URL | it can be demoed and shared | Beta |
| US-16 | Employee | optionally set an expiry date on a request | temporary access is clearly temporary | Beta (stretch) |

## 6. Release Plan

### MVP (mid-term demo, runs locally)

The core features, exposed through REST APIs, running locally.

- CRUD for tools and users.
- Create, list, cancel and decide access requests.
- Audit log entries written for each action.
- Basic React pages for the above.
- No real login yet. The acting user is chosen with a development-only user switcher, sent to the API in an `X-User-Id` header. This is a temporary placeholder and is removed in Beta.
- Local SQLite database.

### Beta (final demo)

- Authentication with JWT, hashed passwords.
- RBAC with the three roles and security scopes enforced on every protected endpoint.
- Role-based UI (protected routes, hidden buttons and menus) and user profile dashboard.
- Audit log viewer for admins.
- Hosted PostgreSQL and deployment on Vercel.
- Stretch: request expiry date.

## 7. Success Criteria

- Each of the three roles can complete its main flow end to end.
- Every protected endpoint rejects unauthenticated calls (401) and calls without the needed scope (403).
- Every create, update, decision and cancel action produces an audit entry.
- The project can be explained in 2-3 sentences, and the backend API is documented automatically at `/api/docs`.
- The MVP runs locally; the Beta is reachable at a public URL.

## 8. Assumptions and Constraints

- Tech stack is fixed: React with TypeScript (frontend) and FastAPI with Python (backend).
- Only free-tier services are used (GitHub, Vercel Hobby, hosted PostgreSQL free tier).
- Every Employee and Manager has one assigned manager. A user with no manager cannot submit requests.
- The system is for one organisation (no multi-tenancy).

## 9. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Scope grows too large | Unfinished project | Keep optional features (expiry) last; defer notifications. |
| Serverless hosting cannot persist a local database file | Data lost on deploy | Use hosted PostgreSQL in Beta; SQLite only for local MVP. |
| Authorization bugs (users doing things they should not) | Security failure | Enforce scopes in the backend on every endpoint; test the 403 cases. |
| Free-tier database pauses when idle | Slow first request in demo | Open the app shortly before the demo. |

## 10. Future Work

Email notifications, access expiry enforcement with scheduled jobs, bulk approvals, SSO, integration with real tool providers.
