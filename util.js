var {_hash} = require("./lib");

const family_name='pharmhedge'
const FAMILY_NAME=_hash(family_name).substring(0,6);
const TABLES=_hash('tables').substring(0,6);

const MANUFACTURER_ENTRIES= _hash('manufacturer-entries').substring(0,6);
const MANUFACTURERS=_hash('manufacturers');
exports.MANUFACTURERS_TABLE=FAMILY_NAME+TABLES+MANUFACTURERS.substring(0,58);
exports.FAMILY_NAME=FAMILY_NAME;
exports.MANUFACTURER_ENTRIES=MANUFACTURER_ENTRIES;
exports.TABLES=TABLES;

exports.DISTRIBUTOR_ENTRIES=_hash('distributor-entries').substring(0,6);
const DISTRIBUTORS=_hash('distributors');
exports.DISTRIBUTORS_TABLE= FAMILY_NAME+TABLES+DISTRIBUTORS.substring(0,58);



exports.PHARMACY_ENTRIES=_hash('pharmacy-entries').substring(0,6);
const PHARMACIES=_hash('pharmacies');
exports.PHARMACIES_TABLE= FAMILY_NAME+TABLES+PHARMACIES.substring(0,58);