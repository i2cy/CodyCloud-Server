#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys, time

def echo(msg):
    print("<CCInstaller> "+msg)

def service_gen(file_path):
    cs = """#!/bin/sh
### BEGIN INIT INFO
# Provides:             cody_cloud
# Required-Start:       $local_fs $remote_fs $network $syslog $named
# Required_Stop:        $local_fs $remote_fs $network $syslog $named
# Default-Start:        2 3 4 5
# Default-Stop:         0 1 6
# Short-Description:    CodyCloud Server
# Description:          CodyCloud Ngrok Manager Server
### END INIT INFO

codycloud_path="""
    path = sys.path[0]
    cs = cs + path
    cs = cs + """

do_start()
{
    cd ${codycloud_path}
    python3 main.py &
}

do_stop()
{
    echo "">${codycloud_path}/cache/CMD_STOP
    while(($wait<50))
    do
        sleep 0.2
        wait=$(($wait+1))
        if [ -f ${codycloud_path}/cache/FB_STOPPED ]
        then
            echo "CodyCloud Stopped" >&2
            break
        fi
    done
}

do_restart()
{
    do_stop
    sleep 3
    do_start
}

case "$1" in
    start)
        do_start
        ;;
    stop)
        do_stop
        ;;
    restart)
        do_restart
        ;;
    *)
        echo "Usage: {start|stop|restart}" >&2
        exit 3
esac"""
    file = open(file_path,"w")
    file.write(cs)
    file.close

def main():
    if os.geteuid() != 0:
        echo("This installer must be run as root, exiting")
        sys.exit(1)
    echo("Ready for the installation? (input \"y\" for yes, else to exit)")
    temp = input("")
    if temp != "y":
        sys.exit(1)
    echo("Exporting codycloud.service")
    service_gen("/etc/init.d/codycloud")
    echo("Changing file mode to EXECUTABLE")
    os.system("chmod +x /etc/init.d/codycloud")
    echo("Registing service to defaults")
    os.system("update-rc.d codycloud defaults")
    echo("Installation compeleted, run a simple test? (input \"y\" for yes, else to exit)")
    temp = input("")
    if temp != "y":
        sys.exit(0)
    os.system("service codycloud start")
    echo("Service started")
    time.sleep(1)
    echo("Stopping service")
    os.system("service codycloud stop")
    n = 0
    while not os.path.exists("cache/FB_STOPPED"):
        time.sleep(0.5)
        n += 1
        if n > 20:
            echo("Stop_test timeout")
            break
    echo("Catching log")
    os.system("cat logs/codycloud.log")
    echo("Test end")
    sys.exit(0)

if __name__ == '__main__':
    main()
