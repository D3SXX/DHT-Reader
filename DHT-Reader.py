#DHT Reader v0.1 by DSXX

try:
    import os
    import time
    from datetime import datetime
    import configparser
    import board
    import adafruit_dht
    import matplotlib.pyplot as plt
    import xlsxwriter
except:
    print("Some dependencies are missing. Please run the following command to install them:")
    print("pip3 install adafruit_blinka adafruit-circuitpython-dht matplotlib xlsxwriter")
    raise SystemExit()

def highlight_word(word, flag):
    # Set the color based on the input parameter
    if flag == 3:
        color_code = '\033[97m'  # White
    elif flag == 0:
        color_code = '\033[91m'  # Red
    elif flag == 1:
        color_code = '\033[92m'  # Green
    elif flag == 4:
        color_code = '\033[93m'  # Yellow
    else:
        color_code = '\033[0m'  # Default color (no highlighting)
    print(f"{color_code}{word}\033[0m", end="")

def clear_screen():

    os_name = os.name
    # For windows
    if os_name == 'nt':
        _ = os.system('cls')
 
    # For posix
    else:
        _ = os.system('clear')

def delay_wait(time_s):
    print("\nThe next reset will be in %d" %time_s, end='..', flush=True)
    for i in reversed(range(time_s)):
        print("%d" % i, end= '..', flush=True)
        time.sleep(1)
    print("Resetting!")

# A converter for dht name
# Also if flag is set to 1 it checks for correct name
def dht_convert(device, flag=None):
    if device == "DHT11":
        if flag == 1:
            highlight_word("\nSomething went wrong, is there enought entries in your config file?\n",0)
            raise Exception
        return adafruit_dht.DHT11
    elif device == "DHT22":
        if flag == 1:
            highlight_word("\nSomething went wrong, is there enought entries in your config file?\n",0)
            raise Exception        
        return adafruit_dht.DHT22
    elif device == "DHT21":
        if flag == 1:
            highlight_word("\nSomething went wrong, is there enought entries in your config file?\n",0)
            raise Exception
        return adafruit_dht.DHT21
    elif device == adafruit_dht.DHT11:
        return "DHT11"
    elif device == adafruit_dht.DHT22:
        return "DHT22"
    elif device == adafruit_dht.DHT21:
        return "DHT21"
    else:
        print("Something went wrong, check your config file!")
        raise Exception("Unknown device " + str(device)) 

def check_config():
    config_file = 'dhtreader.ini'
    device = "DHT11"
    pin = board.D4
    allowtxt = 0
    allowxl = 0
    allowpng = 0
    delay_sec = 5
    reset_data = 0
    allow_pulseio = 1
    if not os.path.isfile(config_file):
        create_new_config = input(f"Config file '{config_file}' does not exist.\nDo you want to create a new config file? (y/n): ")
        if create_new_config.lower() == 'y':
            # Create a new config file
            config = configparser.ConfigParser()
            tmp = 0
            print("Type y or n, or press enter to select the default option")
            while True:
                tmp = str(input("Choose any model of DHT which you would like to read\n1. DHT11\n2. DHT22\n3. DHT21/AM2301\n"))
                if input == '1':
                    break
                elif input == '2':
                    device = "DHT22"
                    break
                elif input == '3':
                    device = "DHT21"
                    break
                else:
                    break
            while True:
                tmp = str(input("Choose any pin\n1. D4\n2. D5\n3. D17\n4. D22\n5. D27\n"))
                if input == '1':
                    break
                elif input == '2':
                    pin = board.D5
                    break
                elif input == '3':
                    pin = board.D17
                    break
                elif input == '4':
                    pin = board.D22
                    break
                elif input == '5':
                    pin = board.D27
                    break
                else:
                    break
                            
            tmp = str(input("Write data in txt file? (default is no)"))
            if tmp.lower() == "y":
                allowtxt = 1
            tmp = str(input("Write data in excel file? (default is no)"))
            if tmp.lower() == "y":
                allowxl = 1
            tmp = input("Make a DHT_Reader.png image with temperature and humidity?")
            if tmp.lower() == "y":
                allowpng = 1
            while True:
                tmp = str(input("Type any delay value in seconds (default is 5)"))
                if tmp == "":
                    break
                elif tmp.isdecimal() == True:
                    if int(tmp) > 0:
                        delay_sec = int(tmp)   
                        break
                else:
                    print("Wrong input! Use any numbers that are greater than 0")
            tmp = input("Use pulseio(Change this option only if you can't read any data, default is yes)")
            if tmp.lower() == "n":
                allow_pulseio = 0
            tmp = str(input("Would you like to reset data every time the program is run?"))
            if tmp.lower() == "y":
                reset_data = 1
            config['dhtreader'] = {
                'DeviceModel':device,
                'Pin':pin,
                'SaveDataInTxt':allowtxt,
                'RecordToExcel':allowxl,
                'CreateImage':allowpng,
                'DelayTime':delay_sec,
                'UsePulseio':allow_pulseio,
                'ResetData':reset_data
            }

            with open(config_file, 'w') as file:
                config.write(file)
            #change device type so the program will work
            device = dht_convert(device)
            print(f"New config file '{config_file}' created.")
        else:
            print("No new config file created, using default values.")
            #change device type so the program will work
            device = dht_convert(device)
    else:
        # Create a ConfigParser object
        config = configparser.ConfigParser()

        try:
            # Read the configuration file
            config.read(config_file)

            # Access the values
            device = config.get('dhtreader','DeviceModel')
            pin = config.get('dhtreader','Pin')
            allowtxt = config.getint('dhtreader', 'SaveDataInTxt')
            allowxl = config.getint('dhtreader', 'RecordToExcel')
            allowpng = config.getint('dhtreader','CreateImage')
            delay_sec = config.getint('dhtreader', 'DelayTime')
            allow_pulseio = config.getint('dhtreader','UsePulseio')
            reset_data = config.getint('dhtreader','resetdata')
            
            # Convert "device" from str to appropriate type
            device = dht_convert(device)
                
        except configparser.Error as e:
            print(f"Error reading the config file: {e}")
    return allowtxt, allowxl, allowpng, delay_sec, allow_pulseio, reset_data, device, pin

