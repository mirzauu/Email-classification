"""
Central registry mapping all SQLAlchemy models for Alembic and metadata generation.
Importing this file ensures that `Base.metadata` contains all tables.
"""
from core.database import Base

# Import all models to register them with Base.metadata
from modules.auth.models import FastAPIUser, User, Account, Connection
from modules.emails.models import EmailAccount, Email, EmailEvent
from modules.financials.models import Platform, PaymentChannel, Client, ExternalAccount, Invoice, Transaction, PaymentChain, PaymentChainItem
from modules.ai.models import BackgroundTask, EmbeddingRecord

# Optionally, expose Base for easy import elsewhere
__all__ = ["Base"]
