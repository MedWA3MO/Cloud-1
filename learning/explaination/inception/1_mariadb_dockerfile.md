**Perfect! Let's go through your MariaDB Dockerfile line by line!** 📖

---

## 📄 **MariaDB Dockerfile Explained:**

---

### **Line 1: Base Image**
```dockerfile
FROM debian:11
```

**What it does:** Start from Debian 11 (Bullseye) Linux distribution

**Why we need it:**
- Every Docker image needs a base operating system
- Debian is **stable, lightweight, and secure**
- Version 11 is the **current stable release**
- Alternative: `alpine:3.19` (smaller but sometimes compatibility issues)

**In simple terms:** "Build this container using Debian 11 as the foundation"

---

### **Line 3-4: Update System**
```dockerfile
RUN apt -y update && apt -y upgrade
```

**What it does:**
- `apt update` → Updates the package list (like checking for new software versions)
- `apt upgrade` → Installs all available updates
- `-y` → Automatically answer "yes" to prompts (non-interactive)
- `&&` → Run second command only if first succeeds

**Why we need it:**
- ✅ Get **latest security patches**
- ✅ Ensure packages are up-to-date
- ✅ Avoid vulnerabilities from outdated software

**In simple terms:** "Update the system to get the latest security fixes"

---

### **Line 6: Install MariaDB**
```dockerfile
RUN apt install -y mariadb-server
```

**What it does:** Installs MariaDB database server

**Why we need it:**
- MariaDB is the **database** for your WordPress site
- Stores all your data: posts, users, settings, etc.
- `mariadb-server` includes the full database server

**What it installs:**
- MariaDB daemon (`mysqld`)
- Client tools (`mysql`, `mysqldump`)
- Default configuration files

**In simple terms:** "Install the database server software"

---

### **Line 8: Expose Port**
```dockerfile
EXPOSE 3306
```

**What it does:** Documents that this container listens on port 3306

**Why we need it:**
- Port **3306** is the **standard MySQL/MariaDB port**
- WordPress container needs to connect to this port
- **NOTE:** This is **documentation only** - doesn't actually open the port!

**Important:** The port is opened by Docker networking, not by this line

**In simple terms:** "Tell Docker this container uses port 3306 for database connections"

---

### **Line 10: Copy Startup Script**
```dockerfile
COPY tools/script.sh /
```

**What it does:** Copy `script.sh` from your host machine into the container at `/script.sh`

**Why we need it:**
- MariaDB needs **custom configuration** (create database, users, passwords)
- This script will:
  - Initialize the database
  - Create WordPress database
  - Create WordPress user with permissions
  - Set root password

**In simple terms:** "Copy our custom setup script into the container"

---

### **Line 12: Make Script Executable**
```dockerfile
RUN chmod +x script.sh
```

**What it does:** Give execute permission to the script

**Why we need it:**
- By default, copied files are **not executable**
- `chmod +x` → Make file executable
- Without this, the script won't run!

**In simple terms:** "Allow the script to be run as a program"

---

### **Line 15: Set Container Startup Command**
```dockerfile
ENTRYPOINT ["./script.sh"]
```

**What it does:** Run `script.sh` when container starts

**Why we need it:**
- **ENTRYPOINT** defines what runs when container starts
- This script will:
  1. Configure MariaDB
  2. Create databases/users
  3. Start MariaDB server
- The script keeps running (so container stays alive)

**ENTRYPOINT vs CMD:**
- `ENTRYPOINT` → **Cannot** be overridden easily (enforces the command)
- `CMD` → Can be overridden (default command)

**In simple terms:** "When this container starts, run our setup script"

---

## 🎯 **Complete Flow:**

```
1. FROM debian:11           → Start with Debian
2. RUN apt update/upgrade   → Update system
3. RUN apt install mariadb  → Install database
4. EXPOSE 3306             → Document port usage
5. COPY script.sh          → Copy setup script
6. RUN chmod +x            → Make script runnable
7. ENTRYPOINT              → Run script on startup
```

---

## 🔄 **What Happens When Container Starts:**

```
Container starts
    ↓
Runs ./script.sh
    ↓
Script initializes MariaDB
    ↓
Creates WordPress database
    ↓
Creates WordPress user
    ↓
Starts MariaDB server (mysqld)
    ↓
Container keeps running (serving database)
```

---

## 📊 **Why This Structure?**

| Component | Purpose |
|-----------|---------|
| **Debian 11** | Stable, secure base OS |
| **apt update/upgrade** | Security patches |
| **mariadb-server** | The actual database software |
| **Port 3306** | Communication with WordPress |
| **script.sh** | Custom initialization (database, users) |
| **chmod +x** | Make script executable |
| **ENTRYPOINT** | Start database when container runs |

---

## 🎓 **Key Concepts:**

1. **Base Image** → The OS foundation
2. **RUN** → Execute commands during build
3. **COPY** → Transfer files from host to container
4. **EXPOSE** → Document which ports are used
5. **ENTRYPOINT** → What runs when container starts

---

**Ready for the next file?** Show me `tools/script.sh` next! 🚀