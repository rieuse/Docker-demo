![image.png](http://upload-images.jianshu.io/upload_images/4701426-909013d4e2884d7f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


# 一：简介和安装docker
对于较大型的爬虫需求可以利用服务器搭建docker 的python爬虫框架，这样可以充分利用服务器的资源而且可以限制cpu 内存的使用 监控爬虫程序的情况。
利用docker的另一个好处就是可以很方便的把容器导出来然后在另一个有docker环境的主机中就可以运行，十分方便。
默认服务器上已装好docker。如果还没安装docker 请先安装一下。
参考文档：[https://docs.docker.com/engine/installation/](https://docs.docker.com/engine/installation/)
# 二：安装docker-compose
![](http://upload-images.jianshu.io/upload_images/4701426-2de818dc611f3bab.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

Docker Compose是一个用来定义和运行复杂应用的Docker工具。使用Compose，可以在一个文件中定义一个多容器应用，利用配置文件docker-compose.yml 就可以创建管理一组容器，方便容器间的数据连接和网络通讯。
参考文档：[https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
Compose是一个用来运行多容器组合的Docker应用，
```   
pip install docker-compose
```   

# 三：准备文件
新建一个文件夹，并进入执行下面操作。
* 1.把python爬虫程序放进去
* 2.新建文件 Dockerfile 和 requirements.txt 用于手动构建镜像
* 3.新建文件docker-compose.yml 后面利用docker-compose控制多个容器协作工作。


爬虫程序demo:
```
import pymongo
import redis
import requests
client = pymongo.MongoClient('mongodb')
db = client['test']
col = db['new']


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6'}


def crawl():
    url = 'http://www.ximalaya.com/tracks/57774592.json'
    data = requests.get(url, headers=headers).json()
    print(data)
    col.insert(data)    
    to_redis(data['play_path_64'])


def to_redis(data):
    r = redis.StrictRedis(host='redis', port=6379)
    r.sadd("test", '{}'.format(data))
    print("{} into redis".format(data))


def pop_redis():
    r = redis.StrictRedis(host='redis', port=6379, decode_responses=True)
    r.spop("test")


if __name__ == '__main__':
    crawl()
```
注意上面的redis 数据库和mongodb 数据库连接host 填写 redis 和mongodb 即可,不用填入分配的ip 和 容器ID 就行了。
# 四：利用Dockerfile准备镜像
![](http://upload-images.jianshu.io/upload_images/4701426-e07904802f6559dd.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

爬虫需要的镜像为mongo redis python 这些可以直接pull官网的即可。
官方镜像获取命令为：
``` 
docker pull name:tag
```   
name 镜像的名字  tag 即为标签名

执行命令：

```   
docker pull redis  
docker pull mongo
```


默认情况不加标签会拉取最新的官网镜像  redis:latest 和mongo:latest

执行命令：
```   
docker pull python:3.6
 ```   
即可拉取官网python标签是3.6镜像,但是这个镜像还没有任何的模块，下面将使用Dockerfile构建一个有模块的镜像：
打开之前新建的Dockerfile 文件写入以下信息
```
FROM python:3.6
MAINTAINER lulu@guo
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "test.py"]
```
命令解释：
>**FROM**  
FROM 后面指定的镜像为后续的指令设置一个基础的镜像

>**MAINTAINER**  
字面意思，Dockerfile 维护人员

>**ADD**  
ADD指令是从本地一个文件夹中copy文件、目录或者远程文件URL中的文件，然后添加它们到镜像的文件系统中。```ADD . /code``` 把Dockerfile当前目录全部文件导入到镜像中的/code位置。

>**WORKDIR**
指定容器的工作目录

>**RUN**
RUN 命令的exec形式，利用该命令给python镜像添加爬虫必备模块
>```
>RUN ["executable", "param1", "param2"]


>**CMD**
利用该命令即可在容器开启后执行爬虫代码。
>```
>CMD ["executable","param1","param2"]（exec形式，一个首选的形式）


Dockerfile 构建完成后执行下面命令创建镜像，名字及标签为python:v1
```
docker run -t python:v1
```
手动构建镜像后执行下面命令查看当前已有的镜像，即可看到新的python:v1 镜像
```
docker images
```

#五：配置docker-compose.yml 文件，构建多容器配合爬虫系统
![](http://upload-images.jianshu.io/upload_images/4701426-f3db6763e1018cc9.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

打开之前新建的docker-compose.yml 文件，写入下面代码
```
version: '1'
services:
  main-python:
    image: "python:v1"
    volumes:
     - .:/code
  mongodb:
    image: "mongo:latest"
    links:
      - main-python
    volumes: 
      - ./db:/data/db
    ports:
     - "27017:27017"
  redis:
    image: "redis:latest"
    links:
      - main-python
    volumes: 
      - ./redis-data:/redis/data
    ports:
     - "6379:6379"
```
命令简单介绍：
>**version**
docker-compose 的版本

>**services** 
>```
>services:
>  main-python:
>    image: "python:v1"
>```
>services 下有共三个服务，它的下一级标签 image 指定该服务的镜像。
>第一个是main-python 用于执行爬虫程序，第二个服务是mongo数据库，第三个是redis数据库

>image 则是指定服务的镜像名称或镜像 ID。如果镜像在本地不存在，Compose 将会尝试拉取这个镜像。
例如下面这些格式都是可以的：
>```
>image: redis
>image: ubuntu:14.04
>image: tutum/influxdb
>image: example-registry.com:4000/postgresql
>image: a4bc65fd
>```

>**volumes**
从本地指定一个目录挂载到镜像容器中
>```
>volumes: 
>  - ./db:/data/db
>```

>**links**
links 优先于指定一个爬虫程序的容器启动数据库
>```
>links:
>  - main-python
>```

>**ports**
指定映射端口。
>```
>ports:
> - "6379:6379"
>```

# 六：通过docker-compose 运行多容器服务
docker-compose --help 可以查看基本命令

```
  build              Build or rebuild services
  bundle             Generate a Docker bundle from the Compose file
  config             Validate and view the Compose file
  create             Create services
  down               Stop and remove containers, networks, images, and volumes
  events             Receive real time events from containers
  exec               Execute a command in a running container
  help               Get help on a command
  images             List images
  kill               Kill containers
  logs               View output from containers
  pause              Pause services
  port               Print the public port for a port binding
  ps                 List containers
  pull               Pull service images
  push               Push service images
  restart            Restart services
  rm                 Remove stopped containers
  run                Run a one-off command
  scale              Set number of containers for a service
  start              Start services
  stop               Stop services
  top                Display the running processes
  unpause            Unpause services
  up                 Create and start containers
  version            Show the Docker-Compose version information

```
常用的命令有：
* docker-compose ps   查看项目容器列表
* docker-compose up  创建并且启动多个容器的服务容器，数据卷，网络的一系列组件。
* docker-compose down 与up相对，down命令可以停止容器并删除包括容器、网络、数据卷等内容。如果网络、数据卷等资源正在被使用，down命令会跳过这些组件。
* docker-compose stop / start / restart 为停止 / 开启 / 重启 服务容器

**最后一步——运行该服务**：
```
docker-compose up
```
![](http://upload-images.jianshu.io/upload_images/4701426-af714a9f37ef2bfe.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

运行后就抓取了一条喜马拉雅的json数据保存到了mongodb数据库中，另外将一条音频url 保存到redis数据库中。

#七：总结
由于时间有限先完成以上记录，后面还需要做的有：限制docker容器对 cpu 内存 网络等资源的使用，多数据库的集群，或者多主机的爬虫集群负载均衡
![](http://upload-images.jianshu.io/upload_images/4701426-702e12e2afc2bf20.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
