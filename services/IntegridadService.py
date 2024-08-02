import pandas as pd
from sqlalchemy import text

class IntegridadReferencialService:
    def __init__(self, engine):
        self.engine = engine

    def check_foreign_keys_without_index(self):
        query = text("""
        SELECT
            OBJECT_NAME(f.parent_object_id) AS TableName,
            COL_NAME(fc.parent_object_id, fc.parent_column_id) AS ColumnName
        FROM
            sys.foreign_keys AS f
        INNER JOIN
            sys.foreign_key_columns AS fc
            ON f.object_id = fc.constraint_object_id
        LEFT JOIN
            sys.index_columns AS ic
            ON ic.object_id = fc.parent_object_id
            AND ic.column_id = fc.parent_column_id
        WHERE
            ic.object_id IS NULL;
        """)
        return pd.read_sql(query, self.engine)

    def check_orphaned_records(self):
        query = text("""
        DECLARE @sql NVARCHAR(MAX) = N'';
        SELECT @sql += N'
        SELECT ''' + OBJECT_NAME(parent_object_id) + ''' AS ChildTable,
               ''' + OBJECT_NAME(referenced_object_id) + ''' AS ParentTable,
               ''' + COL_NAME(parent_object_id, parent_column_id) + ''' AS ChildColumn,
               ''' + COL_NAME(referenced_object_id, referenced_column_id) + ''' AS ParentColumn,
               COUNT(*) AS OrphanCount
        FROM ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id)) + '.' + QUOTENAME(OBJECT_NAME(parent_object_id)) + ' c
        LEFT JOIN ' + QUOTENAME(OBJECT_SCHEMA_NAME(referenced_object_id)) + '.' + QUOTENAME(OBJECT_NAME(referenced_object_id)) + ' p
        ON c.' + QUOTENAME(COL_NAME(parent_object_id, parent_column_id)) + ' = p.' + QUOTENAME(COL_NAME(referenced_object_id, referenced_column_id)) + '
        WHERE p.' + QUOTENAME(COL_NAME(referenced_object_id, referenced_column_id)) + ' IS NULL
        AND c.' + QUOTENAME(COL_NAME(parent_object_id, parent_column_id)) + ' IS NOT NULL
        GROUP BY c.' + QUOTENAME(COL_NAME(parent_object_id, parent_column_id)) + '
        HAVING COUNT(*) > 0
        UNION ALL
        '
        FROM sys.foreign_key_columns;
        SET @sql = LEFT(@sql, LEN(@sql) - 11) + ';';
        EXEC sp_executesql @sql;
        """)
        return pd.read_sql(query, self.engine)

    def check_duplicate_primary_keys(self):
        query = text("""
        SELECT 'Duplicate primary keys found in ' +
               QUOTENAME(OBJECT_SCHEMA_NAME(i.object_id)) + '.' +
               QUOTENAME(OBJECT_NAME(i.object_id)) AS Issue,
               COUNT(*) AS DuplicateCount
        FROM sys.indexes i
        INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        CROSS APPLY (
            SELECT COUNT(*) AS KeyCount
            FROM (
                SELECT DISTINCT c.name
                FROM sys.index_columns ic2
                INNER JOIN sys.columns c ON ic2.object_id = c.object_id AND ic2.column_id = c.column_id
                WHERE ic2.object_id = i.object_id AND ic2.index_id = i.index_id
            ) t
        ) ca
        WHERE i.is_primary_key = 1
        GROUP BY i.object_id, ca.KeyCount
        HAVING COUNT(*) > ca.KeyCount;
        """)
        return pd.read_sql(query, self.engine)

    def check_data_type_mismatch(self):
        query = text("""
        SELECT 
            fk.name AS ForeignKeyName,
            OBJECT_NAME(fk.parent_object_id) AS TableName,
            c1.name AS ColumnName,
            t1.name AS ColumnDataType,
            OBJECT_NAME(fk.referenced_object_id) AS ReferencedTableName,
            c2.name AS ReferencedColumnName,
            t2.name AS ReferencedColumnDataType
        FROM 
            sys.foreign_keys fk
        INNER JOIN 
            sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        INNER JOIN 
            sys.columns c1 ON fkc.parent_object_id = c1.object_id AND fkc.parent_column_id = c1.column_id
        INNER JOIN 
            sys.columns c2 ON fkc.referenced_object_id = c2.object_id AND fkc.referenced_column_id = c2.column_id
        INNER JOIN 
            sys.types t1 ON c1.user_type_id = t1.user_type_id
        INNER JOIN 
            sys.types t2 ON c2.user_type_id = t2.user_type_id
        WHERE 
            t1.name != t2.name OR c1.max_length != c2.max_length;
        """)
        return pd.read_sql(query, self.engine)

    def check_nullability_mismatch(self):
        query = text("""
        SELECT 
            fk.name AS ForeignKeyName,
            OBJECT_NAME(fk.parent_object_id) AS TableName,
            c1.name AS ColumnName,
            c1.is_nullable AS ColumnNullable,
            OBJECT_NAME(fk.referenced_object_id) AS ReferencedTableName,
            c2.name AS ReferencedColumnName,
            c2.is_nullable AS ReferencedColumnNullable
        FROM 
            sys.foreign_keys fk
        INNER JOIN 
            sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
        INNER JOIN 
            sys.columns c1 ON fkc.parent_object_id = c1.object_id AND fkc.parent_column_id = c1.column_id
        INNER JOIN 
            sys.columns c2 ON fkc.referenced_object_id = c2.object_id AND fkc.referenced_column_id = c2.column_id
        WHERE 
            c1.is_nullable != c2.is_nullable;
        """)
        return pd.read_sql(query, self.engine)

    def run_all_checks(self):
        checks = {
            "foreign_keys_without_index": self.check_foreign_keys_without_index,
            "orphaned_records": self.check_orphaned_records,
            "duplicate_primary_keys": self.check_duplicate_primary_keys,
            "data_type_mismatch": self.check_data_type_mismatch,
            "nullability_mismatch": self.check_nullability_mismatch
        }

        results = {}
        for check_name, check_function in checks.items():
            try:
                df = check_function()
                if not df.empty:
                    results[check_name] = df.to_dict(orient='records')
                    results[f"{check_name}_explanation"] = self.get_explanation(check_name, df)
            except Exception as e:
                results[check_name] = f"Error en {check_name}: {str(e)}"

        return results

    def get_explanation(self, check_name, df):
        if check_name == "foreign_keys_without_index":
            return f"Se encontraron {len(df)} claves foráneas sin índice. Esto puede afectar el rendimiento de las consultas."
        elif check_name == "orphaned_records":
            return f"Se encontraron {len(df)} casos de registros huérfanos. Estos son registros en la tabla hija que no tienen correspondencia en la tabla padre."
        elif check_name == "duplicate_primary_keys":
            return f"Se encontraron {len(df)} casos de claves primarias duplicadas. Esto viola la unicidad de las claves primarias."
        elif check_name == "data_type_mismatch":
            return f"Se encontraron {len(df)} casos de incompatibilidad de tipos de datos entre claves foráneas y primarias."
        elif check_name == "nullability_mismatch":
            return f"Se encontraron {len(df)} casos de incompatibilidad en la nulabilidad entre claves foráneas y primarias."
        return ""
