import os
from time import sleep
from random import uniform
import os
import zipfile
import csv


def read_first_line(file_temp, change_line):
    # If file does not exists
    if not os.path.exists(file_temp):
        with open(file_temp, 'w') as f_write:
            f_write.write(change_line)
            return False

    # If file exists
    with open(file_temp) as f_read:
        first_line = f_read.readline()
        print("FIRST LINE {} line".format(first_line))
        # If first line empty
        if not first_line:
            with open(file_temp, 'w') as f_write:
                f_write.write(change_line)
        return first_line


def write_first_line(file_temp, replace_first_line):
    with open(file_temp) as f:
        lines = f.readlines()

    lines[0] = replace_first_line

    with open(file_temp, "w") as f:
        f.writelines(lines)


def wait_only_after(file_temp, expected_line, change_line, times=60):
    # Will wait max 5 * 60 seconds
    current_line = ''
    for i in range(0, times):
        current_line = read_first_line(file_temp, change_line)
        # First time
        if not current_line:
            print("File just was created {} and added {}".format(file_temp, change_line))
            current_line = expected_line
            break
        if current_line == expected_line:
            print("Thread can start replace from file {} first line with {}".format(file_temp, change_line))
            write_first_line(file_temp, change_line)
            break
        else:
            print("current line is {} while expected {}".format(current_line, expected_line))
            print("Thread wait for first line from {} to have {}, currently: {}".format(file_temp,
                                                                                        expected_line, current_line))
            sleep(uniform(1, 5))
    return current_line == expected_line



def zipdir(zipfile_path, zipfile_name):
    # ziph is zipfile handle
    zipf = zipfile.ZipFile(os.path.join(zipfile_path, zipfile_name), 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(zipfile_path):
        for file in files:
            if file == zipfile_name:
                continue
            zipf.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(zipfile_path, '..')))
    print("zipfile_path and zipf")
    print(zipfile_path)
    print(zipf)
    zipf.close()

def generate_csv(path, headers, data):

    with open(path, 'w', encoding='UTF8') as f:

        # create writer object
        writer = csv.writer(f)

        # write the headers
        writer.writerow(headers)

        for row in data:
            writer.writerow(row)