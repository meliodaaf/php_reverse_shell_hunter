# php_shell_hunter.py

![logo](https://github.com/meliodaaf/php_reverse_shell_hunter/blob/main/docs/logo.png)

## Features
* Hunts basic unobfuscated PHP shell files to a target directory
* Can be ran locally or to a remote linux server
* If PHP shell is found, it will notify on specified slack channel
* This script leverages [Slack Incoming Webhooks App](https://api.slack.com/messaging/webhooks)

## Installation

```bash
git clone https://github.com/meliodaaf/threat-hunting-php-shell.git
pip3 install -r requirements.txt
```

**Running the script against a remote server**
```bash
Usage: python3 php_shell_hunter.py --remote-host 192.168.100.1 --directory /var/www/html
```

**Running the script locally**
```bash
Usage: python3 php_shell_hunter.py --directory /var/www/html
```

**Setting up SSH passwordless connection to a remote server**
```bash
ssh-key-gen -t rsa # There's no need for this command if you already have one
ssh-copy-id user@serverip
```

**Sample**
1. Sample files on a remote host
![webshells](https://github.com/meliodaaf/php_reverse_shell_hunter/blob/main/docs/webshells.png)
2. Run the script againts the remote host and directory
![script](https://github.com/meliodaaf/php_reverse_shell_hunter/blob/main/docs/script.png)
3. Slack notification
![slack](https://github.com/meliodaaf/php_reverse_shell_hunter/blob/main/docs/slack.png)


## References
- [IppSec Slack Webhook Setup](https://www.youtube.com/watch?v=1w0btuMAvZk&list=PLidcsTyj9JXJ8TgmjfMo5Dlt___FN1XAn&index=5)
- [Paramiko Setup](https://linuxhint.com/paramiko-python/)
