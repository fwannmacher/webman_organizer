# webman_organizer
As I always wanted to organize my WebMan games into alphabetical subfolders but I'm too lazy to change the WebMan's code itself then I wrote this script to do it for me. :D

This script downloads the XML file from the PS3 then make the necessary changes and last uploads the XML to the PS3. In addition the script will restart the PS3 as well.

IMPORTANT!
--------------------------------------------------------------------------------

As this is an external tool you have to run this script again after every time the XML is updated (a.k.a. the game list is refreshed).

Usage
--------------------------------------------------------------------------------

You just have to run the python script passing your PS3's IP as argument.

```terminal
python organize_xml.py 192.168.0.100
```
