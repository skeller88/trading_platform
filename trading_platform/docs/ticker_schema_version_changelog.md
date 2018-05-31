# v4
Add the 'last' field. Round numerical/financial values to 15 decimal places using round().
https://gist.github.com/jackiekazil/6201722#1-round-decimal-using-round

# v3
Now actually write the "exchange_id" int. In v2 the column name was changed, but exchange names
were still being written instead of exchange ids.  

# v2
"exchange_name" str to "exchange_id" int. 

# v1
Bump version from 0 to 1. Start populating 'bid' and 'ask' fields. Unfortunately, forgot to update file name prefix
as well, so the file name still has "v0", even though the "version" field in the file is "1".