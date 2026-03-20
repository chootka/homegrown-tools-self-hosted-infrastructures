# Setting Up Mosquitto Authentication

By default, our Mosquitto broker allows anonymous connections (no username or password). This guide walks through adding username/password authentication.

## Step 1: Create a Password File

SSH into the server running Mosquitto and create a user:

```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd myusername
```

You'll be prompted to enter and confirm a password. This creates a new password file with one user.

**Important:** The `-c` flag **creates** a new file (or overwrites an existing one). Only use `-c` for the first user.

## Step 2: Add More Users

To add additional users without overwriting the file, use `-b` (or omit `-c`):

```bash
sudo mosquitto_passwd -b /etc/mosquitto/passwd anotherusername theirpassword
```

Or interactively (prompts for password):

```bash
sudo mosquitto_passwd /etc/mosquitto/passwd anotherusername
```

## Step 3: Set File Permissions

The `mosquitto` user needs to be able to read the password file:

```bash
sudo chown root:mosquitto /etc/mosquitto/passwd
sudo chmod 640 /etc/mosquitto/passwd
```

This keeps root as the owner but lets the `mosquitto` group read it.

## Step 4: Update Mosquitto Config

Edit the Mosquitto config file:

```bash
sudo nano /etc/mosquitto/conf.d/default.conf
```

Make sure these two lines are present:

```
allow_anonymous false
password_file /etc/mosquitto/passwd
```

- `allow_anonymous false` — rejects connections without credentials
- `password_file` — tells Mosquitto where to find the username/password file

If you want to allow **both** anonymous and authenticated connections, set `allow_anonymous true` instead. But this defeats the purpose of authentication.

## Step 5: Restart Mosquitto

```bash
sudo systemctl restart mosquitto
```

Check it's running:

```bash
sudo systemctl status mosquitto
```

## Step 6: Test

### With credentials (should work):

```bash
mosquitto_sub -h localhost -p 1883 -u myusername -P mypassword -t 'test/#' -v
```

### Without credentials (should be rejected):

```bash
mosquitto_sub -h localhost -p 1883 -t 'test/#' -v
```

You should see: `Connection Refused: not authorised.`

## Updating Passwords

To change an existing user's password:

```bash
sudo mosquitto_passwd /etc/mosquitto/passwd myusername
```

Then reload Mosquitto to pick up the change:

```bash
sudo systemctl reload mosquitto.service
```

## Deleting Users

```bash
sudo mosquitto_passwd -D /etc/mosquitto/passwd myusername
sudo systemctl reload mosquitto.service
```

## What Needs to Update When You Enable Auth

Anything that connects to the broker needs credentials:

| Thing | What to update |
|---|---|
| Python web app | Set `MQTT_USERNAME` and `MQTT_PASSWORD` in `.env` |
| Meshtastic devices | Set username and password in MQTT module settings |
| mosquitto_sub/pub commands | Add `-u username -P password` flags |

## Common Issues

| Problem | Fix |
|---|---|
| `Connection Refused: not authorised` | Wrong username/password, or auth not set up |
| Mosquitto won't start after adding password_file | Check file permissions — `mosquitto` user must be able to read the file |
| Mosquitto crashes with exit code 13 | Password file is owned by root with `600` permissions — change to `640` and `chgrp mosquitto` |
| Changed password but old one still works | Run `sudo systemctl reload mosquitto.service` to pick up changes |
