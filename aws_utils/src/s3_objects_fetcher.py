import csv
import datetime
import os

import boto3


class S3ObjectFetcher():
    def __init__(self,
                 bucket_name='arbitrage-bot',
                 object_type='ticker',
                 record_version='0',
                 fieldnames=[]
                 ):
        s3 = boto3.resource('s3')
        self.bucket = s3.Bucket(bucket_name)
        self.object_type=object_type
        self.record_version=record_version
        self.fieldnames=fieldnames

    def get_output_file(self,
                        timedelta_days,
                        timedelta_hours,
                        time_filter="%Y-%m"):
        filename_prefix = datetime.datetime.utcnow() - datetime.timedelta(days=timedelta_days, hours=timedelta_hours)
        prefix = '{0}/{0}_v{1}_{2}'.format(self.object_type,
                                           self.record_version,
                                           filename_prefix.strftime(time_filter))
        local_filepath = os.getcwd().replace("data_engineering", os.path.join("data/windows", self.object_type))
        output_file = os.path.join(local_filepath, prefix + '.csv')

        return output_file, prefix

    def get_data(self, prefix):
        lines = []
        for obj in self.bucket.objects.filter(Prefix=prefix):
            response = obj.get()
            body = response['Body'].read().decode('utf-8')
            body_lines = body.split('\n')
            for body_line in body_lines:
                lines.append(body_line)
        return lines

    def write_data(self, output_file, lines):
        output_dir = os.path.dirname(output_file)
        os.makedirs(output_dir, exist_ok=True)

        if os.path.exists(output_file):
            append_write = 'a'  # append if already exists
        else:
            append_write = 'w'  # make a new file if not

        with open(output_file, append_write) as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(self.fieldnames)
            for line in lines:
                if not self.is_header_line(line):
                    line = line.replace('\r', '')
                    # print(line.split(','))
                    writer.writerow(line.split(','))
                    # print(line)



    @staticmethod
    def is_header_line(line):
        return line.startswith('ask')