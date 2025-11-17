**Perfect! Let's break down the MariaDB initialization script!** 📖

---

## 📄 **MariaDB Script Explained:**

---

### **Line 1: Shebang**
```bash
#!/bin/bash
```

**What it does:** Tells the system to run this script with Bash shell

**Why we need it:**
- `#!` = Shebang (special directive)
- bash = Path to Bash interpreter
- Without this, the system doesn't know how to execute the script

**In simple terms:** "Use Bash to run this script"

---

## 🔵 **SECTION 1: Start MariaDB Temporarily**

### **Line 5-6: Start MariaDB Service**
```bash
service mariadb start
```

**What it does:** Starts MariaDB in the background (temporary startup)

**Why we need it:**
- MariaDB must be **running** before we can configure it
- This is a **temporary start** (we'll stop it later)
- We need it running to create databases and users

**In simple terms:** "Turn on the database so we can set it up"

---

### **Line 10: Wait for Database**
```bash
sleep 5
```

**What it does:** Wait 5 seconds

**Why we need it:**
- MariaDB takes a few seconds to **fully start**
- If we try to run commands too quickly, they'll fail
- Gives MariaDB time to initialize

**Better alternative (but this works):**
```bash
while ! mysqladmin ping -h localhost --silent; do
    sleep 1
done
```

**In simple terms:** "Wait for the database to be fully ready"

---

## 🔵 **SECTION 2: Configuration**

### **Line 15: Set Root Password**
```bash
mysqladmin -u root password $MARIADB_ROOT_PASSWORD
```

**What it does:** Set password for root (admin) user

**Breaking it down:**
- `mysqladmin` → MariaDB admin tool
- `-u root` → Run as user "root"
- `password` → Set password command
- `$MARIADB_ROOT_PASSWORD` → Variable from `.env` file (e.g., "MySecurePass123")

**Why we need it:**
- Root user starts with **no password** (insecure!)
- Sets a **strong admin password**
- Prevents unauthorized access

**In simple terms:** "Set admin password for database security"

---

### **Line 17: Create WordPress Database**
```bash
mysql -u root -p$MARIADB_ROOT_PASSWORD -e "CREATE DATABASE IF NOT EXISTS $MARIADB_DATABASE ;"
```

**What it does:** Create the database for WordPress

**Breaking it down:**
- `mysql` → MariaDB client
- `-u root` → Login as root
- `-p$MARIADB_ROOT_PASSWORD` → Use root password (no space after `-p`!)
- `-e` → Execute SQL command
- `CREATE DATABASE IF NOT EXISTS` → Create database if it doesn't exist
- `$MARIADB_DATABASE` → From `.env` (e.g., "wordpress_db")

**Why we need it:**
- WordPress needs a **dedicated database** to store content
- `IF NOT EXISTS` prevents errors if database already exists

**In simple terms:** "Create a storage space for WordPress data"

---

### **Line 18: Create WordPress User**
```bash
mysql -u root -p$MARIADB_ROOT_PASSWORD -e "CREATE USER IF NOT EXISTS '$MARIADB_USER'@'%' IDENTIFIED BY '$MARIADB_PASSWORD' ;"
```

**What it does:** Create a user for WordPress to access the database

**Breaking it down:**
- `CREATE USER IF NOT EXISTS` → Create user if doesn't exist
- `'$MARIADB_USER'` → Username from `.env` (e.g., "wp_user")
- `@'%'` → **IMPORTANT!** Allow connections from **any host** (not just localhost)
  - `%` = wildcard = any IP address
  - Needed because WordPress is in a **different container**!
- `IDENTIFIED BY '$MARIADB_PASSWORD'` → Set user's password

**Why we need it:**
- WordPress shouldn't use **root account** (security!)
- Creates a **limited-privilege user** just for WordPress
- `@'%'` allows **Docker network** connections

**In simple terms:** "Create a username/password for WordPress to login to the database"

---

### **Line 19: Grant Permissions**
```bash
mysql -u root -p$MARIADB_ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON $MARIADB_DATABASE.* TO '$MARIADB_USER'@'%' ;"
```

**What it does:** Give WordPress user full access to WordPress database

**Breaking it down:**
- `GRANT ALL PRIVILEGES` → Give all permissions (read, write, delete, etc.)
- `ON $MARIADB_DATABASE.*` → Only on this database (and all tables `.*`)
- `TO '$MARIADB_USER'@'%'` → To this specific user from any host

**Why we need it:**
- Creating a user doesn't automatically give permissions!
- WordPress needs to **create tables, insert data, update posts, etc.**
- Limits access to **only the WordPress database** (not other databases)

**In simple terms:** "Allow WordPress user to fully manage the WordPress database"

---

### **Line 20: Apply Changes**
```bash
mysql -u root -p$MARIADB_ROOT_PASSWORD -e "FLUSH PRIVILEGES;"
```

**What it does:** Reload permission tables

**Why we need it:**
- Changes to users/permissions are **cached in memory**
- `FLUSH PRIVILEGES` forces MariaDB to **reload** the permission tables
- Ensures changes take effect **immediately**

**In simple terms:** "Save and apply all the changes we just made"

---

## 🔵 **SECTION 3: Start MariaDB in Foreground**

### **Line 24: Stop Temporary Service**
```bash
service mariadb stop
```

**What it does:** Stop the temporary MariaDB we started earlier

**Why we need it:**
- We started MariaDB with `service mariadb start` (runs in background)
- Now we need to start it in **foreground mode** (so Docker container stays alive)
- Must stop background process first (can't have two instances!)

**In simple terms:** "Turn off the temporary database process"

---

### **Line 27-28: Start MariaDB in Foreground**
```bash
mysqld_safe --port=3306 --bind-address=0.0.0.0
```

**What it does:** Start MariaDB server in foreground mode

**Breaking it down:**
- `mysqld_safe` → MariaDB daemon wrapper (safer than plain `mysqld`)
  - Automatically restarts if crashes
  - Logs errors
- `--port=3306` → Listen on port 3306 (standard MySQL/MariaDB port)
- `--bind-address=0.0.0.0` → **CRITICAL!** Accept connections from **any IP**
  - `0.0.0.0` = Listen on all network interfaces
  - Allows WordPress container to connect
  - Default is `127.0.0.1` (localhost only) → would block Docker connections!

**Why we need it:**
- **Keeps container running** (foreground process)
- Allows **Docker network** connections from WordPress
- If this stops, container stops!

**In simple terms:** "Start the database server and keep it running forever, accepting connections from WordPress"

---

## 🎯 **Complete Flow:**

```
1. Start MariaDB temporarily (background)
      ↓
2. Wait 5 seconds for it to initialize
      ↓
3. Set root password (security)
      ↓
4. Create WordPress database
      ↓
5. Create WordPress user
      ↓
6. Grant WordPress user full access to WordPress database
      ↓
7. Apply all changes (flush privileges)
      ↓
8. Stop temporary MariaDB
      ↓
9. Start MariaDB in foreground (keeps container alive)
      ↓
10. Accept connections from any IP (WordPress can connect!)
```

---

## 📊 **Key Variables from .env:**

| Variable | Example | Purpose |
|----------|---------|---------|
| `$MARIADB_ROOT_PASSWORD` | `SuperSecret123!` | Admin password |
| `$MARIADB_DATABASE` | `wordpress_db` | Database name |
| `$MARIADB_USER` | `wp_user` | WordPress username |
| `$MARIADB_PASSWORD` | `WpPass456!` | WordPress password |

---

## 🔐 **Security Notes:**

1. ✅ **Root password** set (protects admin account)
2. ✅ **Separate user** for WordPress (least privilege)
3. ✅ **`@'%'` allows Docker network** connections (needed for containers)
4. ⚠️ **In production**, you'd use:
   - `@'wordpress_container_ip'` instead of `@'%'`
   - But Docker networks make `%` acceptable

---

## 🎓 **Why `0.0.0.0` and `@'%'`?**

**Docker Networking:**
```
WordPress Container (IP: 172.18.0.3)
         ↓
    Docker Network
         ↓
MariaDB Container (IP: 172.18.0.2)
```

- **Without `0.0.0.0`** → MariaDB only listens on `127.0.0.1` (localhost) → WordPress can't connect!
- **Without `@'%'`** → User only allowed from localhost → WordPress denied!

**With both** → WordPress can connect from its container IP! ✅

---

**Ready for the next file?** Show me WordPress Dockerfile next! 🚀