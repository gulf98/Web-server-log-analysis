# Web-server-log-analysis
Course: Python QA Engineer - 2022 (OTUS).\
Homework 10: Web server log analysis.

The script parses and collects metrics from logs named *.log.\
The result of the analysis is output to the console and to the report.json file.

To start, you need to run the command:\
python log_parser.py --file={*.log} or --folder={folder_name}

The file parameter specifies the name of the file.\
The folder parameter specifies the directory with the log files.

Parameter explanations:
- --file and --folder options are mutually exclusive
- be sure to specify one of the parameters
- if you specify --file without a value, the access.log value will be substituted
- if you specify --folder without a value, the value ./ will be substituted

Log file format:\
%h %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i" %D\
%h - remote host name\
%t - request receipt time\
%r - request type, content and version\
%s - HTTP status code\
%b - number of bytes returned by the server\
%{Referer} - request source URL\
%{User-Agent} - HTTP header containing information about the request\
%D - request duration in milliseconds