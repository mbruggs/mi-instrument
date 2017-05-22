#!/usr/bin/env python

"""
@package mi.dataset.parser.test.test_flort_dj_dcl
@file marine-integrations/mi/dataset/parser/test/test_flort_dj_dcl.py
@author Steve Myerson
@brief Test code for a flort_dj_dcl data parser

In the following files, Metadata consists of 4 records.
There is 1 group of Sensor Data records for each set of metadata.

Files used for testing:

20010101.flort1.log
  Metadata - 1 set,  Sensor Data - 0 records

20020215.flort2.log
  Metadata - 2 sets,  Sensor Data - 15 records

20030413.flort3.log
  Metadata - 4 sets,  Sensor Data - 13 records

20040505.flort4.log
  Metadata - 5 sets,  Sensor Data - 5 records

20050406.flort5.log
  Metadata - 4 sets,  Sensor Data - 6 records

20061220.flort6.log
  Metadata - 1 set,  Sensor Data - 300 records

20071225.flort7.log
  Metadata - 2 sets,  Sensor Data - 200 records

20080401.flort8.log
  This file contains a boatload of invalid sensor data records.
  See metadata in file for a list of the errors.
  20 metadata records, 47 sensor data records

Change History:

    Date         Ticket#    Engineer     Description
    ------------ ---------- -----------  --------------------------
    5/16/17      #9809      janeenP      Added functionality for testing
                                         combined CTDBP with FLORT
"""

import os

from nose.plugins.attrib import attr

from mi.core.log import get_logger
from mi.dataset.dataset_parser import DataSetDriverConfigKeys
from mi.dataset.driver.flort_dj.dcl.resource import RESOURCE_PATH
from mi.dataset.parser.flort_dj_dcl import \
    FlortDjDclParser, \
    FlortDjDclRecoveredInstrumentDataParticle, \
    FlortDjDclTelemeteredInstrumentDataParticle
from mi.dataset.test.test_parser import ParserUnitTestCase
from mi.core.exceptions import RecoverableSampleException

log = get_logger()
MODULE_NAME = 'mi.dataset.parser.flort_dj_dcl'
PARSER_NAME = 'FlortDjDclParser'

