import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAdminStore = defineStore('admin', () => {
  // Users
  const users = ref([
    { id: 1, studentId: '20240001', nickname: 'Leo Zhang', totalPoints: 45, avatarUrl: '👨‍🎓', registeredActivities: [1, 2, 5], createdAt: '2024-09-01' },
    { id: 2, studentId: '20240002', nickname: 'Emma Li', totalPoints: 78, avatarUrl: '👩‍🎓', registeredActivities: [1, 3, 6, 8], createdAt: '2024-09-02' },
    { id: 3, studentId: '20240003', nickname: 'Alex Wang', totalPoints: 92, avatarUrl: '🧑‍🎓', registeredActivities: [2, 3, 4, 7, 9], createdAt: '2024-09-03' },
    { id: 4, studentId: '20240004', nickname: 'Sophie Chen', totalPoints: 35, avatarUrl: '👩‍💻', registeredActivities: [1, 4], createdAt: '2024-09-05' },
    { id: 5, studentId: '20240005', nickname: 'James Liu', totalPoints: 60, avatarUrl: '👨‍💻', registeredActivities: [2, 5, 8], createdAt: '2024-09-08' },
    { id: 6, studentId: '20240006', nickname: 'Mia Zhao', totalPoints: 15, avatarUrl: '🧑‍🔬', registeredActivities: [], createdAt: '2024-09-10' },
    { id: 7, studentId: '20240007', nickname: 'Oliver Wu', totalPoints: 88, avatarUrl: '👨‍🎨', registeredActivities: [1, 2, 3, 6, 7, 10], createdAt: '2024-09-12' },
    { id: 8, studentId: '20240008', nickname: 'Lily Huang', totalPoints: 52, avatarUrl: '👩‍🎤', registeredActivities: [3, 5], createdAt: '2024-09-15' }
  ])

  // Activities
  const activities = ref([
    { id: 1, name: 'Welcome Orientation', date: '2024-09-05', venue: 'Main Auditorium', totalPoint: 15, signUpCount: 120, completedCount: 98, status: 'completed',
      subActivities: [{ id: 1, name: 'Check-in', point: 5 }, { id: 2, name: 'Campus Tour', point: 5 }, { id: 3, name: 'Ice Breaker Game', point: 5 }] },
    { id: 2, name: 'Mid-Autumn Festival', date: '2024-09-17', venue: 'Student Plaza', totalPoint: 20, signUpCount: 85, completedCount: 72, status: 'completed',
      subActivities: [{ id: 1, name: 'Attendance', point: 5 }, { id: 2, name: 'Lantern Making', point: 10 }, { id: 3, name: 'Mooncake Tasting', point: 5 }] },
    { id: 3, name: 'Hackathon 2024', date: '2024-10-12', venue: 'Innovation Hub', totalPoint: 30, signUpCount: 60, completedCount: 45, status: 'completed',
      subActivities: [{ id: 1, name: 'Team Registration', point: 5 }, { id: 2, name: 'Project Submission', point: 15 }, { id: 3, name: 'Demo Presentation', point: 10 }] },
    { id: 4, name: 'Sports Day', date: '2024-10-28', venue: 'Sports Field', totalPoint: 25, signUpCount: 150, completedCount: 130, status: 'completed',
      subActivities: [{ id: 1, name: 'Opening Ceremony', point: 5 }, { id: 2, name: 'Relay Race', point: 10 }, { id: 3, name: 'Tug of War', point: 5 }, { id: 4, name: 'Awards Ceremony', point: 5 }] },
    { id: 5, name: 'Career Workshop', date: '2024-11-08', venue: 'Conference Room A', totalPoint: 20, signUpCount: 40, completedCount: 35, status: 'completed',
      subActivities: [{ id: 1, name: 'Attendance', point: 5 }, { id: 2, name: 'Resume Review', point: 10 }, { id: 3, name: 'Mock Interview', point: 5 }] },
    { id: 6, name: 'Charity Bazaar', date: '2024-11-22', venue: 'Student Center', totalPoint: 20, signUpCount: 70, completedCount: 58, status: 'completed',
      subActivities: [{ id: 1, name: 'Booth Setup', point: 5 }, { id: 2, name: 'Sales Participation', point: 10 }, { id: 3, name: 'Cleanup', point: 5 }] },
    { id: 7, name: 'Winter Concert', date: '2024-12-15', venue: 'Main Auditorium', totalPoint: 15, signUpCount: 200, completedCount: 180, status: 'completed',
      subActivities: [{ id: 1, name: 'Check-in', point: 5 }, { id: 2, name: 'Watch Performance', point: 5 }, { id: 3, name: 'Post-event Survey', point: 5 }] },
    { id: 8, name: 'New Year Gala', date: '2025-01-10', venue: 'Grand Hall', totalPoint: 25, signUpCount: 180, completedCount: 160, status: 'completed',
      subActivities: [{ id: 1, name: 'Red Carpet Entry', point: 5 }, { id: 2, name: 'Talent Show', point: 10 }, { id: 3, name: 'Countdown Party', point: 10 }] },
    { id: 9, name: 'Spring Volunteer Day', date: '2025-03-08', venue: 'Community Center', totalPoint: 25, signUpCount: 30, completedCount: 22, status: 'active',
      subActivities: [{ id: 1, name: 'Sign-in', point: 5 }, { id: 2, name: 'Community Service', point: 15 }, { id: 3, name: 'Reflection Report', point: 5 }] },
    { id: 10, name: 'Spring Festival Gala', date: '2025-04-18', venue: 'Main Auditorium', totalPoint: 30, signUpCount: 95, completedCount: 0, status: 'upcoming',
      subActivities: [{ id: 1, name: 'Check-in', point: 5 }, { id: 2, name: 'Watch Performance', point: 10 }, { id: 3, name: 'Participate in Games', point: 10 }, { id: 4, name: 'Post-event Survey', point: 5 }] },
    { id: 11, name: 'Earth Day Cleanup', date: '2025-04-22', venue: 'Campus Grounds', totalPoint: 15, signUpCount: 45, completedCount: 0, status: 'upcoming',
      subActivities: [{ id: 1, name: 'Check-in', point: 5 }, { id: 2, name: 'Cleanup Duty', point: 5 }, { id: 3, name: 'Photo Submission', point: 5 }] },
    { id: 12, name: 'Summer Farewell', date: '2025-06-20', venue: 'Lakeside Garden', totalPoint: 20, signUpCount: 0, completedCount: 0, status: 'upcoming',
      subActivities: [{ id: 1, name: 'Attendance', point: 5 }, { id: 2, name: 'Yearbook Signing', point: 5 }, { id: 3, name: 'Group Photo', point: 5 }, { id: 4, name: 'Farewell Speech', point: 5 }] }
  ])

  // Announcements
  const announcements = ref([
    { id: 1, title: 'Welcome to Leo the Billionaire!', content: 'Start your journey to become a billionaire by participating in activities and earning points! Complete activities to level up your virtual business from a small garage store to a world-class headquarters.', createdAt: '2024-09-01', status: 'published' },
    { id: 2, title: 'Mid-Autumn Festival Registration Open', content: 'Join us for lantern making and mooncake tasting at Student Plaza! Earn up to 20 points by participating in all activities. Register now through the mobile app.', createdAt: '2024-09-10', status: 'published' },
    { id: 3, title: 'Hackathon 2024 Announced', content: 'Form your teams and get ready for 24 hours of innovation at the Innovation Hub. This year\'s theme is "Sustainable Campus Solutions". Prize pool: 5000 RMB + bonus points!', createdAt: '2024-10-01', status: 'published' },
    { id: 4, title: 'Leaderboard Update', content: 'Check out the top performers this semester. Alex Wang leads with 92 points! Can you make it to the top 10? Keep participating and climb the ranks!', createdAt: '2024-11-15', status: 'published' },
    { id: 5, title: 'Spring Semester Activities', content: 'New activities for Spring 2025 are now available. Sign up early to secure your spot! Highlights include Spring Volunteer Day, Spring Festival Gala, and more.', createdAt: '2025-02-20', status: 'published' }
  ])

  // Settings
  const settings = ref({
    qrExpiry: 30,
    maxPoints: 100,
    siteName: 'Leo the Billionaire',
    maintenanceMode: false
  })

  // Check-in records for analytics
  const checkIns = ref(generateMockCheckIns())

  // Computed
  const totalUsers = computed(() => users.value.length)
  const totalActivities = computed(() => activities.value.length)
  const activeActivities = computed(() => activities.value.filter(a => a.status === 'active').length)
  const todayCheckIns = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return checkIns.value.filter(c => c.date === today).length
  })

  // Methods
  function nextId(collection) {
    const items = collection === 'users' ? users.value :
                  collection === 'activities' ? activities.value : announcements.value
    return Math.max(...items.map(i => i.id), 0) + 1
  }

  function addUser(user) {
    users.value.push({ ...user, id: nextId('users') })
  }

  function updateUser(id, data) {
    const index = users.value.findIndex(u => u.id === id)
    if (index > -1) {
      users.value[index] = { ...users.value[index], ...data }
    }
  }

  function deleteUser(id) {
    const index = users.value.findIndex(u => u.id === id)
    if (index > -1) users.value.splice(index, 1)
  }

  function addActivity(activity) {
    activities.value.push({ ...activity, id: nextId('activities'), signUpCount: 0, completedCount: 0 })
  }

  function updateActivity(id, data) {
    const index = activities.value.findIndex(a => a.id === id)
    if (index > -1) {
      activities.value[index] = { ...activities.value[index], ...data }
    }
  }

  function deleteActivity(id) {
    const index = activities.value.findIndex(a => a.id === id)
    if (index > -1) activities.value.splice(index, 1)
  }

  function addAnnouncement(announcement) {
    announcements.value.unshift({ ...announcement, id: nextId('announcements'), createdAt: new Date().toISOString().split('T')[0], status: 'published' })
  }

  function deleteAnnouncement(id) {
    const index = announcements.value.findIndex(a => a.id === id)
    if (index > -1) announcements.value.splice(index, 1)
  }

  function updateSettings(newSettings) {
    settings.value = { ...settings.value, ...newSettings }
  }

  return {
    users,
    activities,
    announcements,
    settings,
    checkIns,
    totalUsers,
    totalActivities,
    activeActivities,
    todayCheckIns,
    nextId,
    addUser,
    updateUser,
    deleteUser,
    addActivity,
    updateActivity,
    deleteActivity,
    addAnnouncement,
    deleteAnnouncement,
    updateSettings
  }
})

function generateMockCheckIns() {
  const records = []
  const today = new Date()

  for (let i = 0; i < 30; i++) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    const dateStr = date.toISOString().split('T')[0]

    // Random number of check-ins per day
    const count = Math.floor(Math.random() * 50) + 10
    for (let j = 0; j < count; j++) {
      records.push({
        id: records.length + 1,
        date: dateStr,
        userId: Math.floor(Math.random() * 8) + 1,
        activityId: Math.floor(Math.random() * 12) + 1
      })
    }
  }

  return records
}
