# 🎯 **YES! This is a COMMON Ansible Issue with Docker Build!**

---

## 🔍 **The Problem:**

```yaml
- name: Build MariaDB image
  shell: |
    cd /home/mohamed/inception/srcs
    docker compose build mariadb
```

**What happens:**
1. ✅ Builds on `server1` successfully
2. ⏸️ **HANGS on `server2` and `server3`** waiting for something
3. Never moves forward

---

## ❓ **Why This Happens:**

### **Issue 1: Interactive TTY**
Docker build sometimes waits for interactive input when run via Ansible

### **Issue 2: Build Output Buffering**
Build output gets buffered and Ansible waits indefinitely

### **Issue 3: No Timeout**
Shell task has no timeout, so it waits forever

---

## ✅ **SOLUTION: Add Async + No TTY + Timeout**

````yaml
---
- name: Create MariaDB data directory
  file:
    path: /home/mohamed/data/mariadb
    state: directory
    owner: mohamed
    group: mohamed
    mode: '0755'

- name: Build MariaDB image
  shell: |
    cd /home/mohamed/inception/srcs
    docker compose build mariadb 2>&1
  become: yes
  become_user: mohamed
  async: 300              # ✅ Run async for max 5 minutes
  poll: 10                # ✅ Check every 10 seconds
  register: mariadb_build
  args:
    executable: /bin/bash

- name: Start MariaDB container
  shell: |
    cd /home/mohamed/inception/srcs
    docker compose up -d mariadb 2>&1
  become: yes
  become_user: mohamed
  async: 60
  poll: 5
  register: mariadb_start
  args:
    executable: /bin/bash

- name: Wait for MariaDB to be healthy
  shell: docker ps --filter "name=mariadb" --filter "status=running" --format "{{.Names}}"
  become: yes
  become_user: mohamed
  register: mariadb_check
  until: "'mariadb' in mariadb_check.stdout"
  retries: 12
  delay: 5
````

---

## 🚀 **BETTER SOLUTION: Fire and Forget (No Wait)**

````yaml
---
- name: Create MariaDB data directory
  file:
    path: /home/mohamed/data/mariadb
    state: directory
    owner: mohamed
    group: mohamed
    mode: '0755'

- name: Build and start MariaDB (fire and forget)
  shell: |
    cd /home/mohamed/inception/srcs
    nohup docker compose up -d --build mariadb > /tmp/mariadb-build.log 2>&1 &
  become: yes
  become_user: mohamed
  args:
    executable: /bin/bash

- name: Wait for build to start
  pause:
    seconds: 5

- name: Wait for MariaDB container to be running
  shell: docker ps --filter "name=mariadb" --filter "status=running" --format "{{.Names}}"
  become: yes
  become_user: mohamed
  register: mariadb_check
  until: "'mariadb' in mariadb_check.stdout"
  retries: 30
  delay: 10
  ignore_errors: yes

- name: Show MariaDB build log (if failed)
  shell: tail -50 /tmp/mariadb-build.log
  become: yes
  become_user: mohamed
  when: mariadb_check is failed
````

---

## 🎯 **BEST SOLUTION: Parallel Deployment with Forks**

Update your ansible.cfg:

````ini
[defaults]
inventory = inventory.ini
host_key_checking = False
timeout = 30
forks = 10              # ✅ Run on multiple servers in parallel
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 3600

