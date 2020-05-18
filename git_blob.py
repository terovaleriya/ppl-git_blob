import zlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import typing as tp


class BlobType(Enum):
    """Helper class for holding blob type"""
    COMMIT = b'commit'
    TREE = b'tree'
    DATA = b'blob'

    @classmethod
    def from_bytes(cls, type_: bytes) -> 'BlobType':
        for member in cls:
            if member.value == type_:
                return member
        assert False, f'Unknown type {type_}'


@dataclass
class Blob:
    """Any blob holder"""
    type_: BlobType
    content: bytes


@dataclass
class Commit:
    """Commit blob holder"""
    tree_hash: str
    parents: tp.List[str]
    author: str
    committer: str
    message: str


@dataclass
class Tree:
    """Tree blob holder"""
    children: tp.Dict[str, Blob]


def read_blob(path: Path) -> Blob:
    """
    Read blob-file, decompress and parse header
    :param path: path to blob-file
    :return: blob-file type and content
    """
    data = path.read_bytes()
    raw = zlib.decompress(data)
    x = raw.find(b' ')
    fmt = raw[0:x]
    y = raw.find(b'\x00', x)
    size = int(raw[x:y].decode("ascii"))
    # if size != len(raw) - y - 1:
    #     raise Exception("Malformed object {0}: bad length")
    if fmt == b'commit':
        c = BlobType.COMMIT
    elif fmt == b'tree':
        c = BlobType.TREE
    elif fmt == b'blob':
        c = BlobType.DATA
    # else:
    #     raise Exception("Unknown type %s for object %s".format(fmt.decode("ascii")))
    return Blob(c, raw[y + 1:])


def traverse_objects(obj_dir: Path) -> tp.Dict[str, Blob]:
    """
    Traverse directory with git objects and load them
    :param obj_dir: path to git "objects" directory
    :return: mapping from hash to blob with every blob found
    """
    hash_to_blob: tp.Dict[str, Blob] = {}
    paths = list(obj_dir.rglob("*"))
    for path in paths:
        cur_paths = list(path.rglob("*"))
        for to_blob in cur_paths:
            hash_to_blob.update({str(path.name) + str(to_blob.name): read_blob(to_blob)})
    return hash_to_blob


def parse_commit(blob: Blob) -> Commit:
    """
    Parse commit blob
    :param blob: blob with commit type
    :return: parsed commit
    """
    data = blob.content
    data = data.decode("ascii")
    # data = data.split()
    # tree_hash_start = (data.find("tree"))
    # parent_start = data.find("parent")
    # author_start = data.find("author")
    # committer_start = data.find("committer")
    # if parent_start == -1:
    #     parent_start = author_start
    # tree_hash = data[tree_hash_start + len("tree"): parent_start].strip().strip("\n")
    # parents = data[parent_start + len("parent") : author_start].strip().strip("\n").split() if parent_start else []
    # author = str(data[author_start + len("author") : committer_start]).strip().strip("\n")
    # committer_and_message = str(data[committer_start + len("committer"):]).strip().strip("\n")
    # committer, message = committer_and_message.split("\n\n")
    header, message = data.split("\n\n")
    lines = header.split("\n")
    t_index = 0
    p_index = 1
    a_index = 2
    c_index = 3
    tree_hash = lines[t_index][len("tree"):].strip().strip("\n")
    if len(lines) > 3:
        parents = lines[p_index][len("parent"):].strip().strip("\n").split()
    else:
        parents = []
        a_index -= 1
        c_index -= 1
    author = (lines[a_index][len("author"):]).strip().strip("\n")
    committer = (lines[c_index][len("committer"):]).strip().strip("\n")
    message = message.strip().strip("\n")

    return Commit(tree_hash, parents, author, committer, message)


def parse_tree(blobs: tp.Dict[str, Blob], tree_root: Blob, ignore_missing: bool = True) -> Tree:
    """
    Parse tree blob
    :param blobs: all read blobs (by traverse_objects)
    :param tree_root: tree blob to parse
    :param ignore_missing: ignore blobs which were not found in objects directory
    :return: tree contains children blobs (or only part of them found in objects directory)
    NB. Children blobs are not being parsed according to type.
        Also nested tree blobs are not being traversed.
    """


path = Path("/Users/racine/Library/Mobile Documents/com~apple~CloudDocs/fmkn-spring-2020/git_blob/objects")


def find_initial_commit(blobs: tp.Dict[str, Blob]) -> Commit:
    """
    Iterate over blobs and find initial commit (without parents)
    :param blobs: blobs read from objects dir
    :return: initial commit
    """
    blobs = traverse_objects(path)
    for item in blobs.items():
        pair, blob = item
        # print(blob.type_)
        if blob.type_ == BlobType.COMMIT:
            commit = parse_commit(blob)
            # print(type(answer))
            if not commit.parents:
                return commit
            else:
                continue


def search_file(blobs: tp.Dict[str, Blob], tree_root: Blob, filename: str) -> Blob:
    """
    Traverse tree blob (can have nested tree blobs) and find requested file,
    check if file was not found (assertion).
    :param blobs: blobs read from objects dir
    :param tree_root: root blob for traversal
    :param filename: requested file
    :return: requested file blob
    """

# print(path.parent)
# Paths = list(path.rglob("*"))
# for path in Paths:
#     print(list(path.rglob("*")))


# print(type(parse_commit(blob)))
# print(find_initial_commit(traverse_objects(path)))
# print(traverse_objects(path))
# print(parse_commit(blob))

# print(find_initial_commit())
