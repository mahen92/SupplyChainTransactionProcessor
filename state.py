import traceback
import sys
import hashlib
import logging

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor
from constants import Constants



def hash(data):
    return hashlib.sha512(data.encode()).hexdigest()

logging.basicConfig(filename='tp.log',level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


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


def getBatchAddress(batchID):
    return TRACKING_TABLE + hash(batchID)[:58]

def getManufacturerAddress(manufacturerName):
    return FAMILY_NAME + MANUFACTURER_ENTRIES + hash(manufacturerName)[:58]

def getDistributerAddress(distributerName, qualifier = "has"):
    distributerName = str(distributerName)
    return FAMILY_NAME + DISTRIBUTER_ENTRIES + hash(distributerName)[:57] + hash(qualifier)[0]

def getPharmacyAddress(pharmacyname, qualifier = "has"):
    return FAMILY_NAME + PHARMACY_ENTRIES + hash(pharmacyname)[:57] + hash(qualifier)[0]



class PharmaState():
    @classmethod
    def _addDistributer(self, context, distributerName):
        try:
            LOGGER.info("entering addDist")
            distributers = self._readData(context, DISTRIBUTERS_TABLE)
            LOGGER.info ('Distributers: {}'.format(distributers))
            if distributers:
                if distributerName not in distributers:
                    distributers.append(distributerName)
                    medicines = []
                    addresses  = context.set_state({
                                    getDistributerAddress(distributerName): self._encode_data(medicines),
                                    getDistributerAddress(distributerName, 'request'): self._encode_data(medicines)
                                })
                else:
                    raise Exception('no manufacturer: ' + distributerName)
            else:
                distributers = [distributerName]

            addresses  = context.set_state({
                            DISTRIBUTERS_TABLE: self._encode_data(distributers)
                        })
        except Exception as e:
            print('exception: {}'.format(e))
            raise InvalidTransaction("State Error")

    @classmethod
    def _addManufacturer(self, context, manufacturerName):
        try:
            print("entering add manufacture")
            manufacturers = self._readData(context, MANUFACTURERS_TABLE)
            print('Manufacturers: {}'.format(manufacturers))
            if manufacturers:
                if manufacturerName not in manufacturers:
                    print("in if")
                    manufacturers.append(manufacturerName)
                    medicines = []
                    print("after medray")
                    addresses  = context.set_state({
                                    getManufacturerAddress(manufacturerName): self._encode_data(medicines)
                                })
                   
                else:
                    raise Exception('no manufacturer: ' + manufacturerName)
            else:
                manufacturers = [manufacturerName]

            addresses  = context.set_state({
                            MANUFACTURERS_TABLE: self._encode_data(manufacturers)
                        })
        except Exception as e:
            print('excecption: {}'.format(e))
            raise InvalidTransaction("State Error")

    @classmethod
    def _addPharmacy(self, context, pharmacyName):
        try:
            #LOGGER.info("entering add pharmacy")
            pharmacy = self._readData(context, PHARMACY_TABLE)
            #LOGGER.info ('Manufacturers: {}'.format(pharmacy))
            if pharmacy:
                if pharmacyName not in pharmacy:
                    pharmacy.append(pharmacyName)
                    medicines = []
                    addresses  = context.set_state({
                                    getPharmacyAddress(pharmacyName): self._encode_data(medicines),
                                    getPharmacyAddress(pharmacyName, 'request'):                                                                                         
                                    self._encode_data(medicines)
                                })
                else:
                    raise Exception('no pharmacy: ' + pharmacyName)
            else:
                pharmacy = [pharmacyName]

            addresses  = context.set_state({
                            PHARMACY_TABLE: self._encode_data(pharmacy)
                        })
        except Exception as e:
            logging.debug ('excecption: {}'.format(e))
            raise InvalidTransaction("State Error")


        #l = [manufacturerName, medicineName, batchID, manufactureDate, expiryDate, owner]
    @classmethod
    def _manufacture(self, context, manufacturerName, medicineName, batchID, manufactureDate, expiryDate):
        manufacturerAddress = getManufacturerAddress(manufacturerName)
        medicine_string = ', '.join([manufacturerName, '+' ,medicineName, batchID, manufactureDate, expiryDate])
        batchAddress = getBatchAddress(batchID)
        try:
            LOGGER.info("entering manufacture")
            manufacturers = self._readData(context, MANUFACTURERS_TABLE)
            LOGGER.info ('Manufacturers: {}'.format(manufacturers))
            if manufacturers:
                if manufacturerName in manufacturers:
                    medicines = self._readData(context, manufacturerAddress)
                    medicines.append(batchID)
                    tracking = [medicine_string]

                    addresses = context.set_state({
                        manufacturerAddress: self._encode_data(medicines),
                        batchAddress: self._encode_data(tracking)
                    })
                else:
                    raise Exception('no manufacturer: ' + manufacturerName)
            else:
                raise Exception('no manufacturers')
        except Exception as e:
            logging.debug ('excecption: {}'.format(e))
            raise InvalidTransaction("State Error")

    #l = [manufacturerName, distributer, batchID, date]
    @classmethod
    def _giveToDistributer(self, context, manufacturerName, distributerName, batchid, date):
        print("entering giveToDistributers")
        manufacturerAddress = getManufacturerAddress(manufacturerName)
        distributerAddress = getDistributerAddress(distributerName, "request")
        try:
            manufacturers = self._readData(context, MANUFACTURERS_TABLE)
            distributers = self._readData(context, DISTRIBUTERS_TABLE)
            print('manufacturers: {}'.format(manufacturers))
            print('distributers: {}'.format(distributers))
            if manufacturerName in manufacturers and distributerName in distributers:
                manufacturedMedicines = self._readData(context, manufacturerAddress)
                if batchid in manufacturedMedicines:
                    manufacturedMedicines.remove(batchid)
                    LOGGER.info (batchid + 'removed')
                    distributerMedicine = self._readData(context, distributerAddress)
                    distributerMedicine.append(batchid)
                    addresses = context.set_state({
                        manufacturerAddress: self._encode_data(manufacturedMedicines),
                        distributerAddress: self._encode_data(distributerMedicine)
                    })
                    print('address written')
                else:
                    raise Exception("batchid not in medicineList")
            else:
                raise Exception("manu or pharma not in lists")
            LOGGER.info('{} gave {} to {}.request'.format(manufacturerName, batchid, distributerName))
        except TypeError as t:
            logging.debug('TypeError in _giveTo: {}'.format(t))
            raise InvalidTransaction('Type error')
        except InvalidTransaction as e:
            logging.debug ('excecption: {}'.format(e))
            raise e
        except Exception as e:
            logging.debug('exception: {}'.format(e))
            raise InvalidTransaction('excecption: {}'.format(e))

    # l = [manufacturerName, distributer, batchID, date, owner, action]
    @classmethod
    def _getFromManufacturer(self, context, manufacturerName, distributerName, batchID, date, action):
        print("entering getFromManufacturer")
        action = str(action)
        manufacturerAddress = getManufacturerAddress(manufacturerName)
        distributerRequestAddress = getDistributerAddress(distributerName,"request")
        distributerHasAddress = getDistributerAddress(distributerName,"has")
        batchAddress = getBatchAddress(batchID)
        try:
            manufacturers = self._readData(context, MANUFACTURERS_TABLE)
            distributers = self._readData(context, DISTRIBUTERS_TABLE)
            print('manufacturers: {}'.format(manufacturers))
            print('distributers: {}'.format(distributers))
            if manufacturerName in manufacturers and distributerName in distributers:
                distributerRequestMedicine = self._readData(context,distributerRequestAddress)
                if batchID in distributerRequestMedicine:
                    distributerRequestMedicine.remove(batchID)
                    print(batchID + 'removed from request list of distributer')
                    if action == "Accept":
                        distributerHasMedicine = self._readData(context, distributerHasAddress)
                        distributerHasMedicine.append(batchID)

                        tracking = self._readData(context, batchAddress)
                        tracking = [distributerName] + tracking

                        addresses = context.set_state({
                            distributerHasAddress: self._encode_data(distributerHasMedicine),
                            distributerRequestAddress: self._encode_data(distributerRequestMedicine),
                            batchAddress: self._encode_data(tracking)
                        })
                        print(batchID + 'added to has list of distributer and tracking updated')
                    elif action == "Reject":
                        manufacturerMedicine = self._readData(context, manufacturerAddress)
                        manufacturerMedicine.append(batchID)

                        addresses = context.set_state({
                            manufacturerAddress: self._encode_data(manufacturerMedicine),
                            distributerRequestAddress: self._encode_data(distributerRequestMedicine)
                        })

                        print(batchID + 'added back to manufacturer')
                else:
                    raise Exception("batchid not in medicine list")
            else:
                raise Exception("manu or dist not in lists")
            #LOGGER.info('{} gave {} to {}'.format(manufacturerName, medicineDetails, distributerName))
        except TypeError as t:
            logging.debug('TypeError in _giveTo: {}'.format(t))
            raise InvalidTransaction('Type error')
        except InvalidTransaction as e:
            logging.debug ('excecption: {}'.format(e))
            raise e
        except Exception as e:
            logging.debug('exception: {}'.format(e))
            raise InvalidTransaction('excecption: {}'.format(e))

    @classmethod
    def _giveToPharmacy(self, context, distributerName, pharmacyName, batchid, date):
        LOGGER.info("entering giveToPharmacy")
        distributerAddress = getDistributerAddress(distributerName)
        pharmacyAddress = getPharmacyAddress(pharmacyName, "request")
        try:
            distributers = self._readData(context, DISTRIBUTERS_TABLE)
            pharmacies = self._readData(context, PHARMACY_TABLE)
            LOGGER.info ('distributers: {}'.format(distributers))
            LOGGER.info ('pharmacies: {}'.format(pharmacies))
            if distributerName in distributers and pharmacyName in pharmacies:
                distributerMedicines = self._readData(context, distributerAddress)
                if batchid in distributerMedicines:
                    distributerMedicines.remove(batchid)
                    LOGGER.info (batchid + 'removed from distributers')
                    pharmacyMedicine = self._readData(context, pharmacyAddress)
                    pharmacyMedicine.append(batchid)
                    addresses = context.set_state({
                        distributerAddress: self._encode_data(distributerMedicines),
                        pharmacyAddress: self._encode_data(pharmacyMedicine)
                    })
                else:
                    raise Exception("batchId not in medicineList")
            else:
                raise Exception("distributer or pharmacy not existent")
            LOGGER.info('{} gave {} to {}.request'.format(distributerName, batchid, pharmacyName))
        except TypeError as t:
            logging.debug('TypeError in _giveTo: {}'.format(t))
            raise InvalidTransaction('Type error')
        except InvalidTransaction as e:
            logging.debug ('excecption: {}'.format(e))
            raise e
        except Exception as e:
            logging.debug('exception: {}'.format(e))
            raise InvalidTransaction('excecption: {}'.format(e))

    @classmethod
    def _getFromDistributer(self, context, distributerName, pharmacyName, batchID, date, action):
        LOGGER.info("entering getFromDistributer")
        action = str(action)
        distributerAddress = getDistributerAddress(distributerName)
        pharmacyRequestAddress = getPharmacyAddress(pharmacyName,"request")
        pharmacyHasAddress = getPharmacyAddress(pharmacyName,"has")
        batchAddress = getBatchAddress(batchID)
        try:
            pharmacy = self._readData(context, PHARMACY_TABLE)
            distributers = self._readData(context, DISTRIBUTERS_TABLE)
            LOGGER.info ('pharmacy: {}'.format(pharmacy))
            LOGGER.info ('distributers: {}'.format(distributers))
            if pharmacyName in pharmacy and distributerName in distributers:
                pharmacyRequestMedicine = self._readData(context,pharmacyRequestAddress)
                if batchID in pharmacyRequestMedicine:
                    pharmacyRequestMedicine.remove(batchID)
                    LOGGER.info (batchID + 'removed from request list of pharmacy')
                    if action == "Accept":
                        pharmacyHasMedicine = self._readData(context, pharmacyHasAddress)
                        pharmacyHasMedicine.append(batchID)

                        tracking = self._readData(context, batchAddress)
                        tracking = [pharmacyName] + tracking

                        addresses = context.set_state({
                            pharmacyHasAddress: self._encode_data(pharmacyHasMedicine),
                            pharmacyRequestAddress: self._encode_data(pharmacyRequestMedicine),
                            batchAddress: self._encode_data(tracking)
                        })
                        LOGGER.info (batchID + 'added to has list of distributer and tracking updated')
                    elif action == "Reject":
                        distributerMedicine = self._readData(context, distributerAddress)
                        distributerMedicine.append(batchID)

                        addresses = context.set_state({
                            distributerAddress: self._encode_data(distributerMedicine),
                            pharmacyRequestAddress: self._encode_data(pharmacyRequestMedicine)
                        })

                        LOGGER.info (batchID + 'added back to distributer')
                else:
                    raise Exception("batchid not in list")
            else:
                raise Exception("dist or pharma not in lists")
            #LOGGER.info('{} gave {} to {}'.format(manufacturerName, medicineDetails, distributerName))
        except TypeError as t:
            logging.debug('TypeError in _giveTo: {}'.format(t))
            raise InvalidTransaction('Type error')
        except InvalidTransaction as e:
            logging.debug ('excecption: {}'.format(e))
            raise e
        except Exception as e:
            logging.debug('exception: {}'.format(e))
            raise InvalidTransaction('excecption: {}'.format(e))

    # returns a list
    @classmethod
    def _readData(self, context, address):
        state_entries = context.get_state([address])
        if state_entries == []:
            return []
        data = self._decode_data(state_entries[0].data)
        return data

    # returns a list
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
        return payload_list