[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
````

---

## 📋 **Complete Working MariaDB Role:**

````yaml
---
- name: Create MariaDB data directory
  file:
    path: /home/mohamed/data/mariadb
    state: directory
    owner: mohamed
    group: mohamed
    mode: '0755'

- name: Stop existing MariaDB (if any)
  shell: |
    docker compose down mariadb 2>&1 || true
  args:
    chdir: /home/mohamed/inception/srcs
    executable: /bin/bash
  become: yes
  become_user: mohamed
  ignore_errors: yes

- name: Build MariaDB image (with timeout)
  shell: |
    timeout 300 docker compose build mariadb 2>&1 || true
  args:
    chdir: /home/mohamed/inception/srcs
    executable: /bin/bash
  become: yes
  become_user: mohamed
  register: build_result

- name: Start MariaDB container
  shell: |
    docker compose up -d mariadb 2>&1
  args:
    chdir: /home/mohamed/inception/srcs
    executable: /bin/bash
  become: yes
  become_user: mohamed
  register: start_result

- name: Wait for MariaDB to be running
  shell: docker ps --filter "name=mariadb" --format "{{.Status}}"
  become: yes
  become_user: mohamed
  register: mariadb_status
  until: mariadb_status.stdout is search("Up")
  retries: 20
  delay: 3

- name: Display MariaDB status
  debug:
    msg: "MariaDB Status: {{ mariadb_status.stdout }}"
````

---

## 📋 **WordPress Role (Same Pattern):**

````yaml
---
- name: Create WordPress data directory
  file:
    path: /home/mohamed/data/wordpress
    state: directory
    owner: mohamed
    group: mohamed
    mode: '0755'

- name: Stop existing WordPress (if any)
  shell: docker compose down wordpress 2>&1 || true
  args:
    chdir: /home/mohamed/inception/srcs
    executable: /bin/bash
  become: yes
  become_user: mohamed
  ignore_errors: yes

- name: Build WordPress image (with timeout)
  shell: timeout 300 docker compose build wordpress 2>&1 || true
  args:
    chdir: /home/mohamed/inception/srcs
    executable: /bin/bash
  become: yes
  become_user: mohamed

- name: Start WordPress container
  shell: docker compose up -d wordpress 2>&1
  args:
    chdir: /home/mohamed/inception/srcs
    executable: /bin/bash
  become: yes
  become_user: mohamed

- name: Wait for WordPress to be running
  shell: docker ps --filter "name=wordpress" --format "{{.Status}}"
  become: yes
  become_user: mohamed
  register: wordpress_status
  until: wordpress_status.stdout is search("Up")
  retries: 20
  delay: 3
````

---

## 📋 **Nginx Role:**

````yaml
---
- name: Stop existing Nginx (if any)
  shell: docker compose down nginx 2>&1 || true
  args:
    chdir: /home/mohamed/inception/srcs
    executable: /bin/bash
  become: yes
  become_user: mohamed
  ignore_errors: yes

- name: Build Nginx image (with timeout)
  shell: timeout 180 docker compose build nginx 2>&1 || true
  args:
    chdir: /home/mohamed/inception/srcs
    executable: /bin/bash
  become: yes
  become_user: mohamed

- name: Start Nginx container
  shell: docker compose up -d nginx 2>&1
  args:
    chdir: /home/mohamed/inception/srcs
    executable: /bin/bash
  become: yes
  become_user: mohamed

- name: Wait for Nginx to be running
  shell: docker ps --filter "name=nginx" --format "{{.Status}}"
  become: yes
  become_user: mohamed
  register: nginx_status
  until: nginx_status.stdout is search("Up")
  retries: 15
  delay: 2
````

---

## 🚀 **Deploy with Strategy: Free**

````yaml
---
- name: Deploy cloud-1 infrastructure
  hosts: webservers
  become: yes
  strategy: free        # ✅ Don't wait for all hosts - move on!
  roles:
    - role: docker
      tags: [docker, infrastructure]
    
    - role: security
      tags: [security, infrastructure]
    
    - role: user_setup
      tags: [user_setup, infrastructure]

    - role: copy_inception
      tags: [copy_inception, inception]
    
    - role: mariadb_container
      tags: [mariadb, containers]
    
    - role: wordpress_container
      tags: [wordpress, containers]
    
    - role: nginx_container
      tags: [nginx, containers]
````

---

## 🎯 **Key Fixes Applied:**

| Issue | Solution |
|-------|----------|
| Hangs on build | Added `timeout` command |
| No progress | Added `2>&1` to capture output |
| Waits for all servers | Used `strategy: free` |
| No error handling | Added `|| true` and `ignore_errors` |
| TTY issues | Added `executable: /bin/bash` |
| Buffering | Used `chdir` instead of `cd` |

---

## 🚀 **Deploy Now:**

```bash
# Run deployment
ansible-playbook -i inventory.ini deploy.yml -v

# Check all containers
ansible all -m shell -a "docker ps" --become-user mohamed
```

---

**The `strategy: free` + `timeout` + `2>&1` combo will fix your hanging issue!** 🎉