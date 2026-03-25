#!/usr/bin/env python3
"""
清理脚本：将数据库中所有字符串 "NULL" 替换为真正的 NULL

使用方法：
    python fix_null_values.py [--dry-run]

选项：
    --dry-run    只显示会被更新的记录，不实际执行更新
"""

import asyncio
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

import aiomysql
from dotenv import load_dotenv

# 加载 .env 文件（从 console/.env）
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ 已加载环境变量: {env_path}")
else:
    print(f"⚠️  未找到 .env 文件: {env_path}")


async def get_connection():
    """创建数据库连接"""
    return await aiomysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME", "ingenuity_lab"),
        charset="utf8mb4",
    )


async def get_text_columns(conn, table_name):
    """获取表中所有文本类型的列名"""
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(
            """
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
              AND TABLE_NAME = %s
              AND DATA_TYPE IN ('varchar', 'text', 'longtext', 'mediumtext', 'char')
            ORDER BY ORDINAL_POSITION
            """,
            (os.getenv("DB_NAME", "ingenuity_lab"), table_name),
        )
        return await cursor.fetchall()


async def get_all_tables(conn):
    """获取数据库中所有表名"""
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(
            """
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = %s
              AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
            """,
            (os.getenv("DB_NAME", "ingenuity_lab"),),
        )
        return [row["TABLE_NAME"] for row in await cursor.fetchall()]


async def find_null_string_records(conn, table_name, column_name):
    """查找包含字符串 "NULL" 的记录"""
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(
            f"""
            SELECT *
            FROM `{table_name}`
            WHERE `{column_name}` = 'NULL'
            LIMIT 1000
            """
        )
        return await cursor.fetchall()


async def update_null_string_to_null(conn, table_name, column_name, dry_run=False):
    """将字符串 "NULL" 更新为真正的 NULL"""
    # 先查找记录
    records = await find_null_string_records(conn, table_name, column_name)

    if not records:
        return 0

    print(f"\n  发现 {len(records)} 条记录在 '{column_name}' 列包含 'NULL' 字符串")

    # 显示前3条记录作为示例
    for i, record in enumerate(records[:3]):
        pk = record.get("id") or record.get("ID") or list(record.values())[0]
        print(f"    [{i+1}] ID: {pk}, 当前值: '{record[column_name]}'")

    if len(records) > 3:
        print(f"    ... 还有 {len(records) - 3} 条记录")

    if dry_run:
        print(f"    [DRY RUN] 将会把 {len(records)} 条记录的 '{column_name}' 从 'NULL' 更新为 NULL")
        return len(records)

    # 执行更新
    async with conn.cursor() as cursor:
        await cursor.execute(
            f"""
            UPDATE `{table_name}`
            SET `{column_name}` = NULL
            WHERE `{column_name}` = 'NULL'
            """
        )
        affected = cursor.rowcount
        await conn.commit()
        print(f"    ✅ 已更新 {affected} 条记录")
        return affected


async def main(dry_run=False):
    """主函数"""
    print("=" * 70)
    print("🔧 清理数据库中的字符串 'NULL'")
    print("=" * 70)
    print(f"数据库: {os.getenv('DB_NAME', 'ingenuity_lab')}")
    print(f"模式: {'DRY RUN (仅预览)' if dry_run else '实际更新'}")
    print("=" * 70)

    conn = await get_connection()

    try:
        # 获取所有表
        tables = await get_all_tables(conn)
        print(f"\n📊 找到 {len(tables)} 个表")

        total_updated = 0
        total_found = 0

        for table_name in tables:
            print(f"\n🔍 检查表: {table_name}")

            # 获取所有文本列
            columns = await get_text_columns(conn, table_name)

            if not columns:
                print("  没有文本列，跳过")
                continue

            print(f"  检查 {len(columns)} 个文本列...")

            for col in columns:
                col_name = col["COLUMN_NAME"]
                updated = await update_null_string_to_null(
                    conn, table_name, col_name, dry_run
                )
                total_found += updated

        print("\n" + "=" * 70)
        if dry_run:
            print(f"✨ DRY RUN 完成！找到 {total_found} 条需要更新的记录")
            print("   移除 --dry-run 参数以执行实际更新")
        else:
            print(f"✨ 清理完成！共更新 {total_found} 条记录")
        print("=" * 70)

    finally:
        conn.close()


if __name__ == "__main__":
    parser = ArgumentParser(description="清理数据库中的字符串 'NULL'")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示会被更新的记录，不实际执行更新",
    )
    args = parser.parse_args()

    # 检查必要的环境变量
    if not os.getenv("DB_PASSWORD"):
        print("❌ 错误: 必须设置环境变量 DB_PASSWORD")
        sys.exit(1)

    asyncio.run(main(dry_run=args.dry_run))
