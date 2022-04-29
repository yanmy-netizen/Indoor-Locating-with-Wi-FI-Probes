import numpy as np
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql

pymysql.install_as_MySQLdb() # 这句？

# initialize the positions of wifi sniffer
p = np.array([[0, 0], [10, 0], [0, 10]])
# set mapping from mac of wifi sniffer to index
mmac2idx = {'14:6b:9c:f3:f1:61': 0, '5e:cf:7f:10:f3:78': 1, '5e:cf:7f:10:f3:79': 2} # 三个探针

# 14:6b:9c:f3:f1:61 是第一个配置好的 id: 00f3f161


# set the mac of smart phone
targetMac = 'a4:56:02:61:7f:57' # 目标检测
# initialize the distances to wifi sniffer
targetPos = np.array([5, 5])
r = np.array([np.linalg.norm(targetPos - p[0]), np.linalg.norm(targetPos - p[1]), np.linalg.norm(targetPos - p[2])])
# mark whether all distances are recalculated
mark = [False, False, False]
receivedTime = ''

app = Flask(__name__)


class Config(object):
    """配置参数"""
    # 设置连接数据库的URL
    user = 'newuser'
    password = 'password'
    database = 'dev_to'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@127.0.0.1:3306/%s' % (user, password, database)

    # 设置sqlalchemy自动更跟踪数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 查询时会显示原始SQL语句
    app.config['SQLALCHEMY_ECHO'] = True

    # 禁止自动提交数据处理
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False


# 读取配置
app.config.from_object(Config) #Web服务的配置

# 创建数据库sqlalchemy工具对象
db = SQLAlchemy(app)


class Pos(db.Model):
    # 定义表名
    __tablename__ = 'Pos'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.Time)
    x = db.Column(db.Float)
    y = db.Column(db.Float)


@app.route('/', methods=['Post']) # 用Post
def register():
    global mark, targetPos, receivedTime
    print(request.headers)
    receivedJson = request.get_json()
    parseJson(receivedJson)
    # if mark[0] and mark[1] and mark[2]
    if True:
        targetPos = trilateration(p[0], p[1], p[2], r[0], r[1], r[2])
        mark[0], mark[1], mark[2] = False, False, False
        datalist = [Pos(time=datetime.strptime(receivedTime, "%c"), x=targetPos[0], y=targetPos[1])]
        db.session.add_all(datalist)
        db.session.commit()
    return 'welcome'

@app.route('/getJson', methods=['Post']) # 从数据结构获取数据, 可以不新建一个Web Server 
def getJson():
    data = request.form['data'] # 已经是json了，就不用dump了
    jdict = json.loads(data)
    return jdict

def parseJson(receivedJson):
    global r, mark, receivedTime
    mmac = receivedJson['mmac']
    assert mmac in mmac2idx.keys()
    idx = mmac2idx[mmac]
    for i in receivedJson["data"]:
        if i['mac'] == targetMac:
            dis, num = 0, 0
            for j in i['rssi']:
                dis += rssi2dis(j)
                num += 1
            if num > 0:
                dis /= num
                r[idx] = dis
                mark[idx] = True
                receivedTime = receivedJson['time']


def rssi2dis(rssi):
    return 1.0


# args:
# p1, p2, p3 are the locations of wifi sniffers, type = nparray.
# r1, r2, r3 are the distances to wifi sniffers.
# return:
# ans is the location of the smart phone, type -npdarry.


def trilateration(p1, p2, p3, r1, r2, r3):
    p2p1Dis = np.linalg.norm(p1 - p2)
    ex = (p2 - p1) / p2p1Dis
    aux = p3 - p1
    i = np.dot(ex, aux)
    aux2 = p3 - p1 - i * ex
    ey = aux2 / np.linalg.norm(aux2)
    j = np.dot(ey, aux)
    x = (r1 ** 2 - r2 ** 2 + p2p1Dis ** 2) / (2 * p2p1Dis)
    y = (r1 ** 2 - r3 ** 2 + i ** 2 + j ** 2) / (2 * j) - i * x / j
    ans = np.array([p1[0] + x * ex[0] + y * ey[0], p1[1] + x * ex[1] + y * ey[1]])
    return ans


if __name__ == '__main__':
    # 删除所有表
    db.drop_all()

    # 创建所有表
    db.create_all()

    app.run(port=8888, debug=True)
