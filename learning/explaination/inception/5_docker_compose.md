**AH! I see the problem! The WordPress volume is persisting old data!** 🎯

Let me explain docker-compose.yml first, then we'll fix the theme issue!

---

# 📄 **Docker Compose File Explained:**

---

## 🔵 **SECTION 1: Networks**

```yaml
networks:
  main_network:
```

**What it does:** Create a private network for containers to communicate

**Why we need it:**
- ✅ Containers can talk to each other by **name** (e.g., `wordpress:9000`, `mariadb:3306`)
- ✅ **Isolated** from other Docker networks (security)
- ✅ **DNS resolution** built-in (Docker provides DNS server)

**How it works:**
```
NGINX container (172.18.0.4)
      ↓ main_network
WordPress container (172.18.0.3)
      ↓ main_network
MariaDB container (172.18.0.2)
```

**In simple terms:** "Create a private network so containers can find each other"

---

## 🔵 **SECTION 2: Volumes**

### **MariaDB Volume:**
```yaml
mariadb_v:
  driver: local
  driver_opts:
    type: none
    device: /home/mohamed/data/mariadb
    o: bind
```

**What it does:** Persist MariaDB database data on host machine

**Breaking it down:**

| Line | Purpose |
|------|---------|
| `driver: local` | Use local filesystem (not NFS/cloud storage) |
| `type: none` | No special filesystem type (just directories) |
| `device: /home/mohamed/data/mariadb` | **HOST PATH** - where data is stored |
| `o: bind` | **Bind mount** - connect host directory to container |

**Why we need it:**
- ✅ **Data persists** when container restarts
- ✅ **Survives container deletion** (data on host, not in container)
- ✅ **Can backup easily** (just copy `/home/mohamed/data/mariadb`)

**Container sees:** `/var/lib/mysql` (inside container)  
**Actually stored:** `/home/mohamed/data/mariadb` (on host) ✅

---

### **WordPress Volume:**
```yaml
wordpress_v:
  driver: local
  driver_opts:
    type: none
    device: /home/mohamed/data/wordpress
    o: bind
```

**What it does:** Persist WordPress files on host

**⚠️ THIS IS YOUR PROBLEM!** 

**Why theme doesn't change:**
```
1st deployment: WordPress installs with Theme A → saved to /home/mohamed/data/wordpress
      ↓
You change script to Theme B
      ↓
2nd deployment: WordPress script runs BUT old files still in volume! ❌
      ↓
Theme A remains because volume has old data!
```

**Container sees:** `/var/www/html` (inside container)  
**Actually stored:** `/home/mohamed/data/wordpress` (on host) ✅

---

## 🔵 **SECTION 3: MariaDB Service**

```yaml
mariadb:
  build: requirements/mariadb/
  container_name: mariadb
  env_file: .env
  networks:
    - main_network
  volumes:
    - mariadb_v:/var/lib/mysql
  restart: on-failure
```

**Breaking it down:**

| Line | Purpose |
|------|---------|
| `build: requirements/mariadb/` | Build from Dockerfile in this directory |
| `container_name: mariadb` | Name container "mariadb" (used for DNS) |
| `env_file: .env` | Load variables from `.env` file |
| `networks: - main_network` | Connect to our private network |
| `volumes: - mariadb_v:/var/lib/mysql` | Mount volume to database directory |
| `restart: on-failure` | Auto-restart if crashes |

**No ports exposed!** Why?
- MariaDB only needs to be accessed by WordPress (same network)
- **More secure** - not exposed to internet
- WordPress connects via `mariadb:3306` (internal network)

---

## 🔵 **SECTION 4: WordPress Service**

```yaml
wordpress:
  build: requirements/wordpress/
  container_name: wordpress
  env_file: .env
  depends_on:
    - mariadb
  networks:
    - main_network
  volumes:
    - wordpress_v:/var/www/html
  restart: on-failure
```

**Breaking it down:**

| Line | Purpose |
|------|---------|
| `depends_on: - mariadb` | **Wait for MariaDB** to start first |
| `volumes: - wordpress_v:/var/www/html` | **THIS IS THE PROBLEM!** Persists WordPress files |

**Why `depends_on`?**
```
Wrong order:
WordPress starts → tries to connect to MariaDB → MariaDB not ready → ERROR ❌

Correct order (with depends_on):
MariaDB starts → WordPress waits → MariaDB ready → WordPress connects ✅
```

**No ports exposed!** Why?
- WordPress (PHP-FPM) only accessed by NGINX (same network)
- NGINX connects via `wordpress:9000`

---

## 🔵 **SECTION 5: NGINX Service**

```yaml
nginx:
  build: requirements/nginx/
  container_name: nginx
  ports:
    - "443:443"
    - "8443:8443"
  depends_on:
    - wordpress
  networks:
    - main_network
  volumes:
    - wordpress_v:/var/www/html
    - /etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem:/etc/nginx/ssl_cer.crt:ro
    - /etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem:/etc/nginx/ssl_cer_key.key:ro
  restart: on-failure
```

**Breaking it down:**

### **Ports:**
```yaml
ports:
  - "443:443"    # HTTPS
  - "8443:8443"  # Alternative HTTPS (if needed)
```

**Port mapping:** `HOST:CONTAINER`
- `443:443` → Host port 443 → Container port 443
- **Only NGINX** exposed to internet! ✅

