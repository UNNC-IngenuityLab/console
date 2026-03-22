# API Integration Guide

This document describes how to integrate the real API into the admin frontend.

## Overview

The admin frontend now includes a complete API integration layer located in `src/api/`:

- `client.ts` - Axios HTTP client with interceptors
- `types.ts` - TypeScript type definitions
- `services.ts` - API service functions
- `stores/api.js` - Pinia store using the real API

## Setup

1. **Install dependencies:**
   ```bash
   cd ui/admin-v2
   pnpm install
   ```

2. **Configure API URL:**
   Copy `.env.example` to `.env.development` and set your API URL:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. **Start the backend:**
   ```bash
   cd ../../console
   uvicorn app.main:app --reload --port 8000
   ```

4. **Start the frontend:**
   ```bash
   pnpm dev
   ```

## Usage

### Using the API Service Directly

```javascript
import { usersApi, activitiesApi, announcementsApi } from '@/api/services'

// Fetch users
const response = await usersApi.list({ page: 1, page_size: 20 })
console.log(response.data.items)

// Create activity
await activitiesApi.create({
  name: 'New Event',
  venue: 'Main Hall',
  date_range: '2025-04-01 10:00~16:00',
})
```

### Using the API Store

Replace the mock store with the API store:

```javascript
// In your components, change:
import { useAdminStore } from '@/stores/index'

// To:
import { useApiStore } from '@/stores/api'

const store = useApiStore()

// Fetch data
await store.fetchUsers()
await store.fetchActivities()

// Access data
console.log(store.users)
console.log(store.usersPagination)
```

### Login Flow

```javascript
import { useApiStore } from '@/stores/api'

const store = useApiStore()

// Login
const success = await store.login('20240001', 'password')
if (success) {
  // Navigate to dashboard
  router.push('/dashboard')
}
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Get current user

### Users
- `GET /api/v1/users/` - List users
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}/points` - Update points
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Activities
- `GET /api/v1/activities/` - List activities
- `GET /api/v1/activities/{id}` - Get activity
- `POST /api/v1/activities/` - Create activity
- `PUT /api/v1/activities/{id}` - Update activity
- `DELETE /api/v1/activities/{id}` - Delete activity
- `POST /api/v1/activities/{id}/qrcode` - Generate QR code

### Announcements
- `GET /api/v1/announcements/` - List announcements
- `POST /api/v1/announcements/` - Create announcement
- `PUT /api/v1/announcements/{id}` - Update announcement
- `DELETE /api/v1/announcements/{id}` - Delete announcement

### Analytics
- `GET /api/v1/analytics/dashboard` - Dashboard stats
- `GET /api/v1/analytics/leaderboard` - Leaderboard
- `GET /api/v1/analytics/level-distribution` - Level distribution

## Migration Notes

The existing `stores/index.js` uses mock data. To migrate to the real API:

1. Update component imports from `useAdminStore` to `useApiStore`
2. Update property names to match API response format (snake_case)
3. Add loading states where appropriate
4. Handle errors using the store's error property

## Response Format

All API responses follow this format:

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

The Axios client automatically unwraps this format, so your code receives `data` directly.
