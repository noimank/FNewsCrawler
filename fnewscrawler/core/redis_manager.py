import json
import os
import pickle
from threading import Lock
from typing import Any, Optional, Union
import redis
from fnewscrawler.utils.logger import LOGGER


class RedisManager:
    """
    Redis管理类 - 单例模式
    提供高性能并发支持，包含数据序列化和反序列化功能
    用于文章内容缓存和登录信息持久化
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(RedisManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self,  max_connections=50):
        """初始化Redis连接池"""
        if hasattr(self, '_initialized'):
            return
            
        self.logger = LOGGER
        

        # 从环境变量中读取参数
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', '6379'))
        db = int(os.getenv('REDIS_DB', '0'))
        password = os.getenv('REDIS_PASSWORD', None)
        decode_responses = os.getenv('REDIS_DECODE_RESPONSES', 'true').lower() == 'true'
        
        try:
            # 创建连接池
            self.pool = redis.ConnectionPool(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses,
                max_connections=max_connections,
                retry_on_timeout=True
            )
            
            # 创建Redis客户端
            self.redis_client = redis.Redis(connection_pool=self.pool)
            
            # 测试连接
            self.redis_client.ping()
            self.logger.info(f"Redis连接成功: {host}:{port}/{db}")
            
            self._initialized = True
            
        except Exception as e:
            self.logger.error(f"Redis连接失败: {e}")
            raise
    
    def get_client(self) -> redis.Redis:
        """获取Redis客户端实例"""
        return self.redis_client
    
    def ping(self) -> bool:
        """检查Redis连接状态"""
        try:
            return self.redis_client.ping()
        except Exception as e:
            self.logger.error(f"Redis ping失败: {e}")
            return False
    
    # ==================== 基础操作 ====================
    
    def set(self, key: str, value: Any, ex: Optional[int] = None, 
            serializer: str = 'json') -> bool:
        """
        设置键值对
        
        Args:
            key: 键名
            value: 值
            ex: 过期时间(秒)
            serializer: 序列化方式 ('json', 'pickle', 'str')
        """
        try:
            serialized_value = self._serialize(value, serializer)
            return self.redis_client.set(key, serialized_value, ex=ex)
        except Exception as e:
            self.logger.error(f"Redis set操作失败 {key}: {e}")
            return False
    
    def get(self, key: str, serializer: str = 'json') -> Any:
        """
        获取键值
        
        Args:
            key: 键名
            serializer: 反序列化方式 ('json', 'pickle', 'str')
        """
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            return self._deserialize(value, serializer)
        except Exception as e:
            self.logger.error(f"Redis get操作失败 {key}: {e}")
            return None
    
    def delete(self, *keys: str) -> int:
        """删除键"""
        try:
            return self.redis_client.delete(*keys)
        except Exception as e:
            self.logger.error(f"Redis delete操作失败: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            self.logger.error(f"Redis exists操作失败 {key}: {e}")
            return False
    
    def expire(self, key: str, time: int) -> bool:
        """设置键过期时间"""
        try:
            return self.redis_client.expire(key, time)
        except Exception as e:
            self.logger.error(f"Redis expire操作失败 {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """获取键剩余生存时间"""
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            self.logger.error(f"Redis ttl操作失败 {key}: {e}")
            return -1
    
    # ==================== 哈希操作 ====================
    
    def hset(self, name: str, mapping: dict, serializer: str = 'json') -> int:
        """设置哈希字段"""
        try:
            serialized_mapping = {}
            for k, v in mapping.items():
                serialized_mapping[k] = self._serialize(v, serializer)
            return self.redis_client.hset(name, mapping=serialized_mapping)
        except Exception as e:
            self.logger.error(f"Redis hset操作失败 {name}: {e}")
            return 0
    
    def hget(self, name: str, key: str, serializer: str = 'json') -> Any:
        """获取哈希字段值"""
        try:
            value = self.redis_client.hget(name, key)
            if value is None:
                return None
            return self._deserialize(value, serializer)
        except Exception as e:
            self.logger.error(f"Redis hget操作失败 {name}.{key}: {e}")
            return None
    
    def hgetall(self, name: str, serializer: str = 'json') -> dict:
        """获取哈希所有字段"""
        try:
            data = self.redis_client.hgetall(name)
            result = {}
            for k, v in data.items():
                if isinstance(k, bytes):
                    k = k.decode('utf-8')
                result[k] = self._deserialize(v, serializer)
            return result
        except Exception as e:
            self.logger.error(f"Redis hgetall操作失败 {name}: {e}")
            return {}
    
    def hdel(self, name: str, *keys: str) -> int:
        """删除哈希字段"""
        try:
            return self.redis_client.hdel(name, *keys)
        except Exception as e:
            self.logger.error(f"Redis hdel操作失败 {name}: {e}")
            return 0
    
    # ==================== 列表操作 ====================
    
    def lpush(self, name: str, *values: Any, serializer: str = 'json') -> int:
        """从左侧推入列表"""
        try:
            serialized_values = [self._serialize(v, serializer) for v in values]
            return self.redis_client.lpush(name, *serialized_values)
        except Exception as e:
            self.logger.error(f"Redis lpush操作失败 {name}: {e}")
            return 0
    
    def rpush(self, name: str, *values: Any, serializer: str = 'json') -> int:
        """从右侧推入列表"""
        try:
            serialized_values = [self._serialize(v, serializer) for v in values]
            return self.redis_client.rpush(name, *serialized_values)
        except Exception as e:
            self.logger.error(f"Redis rpush操作失败 {name}: {e}")
            return 0
    
    def lpop(self, name: str, serializer: str = 'json') -> Any:
        """从左侧弹出列表元素"""
        try:
            value = self.redis_client.lpop(name)
            if value is None:
                return None
            return self._deserialize(value, serializer)
        except Exception as e:
            self.logger.error(f"Redis lpop操作失败 {name}: {e}")
            return None
    
    def lrange(self, name: str, start: int, end: int, 
               serializer: str = 'json') -> list:
        """获取列表范围元素"""
        try:
            values = self.redis_client.lrange(name, start, end)
            return [self._deserialize(v, serializer) for v in values]
        except Exception as e:
            self.logger.error(f"Redis lrange操作失败 {name}: {e}")
            return []
    
    # ==================== 序列化/反序列化 ====================
    
    def _serialize(self, value: Any, serializer: str) -> Union[str, bytes]:
        """序列化数据"""
        if serializer == 'json':
            return json.dumps(value, ensure_ascii=False, default=str)
        elif serializer == 'pickle':
            return pickle.dumps(value)
        elif serializer == 'str':
            return str(value)
        else:
            raise ValueError(f"不支持的序列化方式: {serializer}")
    
    def _deserialize(self, value: Union[str, bytes], serializer: str) -> Any:
        """反序列化数据"""
        if isinstance(value, bytes):
            value = value.decode('utf-8')
            
        if serializer == 'json':
            return json.loads(value)
        elif serializer == 'pickle':
            return pickle.loads(value.encode('utf-8') if isinstance(value, str) else value)
        elif serializer == 'str':
            return value
        else:
            raise ValueError(f"不支持的反序列化方式: {serializer}")
    
    # ==================== 高级功能 ====================
    
    def cache_with_ttl(self, key: str, value: Any, ttl: int = 3600, 
                       serializer: str = 'json') -> bool:
        """带TTL的缓存设置"""
        return self.set(key, value, ex=ttl, serializer=serializer)
    
    def get_or_set(self, key: str, default_func, ttl: int = 3600, 
                   serializer: str = 'json') -> Any:
        """获取缓存，不存在则设置默认值"""
        value = self.get(key, serializer)
        if value is None:
            value = default_func() if callable(default_func) else default_func
            self.set(key, value, ex=ttl, serializer=serializer)
        return value
    
    def increment(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        try:
            return self.redis_client.incr(key, amount)
        except Exception as e:
            self.logger.error(f"Redis incr操作失败 {key}: {e}")
            return 0
    
    def decrement(self, key: str, amount: int = 1) -> int:
        """递减计数器"""
        try:
            return self.redis_client.decr(key, amount)
        except Exception as e:
            self.logger.error(f"Redis decr操作失败 {key}: {e}")
            return 0
    
    def close(self):
        """关闭Redis连接"""
        try:
            if hasattr(self, 'pool'):
                self.pool.disconnect()
            self.logger.info("Redis连接已关闭")
        except Exception as e:
            self.logger.error(f"关闭Redis连接失败: {e}")


# 全局Redis管理器实例
redis_manager = RedisManager()


# ==================== 便捷函数 ====================

def get_redis() -> RedisManager:
    """获取Redis管理器实例"""
    return redis_manager


def cache_news_content(url: str, content: dict) -> bool:
    """缓存新闻内容 (24小时TTL)"""
    key = f"news:content:{url}"
    # 从环境变量获取过期时间,单位天,默认3天
    expired_time = int(os.environ.get("NEWS_CONTENT_EXPIRED_TIME", 3)) * 86400
    return redis_manager.set(key, content, ex=expired_time)


def get_cached_news_content(url: str) -> Optional[dict]:
    """获取缓存的新闻内容"""
    key = f"news:content:{url}"
    return redis_manager.get(key)

