import os

from src.code_generator import CodeGenerator


class TestCodeGenerator:
    def test_init(self):
        # Arrange
        openapi_file_name = "tests/sample.yaml"
        output_dir = "tests/sample_dir/"

        # Act
        code_generator = CodeGenerator(openapi_file_name, output_dir)

        # Assert
        assert len(code_generator._imports) == 3
        assert len(code_generator._classes) == 3

    def test_execute(self):
        # Arrange
        openapi_file_name = "tests/sample.yaml"
        output_dir = "tests/sample_dir/"

        # Act
        CodeGenerator(openapi_file_name, output_dir).execute()

        # Assert
        with os.scandir(output_dir) as entries:
            files = [entry.name for entry in entries if entry.is_file()]
        assert "user.py" in files
        assert "user_create.py" in files
        assert "user_update.py" in files
