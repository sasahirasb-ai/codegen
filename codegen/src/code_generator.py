import ast
import os
import re
import subprocess  # nosec B404
from copy import copy
from pathlib import Path
from typing import List


class CodeGenerator:
    output_dir: str
    _source_code: str
    _imports: list[ast.Import | ast.ImportFrom]
    _classes: list[ast.ClassDef]

    def __init__(self, openapi_file_name: str, output_dir: str):
        self.output_dir = output_dir
        temporary_filename: str = "temporary_model.py"
        temporary_filepath = os.path.join(output_dir, temporary_filename)
        self._generate_temporary_file(temporary_filepath, openapi_file_name)
        source_code = self._import_temporary_file(temporary_filepath)
        self._imports = self._extract_imports(source_code)
        self._classes = self._extract_classes(source_code)
        self._source_code = source_code
        os.remove(temporary_filepath)

    def filter_import_node(
        self, import_node: ast.Import | ast.ImportFrom, used_imports: set[str]
    ):
        new_node = copy(import_node)
        new_node.names = []
        if names := [
            name
            for name in import_node.names
            if (name.asname if name.asname else name.name) in used_imports
        ]:
            new_node.names = names

        return new_node if new_node.names else None

    def execute(self):
        os.makedirs(self.output_dir, exist_ok=True)

        for class_node in self._classes:
            used_imports = self._get_imports_for_class(class_node)
            import_nodes = [
                self.filter_import_node(import_node, used_imports)
                for import_node in self._imports
            ]
            class_source_code = ast.get_source_segment(self._source_code, class_node)
            output_path = os.path.join(
                self.output_dir, f"{self._convert_to_snake_case(class_node.name)}.py"
            )

            if not class_source_code:
                continue

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join([ast.unparse(node) for node in import_nodes if node]))
                f.write("\n\n\n")
                f.write(class_source_code)
                f.write("\n")

    def _get_imports_for_class(self, class_node: ast.ClassDef):
        used_names = set()
        for node in ast.walk(class_node):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
        return used_names

    def _generate_temporary_file(self, temporary_filename: str, openapi_file_name: str):
        openapi_file_path = Path(openapi_file_name).resolve(strict=True)
        temporary_file_path = Path(temporary_filename).resolve()
        subprocess.run(
            [
                "datamodel-codegen",
                "--input",
                openapi_file_path,
                "--input-file-type",
                "openapi",
                "--output",
                temporary_file_path,
                "--use-union-operator",
                "--use-default-kwarg",
                "--use-field-description",
                "--use-double-quotes",
            ],
            check=True,
        )  # nosec B603, B607

    @staticmethod
    def _import_temporary_file(temporary_filename: str):
        with open(temporary_filename, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def _extract_imports(source_code: str) -> List[ast.Import | ast.ImportFrom]:
        """ソースコードからimport文を抽出し、そのテキストリストを返す"""
        tree = ast.parse(source_code)
        return [
            node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))
        ]

    @staticmethod
    def _extract_classes(source_code: str) -> List[ast.ClassDef]:
        """ソースコードからトップレベルのクラス定義のASTノードを抽出する"""
        tree = ast.parse(source_code)
        return [node for node in tree.body if isinstance(node, ast.ClassDef)]

    def _convert_to_snake_case(self, string: str):
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string)
        s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
        return s2.lower()
