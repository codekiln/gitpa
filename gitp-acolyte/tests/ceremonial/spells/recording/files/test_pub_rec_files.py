from pathlib import Path

import pytest
from gitp_acolyte.ceremonial.spells.recording.files.pub_rec_files import (
    filter_files_to_publish,
)
from gitp_acolyte.ceremonial.spells.recording.files.rec_file_constants import (
    FILE_SUFFIXES_TO_SYNC,
    REC_DIR_SUBDIRS_TO_SEARCH,
)


def create_mock_files(base_path: Path, subdirs: list[str] = None):
    if subdirs is None:
        subdirs = [""]
    for subdir in subdirs:
        subdir_path = base_path / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
        for i, suffix in enumerate(FILE_SUFFIXES_TO_SYNC):
            (subdir_path / f"file{i}{suffix}").touch()
        (subdir_path / "file.invalid").touch()


@pytest.fixture
def mock_src_dir_root(tmp_path):
    create_mock_files(tmp_path)
    return tmp_path


@pytest.fixture
def mock_src_dir_subdirs(tmp_path):
    create_mock_files(tmp_path, REC_DIR_SUBDIRS_TO_SEARCH)
    return tmp_path


def test_filter_files_to_publish_all_valid_root(mock_src_dir_root):
    valid_files = filter_files_to_publish(mock_src_dir_root)
    expected_files = [
        mock_src_dir_root / f"file{i}{suffix}"
        for i, suffix in enumerate(FILE_SUFFIXES_TO_SYNC)
    ]
    assert sorted(valid_files, key=str) == sorted(expected_files, key=str)


def test_filter_files_to_publish_all_valid_subdirs(mock_src_dir_subdirs):
    valid_files = filter_files_to_publish(mock_src_dir_subdirs)
    expected_files = [
        mock_src_dir_subdirs / subdir / f"file{i}{suffix}"
        for subdir in REC_DIR_SUBDIRS_TO_SEARCH
        for i, suffix in enumerate(FILE_SUFFIXES_TO_SYNC)
    ]
    assert sorted(valid_files, key=str) == sorted(expected_files, key=str)


def test_filter_files_to_publish_some_invalid_root(mock_src_dir_root):
    valid_files = filter_files_to_publish(mock_src_dir_root)
    expected_files = [
        mock_src_dir_root / f"file{i}{suffix}"
        for i, suffix in enumerate(FILE_SUFFIXES_TO_SYNC)
    ]
    assert sorted(valid_files, key=str) == sorted(expected_files, key=str)


def test_filter_files_to_publish_some_invalid_subdirs(mock_src_dir_subdirs):
    valid_files = filter_files_to_publish(mock_src_dir_subdirs)
    expected_files = [
        mock_src_dir_subdirs / subdir / f"file{i}{suffix}"
        for subdir in REC_DIR_SUBDIRS_TO_SEARCH
        for i, suffix in enumerate(FILE_SUFFIXES_TO_SYNC)
    ]
    assert sorted(valid_files, key=str) == sorted(expected_files, key=str)


def test_filter_files_to_publish_all_invalid(tmp_path):
    (tmp_path / "file.invalid").touch()
    for subdir in REC_DIR_SUBDIRS_TO_SEARCH:
        subdir_path = tmp_path / subdir
        subdir_path.mkdir(parents=True, exist_ok=True)
        (subdir_path / "file.invalid").touch()
    valid_files = filter_files_to_publish(tmp_path)
    assert valid_files == []


def test_filter_files_to_publish_empty_list(tmp_path):
    for subdir in REC_DIR_SUBDIRS_TO_SEARCH:
        (tmp_path / subdir).mkdir(parents=True, exist_ok=True)
    valid_files = filter_files_to_publish(tmp_path)
    assert valid_files == []
