# FTP-py
FTP Server implementation in Python

## Config

Most of the modules used should be included in a standard python instalation. The ttkthemes package and a third party themes pack is required for the GUI.

`pip install ttkthemes` 

` python3 -m pip install git+https://github.com/RedFantom/ttkthemes`

The installation can be verified by running `setup.py`

## Environment/Execution

The server and client reside in separate folders, please `cd` to those folders before running the scripts (You will need two terminals if running on one machine).

Client:

`cd Client`

`py GUI_Client.py` or `python GUI_Client.py`

Please do not use the CL client as its functionality has not been updated. The client can be used by interacting with the given buttons and supplying appropriate inputs in pop-ups. These buttons are selectively enabled/disabled: if a button is disabled it means that a prior action must be taken e.g. do a PASV before RETR.

Please do not use the CL client as its functionality has not been updated.

Server:

`cd Server`

`py FTP-Server.py` or `python FTP-Server.py`


### Firewall Settings

When tested on Windows, it is found that using port 21 as the listen port for the server causes Windows firewall to prevent passive data connections being made (PORT will still work). In order to use passive connections, either change the port used or instead temporarily disable Windows firewall.

## Docs

The group report has been included in the root folder of this repo. The report consists of the main body and appendicies of screenshots and wireshark captures.