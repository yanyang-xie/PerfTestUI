# VEX Performance Test UI
1. Start/Stop VEX performance test
2. Show vex performance test result 

# Technique
Django(1.8) + bootstrap3

# Installation
pip install -r requirment.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

--------------------调试阶段------------------
手工启动
python manage.py runserver 0.0.0.0:8000

或者采用supervisord
vi /etc/supervisord.conf
[program:vex-test-ui]
directory=/home/yanyang/VEXTestUI
user=root
command=python manage.py runserver 0.0.0.0:8000
process_name=vex-test-ui
numprocs=1
autostart=true
autorestart=true

--------------------生产环境阶段------------------
项目代码目录:/home/yanyang/VEXTestUI
1. 首先需要把静态文件复制到指定文件夹。下述命令将css,js, image等文件拷贝到settings.STATIC_ROOT(/home/yanyang/PerfTestUI/src/static)目录中
python manage.py collectstatic

2. uwsgi启动
执行uwsgi --ini config/uwsgi.ini （可以启动supervisord service去维护项目运行),执行后看看状态ps -ef | grep uwsgi

[uwsgi]
http=:8000
chdir=/home/yanyang/PerfTestUI/src   #注意,这个文件夹必须是项目的根目录(src, 就是项目包的根)
wsgi-file=PerfTestUI/wsgi.py
master=true
processes=8
threads=8
buffer-size=32768
reload-mercy=8
max-requests=5000
py-autoreload=3 #如果有文件更新，自动重启服务
py-autoreload=3 #实现和django自带server一样更新文件自动重启功能

3. 采用nginx转发
static URL要配置成settings.STATIC_ROOT的目录
location /static {
    alias /home/yanyang/PerfTestUI/src/static;
}

service nginx restart

4. 采用supervisord增加自启动
vi /etc/supervisord.conf
[program:perftestui]
directory=/home/yanyang/PerfTestUI
user=root
command=uwsgi --ini /home/yanyang/PerfTestUI/src/config/uwsgi.ini
stopsignal=QUIT
process_name=perftestui
numprocs=1
autostart=true
autorestart=true
stdout_logfile=/var/log/perftestui.log
redirect_stderr=true

注意:supervisord默认管理的是非守护进程的程序，如果采用守护进程用supervisord启动的话，会出现backoff的错误或者exit too fast的错误。当需要采用supervisord进行守护程序的时候，在uwsgi配置文件或者参数中必须不能设置daemonize=/var/log/vextestui.log(此时的log文件使用的是setting.py中的log文件设置)

supervisord的UI上可以启动和停止服务
http://54.169.51.190:9001/

5. 压力测试
--------------------压力测试----------------------
ab -c 100 -n 6000 http://127.0.0.1/
Percentage of the requests served within a certain time (ms)
  50%    549
  66%    566
  75%    575
  80%    582
  90%    600
  95%    614
  98%    634
  99%    648
 100%    711 (longest request)
