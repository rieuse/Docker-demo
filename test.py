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