# Expected tuples for data in file 20040505.flort4.log
EXPECTED_20040505_flort4 = [
    ('2004/05/05 09:11:21.093', '2004', '05', '05', '09', '11', '21',
        '05/05/03', '21:11:21', '0', '1', '2', '3', '4', '5', '6'),
    ('2004/05/05 09:11:23.451', '2004', '05', '05', '09', '11', '23',
        '05/05/03', '21:11:23', '2730', '2731', '2732', '2733', '2734', '2735', '2736'),
    ('2004/05/05 09:11:25.809', '2004', '05', '05', '09', '11', '25',
        '05/05/03', '21:11:25', '5460', '5461', '5462', '5463', '5464', '5465', '5466'),
    ('2004/05/05 09:11:28.167', '2004', '05', '05', '09', '11', '28',
        '05/05/03', '21:11:28', '8190', '8191', '8192', '8193', '8194', '8195', '8196'),
    ('2004/05/05 09:11:30.525', '2004', '05', '05', '09', '11', '30',
        '05/05/03', '21:11:30', '10920', '10921', '10922', '10923', '10924', '10925', '10926'),
    ('2004/05/05 09:11:39.957', '2004', '05', '05', '09', '11', '39',
        '05/05/03', '21:11:39', '13650', '13651', '13652', '13653', '13654', '13655', '13656'),
    ('2004/05/05 09:11:42.315', '2004', '05', '05', '09', '11', '42',
        '05/05/03', '21:11:42', '16380', '16381', '16382', '16383', '16384', '16385', '16386'),
    ('2004/05/05 09:11:44.673', '2004', '05', '05', '09', '11', '44',
        '05/05/03', '21:11:44', '19110', '19111', '19112', '19113', '19114', '19115', '19116'),
    ('2004/05/05 09:11:47.031', '2004', '05', '05', '09', '11', '47',
        '05/05/03', '21:11:47', '21840', '21841', '21842', '21843', '21844', '21845', '21846'),
    ('2004/05/05 09:11:49.389', '2004', '05', '05', '09', '11', '49',
        '05/05/03', '21:11:49', '24570', '24571', '24572', '24573', '24574', '24575', '24576'),
    ('2004/05/05 09:11:58.821', '2004', '05', '05', '09', '11', '58',
        '05/05/03', '21:11:58', '27300', '27301', '27302', '27303', '27304', '27305', '27306'),
    ('2004/05/05 09:12:01.179', '2004', '05', '05', '09', '12', '01',
        '05/05/03', '21:12:01', '30030', '30031', '30032', '30033', '30034', '30035', '30036'),
    ('2004/05/05 09:12:03.537', '2004', '05', '05', '09', '12', '03',
        '05/05/03', '21:12:03', '32760', '32761', '32762', '32763', '32764', '32765', '32766'),
    ('2004/05/05 09:12:05.895', '2004', '05', '05', '09', '12', '05',
        '05/05/03', '21:12:05', '35490', '35491', '35492', '35493', '35494', '35495', '35496'),
    ('2004/05/05 09:12:08.253', '2004', '05', '05', '09', '12', '08',
        '05/05/03', '21:12:08', '38220', '38221', '38222', '38223', '38224', '38225', '38226'),
    ('2004/05/05 09:12:17.685', '2004', '05', '05', '09', '12', '17',
        '05/05/03', '21:12:17', '40950', '40951', '40952', '40953', '40954', '40955', '40956'),
    ('2004/05/05 09:12:20.043', '2004', '05', '05', '09', '12', '20',
        '05/05/03', '21:12:20', '43680', '43681', '43682', '43683', '43684', '43685', '43686'),
    ('2004/05/05 09:12:22.401', '2004', '05', '05', '09', '12', '22',
        '05/05/03', '21:12:22', '46410', '46411', '46412', '46413', '46414', '46415', '46416'),
    ('2004/05/05 09:12:24.759', '2004', '05', '05', '09', '12', '24',
        '05/05/03', '21:12:24', '49140', '49141', '49142', '49143', '49144', '49145', '49146'),
    ('2004/05/05 09:12:27.117', '2004', '05', '05', '09', '12', '27',
        '05/05/03', '21:12:27', '51870', '51871', '51872', '51873', '51874', '51875', '51876'),
    ('2004/05/05 09:12:36.549', '2004', '05', '05', '09', '12', '36',
        '05/05/03', '21:12:36', '54600', '54601', '54602', '54603', '54604', '54605', '54606'),
    ('2004/05/05 09:12:38.907', '2004', '05', '05', '09', '12', '38',
        '05/05/03', '21:12:38', '57330', '57331', '57332', '57333', '57334', '57335', '57336'),
    ('2004/05/05 09:12:41.265', '2004', '05', '05', '09', '12', '41',
        '05/05/03', '21:12:41', '60060', '60061', '60062', '60063', '60064', '60065', '60066'),
    ('2004/05/05 09:12:43.623', '2004', '05', '05', '09', '12', '43',
        '05/05/03', '21:12:43', '62790', '62791', '62792', '62793', '62794', '62795', '62796'),
    ('2004/05/05 09:12:45.981', '2004', '05', '05', '09', '12', '45',
        '05/05/03', '21:12:45', '65520', '65521', '65522', '65523', '65524', '65525', '65526')
]

