- `main.py`  
Simply call this script in a cron job or something and it will take care of everything else.
It will run the scripts below in the proper order.

- `3rd-domains.txt`  
Contains a list of common 3rd level domains, such as `co.uk`.

- `common_lib.py`  
Library with useful functions used across multiple python scripts.

- `bundle_import.py`  
Will copy all `*.json` files from `data/_in` to their bundle id dest folder e.g. 
`mv  data/_in/test.json  data/com/apple/notes/id_42.json`.

- `bundle_combine.py`  
Merges all `id_*.json` files from a bundle id into a single `combined.json`.
(run this script with one or multiple bundle ids as parameter.)

- `bundle_download.py`  
Download and cache app metadata from apple servers in de and en given a bundle id. Will also download the app icon and store it in the bundle id out folder.
(run this script with one or multiple bundle ids as parameter.)

- `html_bundle.py`  
Takes the `combined.json` file and generates the graphs and html file.
(run this script with one or multiple bundle ids as parameter.)

- `html_index.py`  
Create all pages for the app index and link to bundle id subpages.

- `html_root.py`  
Create main `index.html`.
