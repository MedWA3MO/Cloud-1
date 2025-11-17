# 🔐 Complete SSL/TLS Setup Guide for Your Project

Let me break this down into **practical, actionable steps** with **explanations** for each part.

---

## 📚 **Understanding the Pieces**

### **What is SSL/TLS?**
- **SSL/TLS** = Encrypted connection between browser and server
- **Self-signed certificate** = You created it yourself → browsers don't trust it → "Not Secure" warning
- **Let's Encrypt certificate** = Free, trusted by all browsers → green lock 🔒

### **Why Certbot?**
- **Certbot** = Tool that talks to Let's Encrypt to prove you own your domain
- Let's Encrypt gives you a certificate **only if** you prove ownership
- Two ways to prove ownership:
  1. **HTTP-01 Challenge**: Certbot puts a file on your web server, Let's Encrypt checks it (won't work for you - 3 servers)
  2. **DNS-01 Challenge**: Add a TXT record to your domain DNS (this will work!)

### **Where Does Everything Live?**
```
Your laptop (Ansible controller)
    │
    ├─> Runs ansible-playbook
    │
    └─> Connects to 3 servers via SSH
            │
            ├─> Server1 (161.35.207.242)
            ├─> Server2 (178.128.200.201)  
            └─> Server3 (165.232.123.218)
                    │
                    ├─> Certbot installed (host machine)
                    │   └─> Gets certificate from Let's Encrypt
                    │       └─> Saves to /etc/letsencrypt/live/your-domain.com/
                    │
                    └─> Docker containers
                            └─> NGINX container mounts certificates from host
```

---

## 🛠️ **Step-by-Step Implementation**

### **STEP 1: Create the Certbot Role**

**Why?** Ansible roles organize tasks. This role will install Certbot and get certificates.

Create the folder structure:
```bash
mkdir -p roles/certbot_ssl/tasks
mkdir -p roles/certbot_ssl/handlers
```

Create the main tasks file:

````yaml
---
# Task 1: Install snapd (snap package manager - modern way to install Certbot)
- name: Install snapd
  ansible.builtin.apt:
    name: snapd
    state: present
    update_cache: yes
  tags: [certbot, ssl]

# Task 2: Make sure snapd service is running
- name: Ensure snapd is running
  ansible.builtin.systemd:
    name: snapd
    state: started
    enabled: yes
  tags: [certbot, ssl]

# Task 3: Wait for snapd to be ready (important!)
- name: Wait for snapd to be ready
  ansible.builtin.pause:
    seconds: 10
  tags: [certbot, ssl]

# Task 4: Install Certbot via snap
- name: Install Certbot via snap
  community.general.snap:
    name: certbot
    classic: yes
  tags: [certbot, ssl]

# Task 5: Create symlink so you can run "certbot" command
- name: Create symlink for certbot command
  ansible.builtin.file:
    src: /snap/bin/certbot
    dest: /usr/bin/certbot
    state: link
  ignore_errors: yes
  tags: [certbot, ssl]

# Task 6: Check if certificate already exists (don't recreate if it exists)
- name: Check if certificate exists
  ansible.builtin.stat:
    path: "/etc/letsencrypt/live/{{ domain_name }}/fullchain.pem"
  register: cert_exists
  tags: [certbot, ssl]

# Task 7: Get certificate using DNS challenge (only if it doesn't exist)
- name: Get SSL certificate via DNS challenge
  ansible.builtin.shell: |
    certbot certonly \
      --manual \
      --preferred-challenges dns \
      --manual-public-ip-logging-ok \
      -d {{ domain_name }} \
      -d www.{{ domain_name }} \
      --agree-tos \
      --email {{ your_email }} \
      --non-interactive \
      --manual-auth-hook /bin/true
  when: not cert_exists.stat.exists
  register: certbot_output
  ignore_errors: yes
  tags: [certbot, ssl]

# Task 8: Show instructions for DNS challenge
- name: Display DNS challenge instructions
  ansible.builtin.debug:
    msg: |
      ================================================================================
      ACTION REQUIRED: Add DNS TXT Record
      ================================================================================
      
      Certbot needs you to prove you own the domain by adding a TXT record.
      
      Go to Namecheap → Domain List → Manage → Advanced DNS
      
      Add this record:
      Type: TXT Record
      Host: _acme-challenge
      Value: (shown in output above)
      TTL: 1 min
      
      Wait 5-10 minutes, then run the playbook again.
      ================================================================================
  when: certbot_output.changed and not cert_exists.stat.exists
  tags: [certbot, ssl]
