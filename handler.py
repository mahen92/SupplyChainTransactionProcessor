import traceback
import sys
import hashlib
import logging

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor
from constants import Constants
from state import PharmaState

DEFAULT_URL = "tcp://127.0.0.1:4004"

def hash(data):
    return hashlib.sha512(data.encode()).hexdigest()

logging.basicConfig(filename='tp.log',level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

# namespaces
family_name = Constants.family_name
FAMILY_NAME = hash(family_name)[:6]

TABLES = Constants.TABLES;

TRACKING = Constants.TRACKING
TRACKING_TABLE = FAMILY_NAME + TRACKING

MANUFACTURER_ENTRIES = Constants.MANUFACTURER_ENTRIES
MANUFACTURERS = Constants.MANUFACTURERS
MANUFACTURERS_TABLE = FAMILY_NAME + TABLES + MANUFACTURERS[:58]

DISTRIBUTER_ENTRIES = Constants.DISTRIBUTER_ENTRIES
DISTRIBUTERS = Constants.DISTRIBUTERS
DISTRIBUTERS_TABLE = FAMILY_NAME + TABLES + DISTRIBUTERS[:58]


PHARMACY_ENTRIES = Constants.PHARMACY_ENTRIES
PHARMACY = Constants.PHARMACY
PHARMACY_TABLE = FAMILY_NAME + TABLES + PHARMACY[:58]



class PharmaTransactionHandler(TransactionHandler):
    '''
    Transaction Processor class for the pharma family
    '''
    def __init__(self, namespace_prefix):
        '''Initialize the transaction handler class.
        '''
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        '''Return Transaction Family name string.'''
        return family_name

    @property
    def family_versions(self):
        '''Return Transaction Family version string.'''
        return ['1.0']

    @property
    def namespaces(self):
        '''Return Transaction Family namespace 6-character prefix.'''
        return [self._namespace_prefix]

    # Get the payload and extract the pharma-specific information.
    # It has already been converted from Base64, but needs deserializing.
    # It was serialized with CSV: action, value
    @classmethod
    def _decode_data(self, data):
        return data.decode().split(',')

    # returns a csv string
    @classmethod
    def _encode_data(self, data):
        return ','.join(data).encode()
    
    def _unpack_transaction(self, transaction):
        header = transaction.header
        payload_list = self._decode_data(transaction.payload)
        print("before unpack return")
        return payload_list

    def apply(self, transaction, context):
        '''This implements the apply function for the TransactionHandler class.
        '''
        LOGGER.info ('starting apply function')
        print('apply')
        try:
            print('after try')
            payload_list = self._unpack_transaction(transaction)
            LOGGER.info ('payload: {}'.format(payload_list))
            action = payload_list[0]
            action=action[1:]
            try:
                if "addManufacturer" in action:
                    print("Manufacturer Addition")
                    manufacturerName = payload_list[1]
                    print("name:"+ manufacturerName)
                    PharmaState._addManufacturer(context, manufacturerName)
                elif "addDistributor" in action :
                    distributerName = payload_list[1]
                    PharmaState._addDistributer(context, distributerName)
                elif "addPharmacy" in action :
                    pharmacyName = payload_list[1]
                    PharmaState._addPharmacy(context, pharmacyName)
                #l = [manufacturerName, medicineName, batchID, manufactureDate,expiryDate]
                elif "produce" in action:
                    [manufacturerName, medicineName, batchID, manufactureDate, expiryDate] = payload_list[1:]
                    # manufacturerName = payload_list[1]
                    # medicineName = payload_list[2]
                    # batchid = pa
                    # medicineDetails = payload_list[3:7]
                    PharmaState._manufacture(context, manufacturerName, medicineName, batchID, manufactureDate, expiryDate)

                elif action == "giveTo":
                    manufacturerName = payload_list[1]
                    distributerName = payload_list[2]
                    PharmaState._giveTo(context, manufacturerName, distributerName, medicineName)
                    action = payload_list[0]

                elif "giveToDistributer" in action:
                    print("Give to Distributor")
                    manufacturerName = payload_list[1]
                    distributerName = payload_list[2]
                    batchid = payload_list[3]
                    date = payload_list[4]
                    # medicineDetails = payload_list[3:7]
                    PharmaState._giveToDistributer(context, manufacturerName, distributerName, batchid, date)

                        # l = [distributer, pharmacy, batchID, date]
                elif action == "giveToPharmacy":
                    distributerName = payload_list[1]
                    pharmacyName = payload_list[2]
                    batchID = payload_list[3]
                    date = payload_list[4]
                    PharmaState._giveToPharmacy(context, distributerName, pharmacyName,batchID, date)
                    action = payload_list[0]

                # l = [manufacturerName, distributer, batchID, date, action]
                elif "getFromManufacturer" in action:
                    print("Get From Manufacturer")
                    manufacturerName = payload_list[1]
                    distributerName = payload_list[2]
                    batchID = payload_list[3]
                    date = payload_list[4]
                    action = payload_list[5]
                    PharmaState._getFromManufacturer(context, manufacturerName, distributerName, batchID, date, action)

                        # l = [distributer, pharmacy, batchID, date, action]
                elif action == "getFromDistributer":
                    ditributerName = payload_list[1]
                    pharmacyName = payload_list[2]
                    batchID = payload_list[3]
                    date = payload_list[4]
                    action = payload_list[5]
                    PharmaState._getFromDistributer(context, ditributerName, pharmacyName, batchID, date, action)
                else:
                    LOGGER.debug("Unhandled action: " + action)
                    print("Unhandled action: "+ action)
            except IndexError as i:
                LOGGER.debug ('IndexError: {}'.format(i))
                raise Exception()
        except Exception as e:
            raise InvalidTransaction("Error: {}".format(e))

   

