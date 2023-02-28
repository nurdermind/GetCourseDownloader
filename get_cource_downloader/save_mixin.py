import os


class SaveMixin:

    @staticmethod
    def _get_output_dir_path(output_path, title=None):
        if not output_path:
            output_path = title
        else:
            output_path = os.path.join(output_path, title)
        SaveMixin._create_output_path(output_path)
        return output_path

    @staticmethod
    def _create_output_path(output_path):
        os.makedirs(output_path, exist_ok=True)