# Expected tuples for data in file 20050406.flort5.log
EXPECTED_20050406_flort5 = [
    ('2005/04/06 11:13:23.095', '2005', '04', '06', '11', '13', '23',
        '04/06/04', '23:13:23', '0', '1', '2', '3', '4', '5', '6'),
    ('2005/04/06 11:13:25.453', '2005', '04', '06', '11', '13', '25',
        '04/06/04', '23:13:25', '2849', '2850', '2851', '2852', '2853', '2854', '2855'),
    ('2005/04/06 11:13:27.811', '2005', '04', '06', '11', '13', '27',
        '04/06/04', '23:13:27', '5698', '5699', '5700', '5701', '5702', '5703', '5704'),
    ('2005/04/06 11:13:30.169', '2005', '04', '06', '11', '13', '30',
        '04/06/04', '23:13:30', '8547', '8548', '8549', '8550', '8551', '8552', '8553'),
    ('2005/04/06 11:13:32.527', '2005', '04', '06', '11', '13', '32',
        '04/06/04', '23:13:32', '11396', '11397', '11398', '11399', '11400', '11401', '11402'),
    ('2005/04/06 11:13:34.885', '2005', '04', '06', '11', '13', '34',
        '04/06/04', '23:13:34', '14245', '14246', '14247', '14248', '14249', '14250', '14251'),
    ('2005/04/06 11:13:44.317', '2005', '04', '06', '11', '13', '44',
        '04/06/04', '23:13:44', '17094', '17095', '17096', '17097', '17098', '17099', '17100'),
    ('2005/04/06 11:13:46.675', '2005', '04', '06', '11', '13', '46',
        '04/06/04', '23:13:46', '19943', '19944', '19945', '19946', '19947', '19948', '19949'),
    ('2005/04/06 11:13:49.033', '2005', '04', '06', '11', '13', '49',
        '04/06/04', '23:13:49', '22792', '22793', '22794', '22795', '22796', '22797', '22798'),
    ('2005/04/06 11:13:51.391', '2005', '04', '06', '11', '13', '51',
        '04/06/04', '23:13:51', '25641', '25642', '25643', '25644', '25645', '25646', '25647'),
    ('2005/04/06 11:13:53.749', '2005', '04', '06', '11', '13', '53',
        '04/06/04', '23:13:53', '28490', '28491', '28492', '28493', '28494', '28495', '28496'),
    ('2005/04/06 11:13:56.107', '2005', '04', '06', '11', '13', '56',
        '04/06/04', '23:13:56', '31339', '31340', '31341', '31342', '31343', '31344', '31345'),
    ('2005/04/06 11:14:05.539', '2005', '04', '06', '11', '14', '05',
        '04/06/04', '23:14:05', '34188', '34189', '34190', '34191', '34192', '34193', '34194'),
    ('2005/04/06 11:14:07.897', '2005', '04', '06', '11', '14', '07',
        '04/06/04', '23:14:07', '37037', '37038', '37039', '37040', '37041', '37042', '37043'),
    ('2005/04/06 11:14:10.255', '2005', '04', '06', '11', '14', '10',
        '04/06/04', '23:14:10', '39886', '39887', '39888', '39889', '39890', '39891', '39892'),
    ('2005/04/06 11:14:12.613', '2005', '04', '06', '11', '14', '12',
        '04/06/04', '23:14:12', '42735', '42736', '42737', '42738', '42739', '42740', '42741'),
    ('2005/04/06 11:14:14.971', '2005', '04', '06', '11', '14', '14',
        '04/06/04', '23:14:14', '45584', '45585', '45586', '45587', '45588', '45589', '45590'),
    ('2005/04/06 11:14:17.329', '2005', '04', '06', '11', '14', '17',
        '04/06/04', '23:14:17', '48433', '48434', '48435', '48436', '48437', '48438', '48439'),
    ('2005/04/06 11:14:26.761', '2005', '04', '06', '11', '14', '26',
        '04/06/04', '23:14:26', '51282', '51283', '51284', '51285', '51286', '51287', '51288'),
    ('2005/04/06 11:14:29.119', '2005', '04', '06', '11', '14', '29',
        '04/06/04', '23:14:29', '54131', '54132', '54133', '54134', '54135', '54136', '54137'),
    ('2005/04/06 11:14:31.477', '2005', '04', '06', '11', '14', '31',
        '04/06/04', '23:14:31', '56980', '56981', '56982', '56983', '56984', '56985', '56986'),
    ('2005/04/06 11:14:33.835', '2005', '04', '06', '11', '14', '33',
        '04/06/04', '23:14:33', '59829', '59830', '59831', '59832', '59833', '59834', '59835'),
    ('2005/04/06 11:14:36.193', '2005', '04', '06', '11', '14', '36',
        '04/06/04', '23:14:36', '62678', '62679', '62680', '62681', '62682', '62683', '62684'),
    ('2005/04/06 11:14:38.551', '2005', '04', '06', '11', '14', '38',
        '04/06/04', '23:14:38', '65527', '65528', '65529', '65530', '65531', '65532', '65533'),
]

