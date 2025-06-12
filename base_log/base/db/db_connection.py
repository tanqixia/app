from sqlalchemy import and_ ,or_
from typing import List, Dict, Any
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
import traceback
try:
    from db.models import Base
except ImportError:
    from base.db.models import Base

db_config = {
    "host": "8.140.162.237",
    "port": 3307,
    "user": "yangyanxi",
    "password": "yangyanxi%4043...", 
    "database": "db_dev_11185",
    'charset': 'utf8mb4'
}
DATABASE_URI = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
# 创建数据库引擎，使用连接池管理数据库连接。
engine = create_engine(
    DATABASE_URI,
    poolclass=QueuePool,
    pool_size=500,
    max_overflow=500,
    pool_recycle=3600,
    pool_pre_ping=True   
)
SessionLocal = sessionmaker(bind=engine)
@contextmanager
def get_session():
    """上下文管理器，用于创建和管理数据库会话。"""
    session = SessionLocal()
    try:
        yield session
    except SQLAlchemyError as e:
        session.rollback()
        print(f"数据库操作失败: {e}")
        traceback.print_exc()
    finally:
        session.close()

def create_engine_with_pool():
    """
    创建数据库引擎，使用连接池管理数据库连接。

    返回:
        engine: SQLAlchemy的数据库引擎对象。
    """
    return create_engine(
        DATABASE_URI,
        poolclass=QueuePool,
        pool_size=500,
        max_overflow=500,
        pool_recycle=3600,
        pool_pre_ping=True
    )

# 创建会话工厂
SessionLocal = sessionmaker(bind=create_engine_with_pool())

def query_data_que_none(table_class, filters: Dict[str, Any] = None, selected_columns: List[str] = None) -> List[Dict]:
    """
    查询指定表的数据，并支持只查询和返回指定的列。

    参数:
        table_class: 表模型类，表示要查询数据的目标表。
        filters: 查询条件字典（可选），支持嵌套的 $or 和时间范围条件。
        selected_columns: 指定返回的列名列表（可选）。如果为 None，则返回所有列。

    返回:
        查询结果列表，包含符合条件的记录。如果数据为空，则返回包含指定列的字典列表，值为 0。
    """
    # print(f"传入的查询数据是 {filters}")
    with get_session() as session:
        if selected_columns:
            selected_columns_objs = [getattr(table_class, col) for col in selected_columns]
            query = session.query(*selected_columns_objs)
        else:
            query = session.query(table_class)

        def parse_conditions(filter_dict):
            """解析过滤条件，包括 $or 和嵌套逻辑"""
            conditions = []
            for key, value in filter_dict.items():
                if key == "$or" and isinstance(value, list):  # 处理 $or 条件
                    or_conditions = [and_(*parse_conditions(sub_filter)) for sub_filter in value]
                    conditions.append(or_(*or_conditions))  # 使用 or_ 将多个条件连接
                elif isinstance(value, dict):
                    # 处理时间范围条件
                    if "start_time" in value and "end_time" in value:
                        conditions.append(getattr(table_class, key).between(value["start_time"], value["end_time"]))

                    if "$ne" in value:  # 处理不等于条件
                        ne_value = value["$ne"]
                        if isinstance(ne_value, list):
                            conditions.append(getattr(table_class, key).notin_(ne_value))
                        else:
                            conditions.append(getattr(table_class, key) != ne_value)
                    elif "$in" in value:  # 处理 $in 条件
                        in_value = value["$in"]
                        # 如果 $in 值为空列表，则跳过该条件
                        if in_value:
                            conditions.append(getattr(table_class, key).in_(in_value))
                elif value not in [None, '', []]:  # 非空值
                    conditions.append(getattr(table_class, key) == value)
            return conditions

        if filters:
            filter_conditions = parse_conditions(filters)
            if filter_conditions:
                query = query.filter(and_(*filter_conditions))

        results = query.all()

        # 处理查询结果
        if not results:
            if selected_columns:
                return [{col: 0 for col in selected_columns}]
            return [{column.name: 0 for column in table_class.__table__.columns}]

        if selected_columns:
            result_dicts = [dict(zip(selected_columns, result)) for result in results]
        else:
            result_dicts = [item.__dict__ for item in results]

        return result_dicts

def create_tables():
    """
    创建所有在Base中定义的数据库表（如果尚不存在）。

    输出:
        控制台打印表创建的状态信息。
    """
    engine = create_engine_with_pool()
    try:
        Base.metadata.create_all(bind=engine)
        print(f"数据库表 已创建（如果尚不存在）")
    except SQLAlchemyError as e:
        print(f"数据库操作失败: {e}")
    finally:
        engine.dispose()  # 确保会话被关闭

def create_record(table_class, data: Dict[str, Any]) -> int:
    try:
        with get_session() as session:
            record = table_class(**data)
            session.add(record)
            session.commit()
            print("记录插入成功:", getattr(record, "id", None))
            return getattr(record, "id", -1)
    except SQLAlchemyError as e:
        print(f"插入失败: {str(e)}")
        return -1



def read_records(table_class, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """检查用户名是否存在"""
    records = []
    try:
        with get_session() as session:
            query = session.query(table_class)
            if filters:
                query = query.filter_by(**filters)
            records = [{col.name: getattr(record, col.name) for col in record.__table__.columns} for record in query.all()]
            print(f"读取到 {len(records)} 条记录")
    except SQLAlchemyError as e:
        print(f"读取失败: {str(e)}")
    return records

def update_record_with_query(table_class, data_before: Dict[str, Any], data_after: Dict[str, Any]) -> int:
    """
    更新记录：通过查询前的数据查找记录并更新为新的数据，该方法不会触发数据库层面before_update 和after_update等需要触发的事件
    使用 SQLAlchemy 的 `update()` 方法进行更新

    params:
        table_class: 表模型类
        data_before: Dict, 用于查询数据库的条件，通常为更新前的数据
        data_after: Dict, 需要更新的字段及其新值

    return:
        int: 更新成功返回更新的记录ID，失败返回-1
    """
    try:
        with get_session() as session:
            # 使用 filter_by 根据更新前的数据查找记录并进行更新
            result = session.query(table_class).filter_by(**data_before).update(data_after)
            session.commit()

            if result > 0:
                # 查询到记录并成功更新
                print(f"记录更新成功, 更新的记录ID: {data_before.get('id', '未知')}")
                return data_before.get('id', -1)  # 假设你通过 id 查询并更新
            else:
                print("未找到匹配的记录")
                return -1
    except SQLAlchemyError as e:
        print(f"更新失败: {str(e)}")
        return -1

def bulk_insert_data(table_class, data_list: List[Dict[str, Any]], batch_size: int = 1000) -> None:
    """
    批量插入数据到指定的表，支持分批插入。

    参数:
        table_class: 表模型类，表示要插入数据的目标表。
        data_list: 包含字典的二维列表，字典的键是列名，值是要插入的值。
        batch_size: 每次插入的批次大小，默认为500。

    输出:
        控制台打印插入操作的状态信息。如果出错，将打印具体的异常信息。
    """
    # print("开始批量插入数据...")
    if not data_list:
        return "数据为空"
    
    try:
        with get_session() as session:
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                session.bulk_insert_mappings(table_class, batch)
            session.commit()
            inserted_rows = len(data_list)
            res_str = f"批量插入成功,插入了：{inserted_rows}行数据"
            return int(inserted_rows)
    except Exception as e:
        return f"批量插入失败: {str(e)}"


if __name__ == "__main__":
    create_tables()


