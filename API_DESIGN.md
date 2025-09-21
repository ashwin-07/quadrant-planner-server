# 🚀 Quadrant Planner API Design

## Overview
This document outlines the backend API requirements for the Quadrant Planner application. The frontend handles Google OAuth authentication and sends JWT tokens to the backend for user identification.

## Base Configuration
```
Base URL: https://api.quadrantplanner.com/v1
Content-Type: application/json
Authentication: JWT Bearer Token in Authorization header
```

## Authentication Strategy
- **Frontend handles**: Google OAuth, JWT token generation, localStorage
- **Backend receives**: JWT Bearer token in `Authorization` header
- **JWT token structure**: Google OAuth compatible with `iss`, `aud`, `sub`, `email` fields
- **User identification**: Extracted from JWT token `sub` field
- **No authentication endpoints** needed on backend

---

## 🎯 Goals APIs

### 1. Get All Goals
```http
GET /goals
Authorization: Bearer <jwt-token>
```

**Headers:**
- `Authorization`: `Bearer <jwt-token>` (required)

**Query Parameters:**
- `category`: `career|health|relationships|learning|financial|personal`
- `archived`: `true|false` (default: false)
- `limit`: `number` (default: 50, max: 100)
- `offset`: `number` (default: 0)

**Response:**
```json
{
  "success": true,
  "data": {
    "goals": [
      {
        "id": "string",
        "userId": "string",
        "title": "string",
        "description": "string",
        "category": "career|health|relationships|learning|financial|personal",
        "timeframe": "3_months|6_months|1_year|ongoing",
        "color": "string",
        "archived": false,
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z"
      }
    ],
    "total": 0,
    "hasMore": false
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### 2. Create Goal
```http
POST /goals
Authorization: Bearer <jwt-token>
```

**Headers:**
- `Authorization`: `Bearer <jwt-token>` (required)

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "category": "career|health|relationships|learning|financial|personal",
  "timeframe": "3_months|6_months|1_year|ongoing",
  "color": "string"
}
```

**Note:** `userId` is automatically extracted from the JWT token and not required in the request body.