````

---

### **STEP 2: Update Your Variables**

Add your domain and email to the variables file:

````yaml
---
intra_login: mohamed
domain_name: "your-actual-domain.com"  # ← CHANGE THIS
your_email: "your-email@example.com"   # ← CHANGE THIS
````

**Example:**
```yaml
domain_name: "mohamed.tech"
your_email: "hassan@example.com"
```

---

### **STEP 3: Add Certbot Role to Deploy Playbook**

````yaml
---
- name: Deploy cloud-1 infrastructure
  hosts: webservers
  become: yes
  roles:
    - role: docker
      tags: [docker, infrastructure, always]
    
    - role: security
      tags: [security, infrastructure]
    
    - role: user_setup
      tags: [user_setup, user, infrastructure, always]

    - role: certbot_ssl  # ← ADD THIS LINE
      tags: [certbot, ssl, infrastructure]

    - role: copy_inception
      tags: [copy_inception, inception, always]

    - role: mariadb_container
      tags: [mariadb, database, containers]

    - role: wordpress_container
      tags: [wordpress, containers]

    - role: nginx_container
      tags: [nginx, webserver, containers]
````

---

### **STEP 4: Update Docker Compose to Use Let's Encrypt Certificates**

**Current state:** Self-signed certificates are generated inside the NGINX Dockerfile.

**New state:** Mount real certificates from the host machine into the container.

````yaml
services:
  # ...existing code...
  
  nginx:
    build:
      context: ./requirements/nginx
      dockerfile: Dockerfile
    container_name: nginx
    depends_on:
      - wordpress
    ports:
      - "443:443"
    networks:
      - inception
    volumes:
      - wordpress_files:/var/www/html
      # ← ADD THESE TWO LINES (mount certificates from host)
      - /etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem:/etc/nginx/ssl_cer.crt:ro
      - /etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem:/etc/nginx/ssl_cer_key.key:ro
    restart: always
    env_file:
      - .env

  # ...existing code...
````

**Explanation:**
- `/etc/letsencrypt/live/your-domain.com/` = where Certbot saves certificates on the **host**
- `/etc/nginx/ssl_cer.crt` = where NGINX **inside the container** looks for the certificate
- `:ro` = read-only (container can't modify the certificates)

---

### **STEP 5: Remove Self-Signed Certificate from NGINX Dockerfile**

````dockerfile
FROM alpine:3.19

RUN apk update && apk add --no-cache nginx openssl gettext

# ← REMOVE THIS LINE (we don't generate self-signed certs anymore)
# RUN openssl req -x509 -nodes -out /etc/nginx/ssl_cer.crt -keyout /etc/nginx/ssl_cer_key.key -subj "/C=Ma/L=khouribga/CN=mohamed/UID=mohamed"

COPY conf/nginx.conf /etc/nginx/nginx.conf

EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]
````

---

### **STEP 6: Run the Playbook (First Time - Will Fail, That's OK!)**

```bash
cd /home/hassan/Desktop/cloud-1

# Run only the certbot role
ansible-playbook -i inventory.ini deploy.yml --tags certbot
```

**What happens:**
1. Ansible installs Certbot on all 3 servers
2. Certbot tries to get a certificate
3. **Let's Encrypt says:** "Prove you own the domain by adding this DNS record"
4. Certbot prints the DNS challenge value
5. **The playbook pauses** and shows you what to do next

**Output will look like:**
```
TASK [certbot_ssl : Display DNS challenge instructions]
ok: [server1] => {
    "msg": "Add TXT record: _acme-challenge.your-domain.com = dGhpc19pc19hX3Rlc3Q"
}
```

---

### **STEP 7: Add DNS TXT Record in Namecheap**

1. **Login to Namecheap:** https://www.namecheap.com/myaccount/login/
2. **Go to Domain List** → Click **Manage** next to your domain
3. **Advanced DNS tab**
4. **Add New Record:**
   - Type: `TXT Record`
   - Host: `_acme-challenge`
   - Value: `paste the value from Certbot output`
   - TTL: `1 min` (or `Automatic`)

**Example:**
```
Type         Host                Value
TXT Record   _acme-challenge     dGhpc19pc19hX3Rlc3Q
```

