import datetime
from sqlalchemy import Integer, String, Numeric, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.dialects.postgresql import JSON


Base = declarative_base()


class Trade(Base):
    __tablename__ = "trades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    counterparty_id: Mapped[int] = mapped_column(Integer, ForeignKey("counterparty.id"))
    settlement_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    side: Mapped[str] = mapped_column(String, nullable=False)
    currency_pair: Mapped[str] = mapped_column(String, nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    quote_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    notional: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    status: Mapped[enumerate] = mapped_column(Enum, nullable=False)
    
class Counterparty(Base):
    __tablename__ = "counterparty"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String,nullable=False)
    legal_entity: Mapped[str] = mapped_column(String,nullable=False)
    margin_limit: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    #Possible currency field
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True),nullable=True)
    description: Mapped[str]

class Break(Base):
    __tablename__ = "break"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reconciliation_run_id: [int] = mapped_column(Integer, ForeignKey("reconciliation_run.id"))
    trade_id: Mapped[str] = mapped_column(Integer, ForeignKey("trade.id"))
    description: Mapped[JSON] = mapped_column(JSON)

    break_type: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[enumerate] = mapped_column(Enum, nullable=False)
    reconciled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reconciled_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class ReconciliationRun(Base):
    __tablename = "reconciliation_run"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trade_id = Mapped[int] = mapped_column(Integer, ForeignKey("trade.id"))
    run_timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    #Possible feed_source(s) field
    status: Mapped[enumerate] = mapped_column(Enum, nullable=False)

class MarginBreaches(Base):
    __tablename__ = "margin breaches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reconciliation_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("reconciliation_run.id"))
    counterparty_id = Mapped[int] = mapped_column(Integer, ForeignKey("counterparty.id"))
    detected_at = Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    exposure_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    threshold: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    breach_type: Mapped[enumerate] = mapped_column(Enum,nullable=False) # Possibly changed to breach_level(enum)
    
