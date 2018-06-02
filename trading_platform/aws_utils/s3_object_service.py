import csv
import datetime
import os
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Generator

import boto3
import pandas
from boto3 import s3

from trading_platform.core.services.file_service import FileService
from trading_platform.exchanges.data.ticker import Ticker
from trading_platform.utils.datetime_operations import strftime_days, strftime_minutes


class S3ObjectService():
    def __init__(self, bucket_name='arbitrage-bot', object_type='ticker', object_version='0'):
        s3 = boto3.resource('s3')
        self.bucket = s3.Bucket(bucket_name)
        self.object_type = object_type
        self.object_version = object_version
        # self.max_workers = 1500
        self.max_workers = 2

    def get_output_file(self, timedelta_days: int, timedelta_hours: int, time_filter="%Y-%m"):
        filename_prefix = datetime.datetime.utcnow() - datetime.timedelta(days=timedelta_days, hours=timedelta_hours)
        prefix = '{0}/{0}_v{1}_{2}'.format(self.object_type,
                                           self.object_version,
                                           filename_prefix.strftime(time_filter))
        local_filepath = os.getcwd().replace("data_engineering", os.path.join("data/windows", self.object_type))
        output_file = os.path.join(local_filepath, prefix + '.csv')

        return output_file, prefix

    def get_data_for_object(self, object) -> str:
        """

        Args:
            prefix:

        Returns:

        """
        response: Dict = object.get()
        body: str = response['Body'].read().decode('utf-8')
        return body

    def write_data(self, output_file: str, lines: List[str], fieldnames: List[str]) -> None:
        output_dir: str = os.path.dirname(output_file)
        os.makedirs(output_dir, exist_ok=True)

        if os.path.exists(output_file):
            append_write: str = 'a'  # append if already exists
        else:
            append_write: str = 'w'  # make a new file if not

        with open(output_file, append_write) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            for line in lines:
                if not self.is_header_line(line):
                    line = line.replace('\r', '')
                    # print(line.split(','))
                    writer.writerow(line.split(','))
                    # print(line)

    def window_objects(self, output_dir: str, start_datetime: datetime.datetime, end_datetime: datetime.datetime,
                       timedelta: datetime.timedelta, multithreading: bool) -> None:
        """
        Windows objects according to timedelta, and writes to output_dir. If multithreading, data in each file is
        not in the same order.
        Args:
            output_dir:
            start_datetime:
            end_datetime:
            timedelta:
            multithreading:

        Returns:

        """
        start_windowing = time.time()
        FileService.create_dir_if_null(output_dir)

        def fetch_and_write_objects_with_datetime_prefix(datetime_instance):
            start = time.time()
            datetime_prefix = datetime_instance.strftime(strftime_days)
            file_prefix = '{0}_v{1}_{2}'.format(self.object_type, self.object_version, datetime_prefix)
            prefix = '{0}/{1}'.format(self.object_type, file_prefix)
            objects = self.bucket.objects.filter(Prefix=prefix)
            if multithreading:
                data_for_prefix = []
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = [executor.submit(self.get_data_for_object, object) for object in objects]
                    for future in as_completed(futures):
                        try:
                            object_body: str = future.result()
                            if object_body is not None:
                                for line in object_body.split('\n'):
                                    data_for_prefix.append(line)
                        except Exception:
                            traceback.print_exc()
            else:
                data_for_prefix: List = []
                for object in objects:
                    body: str = self.get_data_for_object(object)
                    for line in body.split('\n'):
                        data_for_prefix.append(line)

            if len(data_for_prefix) > 1:
                header: List[str] = data_for_prefix.pop(0)
                df: pandas.DataFrame = pandas.DataFrame(data_for_prefix, columns=header)

                # Deal with the case in which the file name doesn't match the version of the file, and a
                # case in which a file has data for multiple versions. See ticker_schema_version_changelog.md for details.
                def df_to_csv(version):
                    # has the nice side effect of dropping duplicate header rows
                    df_for_version = df[df['version'] == version]
                    file_prefix: str = '{0}_v{1}_{2}'.format(self.object_type, version, datetime_prefix)
                    # Example, ticker_v1_2018-05-01.csv
                    output_filename: str = '{0}.csv'.format(file_prefix)
                    output_filepath: str = os.path.join(output_dir, output_filename)
                    df_for_version.to_csv(output_filepath)

                map(df_to_csv, df['version'].unique())
            else:
                print('No objects found with prefix {0}'.format(prefix))

            end = time.time()
            print('Fetched and wrote data for {0} objects in {1} seconds'.format(len(list(objects.all())), (end - start)))

        generator = FileService.datetime_generator(start_datetime, end_datetime, timedelta)
        list(map(fetch_and_write_objects_with_datetime_prefix, generator))
        end_windowing = time.time()
        print('Windowed data in {0} seconds'.format(end_windowing - start_windowing))

    @staticmethod
    def is_header_line(line):
        return line.startswith('ask')
