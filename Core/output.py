import xlsxwriter
import matplotlib.pyplot as plt
import os
import mysql.connector
import sqlite3
import psycopg2

from . import get_time

#Creare a txt file    
def txt(temperature, humidity, filename):

    # Record data in a text file
    with open(filename, "a") as f:
        # Make a structure that holds all the data
        entry = f"{get_time.date()} Temperature: {temperature} Humidity: {humidity}\n"
        # Write this structure to a file
        f.write(entry)
    txt_size = os.path.getsize(filename)
    return_list = [f"{filename} ({txt_size} bytes) file was updated "]
    print(return_list[0])
    return return_list

# Create an Excel file and an Image
def xl(temperature, humidity,filename,tmp_folderpath,tmp_filename):
    df = [get_time.date(), temperature, humidity]
    str_time,str_t,str_h, len_tmp = get_tmp(tmp_filename,tmp_folderpath, df)

    # Create an Excel workbook and worksheet
    
    workbook = xlsxwriter.Workbook(filename, {'strings_to_numbers': True})
    worksheet = workbook.add_worksheet()
    datetime_format = workbook.add_format({'num_format': 'dd/mm/yyyy, hh:mm:ss'})
    number_format = workbook.add_format({'num_format': '0'})

    str_legend = ['Date and Time', 'Temperature', 'Humidity']
    for col_num, data in enumerate(str_legend):
        worksheet.write(0, col_num, data)

    # Write the data to the worksheet
    for row_num, data in enumerate(str_time):
        worksheet.write(row_num + 1, 0, data, datetime_format)

    for row_num, data in enumerate(str_t):
        worksheet.write(row_num + 1, 1, int(data), number_format)

    for row_num, data in enumerate(str_h):
        worksheet.write(row_num + 1, 2, int(data), number_format)

    # Create charts for temperature and humidity
    chart = workbook.add_chart({'type': 'line'})
    chart.add_series({'values': '=Sheet1!$B$2:$B$%d' % len_tmp})
    chart.set_title({"name": "Temperature"})
    worksheet.insert_chart('E1', chart)

    chart2 = workbook.add_chart({'type': 'line'})
    chart2.add_series({'values': '=Sheet1!$C$2:$C$%d' % len_tmp})
    chart2.set_title({"name": "Humidity"})
    worksheet.insert_chart('E17', chart2)

    # Close the workbook
    workbook.close()
    xl_size = os.path.getsize(filename)
    return_list = [f"An Excel file {filename} ({xl_size} bytes) with {len_tmp} entries was created"]
    print(return_list[0])
    return return_list 

def img(temperature, humidity,filename,tmp_folderpath,tmp_filename):
    start_time = get_time.time_s()

    tmp_filename = "img_tmp"
    df = [get_time.date(), temperature, humidity]
    str_time,str_t,str_h, len_tmp = get_tmp(tmp_filename,tmp_folderpath, df)
    
    # Plot the humidity and temperature data
        
    # Create a figure and axis objects
    fig, ax = plt.subplots()
    
    # Generate dynamic x values based on str_time length
    x = range(len(str_time))
    
    # Plot temperature line
    ax.plot(x, str_t, label='Temperature')
    # Plot humidity line
    ax.plot(x, str_h, label='Humidity')
    # Add labels and legend
    ax.set_xlabel('Amount of reads')
    ax.legend()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    full_time = get_time.time_s() - start_time
    img_size = os.path.getsize(filename)
    return_list = [f"An image {filename} ({img_size} bytes) was created in {full_time:.2f} seconds"]
    print(return_list[0])
    return return_list

def sql(temperature, humidity,data):
    timestamp = get_time.date()
    if data.db_type == "SQLite":
        conn = sqlite3.connect(data.sql_filename)
        cursor = conn.cursor()
        cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {data.device_model} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time DATETIME,
        temperature REAL,
        humidity REAL
    )
    
''')
        cursor.execute(f'''
            INSERT INTO {data.device_model} (time, temperature, humidity)
            VALUES (?, ?, ?)
        ''', (timestamp, temperature, humidity))
        conn.commit()
    return_list = [f"A {data.db_type} database {data.sql_filename} was updated"]
    return return_list


    

def read_tmp(filename,tmp_filepath, data):
    check_tmp_folder(tmp_filepath)
    # Check if 'xl_tmp' temporary file exists, create it if not
    try:
        with open(tmp_filepath + filename, "a") as f:
            f.write("\n" + " ".join(str(x) for x in data))
    except FileNotFoundError:
        with open(tmp_filepath + filename, "w") as f:
            f.write(" ".join(str(x) for x in data))

    # Read the contents of 'xl_tmp' file
    with open(tmp_filepath + filename, "r") as f:
        tmp_data = f.readlines()
        
    return tmp_data    

def get_tmp(filename,tmp_filepath, data):
    tmp_data = read_tmp(filename,tmp_filepath, data)
    str_time = []
    str_t = []
    str_h = []
    
    # Process each line in 'tmp_data' and extract date, time, temperature, and humidity
    for entry in tmp_data:
        data = entry.split()
        if len(data) >= 3:  # Check if line has expected number of elements
            str_time.append(data[0] + " " + data[1])  # Combine date and time
            str_t.append(data[2])
            str_h.append(data[3])
    return str_time, str_t, str_h, len(tmp_data)

def check_tmp_folder(filepath):
    check = os.path.exists(filepath)
    if not check:
        os.makedirs(filepath)
        return False
    else:
        return True
        
def startup_reset_data(data,program_data):
    tmp_files = [data.txt_filename,data.xl_filename,data.img_filename]
    if check_tmp_folder(program_data.tmp_folderpath):
        tmp_files = tmp_files + [program_data.tmp_folderpath + program_data.xl_tmp_filename,program_data.tmp_folderpath + program_data.img_tmp_filename]
    for filename in tmp_files:
        try:
            os.remove(filename)
            print(f"File '{filename}' deleted successfully")
        except FileNotFoundError:
            print(f"File '{filename}' not found")
        except PermissionError:
            print(f"Unable to delete file '{filename}'. Permission denied")
        except Exception as e:
            print(f"An error occurred while deleting file '{filename}': {str(e)}")    
