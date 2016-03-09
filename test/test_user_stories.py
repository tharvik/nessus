from time import sleep

from nessus.editor import NessusTemplateType
from nessus.scans import NessusScanStatus
from test import TestBase


class TestUserStories(TestBase):
    def test_scan_with_template(self):
        templates = self.nessus.editor.list(NessusTemplateType.policy)
        template = next(t for t in templates if t.name == 'discovery')

        policy_id, _ = self.nessus.policies.create(template)
        self.added_policies_id.add(policy_id)
        policy = next(p for p in self.nessus.policies.list() if p.id == policy_id)

        scan = self.nessus.scans.create(policy)
        self.added_scans.add(scan)

        scan_uuid = self.nessus.scans.launch(scan)

        status = None
        while status is not NessusScanStatus.completed:
            scans = self.nessus.scans.list()
            scanning = next(s for s in scans if s.uuid == scan_uuid)
            status = scanning.status
            sleep(1)

        scans = self.nessus.scans.list()
        scanned = next(s for s in scans if s.uuid == scan_uuid)
        self.nessus.scans.details(scanned)
