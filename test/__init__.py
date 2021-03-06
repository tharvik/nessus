from os import environ
from unittest import TestCase

from nessus import LibNessus


class TestBase(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_dir = 'test/data'


    def setUp(self):
        ip = environ['NESSUS_IP']
        port = environ['NESSUS_PORT']
        api_access_key = environ['NESSUS_ACCESS_KEY']
        api_secret_key = environ['NESSUS_SECRET_KEY']
        self.nessus = LibNessus(host=ip, port=port, api_access_key=api_access_key, api_secret_key=api_secret_key)

        # we have it as list to always take the same single target
        self.targets = environ['NESSUS_TARGETS'].split('|')

        self.added_policies = set()
        self.added_policies_id = set()
        self.added_scans = set()

    def tearDown(self):
        super().tearDown()

        for scan in self.added_scans:
            self.nessus.scans.delete(scan)

        self.added_policies |= {p for p in self.nessus.policies.list() if p.id in self.added_policies_id}
        for policy in self.added_policies:
            self.nessus.policies.delete(policy)