5. **Save Changes**

---

### **STEP 8: Wait for DNS Propagation**

```bash
# Check if DNS record is visible (run from your laptop)
dig TXT _acme-challenge.your-domain.com

# Or use online tool:
# https://dnschecker.org/#TXT/_acme-challenge.your-domain.com
```

**Wait until you see the TXT record** (usually 5-10 minutes, sometimes up to 30 minutes).

---

### **STEP 9: Run the Playbook Again (Get Certificate)**

```bash
ansible-playbook -i inventory.ini deploy.yml --tags certbot
```

**This time:**
- Certbot verifies the DNS record
- Let's Encrypt issues a **real certificate**
- Certificate is saved to `/etc/letsencrypt/live/your-domain.com/`

**Verify certificates were created:**
```bash
ansible webservers -a "ls -la /etc/letsencrypt/live/"
ansible webservers -a "certbot certificates"
```

---

### **STEP 10: Rebuild and Restart NGINX Container**

```bash
# Stop all containers
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose down" --become-user mohamed

# Rebuild NGINX (without self-signed cert generation)
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose build --no-cache nginx" --become-user mohamed

# Start all containers
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose up -d" --become-user mohamed
```

---

### **STEP 11: Test Your Website**

```bash
# Check NGINX is running
ansible webservers -a "docker ps"

# Test HTTPS from your laptop
curl -I https://your-domain.com

# Or open in browser
# https://your-domain.com
```

**You should see:**
- 🔒 Green padlock in browser
- "Connection is secure"
- No warning about self-signed certificates

---

## 🔄 **Auto-Renewal (Bonus)**

Let's Encrypt certificates expire in **90 days**. Set up auto-renewal:

````yaml
# ...existing code...

- name: Setup automatic certificate renewal
  ansible.builtin.cron:
    name: "Renew Let's Encrypt certificates"
    job: "certbot renew --quiet && docker restart nginx"
    hour: "3"
    minute: "0"
    day: "*/7"
    user: root
  tags: [certbot, ssl]
````

**What this does:**
- Every 7 days at 3:00 AM
- Certbot checks if certificate needs renewal (< 30 days left)
- If yes, renews it
- Restarts NGINX container to load new certificate

---

## 🧪 **Testing Checklist**

```bash
# 1. Check Certbot is installed
ansible webservers -a "certbot --version"

# 2. Check certificates exist
ansible webservers -a "ls -la /etc/letsencrypt/live/"

# 3. Check certificate details
ansible webservers -a "certbot certificates"

# 4. Check NGINX config is valid
ansible webservers -a "docker exec nginx nginx -t"

# 5. Check NGINX is using the certificates
ansible webservers -a "docker exec nginx ls -la /etc/nginx/ssl_cer.crt"

# 6. Test HTTPS connection
curl -vI https://your-domain.com 2>&1 | grep -i "SSL certificate"

# 7. Test from browser
# Open https://your-domain.com
# Click padlock icon → Certificate → Should say "Let's Encrypt"
```

---

## 📊 **Summary of Changes**

| File | Change |
|------|--------|
| `roles/certbot_ssl/tasks/main.yml` | **NEW** - Install Certbot, get certificates |
| all.yml | **ADDED** - `domain_name` and `your_email` |
| deploy.yml | **ADDED** - `certbot_ssl` role |
| `docker-compose.yml` | **ADDED** - Mount Let's Encrypt certificates |
| `nginx/Dockerfile` | **REMOVED** - Self-signed certificate generation |

---

## ⚠️ **Common Issues**

### **Issue 1: DNS record not found**
```
Error: DNS problem: NXDOMAIN looking up TXT for _acme-challenge.your-domain.com
```
**Solution:** Wait longer (up to 1 hour), check DNS with `dig`

### **Issue 2: Rate limit exceeded**
```
Error: too many certificates already issued
```
**Solution:** Let's Encrypt limits 5 certs/week. Wait or use staging (test) environment:
```bash
certbot certonly --staging ...
```

### **Issue 3: Certificate not found in container**
```
nginx: [emerg] cannot load certificate "/etc/nginx/ssl_cer.crt"
```
**Solution:** Check the volume mount in `docker-compose.yml`, verify file exists on host

---

**Next step:** Tell me your domain name and I'll help you run through this! 🚀