from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .faq import FAQ
from .pdf_document import PDFDocument
from .visit_log import VisitLog
from .admin_action_log import AdminActionLog
