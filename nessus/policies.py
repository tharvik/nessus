from typing import Iterable, Optional, Mapping, Union

from nessus.base import LibNessusBase
from nessus.file import NessusRemoteFile


class NessusPolicy:
    """
    nessus is lying with:
     - `visibility` which is not always there, and is not an int
    """

    def __init__(self, policy_id: int, template_uuid: str, name: str, description: str, owner_id: str, owner: str,
                 shared: int, user_permissions: int, creation_date: int, last_modification_date: int,
                 visibility: Optional[int]) -> None:
        self.id = policy_id
        self.template_uuid = template_uuid
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self.owner = owner
        self.shared = shared
        self.user_permissions = user_permissions
        self.creation_date = creation_date
        self.last_modification_date = last_modification_date
        self.visibility = visibility

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, NessusPolicy):
            return False
        return self.id == other.id

    def __repr__(self) -> str:
        form = 'NessusPolicy({id!r}, {template_uuid!r}, {name!r}, {description!r}, {owner_id!r}, {owner!r}, ' \
               '{shared!r}, {user_permissions!r}, {creation_date!r}, {last_modification_date!r}, {visibility!r})'
        return form.format(**self.__dict__)

    @staticmethod
    def from_json(json_dict: Mapping[str, Union[int, str, bool]]) -> 'NessusPolicy':
        policy_id = int(json_dict['id'])
        template_uuid = str(json_dict['template_uuid'])
        name = str(json_dict['name'])
        description = str(json_dict['description'])
        owner_id = str(json_dict['owner_id'])
        owner = str(json_dict['owner'])
        shared = int(json_dict['shared'])
        user_permissions = int(json_dict['user_permissions'])
        creation_date = int(json_dict['creation_date'])
        last_modification_date = int(json_dict['last_modification_date'])

        if 'visibility' in json_dict:
            visibility = str(json_dict['visibility'])
        else:
            visibility = None

        return NessusPolicy(policy_id, template_uuid, name, description, owner_id, owner, shared, user_permissions,
                            creation_date, last_modification_date, visibility)


class LibNessusPolicies(LibNessusBase):
    def list(self) -> Iterable[NessusPolicy]:
        """
        get the list of policy
        :return: iterable of available policy
        """
        ans = self._get('policies')
        return {NessusPolicy.from_json(policy) for policy in ans.json()['policies']}

    def delete(self, policy: NessusPolicy) -> None:
        url = 'policies/{}'.format(policy.id)
        self._delete(url)

    def import_(self, remote_file: NessusRemoteFile) -> NessusPolicy:
        """
        import the given file as a policy
        sorry about the name, but in python 'import' is a reserved keyword
        :param remote_file: file to treat as nessus policy
        """
        data = {'file': remote_file.name}
        ans = self._post('policies/import', data=data)
        return NessusPolicy.from_json(ans.json())
