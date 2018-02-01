# CodyCloud-Server
It is build for a better managing of NGROK_Server

## Usage Examples:
* python3 main.py &  
* nohup python3 main.py &  
* (or like this if you just used the "setup.py" installer)  
  service codycloud start  

## How to Setup
- make sure you have a ngrokd server exe in ***./bin"*** folder(creat a ***./bin*** folder if it dosen't exist)
- make sure you have edited the ***configs/codycloud.json*** correctly
- run "setup.py" file as root user acount and follow the step

## Config File Example (configs/codycloud.json)
>{  
>  "ngrok_servers": {  
>    "ngrokd_ebian": {  
>      "domain": "codos.club",  
>      "http_port": "8080",  
>      "tunnel_addr": "4440",  
>      "log_path": "logs/ngrokd/ebian/ngrokd.log",  
>      "log_level": "ERROR"  
>    }  
>  },  
>  "codycloud_server_port": 2220,  
>  "max_con": 10,  
>  "log_level": "DEBUG",  
>  "base_key": "CodyCloudBasicLiveKey"  
>}  

## How to stop this service
- Create a file named **"CMD_STOP"** in the **"cache"** folder
- If the service stopped, there should be a file named **"FB_STOPPED"** in the **"cache"** folder
- or like this if you just used the "setup.py" installer  
    service codycloud start