FILE1 = '20010101.flort1.log'
FILE2 = '20020215.flort2.log'
FILE3 = '20030413.flort3.log'
FILE4 = '20040505.flort4.log'
FILE5 = '20050406.flort5.log'
FILE6 = '20061220.flort6.log'
FILE7 = '20071225.flort7.log'
FILE8 = '20080401.flort8.log'

EXPECTED_FILE4 = EXPECTED_20040505_flort4
EXPECTED_FILE5 = EXPECTED_20050406_flort5
RECORDS_FILE6 = 300      # number of records expected
RECORDS_FILE7 = 400      # number of records expected
EXCEPTIONS_FILE8 = 47    # number of exceptions expected

INSTRUMENT_PARTICLE_MAP = [
    ('dcl_controller_timestamp',    0,   str),
    ('date_string',                 7,   str),
    ('time_string',                 8,   str),
    ('measurement_wavelength_beta', 9,   int),
    ('raw_signal_beta',             10,  int),
    ('measurement_wavelength_chl',  11,  int),
    ('raw_signal_chl',              12,  int),
    ('measurement_wavelength_cdom', 13,  int),
    ('raw_signal_cdom',             14,  int),
    ('raw_internal_temp',           15,  int)
]

CTDBP_FLORT_PARTICLE_MAP = [
    ('dcl_controller_timestamp',    0,   str),
    ('raw_signal_beta',             7,   int),
    ('raw_signal_chl',              8,   int),
    ('raw_signal_cdom',             9,   int),
    ('date_time_string',            10,  str)
]


@attr('UNIT', group='mi')
class FlortDjDclParserUnitTestCase(ParserUnitTestCase):
    """
    flort_dj_dcl Parser unit test suite
    """
    def open_file(self, filename):
        my_file = open(os.path.join(RESOURCE_PATH, filename), mode='r')
        return my_file

    def setUp(self):
        ParserUnitTestCase.setUp(self)

        self.rec_config = {
            DataSetDriverConfigKeys.PARTICLE_MODULE: MODULE_NAME,
            DataSetDriverConfigKeys.PARTICLE_CLASS:
            'FlortDjDclRecoveredInstrumentDataParticle'
        }

        self.tel_config = {
            DataSetDriverConfigKeys.PARTICLE_MODULE: MODULE_NAME,
            DataSetDriverConfigKeys.PARTICLE_CLASS:
            'FlortDjDclTelemeteredInstrumentDataParticle'
        }

    def test_big_giant_input(self):
        """
        Read a large file and verify that all expected particles can be read.
        Verification is not done at this time, but will be done during
        integration and qualification testing.
        """
        log.debug('===== START TEST BIG GIANT INPUT RECOVERED =====')
        with self.open_file(FILE6) as in_file:
            parser = FlortDjDclParser(self.rec_config, in_file,
                                      self.exception_callback)

            # In a single read, get all particles in this file.
            number_expected_results = RECORDS_FILE6
            result = parser.get_records(number_expected_results)
            self.assertEqual(len(result), number_expected_results)
            self.assertEqual(self.exception_callback_value, [])

        log.debug('===== START TEST BIG GIANT INPUT TELEMETERED =====')
        with self.open_file(FILE7) as in_file:
            parser = FlortDjDclParser(self.tel_config,
                                      in_file, self.exception_callback)

            # In a single read, get all particles in this file.
            number_expected_results = RECORDS_FILE7
            result = parser.get_records(number_expected_results)
            self.assertEqual(len(result), number_expected_results)
            self.assertEqual(self.exception_callback_value, [])

