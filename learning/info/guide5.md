# 🎯 **Manual Commands to Run on Server2/Server3**

---

## 🚀 **SSH to Server First:**

```bash
# SSH to server2
ssh root@64.226.120.234

# Switch to mohamed user
su - mohamed

# Go to inception directory
cd /home/mohamed/inception/srcs
```

---

## 📦 **Step 1: Clean Everything First**

```bash
# Stop all containers
docker compose down -v

# Remove all volumes
docker volume prune -f

# Remove old images (optional)
docker image prune -a -f

# Verify nothing is running
docker ps -a
```

---

## 🗄️ **Step 2: Start MariaDB Only**

```bash
# Build MariaDB
docker compose build --no-cache mariadb

# Start MariaDB
docker compose up -d mariadb

# Check if it's running
docker ps

# Check logs
docker logs mariadb -f
# (Press Ctrl+C to exit logs)

# Verify it's healthy
docker exec mariadb mysql -uroot -p$MARIADB_ROOT_PASSWORD -e "SELECT 1;"
```

**Wait until you see:**
```
mariadb_1  | [Note] mysqld: ready for connections.
```

---

## 🌐 **Step 3: Start WordPress**

```bash
# Build WordPress (after MariaDB is running!)
docker compose build --no-cache wordpress

# Start WordPress
docker compose up -d wordpress

# Check if it's running
docker ps

# Check logs
docker logs wordpress -f
# (Press Ctrl+C to exit)

# Verify connection to MariaDB
docker exec wordpress php -r "echo 'PHP works!';"
```

**Wait until you see:**
```
SUCCESS: WordPress installed successfully.
```

---

## 🔒 **Step 4: Start Nginx**

```bash
# Build Nginx
docker compose build --no-cache nginx

# Start Nginx
docker compose up -d nginx

# Check all containers
docker ps

# Check Nginx logs
docker logs nginx -f

# Test SSL certificate
docker exec nginx ls -la /etc/nginx/ssl/
```

---

## ✅ **Step 5: Verify Everything Works**

```bash
# Check all containers are running
docker ps

# Expected output:
# nginx       Up X minutes   0.0.0.0:443->443/tcp
# wordpress   Up X minutes   9000/tcp
# mariadb     Up X minutes   3306/tcp

# Test the website
curl -k https://localhost

# Or from your local machine:
curl -k https://64.226.120.234
```

---

## 🔍 **Troubleshooting Commands:**

```bash
# Check volume mounts
docker volume ls
docker volume inspect srcs_mariadb_v
docker volume inspect srcs_wordpress_v

# Check networks
docker network ls
docker network inspect srcs_main_network

# Check container details
docker inspect mariadb
docker inspect wordpress
docker inspect nginx

# Restart a specific container
docker compose restart mariadb
docker compose restart wordpress
docker compose restart nginx

# See all logs at once
docker compose logs -f
```

---

## 🧹 **If Something Fails - Full Reset:**

```bash
# Complete cleanup
docker compose down -v
docker system prune -a -f --volumes
rm -rf /home/mohamed/data/*

# Recreate data directories
mkdir -p /home/mohamed/data/mariadb
mkdir -p /home/mohamed/data/wordpress

# Start fresh
docker compose build --no-cache
docker compose up -d

# Watch logs
docker compose logs -f
```

---

## 📋 **Quick One-Liner (All at Once):**

```bash
# If you want to start everything at once
cd /home/mohamed/inception/srcs && \
docker compose down -v && \
docker volume prune -f && \
docker compose build --no-cache && \
docker compose up -d && \
docker compose logs -f
```

---

## 🎯 **Expected Final State:**

```bash
$ docker ps
CONTAINER ID   IMAGE            COMMAND                  STATUS          PORTS
xxxxxxxxxx     srcs-nginx       "nginx -g 'daemon..."    Up X minutes    0.0.0.0:443->443/tcp
xxxxxxxxxx     srcs-wordpress   "./script.sh"            Up X minutes    9000/tcp
xxxxxxxxxx     srcs-mariadb     "./script.sh"            Up X minutes    3306/tcp
```

---

## 🌐 **Test From Your Local Machine:**

```bash
# Test server2
curl -k https://64.226.120.234

# Test server3  
curl -k https://134.122.94.26

# Or open in browser
https://64.226.120.234
https://134.122.94.26
```

---

**Start with MariaDB first, wait for it to be ready, then WordPress, then Nginx!** 🚀

Let me know which step fails and I'll help debug! 💪