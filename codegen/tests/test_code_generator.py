import os

from src.code_generator import CodeGenerator


class TestCodeGenerator:
    def test_init(self):
        # Arrange
        openapi_file_path = "tests/data/sample.yaml"
        output_dir = "tests/data/sample_dir/"

        # Act
        code_generator = CodeGenerator(
            openapi_file_path=openapi_file_path,
            output_dir=output_dir,
            parameters=[
                "--use-union-operator",
                "--use-default-kwarg",
                "--use-double-quotes",
            ],
        )

        # Assert
        assert len(code_generator._imports) == 3
        assert len(code_generator._classes) == 3

    def test_execute(self):
        # Arrange
        openapi_file_path = "tests/data/sample.yaml"
        output_dir = "tests/data/sample_dir/"

        # Act
        CodeGenerator(
            openapi_file_path=openapi_file_path,
            output_dir=output_dir,
            parameters=[
                "--use-union-operator",
                "--use-default-kwarg",
                "--use-double-quotes",
            ],
        ).execute()

        # Assert
        with os.scandir(output_dir) as entries:
            files = [entry.name for entry in entries if entry.is_file()]
        assert "user.py" in files
        assert "user_create.py" in files
        assert "user_update.py" in files
        assert not os.path.exists("tests/data/sample_dir/temporary_model.py")
        assert not os.path.exists("tests/data/sample_dir/temporary_api.yaml")

    def test_init_with_include_models(self):
        # Arrange
        openapi_file_path = "tests/data/sample.yaml"
        output_dir = "tests/data/sample_dir/"
        include_models_dir = "tests/data/schemas/"

        # Act
        code_generator = CodeGenerator(
            openapi_file_path=openapi_file_path,
            output_dir=output_dir,
            parameters=[
                "--use-union-operator",
                "--use-default-kwarg",
                "--use-double-quotes",
            ],
            include_models_dir=include_models_dir,
        )

        # Assert
        assert len(code_generator._imports) == 3
        assert len(code_generator._classes) == 5

    def test_execute_with_include_models(self):
        # Arrange
        openapi_file_path = "tests/data/sample.yaml"
        output_dir = "tests/data/sample_dir/"
        include_models_dir = "tests/data/schemas/"

        # Act
        CodeGenerator(
            openapi_file_path=openapi_file_path,
            output_dir=output_dir,
            parameters=[
                "--use-union-operator",
                "--use-default-kwarg",
                "--use-double-quotes",
            ],
            include_models_dir=include_models_dir,
        ).execute()

        # Assert
        with os.scandir(output_dir) as entries:
            files = [entry.name for entry in entries if entry.is_file()]
        assert "user.py" in files
        assert "user_create.py" in files
        assert "user_update.py" in files
        assert "other.py" in files
        assert "other2.py" in files
        assert not os.path.exists("tests/data/sample_dir/temporary_model.py")
        assert not os.path.exists("tests/data/sample_dir/temporary_api.yaml")