#        used to create .yml results files only when necessary
#        log.debug('===== call .yml file create =====')
#        self.create_large_yml()
#        self.create_large_yml('20151023.flort.log')
        log.debug('===== END TEST BIG GIANT INPUT =====')

    def test_get_many(self):
        """
        Read a file and pull out multiple data particles at one time.
        Verify that the results are those we expected.
        """
        log.debug('===== START TEST GET MANY RECOVERED =====')

        with self.open_file(FILE5) as in_file:
            parser = FlortDjDclParser(self.rec_config, in_file,
                                      self.exception_callback)

            # Generate a list of expected result particles.
            expected_particle = []
            for expected in EXPECTED_FILE5:
                particle = FlortDjDclRecoveredInstrumentDataParticle(expected)
                particle._data_particle_map = INSTRUMENT_PARTICLE_MAP
                particle.generate_dict()
                expected_particle.append(particle)

            # In a single read, get all particles for this file.
            result = parser.get_records(len(expected_particle))
            self.assertEqual(result, expected_particle)
            self.assertEqual(self.exception_callback_value, [])

        log.debug('===== START TEST GET MANY TELEMETERED =====')
        with self.open_file(FILE4) as in_file:
            parser = FlortDjDclParser(self.tel_config, in_file,
                                      self.exception_callback)

            # Generate a list of expected result particles.
            expected_particle = []
            for expected in EXPECTED_FILE4:
                particle = FlortDjDclTelemeteredInstrumentDataParticle(
                    expected)
                particle._data_particle_map = INSTRUMENT_PARTICLE_MAP
                particle.generate_dict()
                expected_particle.append(particle)

            # In a single read, get all particles for this file.
            result = parser.get_records(len(expected_particle))
            self.assertEqual(result, expected_particle)
            self.assertEqual(self.exception_callback_value, [])

        log.debug('===== END TEST GET MANY =====')

    def test_invalid_sensor_data_records(self):
        """
        Read data from a file containing invalid sensor data records.
        Verify that no instrument particles are produced
        and the correct number of exceptions are detected.
        """
        log.debug('===== START TEST INVALID SENSOR DATA RECOVERED =====')
        with self.open_file(FILE8) as in_file:
            parser = FlortDjDclParser(self.rec_config, in_file,
                                      self.exception_callback)

            # Try to get records and verify that none are returned.
            result = parser.get_records(1)
            self.assertEqual(result, [])
            self.assertEqual(len(self.exception_callback_value),
                             EXCEPTIONS_FILE8)

        log.debug('===== START TEST INVALID SENSOR DATA TELEMETERED =====')

        self.exception_callback_value = []  # reset exceptions
        with self.open_file(FILE8) as in_file:
            parser = FlortDjDclParser(self.tel_config, in_file,
                                      self.exception_callback)

            # Try to get records and verify that none are returned.
            result = parser.get_records(1)
            self.assertEqual(result, [])
            self.assertEqual(len(self.exception_callback_value),
                             EXCEPTIONS_FILE8)

        log.debug('===== END TEST INVALID SENSOR DATA =====')

    def test_no_sensor_data(self):
        """
        Read a file containing no sensor data records
        and verify that no particles are produced.
        """
        log.debug('===== START TEST NO SENSOR DATA RECOVERED =====')
        with self.open_file(FILE1) as in_file:
            parser = FlortDjDclParser(self.rec_config, in_file,
                                      self.exception_callback)

            # Try to get a record and verify that none are produced.
            result = parser.get_records(1)
            self.assertEqual(result, [])
            self.assertEqual(self.exception_callback_value, [])

        log.debug('===== START TEST NO SENSOR DATA TELEMETERED =====')
        with self.open_file(FILE1) as in_file:
            parser = FlortDjDclParser(self.tel_config, in_file,
                                      self.exception_callback)

            # Try to get a record and verify that none are produced.
            result = parser.get_records(1)
            self.assertEqual(result, [])
            self.assertEqual(self.exception_callback_value, [])

        log.debug('===== END TEST NO SENSOR DATA =====')

    def test_many_with_yml(self):
        """
        Read a file and verify that all records can be read.
        Verify that the contents of the particles are correct.
        There should be no exceptions generated.
        """
        log.debug('===== START TEST MANY WITH YML RECOVERED =====')

        num_particles = 30
        with self.open_file(FILE2) as in_file:
            parser = FlortDjDclParser(self.rec_config, in_file,
                                      self.exception_callback)
            particles = parser.get_records(num_particles)
            log.debug("Num particles: %d", len(particles))
            self.assert_particles(particles, "rec_20020215.flort2.yml",
                                  RESOURCE_PATH)
            self.assertEquals(self.exception_callback_value, [])

        log.debug('===== START TEST MANY WITH YML TELEMETERED =====')

        with self.open_file(FILE2) as in_file:
            parser = FlortDjDclParser(self.tel_config, in_file,
                                      self.exception_callback)

            particles = parser.get_records(num_particles)

            log.debug("Num particles: %d", len(particles))

            self.assert_particles(particles, "tel_20020215.flort2.yml",
                                  RESOURCE_PATH)
            self.assertEquals(self.exception_callback_value, [])

        log.debug('===== END TEST MANY WITH YML =====')

    def test_bug_9692(self):
        """
        This test verifies a fix to accommodate DCL timestamps with Seconds >59
        The test file is a trimmed down copy of a recovered file from
        a real deployment
        """
        log.debug('===== START TEST BUG 9692 =====')

        with self.open_file('20151023.flort.log') as in_file:
            parser = FlortDjDclParser(self.rec_config, in_file,
                                      self.exception_callback)

            particles = parser.get_records(5)

            log.debug("Num particles: %d", len(particles))

            self.assertEquals(len(particles), 3)
            self.assertEquals(self.exception_callback_value, [])

        log.debug('===== END TEST BUG 9692 =====')

    log.debug('===== START TESTS ENHANCEMENT 9809  =====')
    """
    Combined ctdbp_cdef_dcl with flort d Parser unit test suite
    """
    def test_ctdbp_cdef_dcl_flort_d(self):
        """
        Verify that data records from a ctdbp with a flort_d plugged in
        will produce expected data particles for the flort_d and ignore the
        ctdbp data.

        test with control data only and CTD ID
        2015/12/11 01:29:19.067 [ctdbp3:DLOGP6]:Instrument Started [Power On]
        """
        log.debug('===== START TEST CTDBPwFLORT:control only =====')
        with self.open_file('20151211.ctdbp3_controlOnly.log') as in_file:
            num_particles_to_request = 10
            num_expected_particles = 0

            parser = eval(PARSER_NAME)(self.tel_config, in_file,
                                       self.exception_callback)
            particles = parser.get_records(num_particles_to_request)

            self.assertEquals(len(particles), num_expected_particles)
            self.assertEquals(len(self.exception_callback_value), 0)

        log.debug('===== END TEST CTDBPwFLORT:control only =====')

        """
        test 1 rec with CTD ID
        2015/01/03 00:30:23.395 [ctdbp3:DLOGP6]: 12.3772,  3.73234,    1.087, 0, 0, 0, 03 Jan 2015 00:30:16
        """
        log.debug('===== START TEST CTDBPwFLORT:1 rec Low Battery =====')
        with self.open_file('20150103.ctdbp3_1recCtdID_w_LowBattery.log') as \
                in_file:

            num_particles_to_request = 10
            num_expected_particles = 1
            parser = eval(PARSER_NAME)(self.tel_config, in_file,
                                       self.exception_callback)
            particles = parser.get_records(num_particles_to_request)

            # Make sure we obtained expected particle(s)
            self.assertEquals(len(particles), num_expected_particles)
            self.assert_particles(
                particles,
                "20150103.ctdbp3_1recCtdID_w_LowBattery_flort.yml",
                RESOURCE_PATH)

        log.debug('===== END TEST CTDBPwFLORT:1 rec Low Battery =====')

        """
        test 3 recs with no CTD ID
        2016/10/09 00:30:26.290  13.3143,  3.56698,    1.088, 1672, 278, 84, 09 Oct 2016 00:30:20
        """
        log.debug('===== START TEST CTDBPwFLORT:3 rec no ctd id =====')
        with self.open_file('20161009.ctdbp3_3rec_noCtdId.log') as in_file:

            num_particles_to_request = 10
            num_expected_particles = 3

            parser = eval(PARSER_NAME)(self.tel_config, in_file,
                                       self.exception_callback)
            particles = parser.get_records(num_particles_to_request)

            # Make sure we obtained expected particle(s)
            self.assertEquals(len(particles), num_expected_particles)
            self.assert_particles(particles,
                                  "20161009.ctdbp3_3rec_noCtdId_flort.yml",
                                  RESOURCE_PATH)
        log.debug('===== END TEST CTDBPwFLORT:3 rec no ctd id =====')

        """
        test 3 recs, 1 with hash separator, no CTD ID
        2014/10/17 21:30:23.684 # 14.7850,  3.96796,    0.981, 740, 222, 73,
        17 Oct 2014 21:30:17
        """
        log.debug('===== START TEST CTDBPwFLORT:3 recs, 1 with #  =====')
        with self.open_file('20141017.ctdbp3_3rec_w_1hash.log') as in_file:

            num_particles_to_request = 10
            num_expected_particles = 3

            parser = eval(PARSER_NAME)(self.tel_config, in_file,
                                       self.exception_callback)
            particles = parser.get_records(num_particles_to_request)

            # Make sure we obtained expected particle(s)
            self.assertEquals(len(particles), num_expected_particles)
            self.assert_particles(particles,
                                  "20141017.ctdbp3_3rec_w_1hash_flort.yml",
                                  RESOURCE_PATH)
        log.debug('===== END TEST CTDBPwFLORT:3 recs, 1 with #  =====')
        """
        test 3 recs with negative pressure
        2014/10/02 00:30:28.063 [ctdbp3:DLOGP6]: 20.9286,  0.00003,   -0.011, 4130, 1244, 4130, 02 Oct 2014 00:30:23
        """
        log.debug('===== START TEST CTDBPwFLORT:3 recs, with neg press  =====')
        with self.open_file('20141002.ctdbp3_3Rec_negPressure.log') as in_file:

            num_particles_to_request = 10
            num_expected_particles = 3

            parser = eval(PARSER_NAME)(self.tel_config, in_file,
                                       self.exception_callback)
            particles = parser.get_records(num_particles_to_request)

            # Make sure we obtained expected particle(s)
            self.assertEquals(len(particles), num_expected_particles)
            self.assert_particles(particles,
                                  "20141002.ctdbp3_3Rec_negPressure_flort.yml",
                                  RESOURCE_PATH)
        log.debug('===== END TEST CTDBPwFLORT:3 recs, with neg press  =====')

        """
        test 18 recs with one damaged data line
        """
        log.debug('===== START TEST CTDBPwFLORT:18 recs, 1 damaged =====')
        with self.open_file('20161025.ctdbp3_damagedRec.log') as in_file:

            num_particles_to_request = 20
            num_expected_particles = 18

            parser = eval(PARSER_NAME)(self.tel_config, in_file,
                                       self.exception_callback)
            particles = parser.get_records(num_particles_to_request)

            # Make sure we obtained expected particle(s)
            self.assertEquals(len(particles), num_expected_particles)
            self.assert_particles(particles,
                                  "20161025.ctdbp3_damagedRec_flort.yml",
                                  RESOURCE_PATH)
        log.debug('===== END TEST CTDBPwFLORT:18 recs, 1 damaged =====')

        """
        test large file, 24 recs
        """
        log.debug('===== START TEST CTDBPwFLORT:24 recs =====')
        with self.open_file('20140928.ctdbp3_24rec.log') as in_file:

            num_particles_to_request = 30
            num_expected_particles = 24

            parser = eval(PARSER_NAME)(self.tel_config, in_file,
                                       self.exception_callback)
            particles = parser.get_records(num_particles_to_request)

            # Make sure we obtained expected particle(s)
            self.assertEquals(len(particles), num_expected_particles)
            self.assert_particles(particles,
                                  "20140928.ctdbp3_24rec_flort.yml",
                                  RESOURCE_PATH)
        log.debug('===== END TEST CTDBPwFLORT:24 recs =====')
        log.debug('===== END TESTS ENHANCEMENT 9809  =====')

    """
    These 2 methods were copied and adapted from /test_zplsc_c.py to facilitate
    the generation of large .yml results files for checking large datasets.
    """
    def create_large_yml(self, filename):
        """
        Create a large yml file corresponding to an actual recovered dataset.
        This is not an actual test - it allows us to create what we need
        for integration testing, i.e. a yml file.
        """
        log.debug('===== create_large_yml =====')
        with self.open_file(filename) as in_file:

            log.debug('===== parser: %s\tin_file name: %s  =====',
                      PARSER_NAME, in_file)

            parser = eval(PARSER_NAME)(self.tel_config, in_file,
                                       self.exception_callback)
            result = parser.get_records(1000)

