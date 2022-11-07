import LogPrg
from pathlib import Path
from datetime import datetime


class ReadArchive(object):
    def __init__(self):
        try:
            self.logger = LogPrg.get_logger(__name__)
            self.init_arch()

        except Exception as e:
            self.logger.error(e)

    def init_arch(self):
        try:
            source_dir = Path('archive/')
            if not source_dir:
                Path.mkdir(source_dir)
            else:
                self.files_dir = source_dir.glob('*.csv')

                self.files_arr = []
                self.files_name_arr = []
                self.files_name_arr_sort = []
                self.count_files = 0

                for i in self.files_dir:
                    self.count_files += 1
                    self.files_arr.append(i)
                    self.files_name_arr.append(i.stem)
                    self.files_name_arr_sort.append(i.stem)

                self.files_name_arr_sort.sort(key=lambda date: datetime.strptime(date, "%d.%m.%Y"), reverse=True)

        except Exception as e:
            self.logger.error(e)