**Let's go through the WordPress Dockerfile line by line!** 📖

---

## 📄 **WordPress Dockerfile Explained:**

---

### **Line 1: Base Image**
```dockerfile
FROM debian:11
```

**What it does:** Start from Debian 11 (Bullseye)

**Why we need it:**
- Same base OS as MariaDB container (consistency)
- Stable and well-supported
- Has all packages WordPress needs

**In simple terms:** "Build this container using Debian 11 as the foundation"

---

### **Line 4: Install All Required Packages**
```dockerfile
RUN apt -y update && apt -y upgrade && apt -y install mariadb-client php php-mysql php-fpm wget
```

**What it does:** Update system and install 5 packages in one command

**Breaking it down:**

| Part | Purpose |
|------|---------|
| `apt update` | Refresh package lists (get latest versions) |
| `apt upgrade` | Install security updates |
| `&&` | Only continue if previous command succeeded |
| `apt install` | Install the following packages: |

**Packages installed:**

| Package | What It Does | Why WordPress Needs It |
|---------|--------------|------------------------|
| **`mariadb-client`** | MySQL/MariaDB command-line tools (`mysql`, `mysqldump`) | Connect to database, run SQL queries |
| **`php`** | PHP interpreter (version 7.4 in Debian 11) | WordPress is written in PHP |
| **`php-mysql`** | PHP extension for MySQL/MariaDB | Allows PHP code to talk to database |
| **`php-fpm`** | FastCGI Process Manager for PHP | Processes PHP files for NGINX efficiently |
| **`wget`** | Download files from internet | Download WP-CLI tool |

**Why all in one RUN command?**
- ✅ Creates fewer Docker layers (smaller image)
- ✅ Faster builds
- ✅ Better cache utilization

**In simple terms:** "Install PHP, database connector, and download tool"

---

## 🔵 **SECTION: Install WP-CLI**

### **Line 9: Download WP-CLI**
```dockerfile
RUN wget https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
```

**What it does:** Download WordPress Command Line Interface tool

**What is WP-CLI?**
- Official WordPress automation tool
- Allows **command-line WordPress management**
- Can install WordPress, themes, plugins without web interface

**Why we need it:**
- ✅ **Automate WordPress installation** (no manual web setup)
- ✅ **Perfect for Docker** (scriptable, no GUI needed)
- ✅ **Professional approach** (infrastructure as code)

**Alternative without WP-CLI:**
```bash
# Manual way (bad for automation):
wget wordpress.org/latest.tar.gz
tar -xzf latest.tar.gz
# Then configure manually... 😫
```

**With WP-CLI:**
```bash
wp core download  # One command! 😎
```

**In simple terms:** "Download a tool that automates WordPress installation"

---

### **Line 10: Move WP-CLI to System Path**
```dockerfile
RUN mv wp-cli.phar /usr/local/bin/wp
```

**What it does:** Move and rename the file to make it globally accessible

**Breaking it down:**
- `mv` = Move/rename file
- `wp-cli.phar` = Downloaded PHP Archive file
- bin = Standard location for custom executables
- `wp` = New name (short and easy)

**Before:** `php wp-cli.phar core download` (awkward)  
**After:** `wp core download` (clean!) ✅

**Why bin?**
- It's in the system's `PATH` (can run from anywhere)
- Standard location for custom tools (not package manager tools)
- Won't conflict with system packages

**In simple terms:** "Install WP-CLI so we can type 'wp' from anywhere"

---

### **Line 11: Make WP-CLI Executable**
```dockerfile
RUN chmod +x /usr/local/bin/wp
```

**What it does:** Grant execute permission

**Why we need it:**
- Downloaded files don't have execute permission by default (security)
- `chmod +x` = Make file executable
- Without this: `bash: /usr/local/bin/wp: Permission denied`

**File permissions:**
```bash
# Before: -rw-r--r-- (read/write only)
# After:  -rwxr-xr-x (executable)
```

**In simple terms:** "Allow WP-CLI to be run as a program"

---

## 🔵 **SECTION: Configure PHP-FPM**

### **Line 16: Configure PHP-FPM Network Listening**
```dockerfile
RUN echo "listen=0.0.0.0:9000" >> /etc/php/7.4/fpm/pool.d/www.conf
```

**What it does:** Add a configuration line to PHP-FPM config file