### **Volumes:**
```yaml
volumes:
  - wordpress_v:/var/www/html  # WordPress files
  - /etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem:/etc/nginx/ssl_cer.crt:ro
  - /etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem:/etc/nginx/ssl_cer_key.key:ro
```

**Breaking it down:**

| Mount | Purpose |
|-------|---------|
| `wordpress_v:/var/www/html` | **Share WordPress files** with WordPress container |
| `fullchain.pem → ssl_cer.crt` | **SSL certificate** (read-only `:ro`) |
| `privkey.pem → ssl_cer_key.key` | **Private key** (read-only `:ro`) |

**Why NGINX needs WordPress files?**
- To serve static files (images, CSS, JS) directly
- PHP files forwarded to WordPress container

**`:ro` flag:** Read-only (security - can't modify certificates)

---

## 🎯 **Complete Architecture:**

```
┌────────────────────────────────────────────┐
│            Host Machine                    │
│  /home/mohamed/data/mariadb    ← Volume   │
│  /home/mohamed/data/wordpress  ← Volume   │
│  /etc/letsencrypt/...          ← Certs    │
└───────────────┬────────────────────────────┘
                │ Bind mounts
                ↓
┌────────────────────────────────────────────┐
│         Docker (main_network)              │
│                                            │
│  ┌─────────────┐  ┌─────────────┐        │
│  │   MariaDB   │  │  WordPress  │        │
│  │   :3306     │←─│   :9000     │        │
│  └─────────────┘  └──────┬──────┘        │
│                           │                │
│                    ┌──────┴──────┐        │
│                    │    NGINX    │        │
│                    │    :443     │        │
│                    └─────────────┘        │
└───────────────────────┬────────────────────┘
                        │ Port 443
                        ↓
                   Internet (Users)
```

---

## ⚠️ **YOUR THEME PROBLEM - THE FIX:**

### **Problem:**
```yaml
volumes:
  - wordpress_v:/var/www/html  # ← Old WordPress files persist here!
```

**WordPress files are SAVED in the volume, so:**
1. First run: Installs SaasLauncher → Saved to `/home/mohamed/data/wordpress`
2. You change script to Airi
3. Second run: Script tries to install Airi BUT old files still there!
4. WordPress sees existing installation → **Skips reinstallation!** ❌

---

### **Solution 1: Clear WordPress Volume (Clean Slate)**

```bash
# Stop containers
ansible webservers -i inventory.ini -m shell -a "cd /home/mohamed/inception/srcs && docker compose down" --become-user mohamed

# Delete WordPress files (keeps database!)
ansible webservers -i inventory.ini -a "rm -rf /home/mohamed/data/wordpress/*" --become

# Redeploy
ansible-playbook -i inventory.ini deploy.yml
```

✅ **Fresh WordPress install with new theme!**

---

### **Solution 2: Change Theme Directly (Keep Data)**

```bash
# Just change the theme without full reinstall
ansible webservers -i inventory.ini -m shell -a "docker exec wordpress wp theme install airi --activate --allow-root --path=/var/www/html" --become
```

✅ **Quick theme change, keeps all data!**

---

### **Solution 3: Make Script Smarter (Best for Demo)**

Update your WordPress script:

````bash
# Check if WordPress is already installed
if ! wp core is-installed --allow-root --path=/var/www/html 2>/dev/null; then
    # Fresh install
    wp core download --allow-root
    wp config create --allow-root --dbname=$MARIADB_DATABASE --dbuser=$WP_ADMIN_LOGIN --dbpass=$WP_ADMIN_PASSWORD --dbhost=$DB_HOST
    wp core install --allow-root --url=$WP_URL --title=$WP_TITLE --admin_user=$WP_ADMIN_LOGIN --admin_password=$WP_ADMIN_PASSWORD --admin_email=$WP_ADMIN_EMAIL
else
    echo "WordPress already installed, skipping installation..."
fi

# ALWAYS install/activate theme (even if WordPress exists)
wp theme install saaslauncher --activate --allow-root --path=/var/www/html

wp user create --allow-root $WP_USER_LOGIN $WP_USER_EMAIL --user_pass=$WP_USER_PASSWORD --role=$WP_USER_ROLE 2>/dev/null || true
````

✅ **Theme changes every deployment, keeps WordPress data!**

---

## 📊 **Why Volumes Cause This:**

| Without Volume | With Volume (Your Setup) |
|----------------|--------------------------|
| WordPress files in container | WordPress files on host |
| **Deleted when container stops** | **Persist after container stops** ✅ |
| Fresh install every time | **Same files every time** |
| Theme changes work | **Theme changes DON'T work** ❌ |

---

## 🎯 **For Your Corrector Demo:**

**Option A (Full Reset):**
```bash
# Show current theme
curl https://livroai.com | grep -i "wp-content/themes"

# Clear data and redeploy with new theme
ansible webservers -i inventory.ini -a "rm -rf /home/mohamed/data/wordpress/*" --become
ansible-playbook -i inventory.ini deploy.yml

# Show new theme
curl https://livroai.com | grep -i "wp-content/themes"
```

**Option B (Quick Switch):**
```bash
# Change theme via WP-CLI
ansible webservers -i inventory.ini -m shell -a "docker exec wordpress wp theme install airi --activate --allow-root --path=/var/www/html" --become
```

---

**Which fix do you prefer? I recommend Solution 1 (clear volume) for demo!** 🚀