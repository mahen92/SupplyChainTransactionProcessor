import traceback
import sys
import hashlib
import logging

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

class Constants(object):

  def hash(data):
      return hashlib.sha512(data.encode()).hexdigest()

  logging.basicConfig(filename='tp.log',level=logging.DEBUG)
  LOGGER = logging.getLogger(__name__)

# namespaces
  family_name = "pharmhedge"
  FAMILY_NAME = hash(family_name)[:6]

  TABLES = hash("tables")[:6]

  TRACKING = hash("tracking")[:6]
  TRACKING_TABLE = FAMILY_NAME + TRACKING

  MANUFACTURER_ENTRIES = hash("manufacturer-entries")[:6]
  MANUFACTURERS = hash("manufacturers")
  MANUFACTURERS_TABLE = FAMILY_NAME + TABLES + MANUFACTURERS[:58]

  DISTRIBUTER_ENTRIES = hash("distributer-entries")[:6]
  DISTRIBUTERS = hash("distributers")
  DISTRIBUTERS_TABLE = FAMILY_NAME + TABLES + DISTRIBUTERS[:58]


  PHARMACY_ENTRIES = hash("pharmacy-entries")[:6]
  PHARMACY = hash("pharmacys")
  PHARMACY_TABLE = FAMILY_NAME + TABLES + PHARMACY[:58]

