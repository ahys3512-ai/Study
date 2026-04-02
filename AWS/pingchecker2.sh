#!/bin/bash
HOST_TO_CHECK=10.4.1.100

if ping -qc 20 -W 1 $HOST_TO_CHECK >/dev/null; then
    echo "IDC-DB $HOST_TO_CHECK is up"
    systemctl restart httpd
else
    echo "IDC-DB $HOST_TO_CHECK is down"
    systemctl stop httpd
fi
