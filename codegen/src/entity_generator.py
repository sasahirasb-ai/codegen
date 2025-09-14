from __future__ import annotations

import os
from datetime import date, datetime, time
from enum import Enum
from pathlib import Path

from jinja2 import Template
from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Time
from sqlglot import Expression, parse
from sqlglot.expressions import ColumnDef

ENTITY_TEMPLATE = """
{%- if has_current_timestamp -%}
from datetime import datetime
{%- endif %}
from sqlalchemy import {{ sqlalchemy_imports | join(', ') }}
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class {{ table.name.capitalize() }}(DeclarativeBase):
    __tablename__ = "{{ table.name }}"
{% for column in table.columns %}
    {{ column.name }}: Mapped[{{ column.data_type.to_python_type().__qualname__ -}}
        {{ '| None' if column.nullable else '' }}] = mapped_column( \
        {{- column.data_type.to_sqlalchemy().__name__ }}
        {%- if column.length %}, length={{ column.length -}}{% endif -%}
        , nullable={{ 'True' if column.nullable else 'False' -}}
        {%- if column.primary_key %}, primary_key=True{% endif -%}
        {%- if column.unique %}, unique=True{% endif -%}
        {%- if column.default -%}
            {%- if column.default == "CURRENT_TIMESTAMP()" -%}
            , default=datetime.utcnow
            {%- else -%}
            , default={{ column.default -}}
            {%- endif -%}
        {%- endif -%}
    )
{%- endfor %}

"""


class DataType(Enum):
    INT = "int"
    STRING = "string"
    BOOL = "bool"
    FLOAT = "float"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"

    def __eq__(self, other):
        if isinstance(other, DataType):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        else:
            return False

    @staticmethod
    def from_str(value: str) -> DataType:
        return DataType(value)

    @staticmethod
    def from_columndef(type_str: str):
        if type_str in ["INT", "INTEGER", "SERIAL", "BIGINT"]:
            return DataType.INT
        elif type_str in ["VARCHAR", "CHAR", "TEXT"]:
            return DataType.STRING
        elif type_str in ["BOOLEAN", "BOOL", "TINYINT"]:
            return DataType.BOOL
        elif type_str in ["FLOAT", "DOUBLE", "REAL", "NUMERIC", "DECIMAL"]:
            return DataType.FLOAT
        elif type_str in ["DATE"]:
            return DataType.DATE
        elif type_str in ["DATETIME", "TIMESTAMP"]:
            return DataType.DATETIME
        elif type_str in ["TIME"]:
            return DataType.TIME
        else:
            raise ValueError(f"Unsupported data type: {type_str}")

    def to_sqlalchemy(self):
        """
        SQLAlchemy の Column 型を返す
        """
        if self is DataType.INT:
            return Integer
        elif self is DataType.STRING:
            return String
        elif self is DataType.BOOL:
            return Boolean
        elif self is DataType.FLOAT:
            return Float
        elif self is DataType.DATE:
            return Date
        elif self is DataType.DATETIME:
            return DateTime
        elif self is DataType.TIME:
            return Time
        else:
            raise ValueError(f"Unsupported data type: {self}")

    def to_python_type(self):
        """
        Python の型を返す
        """
        if self is DataType.INT:
            return int
        elif self is DataType.STRING:
            return str
        elif self is DataType.BOOL:
            return bool
        elif self is DataType.FLOAT:
            return float
        elif self is DataType.DATE:
            return date
        elif self is DataType.DATETIME:
            return datetime
        elif self is DataType.TIME:
            return time
        else:
            raise ValueError(f"Unsupported data type: {self}")


class Column:
    name: str
    data_type: DataType
    length: int | None
    nullable: bool
    primary_key: bool
    unique: bool
    default: str | None

    def __init__(
        self,
        name: str,
        data_type: DataType,
        length: int | None,
        nullable: bool = True,
        primary_key: bool = False,
        unique: bool = False,
        default: str | None = None,
    ):
        self.name = name
        self.data_type = data_type
        self.length = length
        self.nullable = nullable
        self.primary_key = primary_key
        self.unique = unique
        self.default = default

    def __repr__(self):
        return f"Column(name={self.name}, data_type={self.data_type}, length={self.length}, nullable={self.nullable}, primary_key={self.primary_key}, unique={self.unique}, default={self.default})"

    def __eq__(self, other):
        if not isinstance(other, Column):
            return super().__eq__(other)

        return all(
            (
                self.name == other.name,
                self.data_type.value == other.data_type.value,
                self.length == other.length,
                self.nullable == other.nullable,
                self.primary_key == other.primary_key,
                self.unique == other.unique,
                self.default == other.default,
            )
        )


class Table:
    name: str
    columns: list[Column]

    def __init__(self, name: str, columns: list[Column]):
        self.name = name
        self.columns = columns

    def __repr__(self):
        return f"Table(name={self.name}, columns={self.columns})"


class EntityGenerator:
    db_type: str
    output_dir: str
    asts: list[Expression]

    def __init__(self, file_path: str, output_dir: str, db_type: str):
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        self.db_type = db_type

        with open(file_path, "r", encoding="utf-8") as f:
            self.asts = [ast for ast in parse(f.read(), read=db_type) if ast]

    def _get_columns(self, schema: Expression) -> list[Column]:
        """
        カラム一覧取得
        """
        if not schema.key == "schema":
            ValueError("schema is not found")

        columndefs: list[ColumnDef] = schema.expressions

        columns: list[Column] = []
        for columndef in columndefs:
            # 不備があるカラム定義はスキップ
            if columndef.key != "columndef" or not columndef.kind:
                continue

            column_name = columndef.this.name
            column_type = columndef.kind.this.value
            column_type_lengths = [exp.this.this for exp in columndef.kind.expressions]
            constraints = {c.kind.key: c.kind.this for c in columndef.constraints}

            is_primary_key = "primarykeycolumnconstraint" in constraints
            is_unique = "uniquecolumnconstraint" in constraints or is_primary_key
            is_not_null = "notnullcolumnconstraint" in constraints or is_unique

            column = Column(
                name=column_name,
                data_type=DataType.from_columndef(column_type),
                length=int(column_type_lengths[0]) if column_type_lengths else None,
                nullable=not is_not_null,
                primary_key=is_primary_key,
                unique=is_unique,
                default=(
                    str(constraints["defaultcolumnconstraint"])
                    if "defaultcolumnconstraint" in constraints
                    else None
                ),
            )
            columns.append(column)

        return columns

    def _get_tables(self) -> list[Table]:
        """
        テーブル一覧取得
        """
        tables: list[Table] = []
        for ast in self.asts:
            if not ast.this.key == "schema":
                continue

            table_name = ast.this.this.this.this
            columns = self._get_columns(ast.this)
            tables.append(
                Table(
                    name=table_name,
                    columns=columns,
                )
            )

        return tables

    def _generate_entity_file(self, tables: list[Table]):
        """
        Entityファイル生成
        """
        template: Template = Template(source=ENTITY_TEMPLATE)

        for table in tables:
            has_current_timestamp = any(
                col.default == "CURRENT_TIMESTAMP()" for col in table.columns
            )

            sqlalchemy_imports = sorted(
                {col.data_type.to_sqlalchemy().__name__ for col in table.columns}
            )

            rendered = template.render(
                table=table,
                sqlalchemy_imports=sqlalchemy_imports,
                has_current_timestamp=has_current_timestamp,
            )

            out_path = Path(self.output_dir, f"{table.name}.py")
            out_path.write_text(rendered, encoding="utf-8")
