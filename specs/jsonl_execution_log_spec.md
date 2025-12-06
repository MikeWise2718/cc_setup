# jsonl exuction log for adws workflows
- There should be an environment variable ADW_LOGGING_DIR that specfies the location of a log file in jsonl
- at script startup a json enttry should be added to that log with the name of the script, the time, the directory name of the project, and any parameters it was invoked with.
- at script end a json enttry should be added to that log with the name of the script, the time, the directory name of the project, the execution time, and which files it created and modified. Token consumption and if ran in max mode or licensing mode should be included. 
- Other important relevent information that may have been overlooked in this spec should also be included in both the start and end entries.
- this functionality should be added to scripts in iso_v1 only, scripts in basic and iso should be left alone.

# changes
- lnav compatiblity
- entries will be made by all scripts even when a script calls another script
- if a script calls one or more other scripts, there should be a list of those invoked, the times of their invokation, the time the process ended, and the return status
- Instead of an environment variable, I would like a two-stage configuration file hosted in local directory .adw or global ones in my home director .adw 
- local directory settings should take precidence ver global settings.
- Both directories will have json specified settings in a file settings.json. 
- Initially I want the following settings:
   - Logging directory (absolute or releative path)
   - verbosity (0=low,1=more)
      - at verbosity 0 it will not print out all files created or changed, but just how many of each
      - at verbosity 1 it will print out the names of all files
      - at verbosity 2 it will print out the names of all files, their lenths, and for the ones that changed their diff statistics
   - Claude key/max use (should have three settings, apikey, max, or default (with no entry being interpreted as default). 
