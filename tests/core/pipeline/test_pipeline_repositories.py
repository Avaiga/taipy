# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os

import pytest

from src.taipy.core.exceptions import ModelNotFound
from src.taipy.core.sequence._sequence_fs_repository import _SequenceFSRepository
from src.taipy.core.sequence._sequence_sql_repository import _SequenceSQLRepository
from src.taipy.core.sequence.sequence import Sequence, SequenceId


class TestSequenceRepository:
    @pytest.mark.parametrize("repo", [_SequenceFSRepository, _SequenceSQLRepository])
    def test_save_and_load(self, tmpdir, sequence, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(sequence)

        obj = repository._load(sequence.id)
        assert isinstance(obj, Sequence)

    @pytest.mark.parametrize("repo", [_SequenceFSRepository, _SequenceSQLRepository])
    def test_exists(self, tmpdir, sequence, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(sequence)

        assert repository._exists(sequence.id)
        assert not repository._exists("not-existed-sequence")

    @pytest.mark.parametrize("repo", [_SequenceFSRepository, _SequenceSQLRepository])
    def test_load_all(self, tmpdir, sequence, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._delete_all()
        for i in range(10):
            sequence.id = SequenceId(f"sequence-{i}")
            repository._save(sequence)
        data_nodes = repository._load_all()

        assert len(data_nodes) == 10

    @pytest.mark.parametrize("repo", [_SequenceFSRepository, _SequenceSQLRepository])
    def test_load_all_with_filters(self, tmpdir, sequence, repo):
        repository = repo()
        repository.base_path = tmpdir

        for i in range(10):
            sequence.id = SequenceId(f"sequence-{i}")
            sequence.owner_id = f"owner-{i}"
            repository._save(sequence)
        objs = repository._load_all(filters=[{"owner_id": "owner-2"}])

        assert len(objs) == 1

    @pytest.mark.parametrize("repo", [_SequenceFSRepository, _SequenceSQLRepository])
    def test_delete(self, tmpdir, sequence, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(sequence)

        repository._delete(sequence.id)

        with pytest.raises(ModelNotFound):
            repository._load(sequence.id)

    @pytest.mark.parametrize("repo", [_SequenceFSRepository, _SequenceSQLRepository])
    def test_delete_all(self, tmpdir, sequence, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._delete_all()

        for i in range(10):
            sequence.id = SequenceId(f"sequence-{i}")
            repository._save(sequence)

        assert len(repository._load_all()) == 10

        repository._delete_all()

        assert len(repository._load_all()) == 0

    @pytest.mark.parametrize("repo", [_SequenceFSRepository, _SequenceSQLRepository])
    def test_delete_many(self, tmpdir, sequence, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._delete_all()

        for i in range(10):
            sequence.id = SequenceId(f"sequence-{i}")
            repository._save(sequence)

        objs = repository._load_all()
        assert len(objs) == 10
        ids = [x.id for x in objs[:3]]
        repository._delete_many(ids)

        assert len(repository._load_all()) == 7

    @pytest.mark.parametrize("repo", [_SequenceFSRepository, _SequenceSQLRepository])
    def test_search(self, tmpdir, sequence, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._delete_all()

        for i in range(10):
            sequence.id = SequenceId(f"sequence-{i}")
            sequence.owner_id = f"owner-{i}"
            repository._save(sequence)

        assert len(repository._load_all()) == 10

        objs = repository._search("owner_id", "owner-2")
        assert len(objs) == 1
        assert isinstance(objs[0], Sequence)

        objs = repository._search("owner_id", "owner-2", filters=[{"version": "random_version_number"}])
        assert len(objs) == 1
        assert isinstance(objs[0], Sequence)

        assert repository._search("owner_id", "owner-2", filters=[{"version": "non_existed_version"}]) == []

    @pytest.mark.parametrize("repo", [_SequenceFSRepository, _SequenceSQLRepository])
    def test_export(self, tmpdir, sequence, repo):
        repository = repo()
        repository.base_path = tmpdir
        repository._save(sequence)

        repository._export(sequence.id, tmpdir.strpath)
        dir_path = repository.dir_path if repo == _SequenceFSRepository else os.path.join(tmpdir.strpath, "sequence")

        assert os.path.exists(os.path.join(dir_path, f"{sequence.id}.json"))