def read_config(txt,xl,img,delay,pulseio,reset_data,device,pin):
    list_delay = 0.3 # Change to make listing longer or faster 
    txt_mode = "ON"
    xl_mode = "ON"
    img_mode = "ON"
    reset_data_mode = "NOT RESET"
    pulseio_mode = "ENABLED"
    if txt == 0:
        txt_mode = "OFF"
    if xl == 0:
        xl_mode = "OFF"
    if img == 0:
        img_mode = "OFF"
    if reset_data == 1:
        reset_data_mode = "RESET"
    if pulseio == 0:
        pulseio_mode = "DISABLED"
    print("Using ", end="") 
    highlight_word(dht_convert(device,1),4) 
    print(" connected to the pin ", end="") 
    highlight_word(str(pin) + "\n",4)
    time.sleep(list_delay)
    print("Writing to a txt file is ", end="")
    highlight_word(txt_mode + "\n",txt) #txt
    time.sleep(list_delay)
    print("Writing to an Excel file ", end="")
    highlight_word(xl_mode + "\n",xl) #excel
    time.sleep(list_delay)
    print("Creating a PNG image is ", end="")
    highlight_word(img_mode + "\n",img) #img
    time.sleep(list_delay)
    print("The delay is set to ", end="")
    highlight_word(delay,4)
    print(" seconds")
    time.sleep(list_delay)
    print("Pulseio is ",end="")
    highlight_word(pulseio_mode + "\n",pulseio)
    time.sleep(list_delay)
    print("The data will be ", end="")
    highlight_word(reset_data_mode + "\n",reset_data)
    if reset_data == 1:
        file_names = ["T_and_H.txt", "xl_tmp"]
        for file_name in file_names:
            try:
                os.remove(file_name)
                print(f"File '{file_name}' deleted successfully.")
            except FileNotFoundError:
                print(f"File '{file_name}' not found.")
            except PermissionError:
                print(f"Unable to delete file '{file_name}'. Permission denied.")
            except Exception as e:
                print(f"An error occurred while deleting file '{file_name}': {str(e)}")
    
    time.sleep(list_delay)
    print(r'''
__  _  _ _____   ___ ___  __  __  ___ ___  
| _\| || |_   _| | _ | __|/  \| _\| __| _ \ 
| v | >< | | |   | v | _|| /\ | v | _|| v / 
|__/|_||_| |_|   |_|_|___|_||_|__/|___|_|_\ 
    ''')
    delay_wait(4)