#            out_file = '.'.join([in_file.name,  'yml'])
            out_file = '.'.join([in_file.name,  '_flort', 'yml'])
            log.debug('===== out_file name  %s  =====', out_file)

            self.particle_to_yml(result, out_file)

    def particle_to_yml(self, particles, filename, mode='w'):
        """
        This is added as a testing helper, not actually as part of the
        parser tests.  Since the same particles will be used for the
        driver test it is helpful to write them to .yml in the same form
        they need in the results.yml file here.
        """
        PARTICLE_NAME = 'FlortDjDclTelemeteredInstrumentDataParticle'
        PARTICLE_TYPE = 'flort_dj_dcl_instrument'

        # open write append, if you want to start from scratch manually
        # delete this file
        log.debug('===== file write file name  %s  =====', filename)
        with open(os.path.join(RESOURCE_PATH, filename), mode) as fid:
            fid.write('header:\n')
            fid.write("    particle_object: MULTIPLE\n")
            fid.write("    particle_type: MULTIPLE\n\n")
            fid.write('data:\n')
            for index in range(len(particles)):
                particle_dict = particles[index].generate_dict()
                fid.write('  - _index: %d\n' % (index+1))
                fid.write("    particle_object: %s\n" % PARTICLE_NAME)
                fid.write("    particle_type: %s\n" % PARTICLE_TYPE)
                fid.write('    internal_timestamp: %.7f\n' %
                          particle_dict.get('internal_timestamp'))
                fid.write('    port_timestamp: %.7f\n' %
                          particle_dict.get('port_timestamp'))
                values_dict = {}
                for value in particle_dict.get('values'):
                    values_dict[value.get('value_id')] = value.get('value')
                    log.debug('===== value_id %s  =====',
                              value.get('value_id'))
                for key in ('raw_signal_beta', 'raw_signal_chl',
                            'raw_signal_cdom', 'date_time_string'):
                    log.debug('===== key  %s  =====', key)
                    value = values_dict.get(key)
                    log.debug('===== just set value for key  %s  =====', key)
                    if value is None:
                        fid.write('    %s: %s\n' % (key, 'Null'))
                    elif isinstance(value, float):
                        fid.write('    %s: %15.5f\n' % (key, value))
                    elif isinstance(value, str):
                        fid.write("    %s: '%s'\n" % (key, value))
                    else:
                        fid.write('    %s: %s\n' % (key, value))
                    log.debug('===== finish write for key  %s  =====', key)