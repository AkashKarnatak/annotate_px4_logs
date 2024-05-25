# Annotate PX4 Logs

Annotate PX4 Logs is a web application for gathering annotated PX4 log files. The web application servers a random log file
to each user which they can review to identify and mark any anomalies.

https://github.com/AkashKarnatak/annotate_px4_logs/assets/54985621/c55a77db-4941-41ad-a369-115c9126e2ae

## Setup and Installation

### 1. Clone the repository:

   ```bash
   git clone https://github.com/AkashKarnatak/annotate_px4_logs.git
   ```

### 2. Navigate to the project directory:

   ```bash
   cd annotate_px4_logs
   ```

### 3. Create a virtual environment:

   ```bash
   python3 -m venv venv
   source ./venv/bin/activate
   ```

### 4. Install dependencies:

   ```bash
   pip3 install -r requirements.txt
   ```

### 5. Download log files:

Use the `./preprocessing/download_logs.py` script to download ulog files from PX4 flight review's
database. Download options are specified in the `./preprocessing/downloader_options.yaml` file.
Update the download parameters as desired and then run the following command:

   ```bash
   python3 preprocessing/download_logs.py
   ```

The above command will start downloading ulog files in the `./data/ulg_files` directory.

### 6. Create database:

Once you have downloaded the ulog files, you need to convert them to csv files for the
application to serve the log files to users. Running the following command will convert
the ulog files into csv files and store them in the `./data/csv_files` directory.

   ```bash
   python3 preprocessing/ulog2csv.py
   ```

### 7. Run the server:

Now you are all set and you can run the server by issuing the following command,

   ```bash
   python3 server/app.py
   ```

All the annotated files will be stored in csv format in the `./data/annotated_csv_files`
directory.

## Contributing

Contributions are welcome! If you find a bug, have an idea for an enhancement, or want to contribute in any way, feel free to open an issue or submit a pull request.

## License

This project is licensed under the AGPL3 License. For details, see the [LICENSE](LICENSE) file.
