"""${message}"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
${upgrades if upgrades else ""}
