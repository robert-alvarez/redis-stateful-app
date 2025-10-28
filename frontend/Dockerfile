# Frontend Dockerfile for Redis Memory Magic Chat UI
FROM nginx:alpine

# Copy static files to nginx html directory
COPY index.html /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# nginx runs in foreground by default
CMD ["nginx", "-g", "daemon off;"]
