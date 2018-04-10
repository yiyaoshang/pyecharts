ps -ef|grep datamanager|awk '{print $2}'|xargs kill -9