# Create an Excel file and an Image.
def write_to_xl(temperature, humidity, flag):
    # flag == 1 -> allow only xl, flag == 2 allow only image, flag == 3 allow both
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
    df = [date_time, temperature, humidity]

    # Check if 'xl_tmp' temporary file exists, create it if not
    try:
        with open("xl_tmp", "a") as f:
            f.write("\n" + " ".join(str(x) for x in df))
    except FileNotFoundError:
        with open("xl_tmp", "w") as f:
            f.write(" ".join(str(x) for x in df))

    # Read the contents of 'xl_tmp' file
    with open("xl_tmp", "r") as f:
        tmp_xl = f.readlines()

    a = len(tmp_xl)
    

    stroftime = []
    strofT = []
    strofH = []
    
    # Process each line in 'xl_tmp' and extract date, time, temperature, and humidity
    for entry in tmp_xl:
        data = entry.split()
        if len(data) >= 3:  # Check if line has expected number of elements
            stroftime.append(data[0] + " " + data[1])  # Combine date and time
            strofT.append(data[2])
            strofH.append(data[3])

    if flag == 2 or flag == 3:
        start_time = time.time()
        # Plot the humidity and temperature data
        img_name = "DHT_Reader.png"
        # Create a figure and axis objects
        fig, ax = plt.subplots()
    
        # Generate dynamic x values based on stroftime length
        x = range(len(stroftime))
    
        # Plot temperature line
        ax.plot(x, strofT, label='Temperature')
        # Plot humidity line
        ax.plot(x, strofH, label='Humidity')
        # Add labels and legend
        ax.set_xlabel('Amount of reads')
        ax.legend()
        plt.savefig(img_name, dpi=300, bbox_inches='tight')
        full_time = time.time() - start_time
        img_size = os.path.getsize(img_name)
        print(f"\nAn image {img_name} ({img_size} bytes) was created in {full_time:.2f} seconds")
        if flag == 2:
            return 0

    # Create an Excel workbook and worksheet
    print("\nThere are %d entries in the Excel\nThe amount of items: %d" % (a, a * 3))
    print("The data that was added to the Excel:")
    print(df)
    workbook = xlsxwriter.Workbook('T_and_H.xlsx', {'strings_to_numbers': True})
    worksheet = workbook.add_worksheet()
    datetime_format = workbook.add_format({'num_format': 'dd/mm/yyyy, hh:mm:ss'})
    number_format = workbook.add_format({'num_format': '0'})

    stroflegend = ['Date and Time', 'Temperature', 'Humidity']
    for col_num, data in enumerate(stroflegend):
        worksheet.write(0, col_num, data)

    # Write the data to the worksheet
    for row_num, data in enumerate(stroftime):
        worksheet.write(row_num + 1, 0, data, datetime_format)

    for row_num, data in enumerate(strofT):
        worksheet.write(row_num + 1, 1, int(data), number_format)

    for row_num, data in enumerate(strofH):
        worksheet.write(row_num + 1, 2, int(data), number_format)

    # Create charts for temperature and humidity
    chart = workbook.add_chart({'type': 'line'})
    chart.add_series({'values': '=Sheet1!$B$2:$B$%d' % a})
    chart.set_title({"name": "Temperature"})
    worksheet.insert_chart('E1', chart)

    chart2 = workbook.add_chart({'type': 'line'})
    chart2.add_series({'values': '=Sheet1!$C$2:$C$%d' % a})
    chart2.set_title({"name": "Humidity"})
    worksheet.insert_chart('E17', chart2)

    # Close the workbook
    workbook.close()
    
def write_to_txt(temperature, humidity):
    # Record data in a text file
    with open("T_and_H.txt", "a") as f:
        # Check what is the time right now
        now = datetime.now()
        # Format it for better readability
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        # Make a structure that holds all the data
        entry = f"{date_time} Temperature: {temperature} Humidity: {humidity}\n"
        # Write this structure to a file
        f.write(entry)

    print(f"\nThe data that was added to the T_and_H.txt:\n{date_time} Temperature: {temperature} Humidity: {humidity}")


allowtxt, allowxl, allowpng, delay_sec, allow_pulseio, data_reset, device, pin = check_config()

read_config(allowtxt, allowxl, allowpng, delay_sec, allow_pulseio, data_reset, device, pin)

# Initial the dht device, with data pin connected to:
pin_value = getattr(board, "D" + str(pin))
dhtDevice = device(pin_value, bool(allow_pulseio))
#dhtDevice = device("board.D" + str(pin))
#pin = board. + "D" + str(pin)
#dhtDevice = device(pin)
while True:
    clear_screen()
    try:
        #start_time, end_time and time_took are for calculation the time of delay of a sensor
        humidity, temperature = None, None
        start_time = time.time()
        while humidity == None or temperature == None: #make readings until there are any values
            try:
                temperature = dhtDevice.temperature
                humidity = dhtDevice.humidity
            except RuntimeError as error:
                # Errors happen fairly often, DHT's are hard to read, just keep going
                if time.time() - start_time >= 5 and time.time() - start_time <= 7:
                    print("Hmm, it takes too much time...\nPerhaps try to toggle pulseio or try to disable 1-wire mode in raspi-config\nThe error from the DHT Library is:\n")
                    print(error.args[0])
                elif time.time() - start_time >= 7:
                    print(error.args[0])
                time.sleep(2.0)
                continue
        
        end_time = time.time()
        time_took = end_time - start_time
        print("Temperature: {:.1f} | Humidity: {:.1f}".format(temperature,humidity))
        print(f"The delay for sensor is {time_took:.3f} seconds. ")

        if allowtxt == 1:
            write_to_txt(temperature,humidity)
        if allowxl == 1 or allowpng == 1:
            flat = 0
            if allowxl == 1 and allowpng == 1:
                flag = 3
            elif allowxl == 1 and allowpng == 0:
                flag = 1
            else:
                flag = 2
            write_to_xl(temperature,humidity,flag)
            
        delay_wait(delay_sec)
    except Exception as error:
            dhtDevice.exit()
            raise error
    except KeyboardInterrupt:
            print("Quitting the program!")
            raise SystemExit
    
