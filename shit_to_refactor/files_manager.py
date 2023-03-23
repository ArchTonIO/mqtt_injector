"""
this module contains utilities to read and write data to txt files
"""


class FilesManager:
    """
    This class is used to manage txt files.
    """
    file_list = []

    @staticmethod
    def wirte_dict_to_file(
        file_name: str,
        data: dict,
        mode: str = "a"
    ) -> None:
        """
        This method is used to write a dictionary to a txt file.
        - Args:
            - file_name: the name of the file to write to
            - data: the data to write to the file
            - mode: the mode to open the file in (either "a" or "w")
        """
        with open(file_name, mode, encoding="utf-8") as file:
            limit = len(data.items())-1
            counter = 0
            for item in data.items():
                endchar = "\n" if counter < limit else ""
                file.write(f"{item[0]} = {item[1]}{endchar}")
                counter += 1

    @staticmethod
    def parse_dict_from_file(file_name: str, key: str = "") -> dict or str:
        """
        This method is used to parse a dictionary from a txt file.
        - Args:
            - file_name: the name of the file to parse from
            - key: the key to return the value of
        - Returns:
            - the dictionary parsed from the file
        """
        data = {}
        with open(file_name, "r", encoding="utf-8") as file:
            data = {}
            for line in file.readlines():
                line = line.strip()
                if line != "":
                    line = line.split("=")
                    if "[" in line[1]:
                        values = line[1].strip("[]").split(",")
                        values = [value.strip() for value in values]
                        data.update({line[0].strip(): values})
                    else:
                        data.update({line[0].strip(): line[1].strip()})
        if key != "":
            return data[key]
        return data

    @staticmethod
    def write_raw_text_to_file(
        file_name: str,
        data: str,
        mode: str = "a"
    ) -> None:
        """
        This method is used to write text to a txt file.
        - Args:
            - file_name: the name of the file to write to
            - data: the data to write to the file
            - mode: the mode to open the file in (either "a" or "w")
        """
        with open(file_name, mode, encoding="utf-8") as file:
            file.write(data)

    @staticmethod
    def parse_raw_text_from_file(file_name: str) -> str:
        """
        This method is used to parse text from a txt file.
        - Args:
            - file_name: the name of the file to parse from
        - Returns:
            - the text parsed from the file
        """
        with open(file_name, "r", encoding="utf-8") as file:
            return file.read()
