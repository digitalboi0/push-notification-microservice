// sw.js - Simple Service Worker for Web Push Test

self.addEventListener('push', function(event) {
    console.log('Push received:', event);

    // Example notification data
    const payload = event.data ? event.data.json() : { title: 'Default Title', body: 'Default Body' };

    const options = {
        body: payload.body || 'Default body',
        icon: payload.icon || '/icon.png', // Optional: Use icon from payload or default
        badge: payload.badge || '/badge.png', // Optional: Use badge from payload or default
        // Use 'data' to pass custom information to the notification click handler
        data: {
            url: payload.url || '/' // Store the URL in the notification's data
        }
    };

    event.waitUntil(
        self.registration.showNotification(payload.title || 'Default Title', options)
    );
});

self.addEventListener('notificationclick', function(event) {
    console.log('Notification clicked:', event);
    // Close the notification
    event.notification.close();

    // Optional: Open a URL when clicked, using the URL stored in the notification's data
    const urlToOpen = event.notification.data?.url || '/'; // Fallback to root if no URL in data

    event.waitUntil(
        clients.openWindow(urlToOpen)
    );
});