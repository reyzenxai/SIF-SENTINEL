from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL
from app.models.database import Base

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _migrate_additive_columns():
    """Base.metadata.create_all() only creates tables that don't exist yet —
    it never ALTERs an existing table. Since this prototype has no Alembic
    migration setup, this adds any new *nullable* columns (like
    source_system, sif_label, sif_confidence, life_saving_rules) to an
    already-existing SQLite dev database in place, so existing report data
    is never dropped or destroyed. This intentionally only ever ADDs
    columns — it never renames or removes anything."""
    if not DATABASE_URL.startswith("sqlite"):
        return  # Postgres deployments should use a real migration tool (Alembic)
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue  # brand new table — create_all() already handled it
            existing_cols = {c["name"] for c in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing_cols:
                    continue
                col_type = column.type.compile(engine.dialect)
                conn.execute(text(f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {col_type}'))


def init_db():
    Base.metadata.create_all(bind=engine)
    _migrate_additive_columns()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
