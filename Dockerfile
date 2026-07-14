FROM nginx:alpine

# Copy static demo to nginx html root
COPY src/webapp/static /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
