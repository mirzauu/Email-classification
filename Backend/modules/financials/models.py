"""Financials module models."""
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship
from core.database import Base

class Platform(Base):
    __tablename__ = "platforms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    website = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PaymentChannel(Base):
    __tablename__ = "payment_channels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    name = Column(String, nullable=False)
    platform_id = Column(UUID(as_uuid=True), ForeignKey("platforms.id"))
    external_ref = Column(String)
    extra_metadata = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ExternalAccount(Base):
    __tablename__ = "external_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    kind = Column(String, nullable=False)
    platform_id = Column(UUID(as_uuid=True), ForeignKey("platforms.id"))
    payment_channel_id = Column(UUID(as_uuid=True), ForeignKey("payment_channels.id"))
    external_handle = Column(String)
    display_name = Column(String)
    extra_metadata = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    platform_id = Column(UUID(as_uuid=True), ForeignKey("platforms.id"))
    invoice_number = Column(String)
    amount = Column(Numeric)
    currency = Column(String)
    issued_at = Column(DateTime(timezone=True))
    due_date = Column(DateTime(timezone=True))
    paid_at = Column(DateTime(timezone=True))
    status = Column(String)
    email_id = Column(Integer, ForeignKey("emails.id"))
    extra_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    email_id = Column(Integer, ForeignKey("emails.id"))
    direction = Column(String, nullable=False)
    kind = Column(String, nullable=False)
    amount = Column(Numeric, nullable=False)
    currency = Column(String, nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    platform_id = Column(UUID(as_uuid=True), ForeignKey("platforms.id"))
    payment_channel_id = Column(UUID(as_uuid=True), ForeignKey("payment_channels.id"))
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    source_account_id = Column(UUID(as_uuid=True), ForeignKey("external_accounts.id"))
    target_account_id = Column(UUID(as_uuid=True), ForeignKey("external_accounts.id"))
    provider = Column(String)
    provider_transaction_id = Column(String)
    reference_ids = Column(ARRAY(String))
    description = Column(Text)
    extra_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PaymentChain(Base):
    __tablename__ = "payment_chains"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    canonical_amount = Column(Numeric)
    canonical_currency = Column(String)
    canonical_client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    status = Column(String, nullable=False)
    confidence = Column(Numeric)
    pattern_hint = Column(String)
    extra_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated_at = Column(DateTime(timezone=True))

class PaymentChainItem(Base):
    __tablename__ = "payment_chain_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    chain_id = Column(UUID(as_uuid=True), ForeignKey("payment_chains.id"), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False)
    role = Column(String, nullable=False)
    sequence_index = Column(Integer, nullable=False)
    matched_at = Column(DateTime(timezone=True), server_default=func.now())
    confidence = Column(Numeric)
    extra_metadata = Column(JSONB)