**Response:**
```json
{
  "success": true,
  "data": {
    "goal": {
      "id": "string",
      "userId": "string",
      "title": "string",
      "description": "string",
      "category": "career",
      "timeframe": "3_months",
      "color": "blue",
      "archived": false,
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-01T00:00:00Z"
    }
  },
  "message": "Goal created successfully",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### 3. Update Goal
```http
PUT /goals/{goalId}
```

**Request Body:**
```json
{
  "userId": "string",
  "title": "string",
  "description": "string",
  "category": "career|health|relationships|learning|financial|personal",
  "timeframe": "3_months|6_months|1_year|ongoing",
  "color": "string",
  "archived": false
}
```

**Response:** Same as Create Goal

### 4. Delete Goal
```http
DELETE /goals/{goalId}?userId={userId}
```

**Response:**
```json
{
  "success": true,
  "message": "Goal deleted successfully",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### 5. Get Goal with Tasks
```http
GET /goals/{goalId}?userId={userId}&includeTasks=true
```

**Response:**
```json
{
  "success": true,
  "data": {
    "goal": {
      "id": "string",
      "userId": "string",
      "title": "string",
      "description": "string",
      "category": "career",
      "timeframe": "3_months",
      "color": "blue",
      "archived": false,
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-01T00:00:00Z"
    },
    "tasks": [
      {
        "id": "string",
        "title": "string",
        "completed": false,
        "quadrant": "Q1"
      }
    ],
    "stats": {
      "totalTasks": 5,
      "completedTasks": 2,
      "activeTasks": 3,
      "completionRate": 40
    }
  }
}
```

### 6. Get Goal Statistics
```http
GET /goals/{goalId}/stats?userId={userId}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "totalTasks": 5,
    "completedTasks": 2,
    "activeTasks": 3,
    "completionRate": 40,
    "averageTaskAge": 7.5,
    "lastActivityAt": "2025-01-01T00:00:00Z"
  }
}
```

---

## 📋 Tasks APIs

### 1. Get All Tasks
```http
GET /tasks?userId={userId}
```

**Query Parameters:**
- `userId` (required): `string`
- `quadrant`: `Q1|Q2|Q3|Q4|staging`
- `goalId`: `string`
- `completed`: `true|false`
- `isStaged`: `true|false`
- `priority`: `low|medium|high|urgent`
- `tags`: `string` (comma-separated)
- `limit`: `number` (default: 100, max: 200)
- `offset`: `number` (default: 0)

**Response:**
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": "string",
        "userId": "string",
        "goalId": "string",
        "title": "string",
        "description": "string",
        "quadrant": "Q1|Q2|Q3|Q4|staging",
        "dueDate": "2025-01-01T00:00:00Z",
        "estimatedMinutes": 60,
        "priority": "low|medium|high|urgent",
        "tags": ["work", "urgent"],
        "completed": false,
        "isStaged": false,
        "position": 0,
        "stagedAt": "2025-01-01T00:00:00Z",
        "organizedAt": "2025-01-01T00:00:00Z",
        "completedAt": null,
        "createdAt": "2025-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z",
        "goal": {
          "id": "string",
          "title": "string",
          "category": "career",
          "color": "blue"
        }
      }
    ],
    "total": 0,
    "hasMore": false
  }
}
```

### 2. Create Task
```http
POST /tasks
```

**Request Body:**
```json
{
  "userId": "string",
  "title": "string",
  "description": "string",
  "goalId": "string",
  "quadrant": "Q1|Q2|Q3|Q4|staging",
  "dueDate": "2025-01-01T00:00:00Z",
  "estimatedMinutes": 60,
  "priority": "low|medium|high|urgent",
  "tags": ["work", "urgent"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "task": {
      "id": "string",
      "userId": "string",
      "goalId": "string",
      "title": "string",
      "description": "string",
      "quadrant": "staging",
      "dueDate": "2025-01-01T00:00:00Z",
      "estimatedMinutes": 60,
      "priority": "medium",
      "tags": ["work"],
      "completed": false,
      "isStaged": true,
      "position": 0,
      "stagedAt": "2025-01-01T00:00:00Z",
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-01T00:00:00Z"
    }
  },
  "message": "Task created successfully"
}
```

### 3. Update Task
```http
PUT /tasks/{taskId}
```

**Request Body:**
```json
{
  "userId": "string",
  "title": "string",
  "description": "string",
  "goalId": "string",
  "quadrant": "Q1|Q2|Q3|Q4|staging",
  "dueDate": "2025-01-01T00:00:00Z",
  "estimatedMinutes": 60,
  "priority": "low|medium|high|urgent",
  "tags": ["work", "urgent"],
  "completed": false,
  "isStaged": false,
  "position": 0
}
```

**Response:** Same as Create Task

### 4. Delete Task
```http
DELETE /tasks/{taskId}?userId={userId}
```

**Response:**
```json
{
  "success": true,
  "message": "Task deleted successfully",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### 5. Toggle Task Completion
```http
PATCH /tasks/{taskId}/toggle
```

**Request Body:**
```json
{
  "userId": "string"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "task": {
      "id": "string",
      "completed": true,
      "completedAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-01T00:00:00Z"
    }
  },
  "message": "Task completion toggled"
}
```

### 6. Move Task (Drag & Drop)
```http
PATCH /tasks/{taskId}/move
```

**Request Body:**
```json
{
  "userId": "string",
  "quadrant": "Q1|Q2|Q3|Q4|staging",
  "position": 0,
  "isStaged": false
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "task": {
      "id": "string",
      "quadrant": "Q1",
      "position": 0,
      "isStaged": false,
      "organizedAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-01T00:00:00Z"
    }
  },
  "message": "Task moved successfully"
}
```

### 7. Bulk Update Tasks (Drag & Drop Multiple)
```http
PATCH /tasks/bulk
```

**Request Body:**
```json
{
  "userId": "string",
  "updates": [
    {
      "taskId": "string",
      "quadrant": "Q1|Q2|Q3|Q4|staging",
      "position": 0,
      "isStaged": false
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "updatedTasks": [
      {
        "id": "string",
        "quadrant": "Q1",
        "position": 0,
        "isStaged": false,
        "organizedAt": "2025-01-01T00:00:00Z"
      }
    ]
  },
  "message": "Tasks updated successfully"
}
```

---

## 📊 Analytics & Insights APIs

### 1. Get Analytics Dashboard
```http
GET /analytics/dashboard?userId={userId}
```

**Query Parameters:**
- `userId` (required): `string`
- `period`: `week|month|quarter|year` (default: week)
- `startDate`: `2025-01-01` (optional)
- `endDate`: `2025-01-31` (optional)

**Response:**
```json
{
  "success": true,
  "data": {
    "period": "week",
    "startDate": "2025-01-01T00:00:00Z",
    "endDate": "2025-01-07T23:59:59Z",
    "taskDistribution": {
      "Q1": 5,
      "Q2": 8,
      "Q3": 3,
      "Q4": 2,
      "staging": 4
    },
    "goalProgress": {
      "goal-123": {
        "totalTasks": 10,
        "completedTasks": 4,
        "activeTasks": 6,
        "completionRate": 40,
        "averageTaskAge": 7.5,
        "lastActivityAt": "2025-01-01T00:00:00Z"
      }
    },
    "stagingEfficiency": {
      "averageStagingTime": 48.5,
      "itemsStaged": 12,
      "itemsProcessed": 8,
      "processingRate": 66.7,
      "oldestStagedItem": {
        "taskId": "task-456",
        "daysSinceStaged": 5
      }
    },
    "productivity": {
      "tasksCreated": 15,
      "tasksCompleted": 12,
      "completionRate": 80,
      "q2Focus": 35.5,
      "goalBalance": 75.2,
      "streakDays": 7
    },
    "insights": [
      {
        "id": "insight-789",
        "type": "q2_focus",
        "severity": "success",
        "title": "Great Q2 Focus!",
        "description": "You're spending 35% of your time on important, non-urgent tasks. Keep it up!",
        "actionable": false,
        "createdAt": "2025-01-01T00:00:00Z"
      }
    ]
  }
}
```

### 2. Get Goal Analytics
```http
GET /analytics/goals/{goalId}?userId={userId}
```

**Query Parameters:**
- `userId` (required): `string`
- `period`: `week|month|quarter|year` (default: month)
- `startDate`: `2025-01-01` (optional)
- `endDate`: `2025-01-31` (optional)

**Response:**
```json
{
  "success": true,
  "data": {
    "goal": {
      "id": "string",
      "title": "Master React Hooks",
      "category": "learning"
    },
    "stats": {
      "totalTasks": 10,
      "completedTasks": 4,
      "activeTasks": 6,
      "completionRate": 40,
      "averageTaskAge": 7.5,
      "lastActivityAt": "2025-01-01T00:00:00Z"
    },
    "taskTrends": [
      {
        "date": "2025-01-01",
        "created": 2,
        "completed": 1,
        "active": 8
      },
      {
        "date": "2025-01-02",
        "created": 1,
        "completed": 2,
        "active": 7
      }
    ],
    "quadrantDistribution": {
      "Q1": 2,
      "Q2": 5,
      "Q3": 1,
      "Q4": 0,
      "staging": 2
    }
  }
}
```

### 3. Dismiss Insight
```http
PATCH /analytics/insights/{insightId}/dismiss
```

**Request Body:**
```json
{
  "userId": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Insight dismissed",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

---

## 🔔 Notifications APIs (Optional)

### 1. Get Notifications
```http
GET /notifications?userId={userId}
```

**Query Parameters:**
- `userId` (required): `string`
- `unread`: `true|false`
- `limit`: `number` (default: 20, max: 50)
- `offset`: `number` (default: 0)

**Response:**
```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "id": "string",
        "userId": "string",
        "type": "task_reminder|goal_deadline|weekly_review|staging_reminder",
        "title": "Task Reminder",
        "message": "You have 3 tasks overdue in Q1",
        "read": false,
        "createdAt": "2025-01-01T00:00:00Z"
      }
    ],
    "total": 5,
    "unreadCount": 3
  }
}
```

### 2. Mark Notification as Read
```http
PATCH /notifications/{notificationId}/read
```

**Request Body:**
```json
{
  "userId": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Notification marked as read",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

---

## 🏗️ Data Models

### User (Frontend Only)
```typescript
interface User {
  id: string;
  email: string;
  name: string;
  fullName?: string;
  avatarUrl?: string;
  onboarded: boolean;
  lastLoginAt: string;
  preferences: UserPreferences;
  createdAt: string;
  updatedAt: string;
}
```

### Goal (Database Model)
```typescript
interface Goal {
  id: string; // UUID
  userId: string; // Foreign key
  title: string; // max 200 chars
  description?: string; // max 1000 chars
  category: 'career' | 'health' | 'relationships' | 'learning' | 'financial' | 'personal';
  timeframe: '3_months' | '6_months' | '1_year' | 'ongoing';
  color: string; // hex color or color name
  archived: boolean; // default: false
  createdAt: string; // ISO timestamp
  updatedAt: string; // ISO timestamp
}
```

### Task (Database Model)
```typescript
interface Task {
  id: string; // UUID
  userId: string; // Foreign key
  goalId?: string; // Foreign key, nullable
  title: string; // max 200 chars
  description?: string; // max 1000 chars
  quadrant: 'Q1' | 'Q2' | 'Q3' | 'Q4' | 'staging';
  dueDate?: string; // ISO timestamp, nullable
  estimatedMinutes?: number; // 1-480 range
  priority: 'low' | 'medium' | 'high' | 'urgent'; // default: medium
  tags: string[]; // max 10 tags, each max 50 chars
  completed: boolean; // default: false
  isStaged: boolean; // true if quadrant is 'staging'
  position: number; // for ordering within quadrant
  stagedAt?: string; // ISO timestamp when moved to staging
  organizedAt?: string; // ISO timestamp when moved from staging
  completedAt?: string; // ISO timestamp when completed
  createdAt: string; // ISO timestamp
  updatedAt: string; // ISO timestamp
}
```

---

## ⚙️ Technical Requirements

### Database Considerations
- **User Identification**: Use `userId` string field in all tables
- **Indexes**: Create indexes on `userId`, `goalId`, `quadrant`, `completed`, `createdAt`
- **Constraints**: 
  - Max 100 goals per user
  - Max 1000 tasks per user
  - Max 50 tasks per goal
- **Position Management**: Ensure position uniqueness within quadrant per user

### Performance
- **Pagination**: Default 50 items, max 100 for goals, max 200 for tasks
- **Caching**: Cache analytics data for 1 hour
- **Rate Limiting**: 1000 requests/hour per userId
- **Bulk Operations**: Support up to 50 items in bulk updates

### Error Handling
```json
{
  "success": false,
  "error": {
    "message": "Goal not found",
    "code": "GOAL_NOT_FOUND",
    "details": {
      "goalId": "invalid-id",
      "userId": "user-123"
    }
  },
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### Common HTTP Status Codes
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `409`: Conflict (duplicate data)
- `422`: Unprocessable Entity
- `429`: Rate Limited
- `500`: Internal Server Error

---

## 🚀 API Priority

### Phase 1 (MVP)
1. **Goals**: Create, Read, Update, Delete
2. **Tasks**: Create, Read, Update, Delete, Toggle Complete
3. **Tasks**: Move/Drag & Drop

### Phase 2 (Enhanced)
1. **Analytics**: Basic dashboard
2. **Bulk Operations**: Multi-task updates
3. **Goal Statistics**

### Phase 3 (Future)
1. **Advanced Analytics**: Trends, insights
2. **Notifications**: Reminders, weekly reviews
3. **Real-time Updates**: WebSocket support

---

## 📝 Notes for Backend Team

1. **No Authentication**: Frontend handles Google OAuth completely
2. **User Identification**: Always include `userId` in requests
3. **Data Validation**: Validate all input data, especially arrays and optional fields
4. **Position Management**: When moving tasks, update positions of other tasks in the same quadrant
5. **Soft Deletes**: Consider soft deletes for goals/tasks for better user experience
6. **Audit Trail**: Track createdAt/updatedAt for all operations
7. **Goal-Task Relationship**: When deleting a goal, decide whether to delete associated tasks or set goalId to null

This API design supports all current frontend functionality while remaining simple and focused on core features.
