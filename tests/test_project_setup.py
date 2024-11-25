# import os
# import shutil
# from pathlib import Path
# from typing import List, Tuple
#
# # this is GitPython
# import git
# import pytest
#
# import project_setup as ps
#
#
# @pytest.mark.parametrize(
#     "name, expected",
#     [
#         ("My Project", "my_project"),
#         ("My-Project", "my_project"),
#         ("My_Project", "my_project"),
#         ("My_Pro-ject", "my_pro_ject"),
#         ("my_project", "my_project"),
#         ("", ""),
#     ],
# )
# def test_make_name_safe(name: str, expected: str):
#     assert ps.make_name_safe(name) == expected
#
#
# @pytest.mark.parametrize(
#     "file_path, expected",
#     [
#         (Path("test.png"), False),
#         (Path("test.jpg"), False),
#         (Path("test.jpeg"), False),
#         (Path(".DS_Store"), False),
#         (Path("project_setup.py"), False),
#         (Path("great_idea.py"), True),
#         (Path("science.txt"), True),
#         (Path("new_ideas.md"), True),
#     ],
# )
# def test_valid_file_predicate(file_path: Path, expected: bool):
#     assert ps.valid_file_predicate(file_path) == expected
#
#
# @pytest.mark.parametrize(
#     "repo_url, expected_output",
#     [
#         (
#             "https://github.com/example/good-idea.git",
#             "good_idea",
#         ),
#         (
#             "https://github.com/example/bet-ter-id_ea.git",
#             "bet_ter_id_ea",
#         ),
#     ],
# )
# def test_get_package_name(
#     repo_url: str,
#     expected_output: str,
# ):
#     assert ps.get_package_name(repo_url) == expected_output
#
#
# @pytest.mark.parametrize(
#     "file_contents, replacement_tuple, expected",
#     [
#         # old texts exists and is replaced
#         (
#             "This is a file\nwith old_text\nand more text\n",
#             [("old_text", "new_text")],
#             True,
#         ),
#         # old text does not exist
#         ("This is a file\nwith some text\nand more text\n", [("old_text", "new_text")], False),
#     ],
# )
# def test_replace_file_contents(
#     file_contents: str,
#     replacement_tuple: List[Tuple[str, str]],
#     expected: bool,
# ):
#     with open("tmp.txt", "w") as f:
#         f.write(file_contents)
#
#     actual_file_changed = ps.replace_file_contents(replacement_tuple, "tmp.txt")
#
#     with open("tmp.txt", "r") as f:
#         actual_contents = f.read()
#
#     old_str, new_str = replacement_tuple[0]
#     old_not_there = old_str not in actual_contents
#     new_there = new_str in actual_contents
#
#     os.remove("tmp.txt")
#
#     assert actual_file_changed == expected
#     if expected:
#         assert expected and old_not_there
#         assert expected and new_there
#     else:
#         assert old_str not in file_contents
#         assert file_contents == actual_contents
#
#
# def test_self_destruct(tmp_path):
#     tmp_path = Path(tmp_path)
#     shutil.copytree(os.getcwd(), tmp_path, dirs_exist_ok=True)
#     ps.self_destruct(Path(tmp_path))
#
#     # check if the files are removed
#     ps_exists = os.path.exists(tmp_path / Path("project_setup.py"))
#     ps_test_exists = os.path.exists(tmp_path / Path("tests/test_project_setup.py"))
#
#     # check if the dependencies are removed
#     with open(tmp_path / Path("requirements/dev.txt"), "r") as f:
#         dev_requirements = f.read()
#     with open(tmp_path / Path("requirements/test.txt"), "r") as f:
#         test_requirements = f.read()
#
#     assert not ps_exists
#     assert not ps_test_exists
#     assert "GitPython" not in dev_requirements
#     assert "GitPython" not in test_requirements
#
#
# @pytest.mark.parametrize(
#     "repo_url, expected",
#     [
#         ("https://www.github.com/amazing-org/really-great-project.git", "really-great-project"),
#     ],
# )
# def test_rtd_project_guess(repo_url: str, expected: str):
#     assert ps.rtd_project_guess(repo_url) == expected
#
#
# @pytest.mark.parametrize(
#     "repo_url, expected",
#     [
#         ("https://www.github.com/amazing-org/really-great-project.git", "amazing-org/really-great-project"),
#     ],
# )
# def test_codecov_project_guess(repo_url: str, expected: str):
#     assert ps.codecov_project_guess(repo_url) == expected
#
#
# @pytest.mark.parametrize(
#     "repo_url, levseq_dash",
#     [
#         ("https://www.github.com/good-org/amazing-project.git", "amazing_project"),
#     ],
# )
# def test_run_setup(repo_url: str, package_name: str, tmp_path):
#     def with_tmp(f):
#         return tmp_path / f
#
#     shutil.copytree(os.getcwd(), tmp_path, dirs_exist_ok=True)
#
#     repo = git.Repo(tmp_path)
#     # sign in to the repo
#     repo.git.config("user.email", "ssec@jhu.edu")
#     repo.git.config("user.name", "ssec")
#
#     ps.run_setup(repo_url, package_name, repo)
#
#     project_setup_py_exists = os.path.exists(with_tmp("project_setup.py"))
#     test_project_setup_py_exists = os.path.exists(with_tmp("tests/test_project_setup.py"))
#
#     template_package_name = ps.TEMPLATE_PACKAGE_NAME
#     template_url = ps.TEMPLATE_REPO_URL
#
#     # open pyproject.toml
#     with open(with_tmp("pyproject.toml"), "r") as f:
#         actual_pyproject = f.read()
#
#     # open README.md
#     with open(with_tmp("README.md"), "r") as f:
#         actual_readme = f.read()
#
#     with open(with_tmp(f"{package_name}/__init__.py"), "r") as f:
#         actual_app = f.read()
#
#     with open(with_tmp(f"{package_name}/util.py"), "r") as f:
#         actual_util = f.read()
#
#     # check file removal
#     assert not project_setup_py_exists
#     assert not test_project_setup_py_exists
#
#     # check pyproject.toml
#     assert template_url not in actual_pyproject
#     assert template_package_name not in actual_pyproject
#     assert package_name in actual_pyproject
#     assert repo_url in actual_pyproject
#
#     # check README.md
#     assert template_url not in actual_readme
#     assert template_package_name not in actual_readme
#     assert package_name in actual_readme
#     assert repo_url in actual_readme
#     assert ps.codecov_project_guess(repo_url) in actual_readme
#     assert ps.rtd_project_guess(repo_url) in actual_readme
#
#     # check the app.py
#     assert template_package_name not in actual_app
#     assert package_name in actual_app
#
#     # check the other.py
#     assert template_package_name not in actual_util
#     assert package_name not in actual_util
