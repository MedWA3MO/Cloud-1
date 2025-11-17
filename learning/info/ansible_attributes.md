Excellent question! This is a **crucial distinction** to understand:

## They are **Ansible-specific**, NOT YAML attributes!

Let me break this down:

### YAML only provides the **structure**:
- Lists (`-`)
- Key-value pairs (`key: value`)
- Indentation
- Data types (strings, numbers, booleans)

### Ansible **uses** YAML structure but adds its own vocabulary:

## Ansible Keywords vs Module Names vs Module Parameters:

```yaml
---
- name: Practice                    # ← Ansible playbook keyword
  hosts: local                      # ← Ansible playbook keyword
  tasks:                            # ← Ansible playbook keyword
  
    - name: Create a directory      # ← Ansible task keyword
      file:                         # ← Ansible MODULE name
        path: /tmp/demo             # ← file module PARAMETER
        state: directory            # ← file module PARAMETER
      become: yes                   # ← Ansible task keyword
      
    - name: Run command
      shell: ls -la                 # ← Ansible MODULE name (shell)
      register: result              # ← Ansible task keyword
      
    - name: Show info
      debug:                        # ← Ansible MODULE name
        msg: "Hello"                # ← debug module PARAMETER
        var: result                 # ← debug module PARAMETER
```

## Categories:

### 1. **Ansible Playbook Keywords** (Ansible understands these):
- `name`
- `hosts`
- `tasks`
- `become`
- `register`
- `when`
- `loop`
- `ignore_errors`

### 2. **Ansible Module Names** (Built-in tools):
- `file` - manage files/directories
- `copy` - copy files
- `apt` - manage packages (Debian/Ubuntu)
- `shell` - run shell commands
- `debug` - print messages
- `user` - manage users
- `service` - manage services

### 3. **Module Parameters** (Each module has its own):

**file module:**
- `path`, `state`, `mode`, `owner`

**copy module:**
- `content`, `dest`, `src`, `backup`

**debug module:**
- `msg`, `var`

**apt module:**
- `name`, `state`, `update_cache`

## Think of it like this:

```yaml
# YAML provides the syntax (structure)
key: value
list:
  - item1
  - item2

# Ansible provides the vocabulary (meaning)
tasks:              # Ansible knows what "tasks" means
  - name: Task 1    # Ansible knows what "name" means
    file:           # Ansible knows "file" is a module
      path: /tmp    # The 'file' module knows what "path" means
```

## Summary:

- **YAML** = The language/format (like JSON or XML)
- **Ansible** = The tool that reads YAML and gives meaning to specific keywords
- If you used the same YAML file with a different tool, it wouldn't understand `file`, `copy`, `debug`, etc.

Does this clarify the distinction? 🎯