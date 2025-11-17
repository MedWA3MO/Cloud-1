# 🎯 Great Idea! Let's Get Inception Running First!

---

## Step 1: Update Makefile to Use Variable Path

You're right - we need to make paths dynamic. But Makefile can't use Ansible variables directly.

**Solution:** Use `$(shell whoami)` to get current user dynamically:

### Update [`inception/Makefile`](inception/Makefile ):

````makefile
USER := $(shell whoami)
DATA_DIR := /home/$(USER)/data

all:
	mkdir -p $(DATA_DIR)/mariadb $(DATA_DIR)/wordpress
	cd srcs && docker compose up -d --build

down:
	cd srcs && docker compose down

clean:
	cd srcs && docker compose down -v
	rm -rf $(DATA_DIR)/mariadb/* $(DATA_DIR)/wordpress/*

fclean: clean
	docker system prune -af

re: fclean all

.PHONY: all down clean fclean re
````

---

## Step 2: Verify Your Current Setup

Let's check what's already deployed:

```bash
# Check if user exists
ansible webservers -a "id mohamed"

# Check if inception files are on server
ansible webservers -a "ls -la /home/mohamed/inception/" --become-user mohamed

# Check if docker works for user
ansible webservers -a "docker ps" --become-user mohamed
```

---

## Step 3: Copy Updated Makefile to Server

Update your [`roles/user_setup/tasks/main.yml`](roles/user_setup/tasks/main.yml ) to include the updated Makefile:

````yaml
---
- name: Create user matching intra login
  user:
    name: "{{ intra_login }}"
    state: present
    shell: /bin/bash
    create_home: yes
    groups: docker
    append: yes
  tags: [user]

- name: Create inception directory structure
  file:
    path: "{{ item }}"
    state: directory
    owner: "{{ intra_login }}"
    group: "{{ intra_login }}"
    mode: '0755'
  loop:
    - "{{ inception_path }}"
    - "{{ data_path }}"
    - "{{ data_path }}/mariadb"
    - "{{ data_path }}/wordpress"
  tags: [user]

- name: Copy entire inception project to server
  copy:
    src: "{{ playbook_dir }}/inception/"
    dest: "{{ inception_path }}/"
    owner: "{{ intra_login }}"
    group: "{{ intra_login }}"
    mode: preserve
  tags: [user]
````

---

## Step 4: Deploy User Setup (with updated Makefile)

```bash
ansible-playbook deploy.yml --tags user
```

---

## Step 5: Test Building Containers One by One

### Build MariaDB only:

```bash
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose build mariadb" --become-user mohamed
```

### Check if image was created:

```bash
ansible webservers -a "docker images" --become-user mohamed
```

You should see:
```
REPOSITORY                    TAG       IMAGE ID
inception-mariadb            latest    xxxxx
```

---

### Build WordPress only:

```bash
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose build wordpress" --become-user mohamed
```

### Check images:

```bash
ansible webservers -a "docker images" --become-user mohamed
```

You should see:
```
REPOSITORY                    TAG       IMAGE ID
inception-mariadb            latest    xxxxx
inception-wordpress          latest    xxxxx
```

---

### Build Nginx only:

```bash
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose build nginx" --become-user mohamed
```


### Check all images:

```bash
ansible webservers -a "docker images" --become-user mohamed
```

You should see:
```
REPOSITORY                    TAG       IMAGE ID
inception-nginx              latest    xxxxx
inception-mariadb            latest    xxxxx
inception-wordpress          latest    xxxxx
```

---

## Step 6: Start Containers One by One

### Start MariaDB only:

```bash
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose up -d mariadb" --become-user mohamed
```

### Check if running:

```bash
ansible webservers -a "docker ps" --become-user mohamed
```

Should show:
```
CONTAINER ID   IMAGE               STATUS    NAMES
xxxxx          inception-mariadb   Up        mariadb
```

---

### Start WordPress:

```bash
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose up -d wordpress" --become-user mohamed
```

### Check:

```bash
ansible webservers -a "docker ps" --become-user mohamed
```

Should show:
```
CONTAINER ID   IMAGE                  STATUS    NAMES
xxxxx          inception-wordpress    Up        wordpress
xxxxx          inception-mariadb      Up        mariadb
```

---

### Start Nginx:

```bash
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose up -d nginx" --become-user mohamed
```

### Check all containers:

```bash
ansible webservers -a "docker ps" --become-user mohamed
```


Should show:
```
CONTAINER ID   IMAGE                  STATUS    PORTS                 NAMES
xxxxx          inception-nginx        Up        0.0.0.0:443->443/tcp  nginx
xxxxx          inception-wordpress    Up                              wordpress
xxxxx          inception-mariadb      Up                              mariadb
```

---

## Step 7: Test Your Website

Open browser:
```
https://46.101.96.66
https://64.226.120.234
https://134.122.94.26
```

---

## 🎯 Summary of Commands

```bash
# 1. Deploy user + inception files
ansible-playbook deploy.yml --tags user

# 2. Build containers one by one
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose build mariadb" --become-user mohamed
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose build wordpress" --become-user mohamed
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose build nginx" --become-user mohamed

# 3. Start containers one by one
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose up -d mariadb" --become-user mohamed
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose up -d wordpress" --become-user mohamed
ansible webservers -m shell -a "cd /home/mohamed/inception/srcs && docker compose up -d nginx" --become-user mohamed

# 4. Check status
ansible webservers -a "docker ps" --become-user mohamed

# 5. Check logs if issues
ansible webservers -a "docker logs mariadb" --become-user mohamed
ansible webservers -a "docker logs wordpress" --become-user mohamed
ansible webservers -a "docker logs nginx" --become-user mohamed
```

---

**Start with Step 4 and paste the output!** 🚀