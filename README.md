# Python+Flask+Mysql 开发微电影网站

## 网站预览

[预览地址](http://132.232.19.246:5001/1/)

## 实现的功能

- 基于蓝图创建红图,更好细分模块与视图函数

- 稍微完善的后台权限

- 自定义登陆检测装饰器与权限检测装饰器

- 多线程异步增加评论与访问数量

- 结合redis实现弹幕发送

- 使用with的上下文特性自动开启事务

- flask-login处理前台登陆逻辑

- 使用Enum枚举类来表示状态，更具可读性

- csrf认证

- WTForms参数验证

- Jinja2模板引擎

- 基于SQLAlchemy的CRUD

- 简单，开箱即用

> Python的运行环境要求3.x。

## 安装所需依赖

| 依赖 | 说明 |
| -------- | -------- |
| Python| `>= 3.6` |
| Flask| `>= 1.0.2` |
| cymysql| `>= 0.9.10` |
| Flask-Login |`>= 0.4.1`|
| Flask-Redis |`>= 0.3.0`|
| Flask-SQLAlchemy  |`>= 2.3.2`|
| itsdangerous |`>= 0.24`|
| Jinja2 |`>= 2.10`|
| requests |`>= 2.18.4`|
| SQLAlchemy  |`>= 1.2.8`|
| Werkzeug |`>= 0.14.1`|
| WTForms |`>= 2.2`|
## 注意

> 数据库在运行fisher.py自动生成。

## 安装运行

- 点击下载安装或者复制地址使用git clone命令下载

```
git clone git@github.com:<你的用户名>/flask-yushu.git
```

- 在app目录下创建secure.py文件（用来管理私密设置信息）
```
DEBUG=True  #是否开启Dubug
HOST='0.0.0.0' #0.0.0.0表示访问权限为全网
PORT=80 #访问端口号

# mysql连接，比如 SQLALCHEMY_DATABASE_URI='mysql+cymysql://root:root@localhost:3306/movie'
SQLALCHEMY_DATABASE_URI='mysql+cymysql://用户名:用户名@ip地址:mysql端口号/数据库名'
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_COMMIT_TEARDOWN = True
SECRET_KEY='任意字符串作为你的秘钥key'
# redis服务器地址  比如  REDIS_URL = "redis://127.0.0.1:6379/10"
REDIS_URL = "redis://你的redis服务器地址:6379/redis里的第几个db"
```

- 相关依赖

最好在venv的虚拟环境中安装，避免全局污染

- 运行

```Python
python movie.py
```

## 项目中的使用

### 在项目中注册路由

前后台部分(home,admin)已经用红图代替了蓝图。

如果是**前台**。在 app/home 下构建 视图(比如test).py文件后，需要到app/home/\_\_init.py\_\_文件中进行注册。比如
```
from flask import Blueprint
from app.home import test
bp = Blueprint('home',__name__)
def create_home_blueprint():
    test.app.register(bp)
    return bp
```
如果 视图(比如test).py文件中注册是视图函数route是
```
from app.libs.redprint import Redprint
app=RedPrint()
@app.route('/test')
def test():
    return 'test'
```
此时API接口地址应为
> http://localhost/test

如果是**后台**。在 app/admin 下构建 视图(比如test).py文件后，需要到app/admin/\_\_init.py\_\_文件中进行注册。比如
```
from flask import Blueprint
from app.admin import test
bp=Blueprint('admin',__name__)
def create_home_blueprint():
    test.app.register(bp,url_prefix='/admin')
    return bp
```
如果 视图(比如test).py文件中注册是视图函数route是
```
from app.libs.redprint import Redprint
app=RedPrint()
@app.route('/test')
def test():
    return 'test'
```
此时API接口地址应为
> http://localhost/admin/test

### 在项目中使用事务

已经使用with和yield对事务做了上下文处理，当进行数据库处理时，请在with下操作，发生错误时自动回滚
```
with db.auto_commit():
    # orm逻辑
    db.session.add(模型实例)
```

# 测试账号与密码

以上都完成后 前后台登录账号均可自行注册

前台地址:

http://你的网址/1/

后台地址:

http://你的网址/admin

# 部署上线云服务器

| 依赖 | 说明 |
| -------- | -------- |
| Centos| `>= 7.2` |
| Python| `>= 3.6` |
| Flask| `>= 1.0.2` |
| MySQL或者MariaDB| `>= 5.5` |
| nginx |`>= 1.4.0`|
| uwsgi |`>= 2.0.17`|
| pipenv | 暂无 |

### 交流

笔者热爱新技术学习、热衷分享。

- QQ：617946852
- Email：stavyan@qq.com
- WeChat stav_yan


### 最后
> 欢迎进入笔者的私人空间---[斯塔夫部落格](https://stavtop.club)
