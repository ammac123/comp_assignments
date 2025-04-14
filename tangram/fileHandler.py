


class FileHandler:
    @staticmethod
    def read_file(filename: str):
        try:
            with open(filename, 'r') as file:
                data = file.read()
            return data
        except FileNotFoundError:
            return []