**Breaking it down:**
- `echo "..."` = Output text
- `>>` = Append to file (don't overwrite!)
- `/etc/php/7.4/fpm/pool.d/www.conf` = PHP-FPM worker pool config
- `listen=0.0.0.0:9000` = The critical part! ⭐

**What `listen=0.0.0.0:9000` means:**

| Part | Meaning | Why Important |
|------|---------|---------------|
| `listen=` | Where PHP-FPM listens for requests | Defines how NGINX connects |
| `0.0.0.0` | All network interfaces (any IP) | **CRITICAL for Docker!** |
| `9000` | Port number | Standard PHP-FPM port |

**Default behavior (without this line):**
```bash
# Default: listen = /run/php/php7.4-fpm.sock
# This is a UNIX socket (localhost only)
# NGINX container CAN'T connect! ❌
```

**With `0.0.0.0:9000`:**
```bash
# PHP-FPM listens on network (TCP)
# NGINX container CAN connect via Docker network! ✅
```

---

### **🔗 Docker Network Communication:**

```
┌─────────────────────┐
│  NGINX Container    │
│  IP: 172.18.0.4     │
└──────────┬──────────┘
           │ Sends .php file requests
           ↓
      Docker Network
           ↓
┌──────────┴──────────┐
│ WordPress Container │
│ IP: 172.18.0.3      │
│ PHP-FPM: 0.0.0.0:9000│ ← Listens on ALL interfaces
└─────────────────────┘
```

**Without `0.0.0.0`:**
- PHP-FPM: "I only accept connections from 127.0.0.1 (myself)"
- NGINX: "I'm at 172.18.0.4, can I connect?"
- PHP-FPM: "Nope! ❌"

**With `0.0.0.0`:**
- PHP-FPM: "I accept connections from any IP!"
- NGINX: "I'm at 172.18.0.4, can I connect?"
- PHP-FPM: "Sure! ✅"

**In simple terms:** "Let NGINX connect to PHP from its container"

---

### **Line 18: Document Port Usage**
```dockerfile
EXPOSE 9000
```

**What it does:** Declare that this container uses port 9000

**Why we need it:**
- **Documentation** for developers/operators
- Shows port 9000 is important for this container
- Used by Docker networking

**⚠️ Important:** `EXPOSE` does NOT actually open the port!
- It's **documentation only**
- The port is opened by Docker Compose networking
- Helps `docker ps` show which ports are used

**In simple terms:** "Tell Docker this container needs port 9000 for PHP"

---

### **Line 20: Copy Initialization Script**
```dockerfile
COPY tools/script.sh /
```

**What it does:** Copy startup script from host into container root

**Why we need it:**
- WordPress needs custom initialization:
  - Download WordPress files
  - Configure database connection
  - Install WordPress
  - Create admin user
  - Start PHP-FPM
- Can't do all this in Dockerfile (need dynamic values from `.env`)

**In simple terms:** "Copy our WordPress setup script into the container"

---

### **Line 22: Make Script Executable**
```dockerfile
RUN chmod +x /script.sh
```

**What it does:** Grant execute permission to the script

**Why we need it:**
- `COPY` doesn't preserve execute permissions
- Without this: Container won't start (script can't run)

**In simple terms:** "Allow the script to be executed"

---

### **Line 24: Define Container Startup**
```dockerfile
ENTRYPOINT ["./script.sh"]
```

**What it does:** Run `script.sh` when container starts

**Why ENTRYPOINT (not CMD)?**
- `ENTRYPOINT` = **Cannot be overridden** easily (enforced)
- `CMD` = Can be overridden (default that can change)
- We **always** want this script to run (no exceptions!)

