import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Integer, String, Numeric, Boolean, Enum as SAEnum, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, declarative_base, mapped_column
from sqlalchemy.dialects.postgresql import JSON

class Base:
    __allow_unmapped__ = True

Base = declarative_base(cls=Base)


class TradeSide(PyEnum):
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus(PyEnum):
    PENDING = "PENDING"
    SETTLED = "SETTLED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class BreakType(PyEnum):
    MISSING_TRADE = "MISSING_TRADE"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    CURRENCY_MISMATCH = "CURRENCY_MISMATCH"
    RATE_MISMATCH = "RATE_MISMATCH"


class BreakSeverity(PyEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RunStatus(PyEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class BreachType(PyEnum):
    WARNING = "WARNING"
    BREACH = "BREACH"
    CRITICAL = "CRITICAL"


class Trade(Base):
    __tablename__ = "trades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    counterparty_id: Mapped[int] = mapped_column(Integer, ForeignKey("counterparty.id"))
    settlement_date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    side: Mapped[TradeSide] = mapped_column(SAEnum(TradeSide, name="trade_side"), nullable=False)
    currency_pair: Mapped[str] = mapped_column(String, nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=True)
    quote_currency: Mapped[str] = mapped_column(String(3), nullable=True)
    notional: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    status: Mapped[TradeStatus] = mapped_column(SAEnum(TradeStatus, name="trade_status"), nullable=False)
    
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

    break_type: Mapped[BreakType] = mapped_column(SAEnum(BreakType, name="break_type"), nullable=False)
    severity: Mapped[BreakSeverity] = mapped_column(SAEnum(BreakSeverity, name="break_severity"), nullable=False)
    reconciled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reconciled_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class ReconciliationRun(Base):
    __tablename = "reconciliation_run"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trade_id = Mapped[int] = mapped_column(Integer, ForeignKey("trade.id"))
    run_timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    #Possible feed_source(s) field
    status: Mapped[RunStatus] = mapped_column(SAEnum(RunStatus, name="run_status"), nullable=False)

class MarginBreaches(Base):
    __tablename__ = "margin breaches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reconciliation_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("reconciliation_run.id"))
    counterparty_id = Mapped[int] = mapped_column(Integer, ForeignKey("counterparty.id"))
    detected_at = Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    exposure_amount: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    threshold: Mapped[float] = mapped_column(Numeric(18, 4), nullable=False)
    breach_type: Mapped[BreachType] = mapped_column(SAEnum(BreachType, name="breach_type"), nullable=False)

class Rates(Base):
    __tablename__ = "rates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    target_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(18, 8), nullable=False)
    fetch_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    fetch_timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.datetime.utcnow,
    )
    source: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
