# Annotate PX4 Logs

Annotate PX4 Logs is a web application for gathering annotated PX4 log files. The web application servers a random log file
to each user which they can review to identify and mark any anomalies.

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
Update the download parameters to your liking and then run the below command,

   ```bash
   python3 preprocessing/download_logs.py
   ```

The above command will start downloading ulog files in the `./data/ulg_files` directory.

### 6. Create database:

Once you have downloaded ulog files, you need to convert them to csv files in order for the
application to server log files to the users. Running the below command will convert the ulog
files into csv files and store it in `./data/csv_files` directory.

   ```bash
   python3 preprocessing/ulog2csv.py
   ```

### 7. Run the server:

Now you are all set and you can run the server by issuing the following command,

   ```bash
   python3 server/app.py
   ```

## Contributing

Contributions are welcome! If you find a bug, have an idea for an enhancement, or want to contribute in any way, feel free to open an issue or submit a pull request.

## License

This project is licensed under the AGPL3 License. For details, see the [LICENSE](LICENSE) file.