**What the script does (we'll cover next):**
1. Wait for MariaDB to be ready
2. Start PHP-FPM temporarily
3. Download WordPress with WP-CLI
4. Configure database connection
5. Install WordPress
6. Create users
7. Install theme
8. Stop temporary PHP-FPM
9. Start PHP-FPM in foreground (keeps container alive)

**In simple terms:** "Run our setup script when container starts"

---

## 🎯 **Complete Build Flow:**

```
1. FROM debian:11
      ↓
2. Install PHP, MariaDB client, wget
      ↓
3. Download WP-CLI tool
      ↓
4. Install WP-CLI globally (/usr/local/bin/wp)
      ↓
5. Make WP-CLI executable
      ↓
6. Configure PHP-FPM to listen on 0.0.0.0:9000
      ↓
7. Document port 9000
      ↓
8. Copy startup script
      ↓
9. Make script executable
      ↓
10. Set script as startup command
```

---

## 🔄 **What Happens When Container Runs:**

```
Docker starts container
      ↓
Runs ENTRYPOINT: ./script.sh
      ↓
Script downloads WordPress
      ↓
Script configures wp-config.php
      ↓
Script installs WordPress
      ↓
Script starts PHP-FPM on 0.0.0.0:9000
      ↓
Container stays running (PHP-FPM foreground)
      ↓
NGINX can now connect and serve WordPress! ✅
```

---

## 📊 **Package Dependencies:**

```
WordPress (PHP code)
      ↓ needs
PHP interpreter (php)
      ↓ needs
PHP-MySQL extension (php-mysql)
      ↓ connects to
MariaDB database (mariadb-client tools)
      ↓ served by
PHP-FPM (php-fpm)
      ↓ receives requests from
NGINX (via port 9000)
```

---

## 🎓 **Key Takeaways:**

1. **WP-CLI** = Automates WordPress installation (no manual setup)
2. **PHP-FPM** = Processes PHP files for NGINX
3. **`0.0.0.0:9000`** = Critical for Docker networking (NGINX connection)
4. **Port 9000** = Standard PHP-FPM port
5. **mariadb-client** = Lets WordPress connect to database
6. **ENTRYPOINT** = Enforces startup script execution

---

**Ready for the WordPress script next?** That's where the magic happens! 🚀



**Perfect! Let's break down the WordPress Dockerfile!** 📖

---

## 📄 **WordPress Dockerfile Explained:**

---

### **Line 1: Base Image**
```dockerfile
FROM debian:11
```

**What it does:** Start from Debian 11 (same as MariaDB)

**Why we need it:**
- Consistent base OS across containers
- Stable and secure
- Good package support for PHP

**In simple terms:** "Build this container using Debian 11"

---

### **Line 4: Install Required Packages**
```dockerfile
RUN apt -y update && apt -y upgrade && apt -y install mariadb-client php php-mysql php-fpm wget
```

**What it does:** Update system and install multiple packages

**Breaking it down:**
- `apt update` → Update package lists
- `apt upgrade` → Install security updates
- `apt install` → Install these packages:

| Package | Purpose |
|---------|---------|
| **`mariadb-client`** | Connect to MariaDB (not server, just client tools like `mysql` command) |
| **`php`** | PHP programming language (WordPress is written in PHP) |
| **`php-mysql`** | PHP extension to talk to MariaDB database |
| **`php-fpm`** | FastCGI Process Manager - runs PHP scripts efficiently |
| **`wget`** | Download files from internet (to get WP-CLI) |

**Why we need each:**
- ✅ **mariadb-client** → WordPress needs to query the database
- ✅ **php** → Run WordPress code
- ✅ **php-mysql** → Bridge between PHP and MariaDB
- ✅ **php-fpm** → Serve PHP to NGINX (NGINX → php-fpm → WordPress)
- ✅ **wget** → Download WordPress installation tool

**In simple terms:** "Install PHP and tools needed to run WordPress"

---

## 🔵 **SECTION: Install WP-CLI**

### **Line 9: Download WP-CLI**
```dockerfile
RUN wget https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
```

**What it does:** Download WP-CLI (WordPress Command Line Interface)

**What is WP-CLI?**
- Official WordPress command-line tool
- Allows **automated WordPress installation** (no manual setup!)
- Can create sites, install themes, manage plugins, etc.

**Why we need it:**
- ✅ **Automate WordPress installation** (no clicking through web installer)
- ✅ **Script-friendly** (perfect for Docker containers)
- ✅ **Download and configure WordPress** automatically

**In simple terms:** "Download a tool to install WordPress automatically"

---

### **Line 10: Move WP-CLI to System Path**
```dockerfile
RUN mv wp-cli.phar /usr/local/bin/wp
```

**What it does:** Move and rename the file

**Breaking it down:**
- `mv` → Move/rename file
- `wp-cli.phar` → Downloaded file (PHP Archive)
- `/usr/local/bin/wp` → System-wide executable location
- Now you can just type `wp` instead of `php wp-cli.phar`

**Why we need it:**
- Makes WP-CLI globally accessible
- Can run `wp` from anywhere
- Standard location for custom executables

**In simple terms:** "Install WP-CLI so we can use it easily"

---

### **Line 11: Make WP-CLI Executable**
```dockerfile
RUN chmod +x /usr/local/bin/wp
```

**What it does:** Give execute permission to WP-CLI

**Why we need it:**
- Without this, you'd need to run `php /usr/local/bin/wp`
- With this, you can just run `wp`
- Makes it act like a normal command

**In simple terms:** "Allow WP-CLI to be run as a command"

---

## 🔵 **SECTION: Configure PHP-FPM**

### **Line 16: Configure PHP-FPM Listening Address**
```dockerfile
RUN echo "listen=0.0.0.0:9000" >> /etc/php/7.4/fpm/pool.d/www.conf
```

**What it does:** Configure PHP-FPM to listen on port 9000 from any IP

**Breaking it down:**
- `echo "..."` → Output text
- `>>` → Append to file (doesn't overwrite)
- `/etc/php/7.4/fpm/pool.d/www.conf` → PHP-FPM configuration file
- `listen=0.0.0.0:9000` → **CRITICAL!** Listen settings:
  - `0.0.0.0` → Accept connections from **any IP** (needed for Docker!)
  - `9000` → Port number (standard PHP-FPM port)

**Why we need it:**
- **Default:** PHP-FPM listens on `127.0.0.1:9000` (localhost only)
- **Problem:** NGINX container can't connect from localhost!
- **Solution:** `0.0.0.0` allows NGINX container to connect via Docker network

**In simple terms:** "Let NGINX connect to PHP from its container"

---

### **Docker Network Flow:**
```
NGINX Container (172.18.0.4)
       ↓
   Port 9000
       ↓
WordPress Container (172.18.0.3)
       ↓
   PHP-FPM listens on 0.0.0.0:9000
       ↓
   Processes PHP code
       ↓
   Returns HTML to NGINX
```

**Without `0.0.0.0`:** ❌ NGINX can't reach PHP-FPM!  
**With `0.0.0.0`:** ✅ NGINX can connect and get PHP responses!

---

### **Line 18: Expose Port**
```dockerfile
EXPOSE 9000
```

**What it does:** Document that this container uses port 9000

**Why we need it:**
- Port **9000** is the **standard PHP-FPM port**
- NGINX will connect to this port to process PHP files
- **NOTE:** This is documentation only (actual port opened by Docker)

**Communication Flow:**
```
Browser → NGINX (443) → PHP-FPM (9000) → WordPress → MariaDB (3306)
```

**In simple terms:** "Tell Docker this container needs port 9000 for PHP processing"

---

### **Line 20: Copy Startup Script**
```dockerfile
COPY tools/script.sh /
```

**What it does:** Copy initialization script into container

**Why we need it:**
- WordPress needs **custom setup** (download WordPress, configure database, create admin user)
- This script will:
  - Download WordPress files with WP-CLI
  - Configure database connection
  - Install WordPress
  - Start PHP-FPM

**In simple terms:** "Copy our WordPress setup script into the container"

---

### **Line 22: Make Script Executable**
```dockerfile
RUN chmod +x /script.sh
```

**What it does:** Give execute permission to the script

**Why we need it:**
- Copied files aren't executable by default
- Without this, the script can't run!

**In simple terms:** "Allow the script to be run"

---

### **Line 24: Set Container Startup Command**
```dockerfile
ENTRYPOINT ["./script.sh"]
```

**What it does:** Run the script when container starts

**Why we need it:**
- This script will:
  1. Download WordPress
  2. Configure WordPress
  3. Start PHP-FPM (keeps container alive)
- Without this, container would start and immediately exit!

**In simple terms:** "Run our setup script when container starts"

---

## 🎯 **Complete Flow:**

```
1. FROM debian:11              → Start with Debian
2. RUN apt install             → Install PHP, MariaDB client, WP-CLI downloader
3. RUN wget wp-cli.phar        → Download WordPress installer tool
4. RUN mv + chmod              → Install WP-CLI globally
5. RUN echo listen=0.0.0.0     → Configure PHP-FPM to accept Docker connections
6. EXPOSE 9000                 → Document PHP-FPM port
7. COPY script.sh              → Copy setup script
8. RUN chmod +x                → Make script executable
9. ENTRYPOINT                  → Run script on startup
```

---

## 🔄 **What Happens When Container Starts:**

```
Container starts
    ↓
Runs ./script.sh
    ↓
Script downloads WordPress with WP-CLI
    ↓
Configures wp-config.php (database connection)
    ↓
Installs WordPress (creates tables in MariaDB)
    ↓
Starts PHP-FPM (keeps container alive)
    ↓
Container keeps running (serving WordPress)
```

---

## 📊 **Package Purposes:**

| Package | What It Does | Why WordPress Needs It |
|---------|--------------|------------------------|
| **php** | Run PHP code | WordPress is written in PHP |
| **php-fpm** | Process PHP for NGINX | NGINX can't run PHP directly |
| **php-mysql** | Connect PHP to MariaDB | WordPress stores data in database |
| **mariadb-client** | Query database | WordPress needs to read/write data |
| **wget** | Download files | Get WP-CLI installer |
| **WP-CLI** | Install WordPress | Automate WordPress setup |

---

## 🔗 **Container Communication:**

```
NGINX Container
    ↓ (sends .php files)
WordPress Container (PHP-FPM on port 9000)
    ↓ (queries database)
MariaDB Container (port 3306)
```

---

## 🎓 **Key Concepts:**

1. **PHP-FPM** → Processes PHP code for NGINX
2. **WP-CLI** → Automates WordPress installation
3. **`0.0.0.0:9000`** → Allows Docker network connections
4. **Port 9000** → Standard PHP-FPM port (NGINX connects here)
5. **mariadb-client** → Lets WordPress talk to database

---

**Ready for the WordPress script?** Show me `tools/script.sh` next! 🚀