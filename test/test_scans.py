from time import sleep

from typing import Optional

from nessus.editor import NessusTemplateType, NessusTemplate
from nessus.error import NessusNetworkError
from nessus.scans import NessusScanStatus, NessusScan
from test import TestBase


class TestScans(TestBase):
    def test_list(self):
        self.nessus.scans.list()

    def __get_template(self, name: str = 'discovery'):
        templates = self.nessus.editor.list(NessusTemplateType.scan)
        return next(t for t in templates if t.name == name)

    def __get_scans_id(self):
        return {s.id for s in self.nessus.scans.list()}

    def __get_policy(self, template: Optional[NessusTemplate] = None):
        if template is None:
            template = self.__get_template()
        policy_id, policy_ = self.nessus.policies.create(template)
        policies = self.nessus.policies.list()
        policy = next(p for p in policies if p.id == policy_id)
        self.added_policies.add(policy)
        return policy

    def test_create(self):
        old_scans = self.__get_scans_id()
        policy = self.__get_policy()

        created = self.nessus.scans.create(policy, default_targets=self.targets)
        self.added_scans.add(created)

        self.assertEqual(created.policy_id, policy.id)

        new_scans = self.__get_scans_id()
        old_scans.add(created.id)
        self.assertSetEqual(new_scans, old_scans)

    def test_create_override_template(self):
        old_scans = self.__get_scans_id()
        template_policy = self.__get_template()
        template_other = self.__get_template('drown')
        policy = self.__get_policy(template_policy)

        created = self.nessus.scans.create(policy, template=template_other, default_targets=self.targets)
        self.added_scans.add(created)

        new_scans = self.__get_scans_id()
        old_scans.add(created.id)
        self.assertSetEqual(new_scans, old_scans)

    def test_create_empty_name(self):
        policy = self.__get_policy()

        self.assertRaises(NessusNetworkError, self.nessus.scans.create, policy, name='')

    def test_create_single_target(self):
        old_scans = self.__get_scans_id()
        policy = self.__get_policy()

        created = self.nessus.scans.create(policy, default_targets=[self.targets[0]])
        self.added_scans.add(created)

        new_scans = self.__get_scans_id()
        old_scans.add(created.id)
        self.assertSetEqual(new_scans, old_scans)

    def __get_scan_status(self, scan_uuid: str) -> NessusScanStatus:
        scans = self.nessus.scans.list()
        scan = next(s for s in scans if s.uuid == scan_uuid)
        return scan.status

    def __wait_scan_completion(self, launched_scan_uuid):
        while self.__get_scan_status(launched_scan_uuid) is not NessusScanStatus.completed:
            sleep(1)

    def __get_scan_by_uuid(self, scan_uuid: str) -> NessusScan:
        return next(s for s in self.nessus.scans.list() if s.uuid == scan_uuid)

    def test_launch(self):
        policy = self.__get_policy()

        scan = self.nessus.scans.create(policy, default_targets=self.targets)
        self.added_scans.add(scan)
        launched_scan_uuid = self.nessus.scans.launch(scan)

        self.__wait_scan_completion(launched_scan_uuid)
        scanned = self.__get_scan_by_uuid(launched_scan_uuid)

        self.assertEqual(scanned.id, scan.id)

    def test_details(self):
        policy = self.__get_policy()

        scan = self.nessus.scans.create(policy, default_targets=self.targets)
        self.added_scans.add(scan)

        self.nessus.scans.details(scan)

    def test_host_details_after_completion(self):
        template = self.__get_template('basic')
        policy = self.__get_policy(template)
        scan = self.nessus.scans.create(policy, default_targets=self.targets)
        self.added_scans.add(scan)
        launched_scan_uuid = self.nessus.scans.launch(scan)
        self.__wait_scan_completion(launched_scan_uuid)
        details = self.nessus.scans.details(scan)
        host = next(x for x in details.hosts)

        self.nessus.scans.host_details(scan=scan, host=host)

    def test_host_plugin_output_after_completion(self):
        template = self.__get_template('basic')
        policy = self.__get_policy(template)
        scan = self.nessus.scans.create(policy, default_targets=self.targets)
        self.added_scans.add(scan)
        launched_scan_uuid = self.nessus.scans.launch(scan)
        self.__wait_scan_completion(launched_scan_uuid)
        details = self.nessus.scans.details(scan)
        host = next(x for x in details.hosts)
        host_details = self.nessus.scans.host_details(scan=scan, host=host)
        vulnerability = next(x for x in host_details.vulnerabilities)

        self.nessus.scans.plugin_output(scan=scan, host=host, plugin_id=vulnerability.plugin_id)
