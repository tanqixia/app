from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, text
from datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship
Base = declarative_base()


class jushuitan_Merchant(Base):
    """创建商户表"""
    __tablename__ = 'jushuitan_Merchant'

    id = Column(Integer, primary_key=True, autoincrement=True,comment='自增主键')
    company_name = Column(String(255), nullable=False,comment='公司名称')
    username = Column(String(255), unique=True, nullable=False,comment='用户名')
    password_hash = Column(String(255), nullable=False,comment='密码哈希值')
    phone_number = Column(String(20), nullable=False,comment='手机号码')
    accessToken = Column(String(255), nullable=True,comment='授权码')  # 分配的表名
    authorized_app_ids = Column(String(255), nullable=True,comment='授权应用ID')
    permissions = Column(Text, nullable=True,comment='权限管理')
    is_admin = Column(Integer, default=0, comment='是否为管理员')
    registration_date =  Column(DateTime, default=datetime.now(),comment='创建时间')
    last_login_time = Column(DateTime, nullable=True, comment='最后登录时间')  # 最后登录时间
    expiration_date = Column(DateTime, default=datetime.now(), comment='到期时间') # 到期时间
    status = Column(Integer, default=1, comment='状态')#账号启用状态，暂时还未使用
    remarks = Column(String(255), nullable=True,comment='备注')  # 备注
    inform = Column(Text, nullable=True,comment='通知')
    ip_address = Column(String(255), nullable=False,comment='ip地址')



class app_info(Base):
    """创建app_key表"""
    __tablename__ = 'app_info'
    id = Column(Integer, primary_key=True, autoincrement=True,comment='自增主键')
    app_id = Column(String(255), nullable=False,comment='app_id')
    app_name = Column(String(255), nullable=False,comment='app_name')
    app_key = Column(String(255), nullable=False,comment='app_key')
    app_secret = Column(String(255), nullable=False,comment='app_secret')
    app_description = Column(Text, nullable=True,comment='软件说明')
    create_time = Column(DateTime, default=datetime.now(),comment='创建时间')
    update_time = Column(DateTime, default=datetime.now(),comment='更新时间')
    remarks = Column(String(255), nullable=True,comment='备注')
    status = Column(Integer, default=1, comment='状态')
    version = Column(String(255), nullable=True, comment='版本')
    version_log = Column(Text, nullable=True, comment='版本日志')
    up_version_address = Column(String(255), nullable=True, comment='升级地址')


class Remaker_User_Login_Log(Base):
    """创建登录日志表"""
    __tablename__ = 'remaker_user_login_log'

    id = Column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
    user_id = Column(Integer, nullable=True, comment="用户ID")  # 外键，关联用户表
    username = Column(String(100), nullable=False, comment="用户名")
    company_name = Column(String(255), nullable=True,comment='公司名称')
    isp = Column(String(255), nullable=True, comment="运营商")
    ip_address = Column(String(50), nullable=False, comment="IP地址")
    prov = Column(String(255), nullable=True, comment="省份")
    city = Column(String(255), nullable=True, comment="城市")
    district = Column(String(255), nullable=True, comment="区县")
    device_info = Column(String(255), nullable=True, comment="设备信息（如操作系统、浏览器等）")
    login_time = Column(DateTime, default=datetime.now(), comment="登录时间")
    status = Column(String(255), nullable=False,  comment="登录状态")  # 记录登录是否成功
    failure_reason = Column(String(255), nullable=True, comment="登录失败原因")
    created_at = Column(DateTime, default=datetime.now(), comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now(), comment="最后修改时间")

    # user = relationship("jushuitan_Merchant", backref="login_logs", foreign_keys=[user_id])
    # def __repr__(self):
    #     return f"<UserLoginLog(id={self.id}, user_id={self.user_id}, username={self.username}, ip_address={self.ip_address}, login_time={self.login_time}, status={self.status})>"



