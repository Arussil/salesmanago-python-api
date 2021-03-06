import random
from tests import utils as tests_utils
from .test_data_base import SalesManagoTestsBase
from salesmanago_python_api.data.client import SalesManagoClientData


class SalesManagoClientDataFeatureTest(SalesManagoTestsBase):

    def test_address_empty(self):
        self.assertEqual(self.clientClass.address, None)

    def test_address_complete(self):
        self.assertIsInstance(self.richClientClass.address, dict)

        self.assertEqual(self.richClientClass.address, {
            "streetAddress": self.rcd['address_streetAddress'],
            "zipCode":self.rcd['address_zipCode'],
            "city": self.rcd['address_city'],
            "country": self.rcd['address_country']
        })

    def gen_addres_test_set(self, only_address=False):
        TEST_ARGS = self.ADDRESS_FIELDS

        if only_address:
            initial_data = self._rich_client_data(fields=[
                'address_%s' % f for f in TEST_ARGS
            ])
        else:
            initial_data = self._rich_client_data()

        validate_against = {}

        num_args = random.randint(1,4)
        RANDOM_TEST_ARGS = random.sample(TEST_ARGS, num_args)

        for arg in TEST_ARGS:
            create_arg_name = 'address_%s' % arg
            if arg not in RANDOM_TEST_ARGS:
                del initial_data[create_arg_name]
            else:
                validate_against[arg] = initial_data[create_arg_name]

        return (initial_data, validate_against)

    def test_address_partial(self):
        for x in range(50):
            initial_data, validate_against = self.gen_addres_test_set()
            rand_address = SalesManagoClientData(**initial_data)
            self.assertEqual(rand_address.address, validate_against)

    def test_contact_empty_insert(self):
        self.assertEqual(self.clientClass.contact('insert'), {'email': self.CLIENT_MAIL})
    
    def test_contact_empty_update(self):
        self.assertEqual(self.clientClass.contact('update'), {})
    
    def get_contact_test_data_set(self, request_format, only_contact=False):
        TEST_ARGS = self.CONTACT_FIELDS

        #IF we need only contact data
        if only_contact:
            #without address
            initial_data = self._rich_client_data(fields=TEST_ARGS[:-1])
        else:
            initial_data = self._rich_client_data(no_address=True)

        #email must be always present
        if request_format == 'insert':
            validate_against = {'email': self.CLIENT_MAIL}
        #update nope
        else:
            validate_against = {}

        num_args = random.randint(1,len(TEST_ARGS))
        RANDOM_TEST_ARGS = random.sample(TEST_ARGS, num_args)

        #we're also adding some address data
        if 'address' in RANDOM_TEST_ARGS:
            a_initial_data, a_validate_against = self.gen_addres_test_set(only_address=True)
            initial_data.update(a_initial_data)
            validate_against['address'] = a_validate_against

        #iterate over args and setup dicts, no address it's added before
        for arg in TEST_ARGS[:-1]:
            if arg not in RANDOM_TEST_ARGS:
                del initial_data[arg]
            else:
                validate_against[arg] = initial_data[arg]

        return (initial_data, validate_against)

    def test_contact_partial_data_insert(self):
        for x in range(50):
            initial_data, validate_against = self.get_contact_test_data_set('insert')
            rand_address = SalesManagoClientData(**initial_data)
            self.assertEqual(rand_address.contact('insert'), validate_against)

    def test_contact_partial_data_update(self):
        for x in range(50):
            initial_data, validate_against = self.get_contact_test_data_set('update')
            rand_address = SalesManagoClientData(**initial_data)
            self.assertEqual(rand_address.contact('update'), validate_against)

    def test_requestDict_empty_for_insert(self):
        AGAINST = {
            'contact': {'email': self.CLIENT_MAIL},
            'owner': self.OWNER_MAIL
        }
        self.assertEqual(self.clientClass.requestDict(request_format='insert'), AGAINST)
    
    def test_requestDict_empty_for_update(self):
        AGAINST = {
            'email': self.CLIENT_MAIL,
            'owner': self.OWNER_MAIL
        }
        self.assertEqual(self.clientClass.requestDict(request_format='update'), AGAINST)

    def test_requestDict_for_delete(self):
        
        AGAINST = {
            'email': self.CLIENT_MAIL,
            'owner': self.OWNER_MAIL
        }

        self.assertEqual(self.clientClass.requestDict(request_format='delete'), AGAINST)
        self.assertNotIn('contact', self.clientClass.requestDict(request_format='delete'))
        self.assertNotIn('properties', self.clientClass.requestDict(request_format='delete'))
        self.assertNotIn('tags', self.clientClass.requestDict(request_format='delete'))
        self.assertNotIn('removeTags', self.clientClass.requestDict(request_format='delete'))

    def test_requestDict_with_partial_data_for_insert(self):
        TEST_ARGS = [
            'birthday', 'province', 'forceOptOut', 'forceOptIn', 'forcePhoneOptOut', 'forcePhoneOptIn', 'useApiDoubleOptIn', 
            'newEmail', 'externalId', 'lang', 'tags', 'removeTags', 'properties', 'contact'
        ]

        for x in range(50):
            initial_data = self._rich_client_data(no_contact=True, no_address=True)
            validate_against = {
                'contact': {'email': self.CLIENT_MAIL},
                'owner': self.OWNER_MAIL
            }

            num_args = random.randint(1,len(TEST_ARGS))
            RANDOM_TEST_ARGS = random.sample(TEST_ARGS, num_args)

            #required
            RANDOM_TEST_ARGS.append('owner')

            if 'contact' in RANDOM_TEST_ARGS:
                contact_initial_data, contact_validate_against = self.get_contact_test_data_set(
                    'insert', only_contact=True)
                initial_data.update(contact_initial_data)
                validate_against['contact'] = contact_validate_against

            #all w/o iterables
            for arg in TEST_ARGS[:-4]:

                if arg not in RANDOM_TEST_ARGS:
                    del initial_data[arg]
                else:
                    validate_against[arg] = initial_data[arg]
                
                if 'birthday' in validate_against:
                    validate_against['birthday'] = initial_data['birthday'].strftime('%Y%m%d')
            
            rand_address = SalesManagoClientData(**initial_data)

            if 'tags' in RANDOM_TEST_ARGS:
                validate_against['tags'] = []
                for tag in tests_utils.gen_list_of_strings(random.randint(1,20)):
                    rand_address.add_tag(tag)
                    validate_against['tags'].append(tag)
            
            if 'removeTags' in RANDOM_TEST_ARGS:
                validate_against['removeTags'] = []
                for tag in tests_utils.gen_list_of_strings(random.randint(1,20)):
                    rand_address.add_removeTags(tag)
                    validate_against['removeTags'].append(tag)
            
            if 'properties' in RANDOM_TEST_ARGS:
                validate_against['properties'] = {}
                for key,value in tests_utils.gen_dict(random.randint(1,20)).items():
                    rand_address.add_property(key,value)
                    validate_against['properties'][key] = value

            self.assertEqual(rand_address.requestDict(request_format='insert'), validate_against)
